import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.policies.models import PolicyModel, PolicyVersionModel, PolicyStatus

def test_policy_model_instantiation():
    policy = PolicyModel(
        organization_id="org_123",
        agent_name="Business Analysis",
        policy_name="Business Strategy Baseline",
        current_version="1.0.0",
        status=PolicyStatus.ACTIVE
    )
    assert policy.organization_id == "org_123"
    assert policy.agent_name == "Business Analysis"
    assert policy.status == PolicyStatus.ACTIVE

def test_policy_version_model_instantiation():
    version = PolicyVersionModel(
        policy_id="pol_123",
        organization_id="org_123",
        agent_name="Business Analysis",
        version="1.1.0",
        status=PolicyStatus.CANDIDATE,
        parameters={"temperature": 0.2, "confidence_threshold": 85.0},
        performance_score=88.5,
        adaptation_delta=5.0,
        parent_version="1.0.0",
        change_reason="Auto-optimization proposed"
    )
    assert version.version == "1.1.0"
    assert version.adaptation_delta == 5.0
    assert version.parent_version == "1.0.0"
