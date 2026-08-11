from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.experiments.models import ExperimentModel, ExperimentVariantModel, ExperimentStatus, ExperimentResult, VariantType
from app.experiments.schemas import ExperimentCreate, ExperimentMeasurementCreate
from app.experiments.repository import ExperimentRepository
from app.experiments.engine import ExperimentDesignEngine, ExperimentEvaluator
from app.learning.models import AgentPolicyModel, PolicyStatus
from app.governance.service import GovernanceService
from app.governance.schemas import ApprovalRequestCreate
from app.governance.models import DecisionType
from app.memory.service import MemoryService
from app.memory.schemas import OutcomeSubmissionRequest
import json
from app.core.redis import redis_manager

class ExperimentService:
    """
    Orchestrates continuous experimentation, controlled evaluation, auto-optimization proposals, and learning integration.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ExperimentRepository(db)

    async def create_experiment(self, org_id: str, payload: ExperimentCreate, user_id: str) -> Dict[str, Any]:
        # Validate policies exist
        stmt_c = select(AgentPolicyModel).where(AgentPolicyModel.id == payload.baseline_policy_id, AgentPolicyModel.organization_id == org_id)
        res_c = await self.db.execute(stmt_c)
        ctrl_pol = res_c.scalar_one_or_none()

        stmt_v = select(AgentPolicyModel).where(AgentPolicyModel.id == payload.variant_policy_id, AgentPolicyModel.organization_id == org_id)
        res_v = await self.db.execute(stmt_v)
        var_pol = res_v.scalar_one_or_none()

        if not ctrl_pol or not var_pol:
            raise ValueError("Invalid baseline or variant policy ID for organization")

        exp = await self.repo.create_experiment(org_id, payload, created_by=user_id)

        # Create control variant & variant A
        ctrl_variant = await self.repo.create_variant(exp.id, org_id, VariantType.CONTROL, "Control Policy", ctrl_pol.id, ctrl_pol.configuration)
        var_variant = await self.repo.create_variant(exp.id, org_id, VariantType.VARIANT_A, "Variant A Policy", var_pol.id, var_pol.configuration)

        await redis_manager.publish_event("experiments", json.dumps({
            "event_type": "experiment.created",
            "organization_id": org_id,
            "experiment_id": exp.id,
            "experiment_name": exp.experiment_name
        }))

        return {
            "experiment": exp,
            "control_variant": ctrl_variant,
            "variant": var_variant
        }

    async def design_experiment(self, exp_id: str, org_id: str, available_sample_size: int = 100) -> Dict[str, Any]:
        exp = await self.repo.get_experiment(exp_id, org_id)
        if not exp:
            raise ValueError("Experiment not found")

        variants = await self.repo.get_variants(exp_id, org_id)
        ctrl_var = next((v for v in variants if v.variant_type == VariantType.CONTROL), None)
        var_var = next((v for v in variants if v.variant_type == VariantType.VARIANT_A), None)

        design_res = ExperimentDesignEngine.design_experiment(
            baseline_policy_config=ctrl_var.configuration if ctrl_var else {},
            variant_policy_config=var_var.configuration if var_var else {},
            baseline_kpi=exp.baseline_value,
            target_kpi=exp.target_value,
            min_detectable_effect=exp.minimum_detectable_effect,
            available_sample_size=available_sample_size
        )

        exp.status = ExperimentStatus.DESIGNED
        await self.db.commit()

        await redis_manager.publish_event("experiments", json.dumps({
            "event_type": "experiment.designed",
            "organization_id": org_id,
            "experiment_id": exp_id,
            "design": design_res
        }))

        return design_res

    async def request_approval(self, exp_id: str, org_id: str, user_id: str) -> Dict[str, Any]:
        exp = await self.repo.get_experiment(exp_id, org_id)
        if not exp:
            raise ValueError("Experiment not found")

        gov_service = GovernanceService(self.db)
        app_req = await gov_service.create_approval_request(
            payload=ApprovalRequestCreate(
                title=f"Run Experiment: {exp.experiment_name}",
                description=exp.objective,
                decision_type=DecisionType.STRATEGY_CHANGE,
                requested_action=f"Run Experiment: {exp.experiment_name}",
                extra_metadata={"experiment_id": exp_id, "objective": exp.objective}
            ),
            org_id=org_id,
            creator_id=user_id
        )

        exp.status = ExperimentStatus.PENDING_APPROVAL
        exp.approval_id = app_req.id
        await self.db.commit()

        await redis_manager.publish_event("experiments", json.dumps({
            "event_type": "experiment.approval.pending",
            "organization_id": org_id,
            "experiment_id": exp_id,
            "approval_id": app_req.id
        }))

        return {"experiment_id": exp_id, "approval_id": app_req.id, "status": exp.status}

    async def start_experiment(self, exp_id: str, org_id: str, user_id: str) -> ExperimentModel:
        exp = await self.repo.get_experiment(exp_id, org_id)
        if not exp:
            raise ValueError("Experiment not found")

        exp.status = ExperimentStatus.RUNNING
        exp.started_at = datetime.now(timezone.utc)
        exp.approved_by = user_id
        await self.db.commit()

        await redis_manager.publish_event("experiments", json.dumps({
            "event_type": "experiment.started",
            "organization_id": org_id,
            "experiment_id": exp_id
        }))

        return exp

    async def record_execution_measurement(self, exp_id: str, org_id: str, payload: ExperimentMeasurementCreate) -> Dict[str, Any]:
        exp = await self.repo.get_experiment(exp_id, org_id)
        if not exp or exp.status not in (ExperimentStatus.RUNNING, ExperimentStatus.MEASURING):
            raise ValueError("Experiment is not active for measurement")

        variants = await self.repo.get_variants(exp_id, org_id)
        # Deterministically assign variant
        assigned_type = self.repo.assign_execution(org_id, exp.client_id, exp_id, payload.execution_id)
        matched_variant = next((v for v in variants if v.variant_type == assigned_type), variants[0])

        meas = await self.repo.record_measurement(exp_id, matched_variant.id, org_id, assigned_type, payload)

        # Update experiment sample size counters
        if assigned_type == VariantType.CONTROL:
            exp.control_sample_size += 1
        else:
            exp.variant_sample_size += 1
        exp.status = ExperimentStatus.MEASURING
        await self.db.commit()

        await redis_manager.publish_event("experiments", json.dumps({
            "event_type": "experiment.measurement.updated",
            "organization_id": org_id,
            "experiment_id": exp_id,
            "assigned_type": assigned_type,
            "kpi_value": payload.kpi_value
        }))

        return {
            "measurement_id": meas.id,
            "assigned_variant": assigned_type,
            "policy_id": matched_variant.policy_id
        }

    async def evaluate_experiment(self, exp_id: str, org_id: str) -> Dict[str, Any]:
        exp = await self.repo.get_experiment(exp_id, org_id)
        if not exp:
            raise ValueError("Experiment not found")

        ctrl_meas = await self.repo.get_measurements(exp_id, org_id, VariantType.CONTROL)
        var_meas = await self.repo.get_measurements(exp_id, org_id, VariantType.VARIANT_A)

        ctrl_kpis = [m.kpi_value for m in ctrl_meas]
        var_kpis = [m.kpi_value for m in var_meas]

        eval_res = ExperimentEvaluator.evaluate(
            control_measurements=ctrl_kpis,
            variant_measurements=var_kpis,
            min_detectable_effect=exp.minimum_detectable_effect,
            confidence_threshold=exp.confidence_threshold,
            min_sample_size=3
        )

        exp.result = eval_res["result"]
        exp.winner = eval_res["winner"]
        exp.confidence = eval_res["confidence"]

        if eval_res["result"] != ExperimentResult.INCONCLUSIVE:
            exp.status = ExperimentStatus.COMPLETED
            exp.completed_at = datetime.now(timezone.utc)

        await self.db.commit()

        # Connect lesson into Memory if conclusive win
        if eval_res["result"] == ExperimentResult.WIN:
            mem_service = MemoryService(self.db)
            await mem_service.submit_outcome(
                payload=OutcomeSubmissionRequest(
                    client_id=exp.client_id,
                    metric_name=exp.metric_name,
                    predicted_value=exp.baseline_value,
                    actual_value=eval_res["variant_mean"],
                    unit="%",
                    notes=f"Experiment '{exp.experiment_name}' won with {eval_res['percentage_improvement']}% improvement."
                ),
                org_id=org_id,
                creator_id="system-experiment-evaluator"
            )

        await redis_manager.publish_event("experiments", json.dumps({
            "event_type": "experiment.evaluated",
            "organization_id": org_id,
            "experiment_id": exp_id,
            "result": eval_res["result"],
            "winner": eval_res["winner"],
            "confidence": eval_res["confidence"]
        }))

        return eval_res

    async def propose_optimization(self, exp_id: str, org_id: str, user_id: str) -> Dict[str, Any]:
        exp = await self.repo.get_experiment(exp_id, org_id)
        if not exp or exp.result != ExperimentResult.WIN or not exp.winner:
            raise ValueError("Only completed winning experiments can generate an optimization proposal")

        variants = await self.repo.get_variants(exp_id, org_id)
        winning_var = next((v for v in variants if v.variant_type == exp.winner), None)
        if not winning_var:
            raise ValueError("Winning variant policy not found")

        # Create Governance request for activating winning policy as a new policy version
        gov_service = GovernanceService(self.db)
        app_req = await gov_service.create_approval_request(
            payload=ApprovalRequestCreate(
                title=f"Activate winning variant from experiment: {exp.experiment_name}",
                description=f"Experiment '{exp.experiment_name}' won with confidence {exp.confidence}%. Proposing policy activation.",
                decision_type=DecisionType.STRATEGY_CHANGE,
                requested_action=f"Activate Policy {winning_var.policy_id}",
                extra_metadata={
                    "experiment_id": exp_id,
                    "winning_policy_id": winning_var.policy_id,
                    "confidence": exp.confidence
                }
            ),
            org_id=org_id,
            creator_id=user_id
        )

        await redis_manager.publish_event("experiments", json.dumps({
            "event_type": "experiment.optimization.proposed",
            "organization_id": org_id,
            "experiment_id": exp_id,
            "winning_policy_id": winning_var.policy_id,
            "approval_id": app_req.id
        }))

        return {
            "experiment_id": exp_id,
            "winning_policy_id": winning_var.policy_id,
            "approval_id": app_req.id,
            "status": "PENDING_GOVERNANCE_APPROVAL"
        }
