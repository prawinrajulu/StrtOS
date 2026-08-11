import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.policies.versioning import PolicyVersioningEngine
from app.policies.models import PolicyStatus

def test_semver_incrementing():
    assert PolicyVersioningEngine.bump_semver("1.0.0", minor=True) == "1.1.0"
    assert PolicyVersioningEngine.bump_semver("1.1.0", minor=True) == "1.2.0"
    assert PolicyVersioningEngine.bump_semver("v1.2.3", minor=False) == "1.2.4"

def test_candidate_version_creation_immutable():
    candidate = PolicyVersioningEngine.create_candidate_version(
        policy_id="pol_1",
        org_id="org_1",
        agent_name="SEO Audit",
        parent_version="1.0.0",
        new_parameters={"depth": 5},
        adaptation_delta=5.0,
        reason="Increase crawl depth for better audit accuracy",
        performance_metrics={"overall_policy_score": 85.0}
    )
    assert candidate.version == "1.1.0"
    assert candidate.parent_version == "1.0.0"
    assert candidate.status == PolicyStatus.CANDIDATE
    assert candidate.adaptation_delta == 5.0
