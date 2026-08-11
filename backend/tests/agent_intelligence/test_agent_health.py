import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.agent_intelligence.engine import AgentHealthEngine
from app.agent_intelligence.models import AgentHealthStatus

def test_deterministic_health_score_calculation():
    score, status = AgentHealthEngine.calculate_health_score(
        outcome_success_rate=95.0,
        prediction_accuracy=90.0,
        evidence_quality_score=90.0,
        reliability_score=90.0,
        confidence_score=90.0,
        tool_success_rate=95.0,
        llm_success_rate=95.0,
        average_latency_ms=1000.0
    )
    assert score >= 90.0
    assert status == AgentHealthStatus.EXCELLENT

def test_degraded_health_score():
    score, status = AgentHealthEngine.calculate_health_score(
        outcome_success_rate=50.0,
        prediction_accuracy=60.0,
        evidence_quality_score=50.0,
        reliability_score=50.0,
        confidence_score=50.0,
        average_latency_ms=4000.0
    )
    assert score < 65.0
    assert status in (AgentHealthStatus.DEGRADED, AgentHealthStatus.AT_RISK, AgentHealthStatus.CRITICAL)
