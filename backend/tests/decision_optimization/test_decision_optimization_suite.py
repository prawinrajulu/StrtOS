# Test Decision Optimization Suite
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.decision_optimization.risk import ActionRiskEngine
from app.decision_optimization.optimizer import DecisionOptimizer
from app.decision_optimization.schemas import RiskLevelEnum
from app.decision_optimization.models import ActionCandidate

@pytest.mark.asyncio
async def test_risk_engine_numeric_and_enum():
    engine = ActionRiskEngine()
    low_risk = engine.evaluate(financial_exposure=0.0, irreversibility=False, uncertainty=0.1)
    assert low_risk == RiskLevelEnum.LOW

    high_risk = engine.evaluate(financial_exposure=0.9, irreversibility=True, uncertainty=0.9)
    assert high_risk in [RiskLevelEnum.HIGH, RiskLevelEnum.CRITICAL]

@pytest.mark.asyncio
async def test_deterministic_optimizer():
    optimizer = DecisionOptimizer()
    now = datetime.now(timezone.utc)
    cand1 = ActionCandidate(
        id="c1",
        organization_id="org-test",
        action_type="GENERATE_REPORT",
        expected_value=800.0,
        expected_confidence=0.9,
        causal_support=0.85,
        historical_success=0.9,
        agent_reliability=0.95,
        expected_risk="LOW",
        expected_cost=20.0,
        reversibility="yes",
        time_to_impact=10,
        status="PENDING",
        created_at=now,
        updated_at=now,
    )
    cand2 = ActionCandidate(
        id="c2",
        organization_id="org-test",
        action_type="RUN_SEO_AUDIT",
        expected_value=400.0,
        expected_confidence=0.7,
        causal_support=0.6,
        historical_success=0.7,
        agent_reliability=0.8,
        expected_risk="MEDIUM",
        expected_cost=100.0,
        reversibility="no",
        time_to_impact=60,
        status="PENDING",
        created_at=now,
        updated_at=now,
    )

    rec1 = await optimizer.optimize([cand1, cand2])
    rec2 = await optimizer.optimize([cand1, cand2])

    assert rec1.recommended_action.id == "c1"
    assert rec1.score_breakdown["total_score"] == rec2.score_breakdown["total_score"]

def test_fastapi_compilation():
    client = TestClient(app)
    res = client.get("/version")
    assert res.status_code == 200
