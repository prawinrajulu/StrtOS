import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.policies.service import SPECIALIST_AGENTS

def test_specialist_agents_coverage():
    assert "Business Analysis" in SPECIALIST_AGENTS
    assert "SEO Audit" in SPECIALIST_AGENTS
    assert "Competitor Research" in SPECIALIST_AGENTS
    assert "Marketing Strategy" in SPECIALIST_AGENTS
    assert "Campaign Planner" in SPECIALIST_AGENTS
    assert len(SPECIALIST_AGENTS) == 5
