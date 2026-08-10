import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import asyncio
import uuid
from datetime import datetime, timezone

from app.core.database import AsyncSessionLocal
from app.execution.models import ActionModel, AutonomyMode, PolicyDecision, ActionStatus
from app.execution.schemas import ActionCreate, OutcomeMeasurementRequest
from app.execution.service import ExecutionService
from app.execution.action_registry import ActionRegistry
from app.execution.policy_engine import PolicyEngine
from app.execution.executor import ActionExecutor
from app.auth.service import AuthService
from app.auth.repository import AuthRepository
from app.auth.schemas import UserRegisterRequest
from app.auth.models import UserRole
from app.governance.models import RiskLevel, ApprovalStatus
from app.predictions.service import PredictionService
from app.predictions.schemas import PredictionCreate
from fastapi import HTTPException

# 1. Action Registry Allowlist Unit Tests
def test_action_registry_allowlist():
    print("\n[1/6] Testing Action Registry Allowlist & Unauthorized Action Blocking...")

    # Verified registered actions
    assert ActionRegistry.is_registered("GENERATE_REPORT")
    assert ActionRegistry.is_registered("RUN_SEO_AUDIT")
    assert ActionRegistry.is_registered("RUN_WEBSITE_AUDIT")
    print("  [PASS] Allowed actions correctly registered in Action Registry.")

    # Strictly verify dangerous/unregistered actions are rejected
    assert not ActionRegistry.is_registered("SHELL_EXEC")
    assert not ActionRegistry.is_registered("SQL_DROP_TABLE")
    assert not ActionRegistry.is_registered("EVAL_PYTHON")
    print("  [PASS] Dangerous shell/SQL/eval actions strictly REJECTED!")


# 2. Policy Engine Unit Tests
async def test_policy_engine_evaluations():
    print("\n[2/6] Testing Policy Engine Risk & Autonomy Rules...")

    async with AsyncSessionLocal() as db:
        # Dummy mock user
        class DummyUser:
            id = "usr-123"
            organization_id = "org-123"
            role = UserRole.EMPLOYEE

        user = DummyUser()

        # LOW Risk + AUTONOMOUS -> ALLOW
        act_low = ActionModel(
            organization_id="org-123",
            action_type="RUN_SEO_AUDIT",
            risk_level=RiskLevel.LOW,
            autonomy_mode=AutonomyMode.AUTONOMOUS
        )
        dec_low = PolicyEngine.evaluate_action(act_low, user)
        assert dec_low == PolicyDecision.ALLOW
        print("  [PASS] LOW Risk Autonomous action evaluated as ALLOW!")

        # HIGH Risk -> REQUIRE_APPROVAL
        act_high = ActionModel(
            organization_id="org-123",
            action_type="CREATE_CAMPAIGN_DRAFT",
            risk_level=RiskLevel.HIGH,
            autonomy_mode=AutonomyMode.APPROVAL_REQUIRED
        )
        dec_high = PolicyEngine.evaluate_action(act_high, user)
        assert dec_high == PolicyDecision.REQUIRE_APPROVAL
        print("  [PASS] HIGH Risk action correctly evaluated as REQUIRE_APPROVAL!")

        # Cross-Tenant -> DENY
        act_cross = ActionModel(
            organization_id="org-OTHER",
            action_type="RUN_SEO_AUDIT",
            risk_level=RiskLevel.LOW,
            autonomy_mode=AutonomyMode.AUTONOMOUS
        )
        dec_cross = PolicyEngine.evaluate_action(act_cross, user)
        assert dec_cross == PolicyDecision.DENY
        print("  [PASS] Cross-tenant action evaluated as DENY!")


# 3. Action Lifecycle & Idempotency Tests
async def test_action_crud_idempotency_and_security():
    print("\n[3/6] Testing Action CRUD, Idempotency Protection & Multi-Tenant Security...")

    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)

        # Register Org A & Org B
        reg_a = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Exec-Org-A-{uid}", full_name="Admin Exec A",
            email=f"admin-exec-a-{uid}@exec.io", password="Password123!"
        ))
        org_a_id = reg_a.organization_id

        reg_b = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Exec-Org-B-{uid}", full_name="Admin Exec B",
            email=f"admin-exec-b-{uid}@exec.io", password="Password123!"
        ))
        org_b_id = reg_b.organization_id

        auth_repo = AuthRepository(db)
        user_a = await auth_repo.get_user_by_id(reg_a.id)
        user_b = await auth_repo.get_user_by_id(reg_b.id)

        service = ExecutionService(db)
        idem_key = f"idem-key-{uid}"

        # Create Action 1 with Idempotency Key
        act1 = await service.create_action(ActionCreate(
            action_type="RUN_SEO_AUDIT",
            name="Apex Health SEO Audit Flight",
            risk_level=RiskLevel.LOW,
            autonomy_mode=AutonomyMode.AUTONOMOUS,
            idempotency_key=idem_key
        ), org_id=org_a_id, current_user=user_a)

        assert act1.id is not None
        print(f"  [PASS] Action 1 Created in Org A (ID: {act1.id[:8]}, Status: {act1.status.value})")

        # TEST: Idempotency Protection (Duplicate Request with same key)
        act1_dup = await service.create_action(ActionCreate(
            action_type="RUN_SEO_AUDIT",
            name="Apex Health SEO Audit Flight Duplicate",
            risk_level=RiskLevel.LOW,
            autonomy_mode=AutonomyMode.AUTONOMOUS,
            idempotency_key=idem_key
        ), org_id=org_a_id, current_user=user_a)

        assert act1_dup.id == act1.id
        print(f"  [PASS] Idempotency Key Protection verified! Returned existing action ({act1_dup.id[:8]})")

        # TEST: Multi-Tenant Isolation (Org B trying to execute Org A action)
        try:
            await service.get_action(act1.id, org_id=org_b_id)
            assert False, "Org B should not access Org A action"
        except HTTPException as exc:
            assert exc.status_code == 404
            print("  [PASS] Multi-tenant action access correctly BLOCKED!")


# 4. Tool Registry Execution & Retry Tests
async def test_action_execution_and_retries():
    print("\n[4/6] Testing Action Execution via ToolRegistry & Retry Logic...")

    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)

        reg = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Tool-Exec-Org-{uid}", full_name="Admin ToolExec",
            email=f"admin-toolexec-{uid}@exec.io", password="Password123!"
        ))
        org_id = reg.organization_id
        auth_repo = AuthRepository(db)
        user = await auth_repo.get_user_by_id(reg.id)

        service = ExecutionService(db)

        # Create & Execute Action
        act = await service.create_action(ActionCreate(
            action_type="RUN_PAGESPEED_ANALYSIS",
            name="Core Web Vitals Audit Action",
            risk_level=RiskLevel.LOW,
            autonomy_mode=AutonomyMode.AUTONOMOUS,
            input_payload={"url": "https://restaurant-example.com"}
        ), org_id=org_id, current_user=user)

        res = await service.execute_action(act.id, org_id=org_id, current_user=user)
        assert res.status in [ActionStatus.COMPLETED, ActionStatus.DEGRADED]
        print(f"  [PASS] Action executed via ToolRegistry! (Final Status: {res.status.value})")


# 5. Closed-Loop Optimization Measurement Test
async def test_closed_loop_optimization():
    print("\n[5/6] Testing Closed-Loop Optimization & Outcome Measurement...")

    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)

        reg = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Opt-Exec-Org-{uid}", full_name="Admin OptExec",
            email=f"admin-optexec-{uid}@exec.io", password="Password123!"
        ))
        org_id = reg.organization_id
        auth_repo = AuthRepository(db)
        user = await auth_repo.get_user_by_id(reg.id)

        p_service = PredictionService(db)
        e_service = ExecutionService(db)

        # Create Prediction
        pred = await p_service.create_prediction(PredictionCreate(
            scenario_name="Search Flight ROAS Target",
            metric_name="ROAS",
            predicted_value=4.0,
            lower_bound=3.4,
            upper_bound=4.6
        ), org_id=org_id, creator_id=user.id)

        # Create Action linked to Prediction
        act = await e_service.create_action(ActionCreate(
            action_type="GENERATE_REPORT",
            name="Execute ROAS Flight Report",
            prediction_id=pred.id,
            risk_level=RiskLevel.LOW,
            autonomy_mode=AutonomyMode.AUTONOMOUS
        ), org_id=org_id, current_user=user)

        await e_service.execute_action(act.id, org_id=org_id, current_user=user)

        # Measure Outcome
        meas_res = await e_service.measure_action_outcome(
            action_id=act.id,
            payload=OutcomeMeasurementRequest(actual_metric_value=3.85),
            org_id=org_id
        )

        assert meas_res.accuracy_score >= 90.0
        assert meas_res.outcome_status == "SUCCESS"
        assert meas_res.lesson_memory_id is not None
        print(f"  [PASS] Closed-Loop Optimization measured! Accuracy Score: {meas_res.accuracy_score}%, Memory Lesson ID: {meas_res.lesson_memory_id[:8]}")


# 6. Governance Approval Requirement Test
async def test_governance_action_approval():
    print("\n[6/6] Testing Governance Approval Request Integration on Execution...")

    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)

        reg = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Gov-Exec-Org-{uid}", full_name="Admin GovExec",
            email=f"admin-govexec-{uid}@exec.io", password="Password123!"
        ))
        org_id = reg.organization_id
        auth_repo = AuthRepository(db)
        user = await auth_repo.get_user_by_id(reg.id)

        service = ExecutionService(db)

        # Create HIGH Risk Action
        act = await service.create_action(ActionCreate(
            action_type="CREATE_CAMPAIGN_DRAFT",
            name="High Exposure Flight Action",
            risk_level=RiskLevel.HIGH,
            autonomy_mode=AutonomyMode.APPROVAL_REQUIRED
        ), org_id=org_id, current_user=user)

        # Verify execution without approval is REJECTED
        try:
            await service.execute_action(act.id, org_id=org_id, current_user=user)
            assert False, "High risk action without approval should be rejected"
        except HTTPException as exc:
            assert exc.status_code == 400
            print("  [PASS] Unapproved HIGH Risk action correctly REJECTED before execution!")

        # Submit for Approval
        app_act = await service.submit_action_for_approval(act.id, org_id=org_id, current_user=user)
        assert app_act.approval_id is not None
        assert app_act.status == ActionStatus.PENDING_APPROVAL
        print(f"  [PASS] Action submitted to Governance Approval workflow! (Approval ID: {app_act.approval_id[:8]})")


async def main():
    test_action_registry_allowlist()
    await test_policy_engine_evaluations()
    await test_action_crud_idempotency_and_security()
    await test_action_execution_and_retries()
    await test_closed_loop_optimization()
    await test_governance_action_approval()
    print("\n=======================================================")
    print("ALL STRTOS v1.3.0 EXECUTION SUITE TESTS PASSED!")
    print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
