import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.agent_intelligence.models import AgentIntelligenceMetricModel, AgentHealthStatus, AgentTrendStatus

def test_agent_metric_model_instantiation():
    metric = AgentIntelligenceMetricModel(
        organization_id="org_101",
        agent_name="Business Analysis",
        policy_version="1.0.0",
        execution_count=10,
        successful_execution_count=9,
        failed_execution_count=1,
        success_rate=90.0,
        average_latency_ms=1100.0,
        prediction_accuracy=85.0,
        overall_agent_score=84.5,
        health_status=AgentHealthStatus.HEALTHY,
        trend=AgentTrendStatus.STABLE
    )
    assert metric.agent_name == "Business Analysis"
    assert metric.overall_agent_score == 84.5
    assert metric.health_status == AgentHealthStatus.HEALTHY
    assert metric.organization_id == "org_101"
