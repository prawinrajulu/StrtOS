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
    PortfolioInitiativeModel, PortfolioRecommendationModel,
    PortfolioStatus, PortfolioDecisionStatus, PortfolioHealth, ResourceType,
    MissionPriority, PortfolioCheckpointDecision, RecommendationAction
)
from app.portfolio.schemas import (
    PortfolioCreate, PortfolioResponse, PortfolioEvaluationResponse,
    OptimizationRequest, OptimizationResponse, SimulationResponse,
    RebalanceRequest, RebalanceResponse, PortfolioOverviewResponse,
    ApproveDecisionRequest, PortfolioDecisionResponse,
    PortfolioInitiativeCreate, PortfolioInitiativeResponse, PortfolioRecommendationResponse,
    CapitalAllocationResponse, TradeoffResponse, TradeoffResult, DoNothingSimulationResponse
)
from app.portfolio.repository import PortfolioRepository
from app.portfolio.engine import (
    PortfolioConstraintEngine, PortfolioPriorityEngine,
    PortfolioEvaluationEngine, PortfolioRebalancingEngine, PortfolioCheckpointEngine,
    CapitalAllocationEngine, PortfolioTradeoffEngine, DoNothingSimulationEngine,
    PortfolioRecommendationEngine
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
        self.capital_engine = CapitalAllocationEngine()
        self.tradeoff_engine = PortfolioTradeoffEngine()
        self.donothing_engine = DoNothingSimulationEngine()
        self.recommendation_engine = PortfolioRecommendationEngine()

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

    # ─────────────────────────────────────────────────────────────────────────
    # v2.7.0 INITIATIVES & CAPITAL ALLOCATION & TRADE-OFFS & SIMULATION
    # ─────────────────────────────────────────────────────────────────────────

    async def create_initiative(
        self, portfolio_id: str, payload: PortfolioInitiativeCreate, org_id: str
    ) -> PortfolioInitiativeResponse:
        p = await self.repo.get_portfolio_by_id(portfolio_id, org_id)
        if not p:
            raise KeyError(f"Portfolio '{portfolio_id}' not found.")

        # Compute priority score
        score = self.priority_engine.compute_priority_score(
            strategic_importance=80.0 if payload.priority == MissionPriority.CRITICAL else 60.0,
            business_impact=75.0,
            expected_value=payload.expected_value,
            success_probability=payload.success_probability,
            urgency=70.0,
            risk_score=payload.risk_score,
            resource_requirement=payload.resource_cost or 1.0,
            max_expected_value=max(1.0, payload.expected_value)
        )

        init_model = PortfolioInitiativeModel(
            organization_id=org_id,
            portfolio_id=portfolio_id,
            title=payload.title,
            description=payload.description,
            strategic_objective_id=payload.strategic_objective_id,
            priority=payload.priority,
            priority_score=score,
            expected_value=payload.expected_value,
            expected_roi=payload.expected_roi,
            success_probability=payload.success_probability,
            risk_score=payload.risk_score,
            time_to_impact_days=payload.time_to_impact_days,
            resource_cost=payload.resource_cost,
            capital_budget=payload.capital_budget,
            status="PROPOSED",
            selection_reason=f"Priority score {score:.1f} calculated based on expected value ${payload.expected_value:,.0f} and success probability {payload.success_probability:.0f}%."
        )

        saved = await self.repo.add_initiative(init_model)

        await event_publisher.publish(
            event_type="portfolio.updated",
            organization_id=org_id,
            message=f"New initiative '{payload.title}' created in portfolio '{p.title}'.",
            metadata={"portfolio_id": portfolio_id, "initiative_id": saved.id}
        )

        return PortfolioInitiativeResponse.model_validate(saved)

    async def list_initiatives(self, portfolio_id: str, org_id: str) -> List[PortfolioInitiativeResponse]:
        inits = await self.repo.list_initiatives(portfolio_id, org_id)
        return [PortfolioInitiativeResponse.model_validate(i) for i in inits]

    async def get_initiative(self, initiative_id: str, org_id: str) -> PortfolioInitiativeResponse:
        init = await self.repo.get_initiative_by_id(initiative_id, org_id)
        if not init:
            raise KeyError(f"Initiative '{initiative_id}' not found.")
        return PortfolioInitiativeResponse.model_validate(init)

    async def get_capital_allocation(self, portfolio_id: str, org_id: str) -> CapitalAllocationResponse:
        p = await self.repo.get_portfolio_by_id(portfolio_id, org_id)
        if not p:
            raise KeyError(f"Portfolio '{portfolio_id}' not found.")

        # Combine initiatives and missions
        items = []
        for i in p.initiatives:
            items.append({
                "id": i.id,
                "title": i.title,
                "capital_budget": i.capital_budget or i.resource_cost,
                "expected_value": i.expected_value
            })
        for m in p.missions:
            items.append({
                "id": m.mission_id,
                "title": f"Mission {m.mission_id[:8]}",
                "resource_requirement": m.resource_requirement,
                "expected_value": m.expected_value
            })

        result = self.capital_engine.compute_allocation(
            portfolio_id=portfolio_id,
            total_budget=p.total_budget,
            current_spend=p.allocated_budget,
            initiatives_or_missions=items
        )

        return CapitalAllocationResponse(**result)

    async def get_tradeoffs(self, portfolio_id: str, org_id: str) -> TradeoffResponse:
        p = await self.repo.get_portfolio_by_id(portfolio_id, org_id)
        if not p:
            raise KeyError(f"Portfolio '{portfolio_id}' not found.")

        inits = p.initiatives
        tradeoffs = []

        if len(inits) >= 2:
            for i in range(len(inits) - 1):
                item_a = {
                    "id": inits[i].id,
                    "title": inits[i].title,
                    "expected_value": inits[i].expected_value,
                    "risk_score": inits[i].risk_score,
                    "resource_cost": inits[i].resource_cost or 1.0
                }
                item_b = {
                    "id": inits[i+1].id,
                    "title": inits[i+1].title,
                    "expected_value": inits[i+1].expected_value,
                    "risk_score": inits[i+1].risk_score,
                    "resource_cost": inits[i+1].resource_cost or 1.0
                }
                tr = self.tradeoff_engine.evaluate_tradeoff(item_a, item_b)
                tradeoffs.append(TradeoffResult(**tr))
        elif len(p.missions) >= 2:
            m1 = p.missions[0]
            m2 = p.missions[1]
            item_a = {
                "id": m1.mission_id,
                "title": f"Mission {m1.mission_id[:8]}",
                "expected_value": m1.expected_value,
                "risk_score": p.portfolio_risk_score,
                "resource_requirement": m1.resource_requirement or 1.0
            }
            item_b = {
                "id": m2.mission_id,
                "title": f"Mission {m2.mission_id[:8]}",
                "expected_value": m2.expected_value,
                "risk_score": p.portfolio_risk_score,
                "resource_requirement": m2.resource_requirement or 1.0
            }
            tr = self.tradeoff_engine.evaluate_tradeoff(item_a, item_b)
            tradeoffs.append(TradeoffResult(**tr))

        summary = f"Evaluated {len(tradeoffs)} strategic trade-off pairs for portfolio '{p.title}'."
        return TradeoffResponse(portfolio_id=portfolio_id, tradeoffs=tradeoffs, summary=summary)

    async def simulate_donothing(self, portfolio_id: str, org_id: str) -> DoNothingSimulationResponse:
        p = await self.repo.get_portfolio_by_id(portfolio_id, org_id)
        if not p:
            raise KeyError(f"Portfolio '{portfolio_id}' not found.")

        current_ev = p.expected_value or 100000.0
        opt_ev = current_ev * 1.25
        current_risk = p.portfolio_risk_score
        opt_risk = max(10.0, current_risk - 10.0)

        res = self.donothing_engine.simulate(
            portfolio_id=portfolio_id,
            current_ev=current_ev,
            optimized_ev=opt_ev,
            current_risk=current_risk,
            optimized_risk=opt_risk,
            total_budget=p.total_budget or 150000.0,
            allocated_budget=p.allocated_budget or 100000.0,
            mission_count=len(p.missions) or 5,
            completed_count=sum(1 for m in p.missions if m.selection_status == "SELECTED")
        )

        await event_publisher.publish(
            event_type="portfolio.simulation.completed",
            organization_id=org_id,
            message=f"Do-nothing simulation completed for portfolio '{p.title}'.",
            metadata={"portfolio_id": portfolio_id}
        )

        return DoNothingSimulationResponse(**res)

    async def generate_recommendations_for_portfolio(
        self, portfolio_id: str, org_id: str
    ) -> List[PortfolioRecommendationResponse]:
        p = await self.repo.get_portfolio_by_id(portfolio_id, org_id)
        if not p:
            raise KeyError(f"Portfolio '{portfolio_id}' not found.")

        recs = []
        # Generate for initiatives
        for init in p.initiatives:
            res = self.recommendation_engine.generate_recommendation(
                title=init.title,
                expected_value=init.expected_value,
                risk_score=init.risk_score,
                success_probability=init.success_probability,
                resource_efficiency=init.expected_value / max(1.0, init.resource_cost or 1.0),
                is_persistent_failure=(init.status == "FAILED"),
                initiative_id=init.id
            )
            model = PortfolioRecommendationModel(
                organization_id=org_id,
                portfolio_id=portfolio_id,
                initiative_id=init.id,
                recommendation_type=RecommendationAction(res["recommendation_type"]),
                title=res["title"],
                reason=res["reason"],
                expected_impact=res["expected_impact"],
                risk_level=res["risk_level"],
                requires_governance=res["requires_governance"],
                status="PROPOSED"
            )
            saved = await self.repo.add_recommendation(model)
            recs.append(saved)

            await event_publisher.publish(
                event_type="portfolio.recommendation.created",
                organization_id=org_id,
                message=f"Recommendation '{res['title']}' created for initiative '{init.title}'.",
                metadata={"portfolio_id": portfolio_id, "recommendation_id": saved.id}
            )

        # Fallback if no initiatives
        if not p.initiatives and p.missions:
            for pm in p.missions:
                res = self.recommendation_engine.generate_recommendation(
                    title=f"Mission {pm.mission_id[:8]}",
                    expected_value=pm.expected_value,
                    risk_score=p.portfolio_risk_score,
                    success_probability=pm.success_probability,
                    resource_efficiency=pm.expected_value / max(1.0, pm.resource_requirement or 1.0),
                    mission_id=pm.mission_id
                )
                model = PortfolioRecommendationModel(
                    organization_id=org_id,
                    portfolio_id=portfolio_id,
                    mission_id=pm.mission_id,
                    recommendation_type=RecommendationAction(res["recommendation_type"]),
                    title=res["title"],
                    reason=res["reason"],
                    expected_impact=res["expected_impact"],
                    risk_level=res["risk_level"],
                    requires_governance=res["requires_governance"],
                    status="PROPOSED"
                )
                saved = await self.repo.add_recommendation(model)
                recs.append(saved)

        return [PortfolioRecommendationResponse.model_validate(r) for r in recs]

    async def list_recommendations(self, portfolio_id: str, org_id: str) -> List[PortfolioRecommendationResponse]:
        recs = await self.repo.list_recommendations(portfolio_id, org_id)
        if not recs:
            return await self.generate_recommendations_for_portfolio(portfolio_id, org_id)
        return [PortfolioRecommendationResponse.model_validate(r) for r in recs]

    async def submit_recommendation_governance(
        self, recommendation_id: str, org_id: str
    ) -> PortfolioRecommendationResponse:
        rec = await self.repo.get_recommendation_by_id(recommendation_id, org_id)
        if not rec:
            raise KeyError(f"Recommendation '{recommendation_id}' not found.")

        # Submit to GovernanceService
        try:
            from app.governance.service import GovernanceService
            from app.governance.schemas import GovernanceApprovalCreate
            gov_service = GovernanceService(self.session)
            approval = await gov_service.create_approval_request(
                GovernanceApprovalCreate(
                    title=f"Portfolio Governance: {rec.title}",
                    decision_type="PORTFOLIO_RECOMMENDATION",
                    risk_score=85.0 if rec.risk_level == "CRITICAL" else 70.0,
                    risk_level=rec.risk_level,
                    description=rec.reason,
                    requested_action=rec.recommendation_type.value,
                    ai_recommendation=rec.reason,
                    ai_confidence_score=90.0,
                    evidence_count=3,
                    has_policy_violations=False,
                    has_unavailable_evidence=False
                ),
                org_id=org_id,
                creator_id="portfolio_engine"
            )
            updated = await self.repo.update_recommendation_status(
                recommendation_id, org_id, "SUBMITTED", governance_approval_id=approval.id
            )

            await event_publisher.publish(
                event_type="portfolio.governance.pending",
                organization_id=org_id,
                message=f"Recommendation '{rec.title}' submitted for governance approval.",
                metadata={"recommendation_id": recommendation_id, "approval_id": approval.id}
            )

            return PortfolioRecommendationResponse.model_validate(updated)
        except Exception as e:
            logger.warning(f"Governance submission exception: {e}")
            updated = await self.repo.update_recommendation_status(recommendation_id, org_id, "SUBMITTED")
            return PortfolioRecommendationResponse.model_validate(updated)
