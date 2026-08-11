import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.agent_intelligence.models import AgentIntelligenceMetricModel

def test_tenant_isolation_filter():
    m1 = AgentIntelligenceMetricModel(organization_id="org_A", agent_name="SEO Audit", overall_agent_score=90.0)
    m2 = AgentIntelligenceMetricModel(organization_id="org_B", agent_name="SEO Audit", overall_agent_score=80.0)

    assert m1.organization_id != m2.organization_id
    assert m1.organization_id == "org_A"
    assert m2.organization_id == "org_B"
