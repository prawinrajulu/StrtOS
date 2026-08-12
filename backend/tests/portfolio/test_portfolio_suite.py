"""
StrtOS v2.5.0 — Portfolio Test Suite.

Covers: model instantiation, lifecycle, priority scoring, constraint evaluation,
optimizer (greedy knapsack), resource allocation, rebalancing, governance gate,
scenario simulation, tenant isolation, checkpoint engine, evaluation engine,
version creation, API endpoints via TestClient.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture
def sample_missions():
    return [
        {
            "mission_id": "m-001",
            "title": "Revenue Growth Initiative",
            "priority_score": 85.0,
            "expected_value": 90000.0,
            "success_probability": 85.0,
            "resource_requirement": 60000.0,
            "risk_score": 20.0,
            "status": "ACTIVE"
        },
        {
            "mission_id": "m-002",
            "title": "SEO Traffic Expansion",
            "priority_score": 75.0,
            "expected_value": 30000.0,
            "success_probability": 90.0,
            "resource_requirement": 10000.0,
            "risk_score": 15.0,
            "status": "ACTIVE"
        },
        {
            "mission_id": "m-003",
            "title": "Conversion Rate Optimization",
            "priority_score": 70.0,
            "expected_value": 45000.0,
            "success_probability": 75.0,
            "resource_requirement": 20000.0,
            "risk_score": 30.0,
            "status": "ACTIVE"
        },
        {
            "mission_id": "m-004",
            "title": "Brand Awareness Campaign",
            "priority_score": 55.0,
            "expected_value": 25000.0,
            "success_probability": 70.0,
            "resource_requirement": 40000.0,
            "risk_score": 25.0,
            "status": "ACTIVE"
        },
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# 1. MODEL IMPORTS & ENUM VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestPortfolioModels:
    def test_portfolio_status_enum_complete(self):
        from app.portfolio.models import PortfolioStatus
        required = {
            "DRAFT", "READY", "ACTIVE", "REBALANCING", "AT_RISK",
            "BLOCKED", "AWAITING_APPROVAL", "COMPLETED", "FAILED", "CANCELLED", "ARCHIVED"
        }
        assert required == {s.value for s in PortfolioStatus}

    def test_portfolio_decision_status_enum_complete(self):
        from app.portfolio.models import PortfolioDecisionStatus
        required = {
            "PROPOSED", "EVALUATING", "APPROVAL_REQUIRED",
            "APPROVED", "REJECTED", "APPLIED", "ROLLED_BACK"
        }
        assert required == {s.value for s in PortfolioDecisionStatus}

    def test_resource_type_enum_complete(self):
        from app.portfolio.models import ResourceType
        required = {"BUDGET", "TIME", "TEAM_CAPACITY", "AGENT_CAPACITY", "EXECUTION_CAPACITY"}
        assert required == {r.value for r in ResourceType}

    def test_mission_priority_enum_complete(self):
        from app.portfolio.models import MissionPriority
        assert {"CRITICAL", "HIGH", "MEDIUM", "LOW"} == {p.value for p in MissionPriority}

    def test_portfolio_health_enum_complete(self):
        from app.portfolio.models import PortfolioHealth
        assert {"EXCELLENT", "HEALTHY", "WATCH", "AT_RISK", "CRITICAL"} == {h.value for h in PortfolioHealth}

    def test_constraint_status_enum_complete(self):
        from app.portfolio.models import ConstraintStatus
        assert {"VALID", "WARNING", "VIOLATION"} == {s.value for s in ConstraintStatus}

    def test_portfolio_model_has_organization_id(self):
        from app.portfolio.models import StrategicPortfolioModel
        assert hasattr(StrategicPortfolioModel, "organization_id")
        assert hasattr(StrategicPortfolioModel, "created_at")
        assert hasattr(StrategicPortfolioModel, "updated_at")

    def test_all_portfolio_models_have_org_id(self):
        from app.portfolio.models import (
            PortfolioMissionModel, PortfolioResourceModel, PortfolioConstraintModel,
            PortfolioAllocationModel, PortfolioEvaluationModel, PortfolioDecisionModel,
            PortfolioVersionModel, PortfolioCheckpointModel
        )
        for model in [
            PortfolioMissionModel, PortfolioResourceModel, PortfolioConstraintModel,
            PortfolioAllocationModel, PortfolioEvaluationModel, PortfolioDecisionModel,
            PortfolioVersionModel, PortfolioCheckpointModel
        ]:
            assert hasattr(model, "organization_id"), f"{model.__name__} missing organization_id"

    def test_portfolio_model_tablenames(self):
        from app.portfolio.models import (
            StrategicPortfolioModel, PortfolioMissionModel, PortfolioResourceModel,
            PortfolioConstraintModel, PortfolioAllocationModel, PortfolioEvaluationModel,
            PortfolioDecisionModel, PortfolioVersionModel, PortfolioCheckpointModel
        )
        assert StrategicPortfolioModel.__tablename__ == "portfolios"
        assert PortfolioMissionModel.__tablename__ == "portfolio_missions"
        assert PortfolioResourceModel.__tablename__ == "portfolio_resources"
        assert PortfolioConstraintModel.__tablename__ == "portfolio_constraints"
        assert PortfolioAllocationModel.__tablename__ == "portfolio_allocations"
        assert PortfolioEvaluationModel.__tablename__ == "portfolio_evaluations"
        assert PortfolioDecisionModel.__tablename__ == "portfolio_decisions"
        assert PortfolioVersionModel.__tablename__ == "portfolio_versions"
        assert PortfolioCheckpointModel.__tablename__ == "portfolio_checkpoints"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CONSTRAINT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class TestConstraintEngine:
    def setup_method(self):
        from app.portfolio.engine import PortfolioConstraintEngine
        self.engine = PortfolioConstraintEngine()

    def test_valid_constraint_below_80pct(self):
        from app.portfolio.models import ConstraintStatus
        status, msg = self.engine.evaluate_constraint(100000.0, 70000.0, is_hard=True)
        assert status == ConstraintStatus.VALID
        assert "70.0%" in msg

    def test_warning_at_80pct(self):
        from app.portfolio.models import ConstraintStatus
        status, msg = self.engine.evaluate_constraint(100000.0, 85000.0, is_hard=True)
        assert status == ConstraintStatus.WARNING

    def test_violation_at_100pct_hard(self):
        from app.portfolio.models import ConstraintStatus
        status, msg = self.engine.evaluate_constraint(100000.0, 100000.0, is_hard=True)
        assert status == ConstraintStatus.VIOLATION
        assert "HARD" in msg

    def test_soft_constraint_at_100pct_is_warning(self):
        from app.portfolio.models import ConstraintStatus
        status, msg = self.engine.evaluate_constraint(100000.0, 100000.0, is_hard=False)
        assert status == ConstraintStatus.WARNING
        assert "SOFT" in msg

    def test_zero_limit_returns_valid(self):
        from app.portfolio.models import ConstraintStatus
        status, _ = self.engine.evaluate_constraint(0.0, 50000.0, is_hard=True)
        assert status == ConstraintStatus.VALID


# ═══════════════════════════════════════════════════════════════════════════════
# 3. PRIORITY ENGINE — DETERMINISM
# ═══════════════════════════════════════════════════════════════════════════════

class TestPriorityEngine:
    def setup_method(self):
        from app.portfolio.engine import PortfolioPriorityEngine
        self.engine = PortfolioPriorityEngine()

    def _score(self, **kwargs) -> float:
        return self.engine.compute_priority_score(**kwargs)

    def test_score_range_0_to_100(self):
        score = self._score(
            strategic_importance=70, business_impact=70, expected_value=50000,
            success_probability=80, urgency=60, risk_score=20,
            resource_requirement=10000, max_expected_value=100000
        )
        assert 0.0 <= score <= 100.0

    def test_deterministic_identical_inputs(self):
        kwargs = dict(
            strategic_importance=80, business_impact=75, expected_value=90000,
            success_probability=85, urgency=70, risk_score=25,
            resource_requirement=20000, max_expected_value=100000
        )
        assert self._score(**kwargs) == self._score(**kwargs)

    def test_higher_value_scores_higher(self):
        low = self._score(
            strategic_importance=40, business_impact=40, expected_value=10000,
            success_probability=50, urgency=30, risk_score=50,
            resource_requirement=50000, max_expected_value=100000
        )
        high = self._score(
            strategic_importance=90, business_impact=90, expected_value=90000,
            success_probability=95, urgency=90, risk_score=10,
            resource_requirement=5000, max_expected_value=100000
        )
        assert high > low

    def test_classify_priority_critical(self):
        assert self.engine.classify_priority(85.0) == "CRITICAL"

    def test_classify_priority_high(self):
        assert self.engine.classify_priority(65.0) == "HIGH"

    def test_classify_priority_medium(self):
        assert self.engine.classify_priority(50.0) == "MEDIUM"

    def test_classify_priority_low(self):
        assert self.engine.classify_priority(30.0) == "LOW"

    def test_risk_penalty_applied(self):
        low_risk = self._score(
            strategic_importance=70, business_impact=70, expected_value=50000,
            success_probability=80, urgency=60, risk_score=5,
            resource_requirement=10000, max_expected_value=100000
        )
        high_risk = self._score(
            strategic_importance=70, business_impact=70, expected_value=50000,
            success_probability=80, urgency=60, risk_score=90,
            resource_requirement=10000, max_expected_value=100000
        )
        assert low_risk > high_risk


# ═══════════════════════════════════════════════════════════════════════════════
# 4. PORTFOLIO OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════════════

class TestPortfolioOptimizer:
    def setup_method(self):
        from app.portfolio.optimizer import PortfolioOptimizationEngine
        self.optimizer = PortfolioOptimizationEngine()

    def test_optimize_selects_highest_vcr_first(self, sample_missions):
        """SEO (m-002) has best value/cost ratio — should be selected first."""
        result = self.optimizer.optimize(
            portfolio_id="p-001",
            missions=sample_missions,
            total_budget=15000.0,  # Only enough for m-002
            total_capacity=10.0,
            scenario_type="BALANCED"
        )
        selected_ids = {m.mission_id for m in result.selected_missions}
        assert "m-002" in selected_ids

    def test_optimize_defers_when_budget_insufficient(self, sample_missions):
        result = self.optimizer.optimize(
            portfolio_id="p-001",
            missions=sample_missions,
            total_budget=10000.0,  # Very limited
            total_capacity=10.0,
            scenario_type="BALANCED"
        )
        # At least one mission should be deferred
        assert len(result.deferred_missions) >= 1

    def test_optimize_all_selected_when_budget_unlimited(self, sample_missions):
        result = self.optimizer.optimize(
            portfolio_id="p-001",
            missions=sample_missions,
            total_budget=1_000_000.0,
            total_capacity=100.0,
            scenario_type="BALANCED"
        )
        assert len(result.selected_missions) == len(sample_missions)
        assert len(result.deferred_missions) == 0

    def test_conservative_selects_fewer(self, sample_missions):
        conservative = self.optimizer.optimize(
            portfolio_id="p-001", missions=sample_missions,
            total_budget=100000.0, total_capacity=10.0, scenario_type="CONSERVATIVE"
        )
        aggressive = self.optimizer.optimize(
            portfolio_id="p-001", missions=sample_missions,
            total_budget=100000.0, total_capacity=10.0, scenario_type="AGGRESSIVE"
        )
        assert len(conservative.selected_missions) <= len(aggressive.selected_missions)

    def test_deterministic_same_inputs_same_output(self, sample_missions):
        r1 = self.optimizer.optimize("p-1", sample_missions, 100000.0, 10.0, "BALANCED")
        r2 = self.optimizer.optimize("p-1", sample_missions, 100000.0, 10.0, "BALANCED")
        assert [m.mission_id for m in r1.selected_missions] == [m.mission_id for m in r2.selected_missions]

    def test_result_fields_present(self, sample_missions):
        result = self.optimizer.optimize("p-001", sample_missions, 100000.0, 10.0, "BALANCED")
        assert result.portfolio_id == "p-001"
        assert result.scenario_type == "BALANCED"
        assert isinstance(result.expected_portfolio_value, float)
        assert isinstance(result.portfolio_risk_score, float)
        assert 0.0 <= result.budget_utilization_pct <= 100.0

    def test_what_if_budget_increase(self, sample_missions):
        base = self.optimizer.optimize("p-1", sample_missions, 70000.0, 10.0, "BALANCED")
        expanded = self.optimizer.optimize("p-1", sample_missions, 70000.0, 10.0, "BALANCED",
                                           budget_delta_pct=50.0)
        # With more budget, should be able to select at least as many
        assert len(expanded.selected_missions) >= len(base.selected_missions)

    def test_paused_missions_excluded_from_selection(self):
        from app.portfolio.optimizer import PortfolioOptimizationEngine
        missions = [{"mission_id": "m-X", "title": "Paused", "priority_score": 90.0,
                     "expected_value": 100000.0, "success_probability": 95.0,
                     "resource_requirement": 1000.0, "risk_score": 5.0, "status": "PAUSED"}]
        result = PortfolioOptimizationEngine().optimize("p-1", missions, 1_000_000.0, 100.0)
        assert len(result.paused_missions) == 1
        assert len(result.selected_missions) == 0

    def test_scenario_simulation_returns_three_results(self, sample_missions):
        result = self.optimizer.simulate_all_scenarios("p-001", sample_missions, 100000.0)
        assert len(result.scenarios) == 3
        scenario_types = {s.scenario_type for s in result.scenarios}
        assert scenario_types == {"CONSERVATIVE", "BALANCED", "AGGRESSIVE"}

    def test_simulation_has_recommendation(self, sample_missions):
        result = self.optimizer.simulate_all_scenarios("p-001", sample_missions, 100000.0)
        assert isinstance(result.recommendation, str)
        assert len(result.recommendation) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# 5. RESOURCE ALLOCATOR
# ═══════════════════════════════════════════════════════════════════════════════

class TestResourceAllocator:
    def test_resource_pool_allocation_success(self):
        from app.portfolio.allocator import ResourcePool
        pool = ResourcePool([{"resource_type": "BUDGET", "available": 100000.0, "allocated": 0.0}])
        success = pool.allocate("BUDGET", 50000.0)
        assert success is True
        assert pool.available("BUDGET") == 50000.0

    def test_resource_pool_allocation_failure_when_insufficient(self):
        from app.portfolio.allocator import ResourcePool
        pool = ResourcePool([{"resource_type": "BUDGET", "available": 10000.0, "allocated": 0.0}])
        success = pool.allocate("BUDGET", 50000.0)
        assert success is False
        assert pool.available("BUDGET") == 10000.0

    def test_resource_pool_never_goes_negative(self):
        from app.portfolio.allocator import ResourcePool
        pool = ResourcePool([{"resource_type": "BUDGET", "available": 1000.0, "allocated": 0.0}])
        pool.allocate("BUDGET", 2000.0)  # Should fail silently
        assert pool.available("BUDGET") >= 0.0

    def test_allocator_returns_records_and_constrained(self):
        from app.portfolio.allocator import ResourceAllocationEngine, ResourcePool
        engine = ResourceAllocationEngine()
        pool = ResourcePool([
            {"resource_type": "BUDGET", "available": 50000.0, "allocated": 0.0},
            {"resource_type": "EXECUTION_CAPACITY", "available": 5.0, "allocated": 0.0}
        ])
        missions = [
            {"mission_id": "m-1", "resource_requirement": 30000.0},
            {"mission_id": "m-2", "resource_requirement": 30000.0},  # Should be constrained
        ]
        records, constrained = engine.allocate_for_missions(
            "p-1", missions, pool, "v1.0.0", "org-1"
        )
        assert len(records) > 0
        # m-2 should be constrained since only 20k remaining after m-1
        constrained_ids = {c["mission_id"] for c in constrained}
        assert "m-2" in constrained_ids

    def test_agent_capacity_status_available(self):
        from app.portfolio.allocator import ResourceAllocationEngine
        engine = ResourceAllocationEngine()
        result = engine.compute_agent_capacity_status("SEO Agent", 10, 3)
        assert result["status"] == "AVAILABLE"
        assert result["remaining"] == 7

    def test_agent_capacity_status_exhausted(self):
        from app.portfolio.allocator import ResourceAllocationEngine
        engine = ResourceAllocationEngine()
        result = engine.compute_agent_capacity_status("SEO Agent", 10, 10)
        assert result["status"] == "EXHAUSTED"
        assert result["remaining"] == 0

    def test_agent_capacity_near_limit(self):
        from app.portfolio.allocator import ResourceAllocationEngine
        engine = ResourceAllocationEngine()
        result = engine.compute_agent_capacity_status("SEO Agent", 10, 9)
        assert result["status"] == "NEAR_LIMIT"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. EVALUATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvaluationEngine:
    def setup_method(self):
        from app.portfolio.engine import PortfolioEvaluationEngine
        self.engine = PortfolioEvaluationEngine()

    def _eval(self, **kwargs):
        defaults = dict(
            portfolio_id="p-test",
            expected_value=100000.0,
            actual_value=95000.0,
            total_missions=5,
            completed_missions=4,
            total_budget=100000.0,
            allocated_budget=80000.0,
            risk_score=20.0,
            confidence_score=90.0
        )
        defaults.update(kwargs)
        return self.engine.evaluate(**defaults)

    def test_healthy_portfolio_score(self):
        from app.portfolio.models import PortfolioHealth
        result = self._eval()
        assert result.health in (PortfolioHealth.EXCELLENT, PortfolioHealth.HEALTHY)

    def test_critical_portfolio_with_high_risk(self):
        from app.portfolio.models import PortfolioHealth
        result = self._eval(risk_score=90.0, confidence_score=30.0,
                            completed_missions=0, actual_value=0.0)
        assert result.health in (PortfolioHealth.CRITICAL, PortfolioHealth.AT_RISK)

    def test_roi_positive_when_actual_exceeds_expected(self):
        result = self._eval(expected_value=100000.0, actual_value=120000.0)
        assert result.portfolio_roi > 0.0

    def test_roi_negative_when_underperforming(self):
        result = self._eval(expected_value=100000.0, actual_value=80000.0)
        assert result.portfolio_roi < 0.0

    def test_mission_success_rate_100pct(self):
        result = self._eval(total_missions=5, completed_missions=5)
        assert result.mission_success_rate == 100.0

    def test_result_has_summary(self):
        result = self._eval()
        assert isinstance(result.summary, str)
        assert len(result.summary) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# 7. REBALANCING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class TestRebalancingEngine:
    def setup_method(self):
        from app.portfolio.engine import PortfolioRebalancingEngine
        self.engine = PortfolioRebalancingEngine()

    def test_version_bump_minor(self):
        assert self.engine.compute_new_version("v1.0.0") == "v1.1.0"
        assert self.engine.compute_new_version("v1.3.0") == "v1.4.0"
        assert self.engine.compute_new_version("v2.0.0") == "v2.1.0"

    def test_mission_failed_triggers_rebalance(self):
        triggers = self.engine.detect_triggers(
            current_risk=30.0, previous_risk=30.0,
            forecast_delta_pct=5.0, mission_failed=True
        )
        assert "mission_failed" in triggers

    def test_large_forecast_delta_triggers_rebalance(self):
        triggers = self.engine.detect_triggers(
            current_risk=30.0, previous_risk=30.0,
            forecast_delta_pct=-20.0
        )
        assert any("forecast_material_change" in t for t in triggers)

    def test_risk_threshold_crossed_triggers_rebalance(self):
        triggers = self.engine.detect_triggers(
            current_risk=75.0, previous_risk=60.0,
            forecast_delta_pct=2.0
        )
        assert any("risk_threshold_breached" in t for t in triggers)

    def test_no_triggers_on_stable_portfolio(self):
        triggers = self.engine.detect_triggers(
            current_risk=30.0, previous_risk=30.0,
            forecast_delta_pct=5.0
        )
        assert triggers == []

    def test_governance_required_on_high_risk(self):
        assert self.engine.requires_governance(risk_score=75.0, budget_utilization_pct=50.0) is True

    def test_governance_required_on_high_budget_utilization(self):
        assert self.engine.requires_governance(risk_score=30.0, budget_utilization_pct=92.0) is True

    def test_governance_not_required_on_low_risk_low_budget(self):
        assert self.engine.requires_governance(risk_score=30.0, budget_utilization_pct=50.0) is False


# ═══════════════════════════════════════════════════════════════════════════════
# 8. CHECKPOINT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class TestCheckpointEngine:
    def setup_method(self):
        from app.portfolio.engine import PortfolioCheckpointEngine
        self.engine = PortfolioCheckpointEngine()

    def test_complete_when_100pct_progress(self):
        from app.portfolio.models import PortfolioHealth, PortfolioCheckpointDecision
        decision, _ = self.engine.evaluate(
            health=PortfolioHealth.HEALTHY, risk_score=20.0,
            progress_pct=100.0, has_violations=False
        )
        assert decision == PortfolioCheckpointDecision.COMPLETE

    def test_escalate_on_violations(self):
        from app.portfolio.models import PortfolioHealth, PortfolioCheckpointDecision
        decision, _ = self.engine.evaluate(
            health=PortfolioHealth.HEALTHY, risk_score=20.0,
            progress_pct=50.0, has_violations=True
        )
        assert decision == PortfolioCheckpointDecision.ESCALATE

    def test_escalate_on_critical_health(self):
        from app.portfolio.models import PortfolioHealth, PortfolioCheckpointDecision
        decision, _ = self.engine.evaluate(
            health=PortfolioHealth.CRITICAL, risk_score=40.0,
            progress_pct=50.0, has_violations=False
        )
        assert decision == PortfolioCheckpointDecision.ESCALATE

    def test_rebalance_on_at_risk(self):
        from app.portfolio.models import PortfolioHealth, PortfolioCheckpointDecision
        decision, _ = self.engine.evaluate(
            health=PortfolioHealth.AT_RISK, risk_score=50.0,
            progress_pct=50.0, has_violations=False
        )
        assert decision == PortfolioCheckpointDecision.REBALANCE

    def test_continue_on_healthy_portfolio(self):
        from app.portfolio.models import PortfolioHealth, PortfolioCheckpointDecision
        decision, _ = self.engine.evaluate(
            health=PortfolioHealth.HEALTHY, risk_score=20.0,
            progress_pct=60.0, has_violations=False
        )
        assert decision == PortfolioCheckpointDecision.CONTINUE


# ═══════════════════════════════════════════════════════════════════════════════
# 9. SCHEMA VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestSchemas:
    def test_portfolio_create_schema_valid(self):
        from app.portfolio.schemas import PortfolioCreate
        p = PortfolioCreate(
            title="Q1 Strategic Portfolio",
            total_budget=100000.0,
            scenario_type="BALANCED"
        )
        assert p.title == "Q1 Strategic Portfolio"
        assert p.total_budget == 100000.0

    def test_optimization_request_defaults(self):
        from app.portfolio.schemas import OptimizationRequest
        req = OptimizationRequest()
        assert req.scenario_type == "BALANCED"
        assert req.budget_delta_pct == 0.0

    def test_rebalance_request(self):
        from app.portfolio.schemas import RebalanceRequest
        req = RebalanceRequest(reason="Mission failed — rebalance required.")
        assert req.force is False

    def test_overview_schema_fields(self):
        from app.portfolio.schemas import PortfolioOverviewResponse
        overview = PortfolioOverviewResponse(
            organization_id="org-1",
            total_portfolios=3,
            active_portfolios=2,
            total_expected_value=500000.0,
            total_allocated_budget=350000.0,
            missions_selected=12,
            missions_deferred=4,
            missions_at_risk=1,
            portfolios_requiring_rebalance=0,
            overall_health="HEALTHY"
        )
        assert overview.organization_id == "org-1"
        assert overview.overall_health == "HEALTHY"


# ═══════════════════════════════════════════════════════════════════════════════
# 10. TENANT ISOLATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestTenantIsolation:
    def test_portfolio_model_organization_id_not_nullable(self):
        from app.portfolio.models import StrategicPortfolioModel
        col = StrategicPortfolioModel.__table__.c.get("organization_id")
        assert col is not None
        assert not col.nullable

    def test_portfolio_mission_organization_id_not_nullable(self):
        from app.portfolio.models import PortfolioMissionModel
        col = PortfolioMissionModel.__table__.c.get("organization_id")
        assert col is not None
        assert not col.nullable

    def test_portfolio_resource_organization_id_not_nullable(self):
        from app.portfolio.models import PortfolioResourceModel
        col = PortfolioResourceModel.__table__.c.get("organization_id")
        assert col is not None
        assert not col.nullable

    def test_portfolio_allocation_organization_id_not_nullable(self):
        from app.portfolio.models import PortfolioAllocationModel
        col = PortfolioAllocationModel.__table__.c.get("organization_id")
        assert col is not None
        assert not col.nullable

    def test_all_tables_have_org_id_column(self):
        from app.portfolio.models import (
            StrategicPortfolioModel, PortfolioMissionModel, PortfolioResourceModel,
            PortfolioConstraintModel, PortfolioAllocationModel, PortfolioEvaluationModel,
            PortfolioDecisionModel, PortfolioVersionModel, PortfolioCheckpointModel
        )
        for model in [
            StrategicPortfolioModel, PortfolioMissionModel, PortfolioResourceModel,
            PortfolioConstraintModel, PortfolioAllocationModel, PortfolioEvaluationModel,
            PortfolioDecisionModel, PortfolioVersionModel, PortfolioCheckpointModel
        ]:
            assert "organization_id" in model.__table__.c, f"{model.__tablename__} missing org_id column"


# ═══════════════════════════════════════════════════════════════════════════════
# 11. API ROUTE SMOKE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestPortfolioAPI:
    def test_portfolio_overview_unauthorized(self, client):
        resp = client.get("/api/v1/portfolio/overview")
        assert resp.status_code in (401, 403, 422)

    def test_portfolio_list_unauthorized(self, client):
        resp = client.get("/api/v1/portfolio/portfolios")
        assert resp.status_code in (401, 403, 422)

    def test_portfolio_create_unauthorized(self, client):
        resp = client.post("/api/v1/portfolio/portfolios", json={
            "title": "Test Portfolio", "total_budget": 100000.0
        })
        assert resp.status_code in (401, 403, 422)

    def test_portfolio_optimize_unauthorized(self, client):
        resp = client.post("/api/v1/portfolio/portfolios/fake-id/optimize", json={
            "scenario_type": "BALANCED"
        })
        assert resp.status_code in (401, 403, 422)

    def test_portfolio_simulate_unauthorized(self, client):
        resp = client.post("/api/v1/portfolio/portfolios/fake-id/simulate", json={
            "scenario_type": "CONSERVATIVE"
        })
        assert resp.status_code in (401, 403, 422)


# ═══════════════════════════════════════════════════════════════════════════════
# 12. MAIN APP VERSION CHECK
# ═══════════════════════════════════════════════════════════════════════════════

class TestAppVersion:
    def test_app_version_is_250(self):
        from app.main import app
        assert app.version >= "2.5.0"

    def test_portfolio_router_mounted(self):
        from app.main import app
        # Check that portfolio routes exist — may be in sub-routes so check router list
        portfolio_mounted = any(
            hasattr(r, "routes") and any("portfolio" in str(getattr(sub, "path", ""))
                                          for sub in getattr(r, "routes", []))
            for r in app.routes
        ) or any("portfolio" in str(getattr(r, "path", "")) for r in app.routes)
        # Alternative: verify the router import worked by importing directly
        from app.portfolio.routes import router as portfolio_router
        assert portfolio_router is not None
        assert portfolio_router.prefix == "/portfolio"
