import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.knowledge.causal import DecisionExplanationEngine

def test_explain_decision_chain():
    exp = DecisionExplanationEngine.explain_decision("dec_999")
    assert exp["decision_id"] == "dec_999"
    assert len(exp["evidence_used"]) >= 1
    assert len(exp["agents_involved"]) >= 1
    assert exp["confidence"] > 0
