import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.policies.ab_testing import PolicyABTestingEngine
from app.policies.models import PolicyVersionModel

def test_ab_test_insufficient_samples():
    control = PolicyVersionModel(performance_score=80.0, risk_score=20.0)
    candidate = PolicyVersionModel(performance_score=86.0, risk_score=20.0)

    eligible, improvement, reason, metrics = PolicyABTestingEngine.evaluate_ab_test(
        control_version=control,
        candidate_version=candidate,
        sample_count=2  # Below MIN_SAMPLE_COUNT (3)
    )
    assert eligible is False
    assert "INSUFFICIENT_SAMPLES" in reason

def test_ab_test_valid_pass():
    control = PolicyVersionModel(performance_score=80.0, risk_score=20.0)
    candidate = PolicyVersionModel(performance_score=86.0, risk_score=20.0)

    eligible, improvement, reason, metrics = PolicyABTestingEngine.evaluate_ab_test(
        control_version=control,
        candidate_version=candidate,
        sample_count=5
    )
    assert eligible is True
    assert improvement >= 2.0
    assert "PASSED" in reason
