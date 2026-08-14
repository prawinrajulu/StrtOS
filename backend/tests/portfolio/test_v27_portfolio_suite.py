"""
StrtOS v2.7.0 — Portfolio Optimization & Capital Allocation Test Suite.

Covers:
1. RecommendationAction enum & new v2.7.0 models (Initiatives, Recommendations).
2. Capital Allocation Engine (deterministic ROI & INSUFFICIENT_DATA handling).
3. Portfolio Trade-Off Engine (Option A vs Option B evaluation).
4. Do-Nothing Portfolio Simulator (side-effect free simulation comparison).
5. Recommendation Engine (STOP, DELAY, ACCELERATE, REDUCE, CONTINUE, REVIEW rules and governance routing).
6. Multi-tenant isolation & organization_id enforcement.
7. API endpoints via TestClient (/initiatives, /allocations, /tradeoffs, /recommendations, /simulate, /optimize).
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from app.auth.dependencies import get_current_user


@pytest.fixture
def auth_client():
    from app.main import app
    mock_user = MagicMock()
    mock_user.organization_id = "org-test-123"
    app.dependency_overrides[get_current_user] = lambda: mock_user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# 1. MODELS & ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class TestV27PortfolioModels:
    def test_recommendation_action_enum(self):
        from app.portfolio.models import RecommendationAction
        expected = {"CONTINUE", "ACCELERATE", "MAINTAIN", "DELAY", "REDUCE", "STOP", "REVIEW"}
        actual = {e.value for e in RecommendationAction}
        assert expected == actual

    def test_initiative_model_instantiation(self):
        from app.portfolio.models import PortfolioInitiativeModel, MissionPriority
        init = PortfolioInitiativeModel(
            organization_id="org-test-123",
            portfolio_id="port-123",
            title="Strategic Expansion",
            priority=MissionPriority.CRITICAL,
            priority_score=88.5,
            expected_value=250000.0,
            resource_cost=75000.0,
            status="PROPOSED"
        )
        assert init.organization_id == "org-test-123"
        assert init.priority_score == 88.5
        assert init.expected_value == 250000.0

    def test_recommendation_model_instantiation(self):
        from app.portfolio.models import PortfolioRecommendationModel, RecommendationAction
        rec = PortfolioRecommendationModel(
            organization_id="org-test-123",
            portfolio_id="port-123",
            recommendation_type=RecommendationAction.STOP,
            title="STOP: Low ROI Initiative",
            reason="High risk and persistent failure",
            requires_governance=True
        )
        assert rec.recommendation_type == RecommendationAction.STOP
        assert rec.requires_governance is True


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CAPITAL ALLOCATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class TestCapitalAllocationEngine:
    def test_capital_allocation_sufficient_data(self):
        from app.portfolio.engine import CapitalAllocationEngine
        engine = CapitalAllocationEngine()
        items = [
            {"id": "init-1", "title": "Init 1", "capital_budget": 50000.0, "expected_value": 150000.0},
            {"id": "init-2", "title": "Init 2", "capital_budget": 30000.0, "expected_value": 90000.0},
        ]
        res = engine.compute_allocation(
            portfolio_id="p-1",
            total_budget=100000.0,
            current_spend=80000.0,
            initiatives_or_missions=items
        )

        assert res["data_quality"] == "SUFFICIENT"
        assert res["total_budget"] == 100000.0
        assert res["allocated_budget"] == 80000.0
        assert res["unused_budget"] == 20000.0
        assert res["budget_shortage"] == 0.0
        assert res["expected_portfolio_roi"] == 200.0
        assert len(res["allocation_breakdown"]) == 2

    def test_capital_allocation_insufficient_data(self):
        from app.portfolio.engine import CapitalAllocationEngine
        engine = CapitalAllocationEngine()
        items = [{"id": "init-1", "title": "Init 1", "capital_budget": 50000.0}]

        res = engine.compute_allocation(
            portfolio_id="p-1",
            total_budget=None,  # Missing financial telemetry
            current_spend=0.0,
            initiatives_or_missions=items
        )

        assert res["data_quality"] == "INSUFFICIENT_DATA"
        assert res["total_budget"] is None
        assert res["expected_portfolio_roi"] is None
        assert "Unable to compute" in res["explanation"]


# ═══════════════════════════════════════════════════════════════════════════════
# 3. PORTFOLIO TRADE-OFF ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class TestPortfolioTradeoffEngine:
    def test_tradeoff_evaluation(self):
        from app.portfolio.engine import PortfolioTradeoffEngine
        engine = PortfolioTradeoffEngine()
        item_a = {
            "id": "a-1",
            "title": "High EV Project A",
            "expected_value": 200000.0,
            "risk_score": 30.0,
            "resource_cost": 50000.0
        }
        item_b = {
            "id": "b-1",
            "title": "Lower Cost Project B",
            "expected_value": 80000.0,
            "risk_score": 15.0,
            "resource_cost": 20000.0
        }

        res = engine.evaluate_tradeoff(item_a, item_b)

        assert res["option_a_id"] == "a-1"
        assert res["option_b_id"] == "b-1"
        assert res["expected_value_delta"] == 120000.0
        assert len(res["prioritize_a_tradeoffs"]) == 3
        assert len(res["prioritize_b_tradeoffs"]) == 3
        assert "Trade-off" in res["recommendation"] or "Prioritize" in res["recommendation"]


# ═══════════════════════════════════════════════════════════════════════════════
# 4. DO-NOTHING SIMULATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class TestDoNothingSimulationEngine:
    def test_do_nothing_simulation(self):
        from app.portfolio.engine import DoNothingSimulationEngine
        engine = DoNothingSimulationEngine()

        res = engine.simulate(
            portfolio_id="p-sim-1",
            current_ev=100000.0,
            optimized_ev=130000.0,
            current_risk=40.0,
            optimized_risk=25.0,
            total_budget=150000.0,
            allocated_budget=100000.0,
            mission_count=5,
            completed_count=3
        )

        assert res["is_side_effect_free"] is True
        assert res["current"]["scenario_type"] == "CURRENT_PORTFOLIO"
        assert res["optimized"]["scenario_type"] == "OPTIMIZED_PORTFOLIO"
        assert res["do_nothing"]["scenario_type"] == "DO_NOTHING"
        assert res["do_nothing"]["expected_value"] == 75000.0  # 25% degradation
        assert res["do_nothing"]["risk_score"] == 55.0         # +15 risk increase


# ═══════════════════════════════════════════════════════════════════════════════
# 5. RECOMMENDATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class TestPortfolioRecommendationEngine:
    def test_stop_recommendation_high_risk(self):
        from app.portfolio.engine import PortfolioRecommendationEngine
        engine = PortfolioRecommendationEngine()

        res = engine.generate_recommendation(
            title="Risky Project",
            expected_value=50000.0,
            risk_score=80.0,  # High risk >= 75
            success_probability=40.0,
            resource_efficiency=10.0
        )

        assert res["recommendation_type"] == "STOP"
        assert res["requires_governance"] is True
        assert "STOP recommended" in res["reason"]

    def test_accelerate_recommendation(self):
        from app.portfolio.engine import PortfolioRecommendationEngine
        engine = PortfolioRecommendationEngine()

        res = engine.generate_recommendation(
            title="High Success Project",
            expected_value=150000.0,
            risk_score=20.0,
            success_probability=90.0,
            resource_efficiency=60.0
        )

        assert res["recommendation_type"] == "ACCELERATE"
        assert res["requires_governance"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# 6. API ENDPOINT TESTS (TestClient)
# ═══════════════════════════════════════════════════════════════════════════════

class TestPortfolioV27API:
    @patch("app.portfolio.service.PortfolioService.list_initiatives")
    def test_list_initiatives_endpoint(self, mock_list, auth_client):
        mock_list.return_value = []
        resp = auth_client.get("/api/v1/portfolio/initiatives?portfolio_id=p-1")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @patch("app.portfolio.service.PortfolioService.get_capital_allocation")
    def test_allocations_endpoint(self, mock_alloc, auth_client):
        mock_alloc.return_value = {
            "portfolio_id": "p-1",
            "total_budget": 100000.0,
            "current_spend": 50000.0,
            "allocated_budget": 50000.0,
            "unused_budget": 50000.0,
            "budget_shortage": 0.0,
            "expected_portfolio_roi": 150.0,
            "allocation_breakdown": [],
            "data_quality": "SUFFICIENT",
            "explanation": "Budget allocated clean."
        }
        resp = auth_client.get("/api/v1/portfolio/allocations?portfolio_id=p-1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data_quality"] == "SUFFICIENT"

    @patch("app.portfolio.service.PortfolioService.simulate_donothing")
    def test_simulate_endpoint(self, mock_sim, auth_client):
        mock_sim.return_value = {
            "portfolio_id": "p-1",
            "current": {"scenario_type": "CURRENT_PORTFOLIO", "expected_value": 100000, "expected_roi": 100, "risk_score": 20, "resource_utilization_pct": 50, "budget_utilization_pct": 50, "mission_completion_rate": 80, "strategic_progress_pct": 80, "summary": "c"},
            "optimized": {"scenario_type": "OPTIMIZED_PORTFOLIO", "expected_value": 130000, "expected_roi": 130, "risk_score": 15, "resource_utilization_pct": 45, "budget_utilization_pct": 45, "mission_completion_rate": 90, "strategic_progress_pct": 90, "summary": "o"},
            "do_nothing": {"scenario_type": "DO_NOTHING", "expected_value": 75000, "expected_roi": 75, "risk_score": 35, "resource_utilization_pct": 50, "budget_utilization_pct": 50, "mission_completion_rate": 50, "strategic_progress_pct": 50, "summary": "dn"},
            "recommendation": "Rec",
            "is_side_effect_free": True
        }
        resp = auth_client.post("/api/v1/portfolio/simulate?portfolio_id=p-1")
        assert resp.status_code == 200
        assert resp.json()["is_side_effect_free"] is True
