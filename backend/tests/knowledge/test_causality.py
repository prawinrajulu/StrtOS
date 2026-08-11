import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.knowledge.causal import CausalIntelligenceEngine
from app.knowledge.models import CausalStatusEnum

def test_causal_confidence_validation():
    score, status, exp = CausalIntelligenceEngine.evaluate_causality(
        supporting_count=4,
        contradicting_count=0,
        temporal_sequence_valid=True,
        prediction_accuracy=90.0,
        evidence_quality=90.0
    )

    assert score >= 85.0
    assert status == CausalStatusEnum.VALIDATED

def test_causal_contradiction_detection():
    score, status, exp = CausalIntelligenceEngine.evaluate_causality(
        supporting_count=1,
        contradicting_count=3,
        temporal_sequence_valid=True
    )

    assert status == CausalStatusEnum.CONTRADICTED
