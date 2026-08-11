import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.agent_intelligence.engine import AgentHealthEngine
from app.agent_intelligence.models import AgentTrendStatus

def test_trend_calculation_improving():
    scores = [88.0, 80.0, 78.0]
    trend = AgentHealthEngine.calculate_trend(scores, min_sample_threshold=3)
    assert trend == AgentTrendStatus.IMPROVING

def test_trend_calculation_insufficient_samples():
    trend = AgentHealthEngine.calculate_trend([85.0, 84.0], min_sample_threshold=3)
    assert trend == AgentTrendStatus.INSUFFICIENT_DATA
