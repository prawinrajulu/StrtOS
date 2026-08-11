import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.predictions.models import PredictionModel

def test_prediction_integration_with_causal_context():
    pred = PredictionModel(
        organization_id="org_101",
        scenario_name="15% SaaS Margin Expansion",
        predicted_value=15.0,
        confidence_score=85.0
    )
    assert pred.scenario_name == "15% SaaS Margin Expansion"
    assert pred.confidence_score == 85.0
