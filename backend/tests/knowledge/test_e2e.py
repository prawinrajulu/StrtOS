import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.knowledge.causal import (
    CausalIntelligenceEngine, DecisionExplanationEngine, OutcomeRootCauseEngine, AgentContributionEngine
)
from app.knowledge.models import CausalStatusEnum

def test_full_knowledge_causal_lifecycle():
    # 1. Evaluate Causality
    score, status, exp = CausalIntelligenceEngine.evaluate_causality(
        supporting_count=4,
        contradicting_count=0,
        temporal_sequence_valid=True,
        prediction_accuracy=90.0,
        evidence_quality=90.0
    )
    assert score >= 80.0
    assert status == CausalStatusEnum.VALIDATED

    # 2. Decision Explainability
    decision_exp = DecisionExplanationEngine.explain_decision("dec_e2e_101")
    assert decision_exp["decision_id"] == "dec_e2e_101"
    assert len(decision_exp["evidence_used"]) >= 1

    # 3. Root Cause Analysis
    rc = OutcomeRootCauseEngine.analyze_root_cause("out_e2e_201", outcome_status="FAILED")
    assert rc["status"] == "FAILED"
    assert len(rc["contributors"]) == 4

    # 4. Agent Influence
    inf = AgentContributionEngine.calculate_agent_influence("Business Analysis", total_executions=25)
    assert inf["agent_name"] == "Business Analysis"
    assert inf["total_contributions"] == 25
