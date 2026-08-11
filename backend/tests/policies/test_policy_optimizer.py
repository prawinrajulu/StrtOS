import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.policies.optimizer import PolicyOptimizer
from app.policies.models import PolicyVersionModel

def test_bounded_adaptation_allowed():
    current_params = {"confidence_threshold": 80.0, "sample_size": 10}
    proposed_params = {"confidence_threshold": 84.0, "sample_size": 10}  # +5% delta
    delta = PolicyOptimizer.calculate_delta(current_params, proposed_params)
    assert delta <= 10.0

def test_adaptation_limit_exceeded_rejected():
    mock_active = PolicyVersionModel(
        policy_id="pol_1",
        organization_id="org_1",
        agent_name="Campaign Planner",
        version="1.0.0",
        parameters={"budget_cap": 1000.0}
    )
    # Propose +20% adjustment (exceeds MAX_ADAPTATION_DELTA = 10%)
    proposed = {"budget_cap": 1200.0}

    opt_status, res_dict, candidate = PolicyOptimizer.propose_candidate(
        policy_id="pol_1",
        org_id="org_1",
        agent_name="Campaign Planner",
        active_version=mock_active,
        proposed_parameters=proposed
    )

    assert opt_status == "REJECTED"
    assert res_dict["status"] == "REJECTED"
    assert res_dict["reason"] == "ADAPTATION_LIMIT_EXCEEDED"
    assert candidate is None
