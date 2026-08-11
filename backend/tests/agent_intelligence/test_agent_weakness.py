import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.agent_intelligence.weakness import AgentWeaknessDetector
from app.agent_intelligence.models import AgentIntelligenceMetricModel, WeaknessSeverity

def test_weakness_detection():
    metric = AgentIntelligenceMetricModel(
        agent_name="Competitor Research",
        prediction_accuracy=60.0,  # Below 75%
        failure_rate=20.0,         # Above 15%
        average_latency_ms=3000.0  # Above 2500ms
    )

    weaknesses = AgentWeaknessDetector.detect_weaknesses("org_101", metric)
    assert len(weaknesses) >= 2
    types = [w.weakness_type for w in weaknesses]
    assert "LOW_ACCURACY" in types
    assert "HIGH_FAILURE_RATE" in types
