import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.policies.optimizer import PolicyOptimizer
from app.policies.models import PolicyVersionModel

def test_policy_impact_chain_evaluation():
    active = PolicyVersionModel(
        policy_id="pol_imp",
        organization_id="org_101",
        version="1.0.0",
        parameters={"confidence_threshold": 80.0}
    )
    status, result, candidate = PolicyOptimizer.propose_candidate(
        policy_id="pol_imp",
        org_id="org_101",
        agent_name="SEO Audit",
        active_version=active,
        proposed_parameters={"confidence_threshold": 84.0}
    )
    assert status == "CANDIDATE_CREATED"
    assert candidate.version == "1.1.0"
