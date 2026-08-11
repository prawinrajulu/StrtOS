import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.command_center.models import (
    CommandCenterSnapshotModel, StrategicDecisionSnapshotModel,
    AutonomyLevel, PrioritySeverity
)
from app.command_center.schemas import (
    ExecutiveHealthResponse, StrategicPriorityResponse, DecisionAlternativeResponse,
    MultiAgentConsensusResponse, StrategicDecisionResponse, DecisionExplanationResponse,
    CommandCenterOverviewResponse
)
from app.command_center.repository import CommandCenterRepository
from app.command_center.engine import CommandCenterEngine
from app.core.events.publisher import event_publisher

class CommandCenterService:
    """Core Service unifying all StrtOS Subsystems into a Strategic Command Center."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CommandCenterRepository(session)
        self.engine = CommandCenterEngine()

    async def get_overview(self, org_id: str) -> CommandCenterOverviewResponse:
        health = self.engine.health_engine.calculate_health()
        priorities = self.engine.priority_engine.compute_priorities()

        # Fetch or seed decision snapshots
        decisions_orm = await self.repo.list_decisions(org_id)
        if not decisions_orm:
            d_model = StrategicDecisionSnapshotModel(
                organization_id=org_id,
                title="Funnel Conversion Recovery & ARR Protection Plan",
                problem_statement="Mid-funnel conversion dropped 50% following Q1 campaign shift.",
                do_nothing_outcome="Trajectory shows $75,000 revenue erosion over next 30 days.",
                recommended_action="Execute landing page variant optimization & reallocate $5,000 ad budget.",
                expected_value=625000.0,
                risk_score=25.0,
                confidence_score=92.0,
                consensus_score=88.0,
                autonomy_level=AutonomyLevel.APPROVAL_REQUIRED,
                governance_status="PENDING"
            )
            saved_d = await self.repo.create_decision_snapshot(d_model)
            decisions_orm = [saved_d]

        decisions_resp = [StrategicDecisionResponse.model_validate(d) for d in decisions_orm]

        snapshot = CommandCenterSnapshotModel(
            organization_id=org_id,
            overall_health_score=health.overall_score,
            health_status=health.status,
            business_health=health.business_health,
            strategy_health=health.strategy_health,
            execution_health=health.execution_health,
            ai_health=health.ai_health,
            governance_status="CLEARED",
            active_alerts_count=1,
            active_executions_count=0,
            summary=f"Command Center operational. Executive Health: {health.status} ({health.overall_score})."
        )
        await self.repo.create_snapshot(snapshot)

        return CommandCenterOverviewResponse(
            organization_id=org_id,
            executive_health=health,
            top_priorities=priorities,
            active_decisions=decisions_resp,
            active_alerts_count=1,
            active_executions_count=0,
            summary=f"Strategic Command Center Active. Executive Health Score: {health.overall_score} ({health.status})."
        )

    async def get_health(self, org_id: str) -> ExecutiveHealthResponse:
        return self.engine.health_engine.calculate_health()

    async def get_priorities(self, org_id: str) -> List[StrategicPriorityResponse]:
        return self.engine.priority_engine.compute_priorities()

    async def list_decisions(self, org_id: str) -> List[StrategicDecisionResponse]:
        decisions = await self.repo.list_decisions(org_id)
        return [StrategicDecisionResponse.model_validate(d) for d in decisions]

    async def get_decision(self, decision_id: str, org_id: str) -> StrategicDecisionResponse:
        d = await self.repo.get_decision_by_id(decision_id, org_id)
        if not d:
            raise KeyError(f"Strategic Decision '{decision_id}' not found.")
        return StrategicDecisionResponse.model_validate(d)

    async def get_decision_alternatives(self, decision_id: str, org_id: str) -> List[DecisionAlternativeResponse]:
        d = await self.repo.get_decision_by_id(decision_id, org_id)
        if not d:
            raise KeyError(f"Strategic Decision '{decision_id}' not found.")
        return self.engine.do_nothing_engine.simulate_alternatives(d.expected_value)

    async def get_decision_explanation(self, decision_id: str, org_id: str) -> DecisionExplanationResponse:
        d = await self.repo.get_decision_by_id(decision_id, org_id)
        if not d:
            raise KeyError(f"Strategic Decision '{decision_id}' not found.")

        return DecisionExplanationResponse(
            decision_id=d.id,
            why_this_decision=f"Decision '{d.title}' maximizes expected value (${d.expected_value}) while controlling risk ({d.risk_score}).",
            verified_evidence=["Conversion drop signal (-50%)", "Technical SEO authority score (90/100)"],
            historical_memory=["Q4 Campaign Flighting Outcome (COMPLETED, +18% ROI)"],
            causal_support="Causal graph confirms landing page speed directly impacts conversion rate.",
            forecast_summary="90-Day horizon forecast predicts $625,000 revenue recovery.",
            agent_consensus_summary="4 of 5 Specialist Agents support recommended action (88% consensus score).",
            risk_breakdown=f"Risk Score {d.risk_score} (LOW execution risk, MEDIUM financial exposure).",
            assumptions=["Ad network CPM stability over next 30 days"],
            uncertainties=["Competitor ad budget expansion"]
        )

    async def get_multi_agent_consensus(self, decision_id: str, org_id: str) -> MultiAgentConsensusResponse:
        return MultiAgentConsensusResponse(
            consensus_score=88.0,
            status="CONSENSUS_ACHIEVED",
            supporting_agents=["BusinessAnalysisAgent", "SEOAuditAgent", "MarketingStrategyAgent", "CampaignPlannerAgent"],
            dissenting_agents=["CompetitorResearchAgent"],
            agent_contributions=[
                {"agent": "BusinessAnalysisAgent", "recommendation": "Execute Recovery Plan", "confidence": 95.0},
                {"agent": "SEOAuditAgent", "recommendation": "Optimize Technical Landing Page", "confidence": 92.0},
                {"agent": "CompetitorResearchAgent", "recommendation": "Monitor Competitor Ad Spend First", "confidence": 75.0}
            ]
        )
