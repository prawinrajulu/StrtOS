"""
Portfolio Service — orchestration layer.

Coordinates: PortfolioRepository, all engines, MissionService (read-only),
GovernanceService (when required), EventPublisher.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.portfolio.models import (
    StrategicPortfolioModel, PortfolioMissionModel, PortfolioResourceModel,
    PortfolioConstraintModel, PortfolioAllocationModel, PortfolioEvaluationModel,
    PortfolioDecisionModel, PortfolioVersionModel, PortfolioCheckpointModel,
    PortfolioStatus, PortfolioDecisionStatus, PortfolioHealth, ResourceType,
    MissionPriority, PortfolioCheckpointDecision
)
from app.portfolio.schemas import (
    PortfolioCreate, PortfolioResponse, PortfolioEvaluationResponse,
    OptimizationRequest, OptimizationResponse, SimulationResponse,
    RebalanceRequest, RebalanceResponse, PortfolioOverviewResponse,
    ApproveDecisionRequest, PortfolioDecisionResponse
)
from app.portfolio.repository import PortfolioRepository
from app.portfolio.engine import (
    PortfolioConstraintEngine, PortfolioPriorityEngine,
    PortfolioEvaluationEngine, PortfolioRebalancingEngine, PortfolioCheckpointEngine
)
from app.portfolio.optimizer import PortfolioOptimizationEngine
from app.portfolio.allocator import ResourceAllocationEngine, ResourcePool
from app.core.events.publisher import event_publisher
from app.core.logging import logger


GOVERNANCE_RISK_THRESHOLD = 70.0       # risk ≥ 70 → require approval
GOVERNANCE_BUDGET_THRESHOLD = 0.90    # budget ≥ 90% used → require approval


class PortfolioService:
    """Core orchestrator for Autonomous Strategic Portfolio Management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PortfolioRepository(session)
        self.constraint_engine = PortfolioConstraintEngine()
        self.priority_engine = PortfolioPriorityEngine()
        self.eval_engine = PortfolioEvaluationEngine()
        self.rebalance_engine = PortfolioRebalancingEngine()
        self.checkpoint_engine = PortfolioCheckpointEngine()
        self.optimizer = PortfolioOptimizationEngine()
        self.allocator = ResourceAllocationEngine()

    # ─────────────────────────────────────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────────────────────────────────────

    async def create_portfolio(self, payload: PortfolioCreate, org_id: str) -> PortfolioResponse:
        portfolio = StrategicPortfolioModel(
            organization_id=org_id,
            objective_id=payload.objective_id,
            title=payload.title,
            summary=payload.summary or f"Strategic portfolio for '{payload.title}'.",
            status=PortfolioStatus.DRAFT,
            current_version="v1.0.0",
            health=PortfolioHealth.HEALTHY,
            expected_value=0.0,
            actual_value=0.0,
            portfolio_risk_score=20.0,
            confidence_score=90.0,
            total_budget=payload.total_budget,
            allocated_budget=0.0,
            scenario_type=payload.scenario_type
        )

        # Seed resources from payload
        for r_in in payload.resources:
            portfolio.resources.append(
                PortfolioResourceModel(
                    organization_id=org_id,
                    resource_type=r_in.resource_type,
                    available=r_in.available,
                    allocated=0.0,
                    remaining=r_in.available,
                    unit=r_in.unit,
                    period=r_in.period,
                    utilization_pct=0.0
                )
            )

        # Seed initial mission entries from payload
        for m_in in payload.missions:
            p_score = self.priority_engine.compute_priority_score(
                strategic_importance=70.0,
                business_impact=70.0,
                expected_value=m_in.expected_value,
                success_probability=m_in.success_probability,
                urgency=60.0,
                risk_score=20.0,
                resource_requirement=m_in.resource_requirement,
                max_expected_value=max(1.0, m_in.expected_value)
            )
            priority_label = self.priority_engine.classify_priority(p_score)
            portfolio.missions.append(
                PortfolioMissionModel(
                    organization_id=org_id,
                    mission_id=m_in.mission_id,
                    priority=MissionPriority[priority_label],
                    priority_score=p_score,
                    expected_value=m_in.expected_value,
                    success_probability=m_in.success_probability,
                    resource_requirement=m_in.resource_requirement,
                    selection_status="SELECTED",
                    selection_reason="Initial portfolio composition."
                )
            )

        # Initial plan version
        portfolio.versions.append(
            PortfolioVersionModel(
                organization_id=org_id,
                version="v1.0.0",
                reason="Initial portfolio creation.",
                risk_change=0.0,
                expected_value_change=0.0
            )
        )

        saved = await self.repo.create_portfolio(portfolio)

        await event_publisher.publish(
            event_type="portfolio.created",
            organization_id=org_id,
            message=f"Portfolio '{saved.title}' created.",
            metadata={"portfolio_id": saved.id, "version": saved.current_version}
        )

        return PortfolioResponse.model_validate(saved)

    # ─────────────────────────────────────────────────────────────────────────
    # READ
    # ─────────────────────────────────────────────────────────────────────────

    async def get_portfolio(self, portfolio_id: str, org_id: str) -> PortfolioResponse:
        p = await self.repo.get_portfolio_by_id(portfolio_id, org_id)
        if not p:
            raise KeyError(f"Portfolio '{portfolio_id}' not found.")
        return PortfolioResponse.model_validate(p)

    async def list_portfolios(
        self, org_id: str, status: Optional[PortfolioStatus] = None
    ) -> List[PortfolioResponse]:
        portfolios = await self.repo.list_portfolios(org_id, status=status)
        return [PortfolioResponse.model_validate(p) for p in portfolios]

    async def get_overview(self, org_id: str) -> PortfolioOverviewResponse:
        portfolios = await self.repo.list_portfolios(org_id)
        active = [p for p in portfolios if p.status == PortfolioStatus.ACTIVE]
        total_ev = sum(p.expected_value for p in portfolios)
        total_alloc = sum(p.allocated_budget for p in portfolios)

        missions_selected = sum(
            1 for p in portfolios for m in p.missions if m.selection_status == "SELECTED"
        )
        missions_deferred = sum(
            1 for p in portfolios for m in p.missions if m.selection_status == "DEFERRED"
        )
        missions_at_risk = sum(
            1 for p in portfolios if p.health in (PortfolioHealth.AT_RISK, PortfolioHealth.CRITICAL)
        )
        rebalancing_needed = sum(
            1 for p in portfolios if p.status == PortfolioStatus.REBALANCING
        )

        return PortfolioOverviewResponse(
            organization_id=org_id,
            total_portfolios=len(portfolios),
            active_portfolios=len(active),
            total_expected_value=round(total_ev, 2),
            total_allocated_budget=round(total_alloc, 2),
            missions_selected=missions_selected,
            missions_deferred=missions_deferred,
            missions_at_risk=missions_at_risk,
            portfolios_requiring_rebalance=rebalancing_needed,
            overall_health="HEALTHY" if not missions_at_risk else "AT_RISK"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # OPTIMIZE
    # ─────────────────────────────────────────────────────────────────────────

    async def optimize_portfolio(
        self, portfolio_id: str, payload: OptimizationRequest, org_id: str
    ) -> OptimizationResponse:
        p = await self.repo.get_portfolio_by_id(portfolio_id, org_id)
        if not p:
            raise KeyError(f"Portfolio '{portfolio_id}' not found.")

        mission_dicts = self._portfolio_missions_to_dicts(p)
        total_capacity = len(p.missions) + 5  # allow headroom

        result = self.optimizer.optimize(
            portfolio_id=portfolio_id,
            missions=mission_dicts,
            total_budget=p.total_budget,
            total_capacity=total_capacity,
            scenario_type=payload.scenario_type,
            budget_delta_pct=payload.budget_delta_pct,
            capacity_delta_pct=payload.capacity_delta_pct
        )

        # Update portfolio mission selection_status
        selected_ids = {m.mission_id for m in result.selected_missions}
        deferred_ids = {m.mission_id for m in result.deferred_missions}

        await self.repo.update_portfolio_fields(
            portfolio_id, org_id,
            status=PortfolioStatus.ACTIVE,
            expected_value=result.expected_portfolio_value,
            portfolio_risk_score=result.portfolio_risk_score,
            confidence_score=result.confidence,
            scenario_type=payload.scenario_type
        )

        await event_publisher.publish(
            event_type="portfolio.priority.updated",
            organization_id=org_id,
            message=f"Portfolio '{p.title}' optimized: {len(result.selected_missions)} selected, "
                    f"{len(result.deferred_missions)} deferred.",
            metadata={"portfolio_id": portfolio_id, "scenario": payload.scenario_type}
        )

        return result

    # ─────────────────────────────────────────────────────────────────────────
    # SIMULATE (side-effect free)
    # ─────────────────────────────────────────────────────────────────────────

    async def simulate_portfolio(
        self, portfolio_id: str, payload: OptimizationRequest, org_id: str
    ) -> SimulationResponse:
        p = await self.repo.get_portfolio_by_id(portfolio_id, org_id)
        if not p:
            raise KeyError(f"Portfolio '{portfolio_id}' not found.")

        mission_dicts = self._portfolio_missions_to_dicts(p)
        total_capacity = len(p.missions) + 5

        return self.optimizer.simulate_all_scenarios(
            portfolio_id=portfolio_id,
            missions=mission_dicts,
            total_budget=p.total_budget,
            total_capacity=total_capacity,
            budget_delta_pct=payload.budget_delta_pct,
            capacity_delta_pct=payload.capacity_delta_pct
        )

    # ─────────────────────────────────────────────────────────────────────────
    # EVALUATE / CHECKPOINT
    # ─────────────────────────────────────────────────────────────────────────

    async def evaluate_portfolio(self, portfolio_id: str, org_id: str) -> PortfolioEvaluationResponse:
        p = await self.repo.get_portfolio_by_id(portfolio_id, org_id)
        if not p:
            raise KeyError(f"Portfolio '{portfolio_id}' not found.")

        total_missions = len(p.missions)
        completed_missions = 0  # read from mission service in production

        result = self.eval_engine.evaluate(
            portfolio_id=portfolio_id,
            expected_value=p.expected_value,
            actual_value=p.actual_value,
            total_missions=total_missions,
            completed_missions=completed_missions,
            total_budget=p.total_budget,
            allocated_budget=p.allocated_budget,
            risk_score=p.portfolio_risk_score,
            confidence_score=p.confidence_score
        )

        # Persist evaluation snapshot
        await self.repo.add_evaluation(PortfolioEvaluationModel(
            organization_id=org_id,
            portfolio_id=portfolio_id,
            health=result.health,
            health_score=result.health_score,
            expected_value=result.expected_value,
            actual_value=result.actual_value,
            portfolio_roi=result.portfolio_roi,
            mission_success_rate=result.mission_success_rate,
            resource_efficiency=result.resource_efficiency,
            risk_score=result.risk_score,
            confidence_score=result.confidence_score,
            summary=result.summary
        ))

        # Update portfolio health
        await self.repo.update_portfolio_fields(portfolio_id, org_id, health=result.health)

        return result

    async def run_checkpoint(self, portfolio_id: str, org_id: str) -> dict:
        p = await self.repo.get_portfolio_by_id(portfolio_id, org_id)
        if not p:
            raise KeyError(f"Portfolio '{portfolio_id}' not found.")

        has_violations = self.constraint_engine.has_violations(p)
        progress = round(
            (sum(1 for m in p.missions if m.selection_status == "SELECTED") /
             max(1, len(p.missions))) * 100.0, 1
        )

        decision, notes = self.checkpoint_engine.evaluate(
            health=p.health,
            risk_score=p.portfolio_risk_score,
            progress_pct=progress,
            has_violations=has_violations
        )

        checkpoint = await self.repo.add_checkpoint(PortfolioCheckpointModel(
            organization_id=org_id,
            portfolio_id=portfolio_id,
            decision=decision,
            health_at_checkpoint=p.health,
            risk_at_checkpoint=p.portfolio_risk_score,
            progress_at_checkpoint=progress,
            notes=notes
        ))

        await event_publisher.publish(
            event_type="portfolio.checkpoint",
            organization_id=org_id,
            message=f"Portfolio '{p.title}' checkpoint: {decision.value}. {notes}",
            metadata={"portfolio_id": portfolio_id, "decision": decision.value}
        )

        return {
            "portfolio_id": portfolio_id,
            "decision": decision.value,
            "notes": notes,
            "progress_pct": progress,
            "checkpoint_id": checkpoint.id
        }

    # ─────────────────────────────────────────────────────────────────────────
    # REBALANCE
    # ─────────────────────────────────────────────────────────────────────────

    async def rebalance_portfolio(
        self, portfolio_id: str, payload: RebalanceRequest, org_id: str
    ) -> RebalanceResponse:
        p = await self.repo.get_portfolio_by_id(portfolio_id, org_id)
        if not p:
            raise KeyError(f"Portfolio '{portfolio_id}' not found.")

        new_version = self.rebalance_engine.compute_new_version(p.current_version)
        budget_util = (p.allocated_budget / max(1.0, p.total_budget)) * 100.0
        needs_governance = self.rebalance_engine.requires_governance(
            p.portfolio_risk_score, budget_util
        )

        governance_approval_id = None
        if needs_governance and not payload.force:
            # Create governance approval request
            try:
                from app.governance.service import GovernanceService
                from app.governance.schemas import ApprovalRequestCreate
                from app.governance.models import DecisionType
                gov_service = GovernanceService(self.session)
                approval = await gov_service.create_approval_request(
                    payload=ApprovalRequestCreate(
                        title=f"Portfolio Rebalance Approval — {p.title} → {new_version}",
                        description=payload.reason,
                        decision_type=DecisionType.STRATEGY_CHANGE,
                        requested_action=f"Rebalance portfolio '{p.title}' from {p.current_version} to {new_version}.",
                        ai_recommendation=f"Rebalance triggered: {payload.reason}",
                        ai_confidence_score=p.confidence_score,
                        evidence_count=len(p.missions),
                        is_reversible=True,
                        has_unavailable_evidence=False
                    ),
                    org_id=org_id,
                    creator_id="portfolio_engine"
                )
                governance_approval_id = approval.id
                await self.repo.update_portfolio_status(portfolio_id, org_id, PortfolioStatus.AWAITING_APPROVAL)
                await event_publisher.publish(
                    event_type="portfolio.governance.pending",
                    organization_id=org_id,
                    message=f"Portfolio rebalance requires governance approval.",
                    metadata={"portfolio_id": portfolio_id, "approval_id": governance_approval_id}
                )
            except Exception as e:
                logger.warning(f"Governance integration warning: {e}")

        # Create immutable version record
        prev_ev = p.expected_value
        prev_risk = p.portfolio_risk_score

        version_record = await self.repo.add_version(PortfolioVersionModel(
            organization_id=org_id,
            portfolio_id=portfolio_id,
            version=new_version,
            parent_version=p.current_version,
            reason=payload.reason,
            risk_change=0.0,
            expected_value_change=0.0
        ))

        # Update portfolio version
        new_status = PortfolioStatus.AWAITING_APPROVAL if needs_governance and not payload.force else PortfolioStatus.REBALANCING
        await self.repo.update_portfolio_fields(
            portfolio_id, org_id,
            current_version=new_version,
            status=new_status
        )

        await event_publisher.publish(
            event_type="portfolio.rebalancing",
            organization_id=org_id,
            message=f"Portfolio '{p.title}' rebalancing to {new_version}. Reason: {payload.reason}.",
            metadata={"portfolio_id": portfolio_id, "new_version": new_version}
        )

        return RebalanceResponse(
            portfolio_id=portfolio_id,
            new_version=new_version,
            parent_version=p.current_version,
            requires_governance=needs_governance,
            governance_approval_id=governance_approval_id,
            risk_change=0.0,
            expected_value_change=0.0,
            summary=f"Portfolio rebalanced to {new_version}. "
                    f"{'Governance approval pending.' if needs_governance and not payload.force else 'Rebalancing in progress.'}"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # APPROVE
    # ─────────────────────────────────────────────────────────────────────────

    async def approve_decision(
        self, portfolio_id: str, payload: ApproveDecisionRequest, org_id: str
    ) -> PortfolioDecisionResponse:
        decision = await self.repo.update_decision_status(
            payload.decision_id, org_id,
            PortfolioDecisionStatus.APPROVED,
            approved_by=payload.approved_by
        )
        if not decision:
            raise KeyError(f"Decision '{payload.decision_id}' not found.")

        await self.repo.update_portfolio_status(portfolio_id, org_id, PortfolioStatus.ACTIVE)

        await event_publisher.publish(
            event_type="portfolio.governance.approved",
            organization_id=org_id,
            message=f"Portfolio decision approved by {payload.approved_by}.",
            metadata={"portfolio_id": portfolio_id, "decision_id": payload.decision_id}
        )

        return PortfolioDecisionResponse.model_validate(decision)

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    def _portfolio_missions_to_dicts(self, portfolio: StrategicPortfolioModel) -> List[Dict[str, Any]]:
        return [
            {
                "mission_id": pm.mission_id,
                "title": f"Mission {pm.mission_id[:8]}",
                "priority_score": pm.priority_score,
                "expected_value": pm.expected_value,
                "success_probability": pm.success_probability,
                "resource_requirement": pm.resource_requirement,
                "risk_score": portfolio.portfolio_risk_score,
                "status": "ACTIVE"
            }
            for pm in portfolio.missions
        ]
