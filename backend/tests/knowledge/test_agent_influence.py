import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.knowledge.causal import AgentContributionEngine

def test_agent_influence_calculation():
    inf = AgentContributionEngine.calculate_agent_influence("SEO Audit", total_executions=20)
    assert inf["agent_name"] == "SEO Audit"
    assert inf["total_contributions"] == 20
    assert inf["decision_influence_score"] > 0
