import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.agent_intelligence.benchmark import AgentBenchmarkEngine, SPECIALIST_AGENTS
from app.agent_intelligence.models import AgentIntelligenceMetricModel

def test_benchmark_generation():
    metrics = {
        "Business Analysis": AgentIntelligenceMetricModel(agent_name="Business Analysis", overall_agent_score=92.0),
        "SEO Audit": AgentIntelligenceMetricModel(agent_name="SEO Audit", overall_agent_score=85.0),
    }

    benchmarks = AgentBenchmarkEngine.generate_benchmarks("org_101", metrics)
    assert len(benchmarks) == 5
    assert benchmarks[0].agent_name == "Business Analysis"
    assert benchmarks[0].rank == 1
