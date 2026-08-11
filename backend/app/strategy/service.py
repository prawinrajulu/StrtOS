import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.strategy.models import (
    StrategicObjectiveModel, StrategicMetricModel, StrategicConstraintModel,
    StrategicPlanModel, StrategicMilestoneModel, StrategicPlanVersionModel,
    ObjectiveLifecycle, HorizonType, ScenarioType
)
from app.strategy.schemas import (
    StrategicObjectiveCreate, StrategicObjectiveResponse,
    StrategicPlanCreate, StrategicPlanResponse, ScenarioResponse,
    StrategyEvaluationResponse, StrategyAdaptationRequest, StrategyAdaptationResponse,
    StrategyExplanationResponse
)
from app.strategy.repository import StrategyRepository
from app.strategy.engine import StrategicPlanningEngine
from app.core.events.publisher import event_publisher
from app.governance.service import GovernanceService

class StrategyService:
    """Core Service orchestrating Autonomous Strategic Intelligence workflows."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = StrategyRepository(session)
        self.engine = StrategicPlanningEngine()
        self.governance_service = GovernanceService(session)

    # ---------------------------------------------------------------------------
    # OBJECTIVES
    # ---------------------------------------------------------------------------
    async def create_objective(self, payload: StrategicObjectiveCreate, org_id: str) -> StrategicObjectiveResponse:
        obj = StrategicObjectiveModel(
            organization_id=org_id,
            title=payload.title,
            description=payload.description,
            category=payload.category,
            status=ObjectiveLifecycle.DRAFT,
            target_horizon=payload.target_horizon,
            baseline_value=payload.baseline_value,
            target_value=payload.target_value,
            current_value=payload.baseline_value,
            unit=payload.unit,
            confidence_score=90.0,
            risk_level="LOW"
        )
        saved = await self.repo.create_objective(obj)

        await event_publisher.publish(
            event_type="strategy.objective.created",
            organization_id=org_id,
            message=f"Strategic Objective '{saved.title}' created.",
            metadata={"objective_id": saved.id, "target_value": saved.target_value}
        )

        return StrategicObjectiveResponse.model_validate(saved)

    async def get_objective(self, objective_id: str, org_id: str) -> StrategicObjectiveResponse:
        obj = await self.repo.get_objective_by_id(objective_id, org_id)
        if not obj:
            raise KeyError(f"Strategic Objective '{objective_id}' not found.")
        return StrategicObjectiveResponse.model_validate(obj)

    async def list_objectives(self, org_id: str, status: Optional[str] = None) -> List[StrategicObjectiveResponse]:
        objectives = await self.repo.list_objectives(org_id, status=status)
        return [StrategicObjectiveResponse.model_validate(o) for o in objectives]

    # ---------------------------------------------------------------------------
    # STRATEGIC PLANS & SCENARIOS
    # ---------------------------------------------------------------------------
    async def generate_scenarios(self, objective_id: str, org_id: str) -> List[ScenarioResponse]:
        obj = await self.repo.get_objective_by_id(objective_id, org_id)
        if not obj:
            raise KeyError(f"Strategic Objective '{objective_id}' not found.")
        scenarios = self.engine.scenario_engine.generate_scenarios(obj)

        await event_publisher.publish(
            event_type="strategy.scenario.created",
            organization_id=org_id,
            message=f"Generated {len(scenarios)} strategic scenarios for '{obj.title}'.",
            metadata={"objective_id": objective_id}
        )

        return scenarios

    async def create_plan(self, payload: StrategicPlanCreate, org_id: str) -> StrategicPlanResponse:
        obj = await self.repo.get_objective_by_id(payload.objective_id, org_id)
        if not obj:
            raise KeyError(f"Strategic Objective '{payload.objective_id}' not found.")

        risk_score, risk_level = self.engine.risk_engine.calculate_risk(obj, payload.scenario_type)
        target_diff = obj.target_value - obj.baseline_value

        plan = StrategicPlanModel(
            organization_id=org_id,
            objective_id=payload.objective_id,
            version="1.0.0",
            scenario_type=payload.scenario_type,
            title=payload.title,
            summary=f"Autonomous strategic plan for '{obj.title}' under scenario '{payload.scenario_type.value}'.",
            horizon=payload.horizon,
            expected_value=round(obj.baseline_value + (target_diff * 0.95), 2),
            confidence_score=92.0,
            risk_score=risk_score,
            risk_level=risk_level,
            status="DRAFT"
        )

        # Generate milestones
        days = [30, 60, 90]
        for day in days:
            m_val = round(obj.baseline_value + (target_diff * (day / 90.0)), 2)
            plan.milestones.append(
                StrategicMilestoneModel(
                    organization_id=org_id,
                    title=f"{day}-Day Milestone Checkpoint",
                    horizon_day=day,
                    target_metric_value=m_val,
                    status="PENDING",
                    expected_outcome=f"Achieve {m_val} {obj.unit} target metric checkpoint.",
                    confidence_score=90.0
                )
            )

        # Generate initial version record
        plan.versions.append(
            StrategicPlanVersionModel(
                organization_id=org_id,
                version="1.0.0",
                parent_version=None,
                change_reason="Initial plan creation",
                performance_before=obj.baseline_value,
                performance_after=plan.expected_value,
                risk_before=0.0,
                risk_after=risk_score,
                created_by="AutonomousStrategicPlanner"
            )
        )

        saved_plan = await self.repo.create_plan(plan)

        await event_publisher.publish(
            event_type="strategy.created",
            organization_id=org_id,
            message=f"Strategic Plan '{saved_plan.title}' created (v1.0.0).",
            metadata={"plan_id": saved_plan.id, "risk_level": risk_level}
        )

        return await self.get_plan(saved_plan.id, org_id)

    async def get_plan(self, plan_id: str, org_id: str) -> StrategicPlanResponse:
        plan = await self.repo.get_plan_by_id(plan_id, org_id)
        if not plan:
            raise KeyError(f"Strategic Plan '{plan_id}' not found.")
        return StrategicPlanResponse.model_validate(plan)

    async def list_plans(self, org_id: str, objective_id: Optional[str] = None) -> List[StrategicPlanResponse]:
        plans = await self.repo.list_plans(org_id, objective_id=objective_id)
        return [StrategicPlanResponse.model_validate(p) for p in plans]

    # ---------------------------------------------------------------------------
    # EVALUATE, SIMULATE, ACTIVATE
    # ---------------------------------------------------------------------------
    async def evaluate_plan(self, plan_id: str, org_id: str) -> StrategyEvaluationResponse:
        plan = await self.repo.get_plan_by_id(plan_id, org_id)
        if not plan:
            raise KeyError(f"Strategic Plan '{plan_id}' not found.")
        obj = await self.repo.get_objective_by_id(plan.objective_id, org_id)

        is_valid, violations = self.engine.constraint_engine.evaluate_constraints(
            objective=obj,
            proposed_cost=1000.0,
            proposed_risk_score=plan.risk_score,
            proposed_days=90
        )

        await event_publisher.publish(
            event_type="strategy.evaluated",
            organization_id=org_id,
            message=f"Evaluated Strategic Plan '{plan.title}'. Valid: {is_valid}.",
            metadata={"plan_id": plan_id, "is_valid": is_valid}
        )

        return StrategyEvaluationResponse(
            plan_id=plan_id,
            objective_id=plan.objective_id,
            is_valid=is_valid,
            evaluation_status="PASSED" if is_valid else "CONSTRAINT_VIOLATION",
            violated_constraints=violations,
            risk_score=plan.risk_score,
            risk_level=plan.risk_level,
            recommendation="Plan complies with business constraints and is recommended for activation." if is_valid else "Resolve constraint violations prior to governance activation."
        )

    async def activate_plan(self, plan_id: str, org_id: str) -> StrategicPlanResponse:
        plan = await self.repo.get_plan_by_id(plan_id, org_id)
        if not plan:
            raise KeyError(f"Strategic Plan '{plan_id}' not found.")

        # Require Governance approval if risk is HIGH or CRITICAL
        if plan.risk_level in ["HIGH", "CRITICAL"]:
            plan.status = "GOVERNANCE_PENDING"
            await self.session.commit()
            await event_publisher.publish(
                event_type="strategy.governance.pending",
                organization_id=org_id,
                message=f"Strategic Plan '{plan.title}' requires mandatory human governance approval.",
                metadata={"plan_id": plan_id, "risk_level": plan.risk_level}
            )
            return await self.get_plan(plan_id, org_id)

        plan.status = "ACTIVE"
        await self.session.commit()

        # Update objective status
        obj = await self.repo.get_objective_by_id(plan.objective_id, org_id)
        if obj:
            obj.status = ObjectiveLifecycle.ACTIVE
            await self.session.commit()

        await event_publisher.publish(
            event_type="strategy.activated",
            organization_id=org_id,
            message=f"Strategic Plan '{plan.title}' activated.",
            metadata={"plan_id": plan_id}
        )

        return await self.get_plan(plan_id, org_id)

    async def get_explanation(self, plan_id: str, org_id: str) -> StrategyExplanationResponse:
        plan = await self.repo.get_plan_by_id(plan_id, org_id)
        if not plan:
            raise KeyError(f"Strategic Plan '{plan_id}' not found.")
        obj = await self.repo.get_objective_by_id(plan.objective_id, org_id)
        return self.engine.explanation_engine.explain_plan(plan, obj)

    async def adapt_plan(self, plan_id: str, payload: StrategyAdaptationRequest, org_id: str) -> StrategyAdaptationResponse:
        plan = await self.repo.get_plan_by_id(plan_id, org_id)
        if not plan:
            raise KeyError(f"Strategic Plan '{plan_id}' not found.")

        new_target, delta_pct, is_bounded = self.engine.adaptation_loop.compute_adaptation(
            current_target=plan.expected_value,
            actual_performance=payload.actual_performance,
            reason=payload.adaptation_reason
        )

        # Version bump
        v_parts = plan.version.split(".")
        new_ver_str = f"{v_parts[0]}.{int(v_parts[1]) + 1}.0"

        ver = StrategicPlanVersionModel(
            organization_id=org_id,
            plan_id=plan.id,
            version=new_ver_str,
            parent_version=plan.version,
            change_reason=f"Closed-loop adaptation: {payload.adaptation_reason}",
            performance_before=plan.expected_value,
            performance_after=new_target,
            risk_before=plan.risk_score,
            risk_after=plan.risk_score,
            created_by="AutonomousStrategyAdaptationEngine"
        )
        self.session.add(ver)

        plan.version = new_ver_str
        plan.expected_value = new_target
        await self.session.commit()

        await event_publisher.publish(
            event_type="strategy.adaptation.recommended",
            organization_id=org_id,
            message=f"Bounded adaptation executed for Strategic Plan '{plan.title}' (v{new_ver_str}).",
            metadata={"plan_id": plan_id, "delta_pct": delta_pct, "bounded": is_bounded}
        )

        return StrategyAdaptationResponse(
            plan_id=plan_id,
            new_version=new_ver_str,
            previous_performance=plan.expected_value,
            new_performance_target=new_target,
            adaptation_delta_pct=delta_pct,
            bounded=is_bounded,
            message=f"Strategy target adapted by {delta_pct}% (Bounded to MAX 10%)."
        )
