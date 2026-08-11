import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.knowledge.causal import OutcomeRootCauseEngine

def test_outcome_root_cause_analysis_failed():
    rc = OutcomeRootCauseEngine.analyze_root_cause(
        outcome_id="out_failed_01",
        outcome_status="FAILED",
        evidence_quality=50.0,
        prediction_accuracy=40.0
    )

    assert rc["status"] == "FAILED"
    assert len(rc["contributors"]) == 4
    assert rc["contributors"][0]["rank"] == 1
    assert rc["confidence"] > 0
