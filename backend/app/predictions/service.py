from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.predictions.models import PredictionModel, ScenarioType, PredictionStatus
from app.predictions.schemas import (
    PredictionCreate, PredictionResponse, PredictionListResponse,
    ScenarioGenerateRequest, ScenarioListResponse,
    WhatIfSimulationRequest, WhatIfSimulationResponse, AccuracyAssessmentResponse
)
from app.predictions.repository import PredictionRepository
from app.predictions.scenario_engine import ScenarioEngine
from app.predictions.accuracy import evaluate_prediction_accuracy
from app.governance.models import RiskLevel, DecisionType, ApprovalStatus
from app.governance.service import GovernanceService
from app.governance.schemas import ApprovalRequestCreate
from app.memory.retrieval import MemoryRetrievalEngine
from app.core.events.publisher import event_publisher
from app.core.logging import logger

class PredictionService:
    """
    Core Predictive Decision Intelligence Service managing scenario simulation,
    what-if analysis, governance integration, and accuracy tracking with multi-tenant isolation.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PredictionRepository(session)
        self.retrieval_engine = MemoryRetrievalEngine(session)

    async def create_prediction(
        self,
        payload: PredictionCreate,
        org_id: str,
        creator_id: Optional[str] = None
    ) -> PredictionResponse:
        prediction = PredictionModel(
            organization_id=org_id,
            client_id=payload.client_id,
            workflow_id=payload.workflow_id,
            report_id=payload.report_id,
            approval_id=payload.approval_id,
            scenario_type=payload.scenario_type,
            scenario_name=payload.scenario_name.strip(),
            objective=payload.objective,
            metric_name=payload.metric_name,
            predicted_value=payload.predicted_value,
            lower_bound=payload.lower_bound,
            upper_bound=payload.upper_bound,
            unit=payload.unit,
            currency=payload.currency,
            confidence_score=payload.confidence_score,
            risk_score=payload.risk_score,
            risk_level=payload.risk_level,
            evidence_count=payload.evidence_count,
            memory_count=payload.memory_count,
            provider=payload.provider,
            model=payload.model,
            assumptions=payload.assumptions or [],
            evidence_references=payload.evidence_references or [],
            memory_references=payload.memory_references or [],
            prediction_status=PredictionStatus.GENERATED,
            created_by=creator_id,
            valid_until=datetime.now(timezone.utc) + timedelta(days=90),
            extra_metadata=payload.extra_metadata or {}
        )

        created = await self.repo.create(prediction)
        await self.session.commit()
        await self.session.refresh(created)

        # SSE Event
        await event_publisher.publish(
            event_type="prediction.created",
            workflow_id=created.workflow_id,
            organization_id=org_id,
            status=created.prediction_status.value,
            metadata={"prediction_id": created.id, "scenario_type": created.scenario_type.value}
        )

        return PredictionResponse.model_validate(created)

    async def get_prediction(self, prediction_id: str, org_id: str) -> PredictionResponse:
        pred = await self.repo.get_by_id_and_org(prediction_id, org_id)
        if not pred:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction record not found.")
        return PredictionResponse.model_validate(pred)

    async def list_predictions(
        self,
        org_id: str,
        page: int = 1,
        page_size: int = 20,
        client_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        scenario_type: Optional[ScenarioType] = None,
        prediction_status: Optional[PredictionStatus] = None,
        search: Optional[str] = None
    ) -> PredictionListResponse:
        skip = (page - 1) * page_size
        preds, total = await self.repo.list_by_org(
            org_id=org_id,
            client_id=client_id,
            workflow_id=workflow_id,
            scenario_type=scenario_type,
            prediction_status=prediction_status,
            search=search,
            skip=skip,
            limit=page_size
        )
        dtos = [PredictionResponse.model_validate(p) for p in preds]
        return PredictionListResponse(predictions=dtos, total=total, page=page, page_size=page_size)

    async def generate_scenarios(
        self,
        payload: ScenarioGenerateRequest,
        org_id: str,
        creator_id: Optional[str] = None
    ) -> ScenarioListResponse:
        # Retrieve historical memories for client context
        historical_memories = []
        try:
            mem_results = await self.retrieval_engine.retrieve_relevant_memories(
                organization_id=org_id,
                client_id=payload.client_id,
                query=payload.objective or payload.metric_name,
                limit=5
            )
            historical_memories = [
                {
                    "memory_id": m.id,
                    "title": m.title,
                    "structured_data": m.structured_data,
                    "confidence_score": m.confidence_score
                }
                for m, s in mem_results
            ]
        except Exception as e:
            logger.warning(f"Memory retrieval skipped in scenario generator: {e}")

        scenario_dicts = ScenarioEngine.generate_default_scenarios(
            metric_name=payload.metric_name,
            monthly_budget=payload.monthly_budget,
            timeline_days=payload.timeline_days,
            historical_memories=historical_memories,
            objective=payload.objective
        )

        created_dtos = []
        scenario_group_id = f"scen-group-{int(datetime.now(timezone.utc).timestamp())}"

        for s_dict in scenario_dicts:
            p_model = PredictionModel(
                organization_id=org_id,
                client_id=payload.client_id,
                workflow_id=payload.workflow_id,
                scenario_id=scenario_group_id,
                scenario_type=s_dict["scenario_type"],
                scenario_name=s_dict["scenario_name"],
                objective=s_dict["objective"],
                metric_name=s_dict["metric_name"],
                predicted_value=s_dict["predicted_value"],
                lower_bound=s_dict["lower_bound"],
                upper_bound=s_dict["upper_bound"],
                unit=s_dict["unit"],
                currency=s_dict["currency"],
                confidence_score=s_dict["confidence_score"],
                risk_score=s_dict["risk_score"],
                risk_level=s_dict["risk_level"],
                evidence_count=s_dict["evidence_count"],
                memory_count=s_dict["memory_count"],
                assumptions=s_dict["assumptions"],
                evidence_references=s_dict["evidence_references"],
                memory_references=s_dict["memory_references"],
                prediction_status=PredictionStatus.GENERATED,
                created_by=creator_id,
                valid_until=datetime.now(timezone.utc) + timedelta(days=payload.timeline_days)
            )
            created = await self.repo.create(p_model)
            created_dtos.append(PredictionResponse.model_validate(created))

        await self.session.commit()

        # SSE Event
        await event_publisher.publish(
            event_type="prediction.scenario.created",
            workflow_id=payload.workflow_id,
            organization_id=org_id,
            status="GENERATED",
            metadata={"scenario_group_id": scenario_group_id, "scenario_count": len(created_dtos)}
        )

        return ScenarioListResponse(
            scenarios=created_dtos,
            recommended_scenario_type=ScenarioType.BALANCED,
            summary=f"Generated 3 decision scenarios for {payload.metric_name} with BALANCED scenario recommended."
        )

    async def simulate_what_if(
        self,
        payload: WhatIfSimulationRequest,
        org_id: str
    ) -> WhatIfSimulationResponse:
        # Deterministic simulation model
        ratio = payload.simulated_budget / max(1.0, payload.current_budget)
        
        baseline_pred = 3.5
        simulated_pred = round(baseline_pred * (ratio ** 0.65), 2)
        delta_val = round(simulated_pred - baseline_pred, 2)
        delta_pct = round(((simulated_pred - baseline_pred) / baseline_pred) * 100.0, 1)

        sim_risk_score = min(100.0, round(45.0 * (ratio ** 0.8), 1))
        sim_risk_lvl = RiskLevel.HIGH if sim_risk_score > 60.0 else RiskLevel.MEDIUM

        response = WhatIfSimulationResponse(
            baseline={
                "budget": payload.current_budget,
                "metric_name": payload.metric_name,
                "predicted_value": baseline_pred,
                "unit": "x"
            },
            simulated_scenario={
                "budget": payload.simulated_budget,
                "metric_name": payload.metric_name,
                "predicted_value": simulated_pred,
                "unit": "x"
            },
            delta={
                "value_delta": delta_val,
                "percentage_delta": delta_pct,
                "budget_delta": payload.simulated_budget - payload.current_budget
            },
            confidence_score=85.0,
            risk_score=sim_risk_score,
            risk_level=sim_risk_lvl,
            assumptions=[
                f"Simulated budget change from ${payload.current_budget:,.0f} to ${payload.simulated_budget:,.0f}",
                f"Diminishing returns exponent (0.65) applied across {payload.timeline_days} days",
                "Channel attribution & auction CPMs remain constant"
            ]
        )

        await event_publisher.publish(
            event_type="prediction.simulation.completed",
            organization_id=org_id,
            status="COMPLETED",
            metadata={"simulated_budget": payload.simulated_budget, "predicted_value": simulated_pred}
        )

        return response

    async def submit_prediction_for_approval(
        self,
        prediction_id: str,
        org_id: str,
        current_user: Any
    ) -> PredictionResponse:
        pred = await self.repo.get_by_id_and_org(prediction_id, org_id)
        if not pred:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found.")

        # Create Governance Approval Request
        gov_service = GovernanceService(self.session)
        approval_req = await gov_service.create_approval_request(
            payload=ApprovalRequestCreate(
                workflow_id=pred.workflow_id,
                client_id=pred.client_id,
                report_id=pred.report_id,
                title=f"Prediction Approval Required: {pred.scenario_name}",
                description=f"Approve predicted {pred.metric_name} of {pred.predicted_value}{pred.unit} (Range: {pred.lower_bound}–{pred.upper_bound}{pred.unit}).",
                decision_type=DecisionType.STRATEGY_CHANGE,
                requested_action=f"Adopt {pred.scenario_name} for strategy execution",
                ai_recommendation=f"Recommended {pred.scenario_type.value} scenario with {pred.confidence_score}% confidence.",
                ai_confidence_score=pred.confidence_score,
                evidence_count=pred.evidence_count
            ),
            org_id=org_id,
            creator_id=current_user.id
        )

        pred.approval_id = approval_req.id
        pred.prediction_status = PredictionStatus.PENDING_APPROVAL
        updated = await self.repo.update(pred)
        await self.session.commit()

        await event_publisher.publish(
            event_type="prediction.approval.pending",
            workflow_id=updated.workflow_id,
            organization_id=org_id,
            status="PENDING_APPROVAL",
            metadata={"prediction_id": updated.id, "approval_id": approval_req.id}
        )

        return PredictionResponse.model_validate(updated)
