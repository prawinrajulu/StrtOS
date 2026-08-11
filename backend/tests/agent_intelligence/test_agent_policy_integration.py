import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.policies.optimizer import PolicyOptimizer
from app.policies.models import PolicyVersionModel

def test_bounded_adaptation_policy_integration():
    active_version = PolicyVersionModel(
        policy_id="pol_int",
        organization_id="org_101",
        agent_name="Campaign Planner",
        version="1.0.0",
        parameters={"confidence_threshold": 80.0}
    )

    opt_status, result, candidate = PolicyOptimizer.propose_candidate(
        policy_id="pol_int",
        org_id="org_101",
        agent_name="Campaign Planner",
        active_version=active_version,
        proposed_parameters={"confidence_threshold": 84.0}  # +5% delta
    )

    assert opt_status == "CANDIDATE_CREATED"
    assert candidate.version == "1.1.0"
    assert candidate.adaptation_delta <= 10.0
