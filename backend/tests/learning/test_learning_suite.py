import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import asyncio
import uuid
from datetime import datetime, timezone

from app.core.database import AsyncSessionLocal
from app.learning.models import ReliabilityClass, PolicyStatus, AdaptationStatus, AgentPolicyModel
from app.learning.reliability_engine import ReliabilityEngine
from app.learning.adaptation_engine import AdaptationEngine
from app.learning.policy_engine import PolicyRollbackEngine
from app.learning.service import LearningService
from app.learning.repository import LearningRepository
from app.auth.service import AuthService
from app.auth.repository import AuthRepository
from app.auth.schemas import UserRegisterRequest
from fastapi import HTTPException

# 1. Reliability Engine Unit Test
def test_reliability_engine_scoring():
    print("\n[1/5] Testing Deterministic Reliability Engine & Weighting...")

    # Insufficient data check (<3 executions)
    score, r_class = ReliabilityEngine.calculate_reliability(
        total_executions=2, successful_executions=2, prediction_accuracy=90.0,
        outcome_success_rate=90.0, evidence_quality_score=90.0, human_approval_rate=90.0,
        tool_success_rate=90.0, swarm_consensus_rate=90.0
    )
    assert r_class == ReliabilityClass.INSUFFICIENT_DATA
    assert score == 0.0
    print("  [PASS] INSUFFICIENT_DATA correctly returned for < 3 executions!")

    # Deterministic High Score Calculation
    score_high, class_high = ReliabilityEngine.calculate_reliability(
        total_executions=10, successful_executions=10, prediction_accuracy=95.0,
        outcome_success_rate=90.0, evidence_quality_score=85.0, human_approval_rate=90.0,
        tool_success_rate=95.0, swarm_consensus_rate=90.0
    )
    assert score_high >= 90.0
    assert class_high == ReliabilityClass.EXCELLENT
    print(f"  [PASS] Deterministic score {score_high}% calculated with EXCELLENT classification!")


# 2. Adaptation Engine Bounded Limits Unit Test
def test_adaptation_engine_bounded_limits():
    print("\n[2/5] Testing Bounded Adaptation Engine Limits (Max 10% Delta)...")

    class MockPerf:
        total_executions = 5
        current_reliability_score = 85.0
        prediction_accuracy = 85.0

    valid, delta, msg = AdaptationEngine.evaluate_adaptation_proposal(MockPerf(), proposed_delta=25.0)
    assert valid is True
    assert delta == 10.0  # Clamped to MAX_ADAPTATION_DELTA 10%
    print(f"  [PASS] Proposed delta of +25% correctly clamped to bounded limit of +{delta}%!")


# 3. Policy Rollback Engine Degradation Test
def test_policy_rollback_engine():
    print("\n[3/5] Testing Policy Rollback Engine Degradation Detection...")

    # Performance drop > 15%
    should_rollback, reason = PolicyRollbackEngine.should_trigger_rollback(
        prior_score=90.0, current_score=70.0, prior_accuracy=85.0, current_accuracy=85.0,
        prior_rejection=10.0, current_rejection=10.0
    )
    assert should_rollback is True
    assert "dropped by 20.0%" in reason
    print(f"  [PASS] Policy Rollback correctly triggered on 20% score drop: {reason}")


# 4. Learning Service E2E Integration Test
async def test_learning_service_e2e():
    print("\n[4/5] Testing Learning Service E2E Telemetry, Policies & Rollback...")

    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)

        # Register Org
        reg = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Learn-Org-{uid}", full_name="Admin Learn",
            email=f"admin-learn-{uid}@exec.io", password="Password123!"
        ))
        org_id = reg.organization_id
        auth_repo = AuthRepository(db)
        user = await auth_repo.get_user_by_id(reg.id)

        service = LearningService(db)

        # Record telemetry for Business Analysis Agent
        for _ in range(3):
            await service.record_execution_telemetry(
                agent_name="Business Analysis Agent",
                status_val="SUCCESS",
                confidence=90.0,
                latency_ms=1200.0,
                token_usage=1500,
                org_id=org_id,
                prediction_accuracy=92.0
            )

        perf = await service.get_agent_performance("Business Analysis Agent", org_id=org_id)
        assert perf.total_executions == 3
        assert perf.current_reliability_score > 0.0
        print(f"  [PASS] Recorded 3 telemetry executions! Reliability Score: {perf.current_reliability_score}%")

        # Propose Bounded Adaptation
        adapt = await service.propose_agent_adaptation(
            agent_name="Business Analysis Agent",
            proposed_delta=5.0,
            org_id=org_id,
            creator_user=user
        )
        assert adapt.id is not None
        assert adapt.adaptation_delta == 5.0
        print(f"  [PASS] Proposed Bounded Adaptation (ID: {adapt.id[:8]}, Delta: +{adapt.adaptation_delta}%)")

        # Create 2 versioned policies & activate sequentially
        repo = LearningRepository(db)
        p1 = await repo.create_agent_policy(AgentPolicyModel(
            organization_id=org_id, agent_name="Business Analysis Agent", policy_version="1.0.0",
            configuration={"temperature": 0.2}, reason="Base policy", status=PolicyStatus.DRAFT
        ))
        p2 = await repo.create_agent_policy(AgentPolicyModel(
            organization_id=org_id, agent_name="Business Analysis Agent", policy_version="1.1.0",
            configuration={"temperature": 0.4}, reason="Adapted policy", status=PolicyStatus.DRAFT
        ))
        await db.commit()

        await service.activate_policy(p1.id, org_id)
        await service.activate_policy(p2.id, org_id)

        rb_res = await service.rollback_policy("Business Analysis Agent", org_id=org_id)
        assert rb_res.rolled_back_policy_id == p2.id
        assert rb_res.activated_policy_id == p1.id
        print("  [PASS] Executed versioned policy rollback back to policy 1.0.0 cleanly!")


# 5. Multi-Tenant Security Test
async def test_learning_multi_tenant_security():
    print("\n[5/5] Testing Learning Multi-Tenant Security Isolation...")

    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)

        reg_a = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Learn-Org-A-{uid}", full_name="Admin Learn A",
            email=f"admin-learn-a-{uid}@exec.io", password="Password123!"
        ))
        org_a_id = reg_a.organization_id

        reg_b = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Learn-Org-B-{uid}", full_name="Admin Learn B",
            email=f"admin-learn-b-{uid}@exec.io", password="Password123!"
        ))
        org_b_id = reg_b.organization_id

        service = LearningService(db)
        await service.record_execution_telemetry(
            agent_name="SEO Audit Agent", status_val="SUCCESS", confidence=95.0,
            latency_ms=1000.0, token_usage=1000, org_id=org_a_id
        )

        perf_b = await service.list_agent_performances(org_id=org_b_id)
        seo_b = [p for p in perf_b if p.agent_name == "SEO Audit Agent"][0]
        assert seo_b.total_executions == 0
        print("  [PASS] Multi-tenant isolation verified: Org B cannot see Org A learning telemetry!")


async def main():
    test_reliability_engine_scoring()
    test_adaptation_engine_bounded_limits()
    test_policy_rollback_engine()
    await test_learning_service_e2e()
    await test_learning_multi_tenant_security()
    print("\n=======================================================")
    print("ALL STRTOS v1.5.0 LEARNING SUITE TESTS PASSED!")
    print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
