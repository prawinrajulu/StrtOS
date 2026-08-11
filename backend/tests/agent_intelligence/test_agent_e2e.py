import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.agent_intelligence.engine import AgentHealthEngine
from app.agent_intelligence.weakness import AgentWeaknessDetector
from app.agent_intelligence.anomaly import AgentAnomalyDetector
from app.agent_intelligence.optimizer import AgentOptimizationEngine
from app.agent_intelligence.models import AgentIntelligenceMetricModel, RecommendationStatus

def test_full_agent_intelligence_lifecycle():
    # 1. Telemetry Metric
    metric = AgentIntelligenceMetricModel(
        organization_id="org_e2e",
        agent_name="Business Analysis",
        prediction_accuracy=68.0,  # Below baseline (85%)
        evidence_quality_score=70.0,
        average_latency_ms=2800.0,
        failure_rate=22.0
    )

    # 2. Health Score & Status
    score, health = AgentHealthEngine.calculate_health_score(
        outcome_success_rate=50.0,
        prediction_accuracy=metric.prediction_accuracy,
        evidence_quality_score=metric.evidence_quality_score,
        average_latency_ms=metric.average_latency_ms
    )
    metric.overall_agent_score = score
    metric.health_status = health

    assert score < 75.0

    # 3. Weakness Detection
    weaknesses = AgentWeaknessDetector.detect_weaknesses("org_e2e", metric)
    assert len(weaknesses) >= 2

    # 4. Anomaly Detection
    anomalies = AgentAnomalyDetector.detect_anomalies("org_e2e", metric)
    assert len(anomalies) >= 1

    # 5. Recommendation Generation
    recs = AgentOptimizationEngine.generate_recommendations("org_e2e", metric, weaknesses, anomalies)
    assert len(recs) >= 1
    assert recs[0].status == RecommendationStatus.DRAFT
    assert recs[0].expected_improvement > 0.0
