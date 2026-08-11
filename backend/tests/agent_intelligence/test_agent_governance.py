import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.governance.risk_engine import calculate_decision_risk
from app.governance.models import DecisionType

def test_governance_risk_assessment_for_recommendation():
    risk = calculate_decision_risk(
        ai_confidence_score=85.0,
        evidence_count=3,
        decision_type=DecisionType.STRATEGY_CHANGE
    )
    assert "risk_level" in risk
    assert "risk_score" in risk
