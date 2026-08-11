import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.policies.engine import PolicyPerformanceEngine
from app.policies.optimizer import PolicyOptimizer
from app.policies.ab_testing import PolicyABTestingEngine
from app.policies.versioning import PolicyVersioningEngine
from app.policies.models import PolicyVersionModel, PolicyStatus

def test_full_policy_evolution_lifecycle():
    # 1. Baseline Policy v1.0.0
    v1 = PolicyVersionModel(
        policy_id="pol_e2e",
        organization_id="org_test",
        agent_name="Marketing Strategy",
        version="1.0.0",
        status=PolicyStatus.ACTIVE,
        parameters={"campaign_budget": 5000.0, "risk_tolerance": 0.2},
        performance_score=80.0,
        confidence_score=85.0
    )

    # 2. Performance Evaluation
    scores = PolicyPerformanceEngine.evaluate_performance(
        predicted_kpi=100.0,
        actual_kpi=94.0,
        prediction_accuracy=88.0,
        confidence=85.0,
        outcome_status="SUCCESS",
        agent_execution_success=True,
        evidence_quality=85.0,
        historical_reliability=80.0
    )
    v1.performance_score = scores["overall_policy_score"]
    assert scores["overall_policy_score"] >= 80.0

    # 3. Bounded Optimization -> Candidate v1.1.0
    proposed_params = {"campaign_budget": 5250.0, "risk_tolerance": 0.2}  # +5% delta
    opt_status, res_dict, candidate = PolicyOptimizer.propose_candidate(
        policy_id="pol_e2e",
        org_id="org_test",
        agent_name="Marketing Strategy",
        active_version=v1,
        proposed_parameters=proposed_params
    )
    assert opt_status == "CANDIDATE_CREATED"
    assert candidate.version == "1.1.0"
    assert candidate.status == PolicyStatus.CANDIDATE

    # 4. A/B Evaluation
    candidate.performance_score = 95.0
    eligible, improvement, reason, metrics = PolicyABTestingEngine.evaluate_ab_test(
        control_version=v1,
        candidate_version=candidate,
        sample_count=5
    )
    assert eligible is True
    assert improvement > 0.0

    # 5. Governance Approval & Activation
    PolicyVersioningEngine.retire_version(v1, PolicyStatus.SUPERSEDED)
    PolicyVersioningEngine.activate_version(candidate)

    assert v1.status == PolicyStatus.SUPERSEDED
    assert candidate.status == PolicyStatus.ACTIVE
    assert candidate.version == "1.1.0"
