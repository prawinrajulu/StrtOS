import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.governance.risk_engine import calculate_decision_risk
from app.governance.models import DecisionType, RiskLevel

def test_governance_risk_escalation_for_policy():
    risk = calculate_decision_risk(
        ai_confidence_score=85.0,
        evidence_count=4,
        decision_type=DecisionType.STRATEGY_CHANGE,
        is_reversible=True
    )
    assert risk["risk_level"] in (RiskLevel.MEDIUM, RiskLevel.HIGH)
    assert "risk_score" in risk
