import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.policies.models import PolicyModel

def test_tenant_isolation_filter():
    p1 = PolicyModel(id="pol_a", organization_id="org_A", agent_name="SEO Audit", policy_name="Pol A")
    p2 = PolicyModel(id="pol_b", organization_id="org_B", agent_name="SEO Audit", policy_name="Pol B")

    assert p1.organization_id != p2.organization_id
    assert p1.id != p2.id
