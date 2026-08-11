import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.agent_intelligence.anomaly import AgentAnomalyDetector
from app.agent_intelligence.models import AgentIntelligenceMetricModel

def test_anomaly_detection_spike():
    current = AgentIntelligenceMetricModel(
        agent_name="SEO Audit",
        failure_rate=30.0,
        average_latency_ms=3500.0
    )
    baseline = AgentIntelligenceMetricModel(
        agent_name="SEO Audit",
        failure_rate=5.0,
        average_latency_ms=1000.0
    )

    anomalies = AgentAnomalyDetector.detect_anomalies("org_101", current, baseline)
    assert len(anomalies) >= 2
    types = [a.anomaly_type for a in anomalies]
    assert "FAILURE_RATE_SPIKE" in types
    assert "LATENCY_SPIKE" in types
