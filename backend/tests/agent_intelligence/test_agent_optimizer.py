import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.agent_intelligence.optimizer import AgentOptimizationEngine
from app.agent_intelligence.models import (
    AgentIntelligenceMetricModel, AgentWeaknessModel, AgentAnomalyModel, RecommendationStatus
)

def test_recommendation_generation_from_weakness():
    metric = AgentIntelligenceMetricModel(agent_name="Marketing Strategy", prediction_accuracy=65.0)
    weakness = AgentWeaknessModel(
        organization_id="org_101",
        agent_name="Marketing Strategy",
        weakness_type="LOW_ACCURACY",
        severity="HIGH",
        metric_name="prediction_accuracy",
        current_value=65.0,
        baseline_value=85.0,
        deviation=20.0,
        explanation="Low accuracy detected"
    )

    recs = AgentOptimizationEngine.generate_recommendations("org_101", metric, [weakness], [])
    assert len(recs) == 1
    assert recs[0].status == RecommendationStatus.DRAFT
    assert recs[0].target_metric == "prediction_accuracy"
