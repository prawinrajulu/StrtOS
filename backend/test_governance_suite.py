import asyncio
import uuid
import time
from datetime import datetime, timezone

from app.core.database import AsyncSessionLocal
from app.governance.models import ApprovalRequestModel, ApprovalStatus, RiskLevel, DecisionType
from app.governance.risk_engine import calculate_decision_risk
from app.governance.schemas import ApprovalRequestCreate, ApprovalActionRequest
from app.governance.service import GovernanceService
from app.auth.service import AuthService
from app.auth.repository import AuthRepository
from app.auth.schemas import UserRegisterRequest
from app.auth.models import UserRole
from app.workflows.service import WorkflowService
from app.workflows.schemas import WorkflowCreateRequest
from app.clients.service import ClientService
from app.clients.schemas import ClientCreateRequest
from fastapi import HTTPException

# 1. Deterministic Risk Engine Unit Tests
def test_risk_engine():
    print("\n[1/5] Testing Deterministic Risk Engine...")
    
    # Low risk
    res_low = calculate_decision_risk(ai_confidence_score=96.0, evidence_count=6, is_reversible=True)
    assert res_low["risk_level"] == RiskLevel.LOW
    assert res_low["risk_score"] <= 25.0
    print(f"  [PASS] Low Risk - Level: {res_low['risk_level'].value}, Score: {res_low['risk_score']}")

    # Medium risk
    res_med = calculate_decision_risk(ai_confidence_score=75.0, evidence_count=3, is_reversible=True)
    assert res_med["risk_level"] == RiskLevel.MEDIUM
    print(f"  [PASS] Medium Risk - Level: {res_med['risk_level'].value}, Score: {res_med['risk_score']}")

    # High risk
    res_high = calculate_decision_risk(
        ai_confidence_score=60.0, evidence_count=0, decision_type=DecisionType.CAMPAIGN_LAUNCH, is_reversible=False
    )
    assert res_high["risk_level"] in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    print(f"  [PASS] High Risk - Level: {res_high['risk_level'].value}, Score: {res_high['risk_score']}")

    # Critical risk
    res_crit = calculate_decision_risk(
        ai_confidence_score=40.0, evidence_count=0, decision_type=DecisionType.BUDGET_CHANGE,
        requested_budget=50000.0, is_reversible=False, has_unavailable_evidence=True, ai_status="DEGRADED"
    )
    assert res_crit["risk_level"] == RiskLevel.CRITICAL
    assert res_crit["risk_score"] > 75.0
    print(f"  [PASS] Critical Risk - Level: {res_crit['risk_level'].value}, Score: {res_crit['risk_score']}")


# 2. Database & Governance Service Integration Tests
async def test_governance_service_and_security():
    print("\n[2/5] Testing Governance Service, RBAC, Multi-Tenant Isolation & Self-Approval Prevention...")
    
    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)
        auth_repo = AuthRepository(db)

        # Setup Org A Users via AuthRepository
        reg_a = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Gov-Org-A-{uid}", full_name="Admin Org A",
            email=f"admin-a-{uid}@gov.io", password="Password123!"
        ))
        org_a_id = reg_a.organization_id
        admin_a = await auth_repo.get_user_by_id(reg_a.id)

        emp_a = await auth_repo.create_user(
            org_id=org_a_id, full_name="Employee Org A",
            email=f"emp-a-{uid}@gov.io", password_hash="hash", role=UserRole.EMPLOYEE
        )
        viewer_a = await auth_repo.create_user(
            org_id=org_a_id, full_name="Viewer Org A",
            email=f"viewer-a-{uid}@gov.io", password_hash="hash", role=UserRole.VIEWER
        )

        # Setup Org B
        reg_b = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Gov-Org-B-{uid}", full_name="Admin Org B",
            email=f"admin-b-{uid}@gov.io", password="Password123!"
        ))
        org_b_id = reg_b.organization_id
        admin_b = await auth_repo.get_user_by_id(reg_b.id)
        await db.commit()

        service = GovernanceService(db)

        # Create Approval Request in Org A by emp_a
        req_create = ApprovalRequestCreate(
            title="High-Value Campaign Launch",
            description="Authorize $25,000 paid ad flighting plan",
            decision_type=DecisionType.CAMPAIGN_LAUNCH,
            ai_confidence_score=65.0,
            evidence_count=2,
            is_reversible=False
        )
        approval_res = await service.create_approval_request(req_create, org_id=org_a_id, creator_id=emp_a.id)
        assert approval_res.status == ApprovalStatus.PENDING_APPROVAL
        assert approval_res.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        print(f"  [PASS] Approval Request Created - Risk Level: {approval_res.risk_level.value}, Score: {approval_res.risk_score}")

        # TEST: Self-Approval Prevention (emp_a trying to approve own request)
        print("  [TEST] Verifying Self-Approval Prevention...")
        try:
            await service.approve_request(approval_res.id, ApprovalActionRequest(comment="Self approve"), org_id=org_a_id, reviewer_user=emp_a)
            assert False, "Should have rejected self-approval attempt"
        except HTTPException as exc:
            assert exc.status_code in [400, 403]
            assert "Self-approval" in exc.detail or "not authorized" in exc.detail
            print("  [PASS] Self-Approval correctly BLOCKED by backend service!")

        # TEST: RBAC Check (viewer_a trying to approve)
        print("  [TEST] Verifying Viewer Role Rejection...")
        try:
            await service.approve_request(approval_res.id, ApprovalActionRequest(comment="Viewer approve"), org_id=org_a_id, reviewer_user=viewer_a)
            assert False, "Should have rejected viewer approval"
        except HTTPException as exc:
            assert exc.status_code == 403
            print("  [PASS] Viewer Role Approval correctly FORBIDDEN!")

        # TEST: Multi-Tenant Isolation (admin_b in Org B trying to access/approve Org A request)
        print("  [TEST] Verifying Multi-Tenant Isolation...")
        try:
            await service.get_approval_request(approval_res.id, org_id=org_b_id)
            assert False, "Org B should not access Org A approval request"
        except HTTPException as exc:
            assert exc.status_code == 404
            print("  [PASS] Multi-tenant isolation verified (Org B blocked from Org A approval)!")

        # TEST: Valid Approval by admin_a (Authorized non-requestor in Org A)
        print("  [TEST] Executing Valid Approval by Admin Org A...")
        approved = await service.approve_request(approval_res.id, ApprovalActionRequest(comment="Approved by Org Admin"), org_id=org_a_id, reviewer_user=admin_a)
        assert approved.status == ApprovalStatus.APPROVED
        assert approved.reviewed_by == admin_a.id
        print("  [PASS] Valid Approval succeeded!")

        # TEST: Invalid State Transition (Approved -> Approved or Approved -> Rejected)
        print("  [TEST] Verifying Terminal State Transition Protection...")
        try:
            await service.approve_request(approval_res.id, ApprovalActionRequest(comment="Double approve"), org_id=org_a_id, reviewer_user=admin_a)
            assert False, "Should reject double approval"
        except HTTPException as exc:
            assert exc.status_code == 400
            print("  [PASS] Terminal state modification correctly REJECTED!")


# 3. Workflow Pause & Resume Integration Test
async def test_workflow_governance_pause():
    print("\n[3/5] Testing Workflow Governance Pause & Approval Continuation...")
    
    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)
        auth_repo = AuthRepository(db)

        reg = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Gov-Wf-Org-{uid}", full_name="Admin Wf",
            email=f"admin-wf-{uid}@gov.io", password="Password123!"
        ))
        org_id = reg.organization_id
        user = await auth_repo.get_user_by_id(reg.id)

        client_service = ClientService(db)
        client = await client_service.create_client(ClientCreateRequest(
            name="Apex Health", industry="Healthcare", website_url="https://apexhealth.io"
        ), org_id=org_id, creator_id=user.id)

        wf_service = WorkflowService(db)
        wf = await wf_service.create_workflow(WorkflowCreateRequest(
            client_id=client.id, title="Governance Approval Required: Apex Hospital Expansion", directive="High impact campaign launch."
        ), org_id=org_id, creator_id=user.id)

        # Start Workflow -> Should PAUSE due to "Approval Required" in title & high risk
        print("  [TEST] Starting Workflow requiring Governance Approval...")
        paused_wf = await wf_service.start_workflow(wf.id, org_id=org_id)
        assert paused_wf.status == "PAUSED"
        assert paused_wf.active_stage == "AWAITING HUMAN APPROVAL"
        print(f"  [PASS] Workflow PAUSED successfully! Status: {paused_wf.status}, Stage: {paused_wf.active_stage}")

        # Retrieve generated Approval Request
        gov_service = GovernanceService(db)
        approvals, total = await gov_service.repo.list_by_org(org_id, workflow_id=wf.id)
        assert total == 1
        app_req = approvals[0]
        assert app_req.status == ApprovalStatus.PENDING_APPROVAL
        print(f"  [PASS] Approval Request automatically generated! Risk: {app_req.risk_level.value}")

        # User 2 approves request
        user2 = await auth_repo.create_user(
            org_id=org_id, full_name="Admin Reviewer",
            email=f"reviewer-{uid}@gov.io", password_hash="hash", role=UserRole.ORG_ADMIN
        )
        await db.commit()

        await gov_service.approve_request(app_req.id, ApprovalActionRequest(comment="Approved execution"), org_id=org_id, reviewer_user=user2)
        print("  [PASS] Approval request approved by reviewer!")

        # Restart Workflow -> Now proceeds to COMPLETED
        print("  [TEST] Resuming Workflow after Governance Approval...")
        resumed_wf = await wf_service.start_workflow(wf.id, org_id=org_id)
        assert resumed_wf.status == "COMPLETED"
        print(f"  [PASS] Workflow resumed and COMPLETED successfully! Progress: {resumed_wf.progress}%")


async def main():
    test_risk_engine()
    await test_governance_service_and_security()
    await test_workflow_governance_pause()
    print("\n=======================================================")
    print("ALL STRTOS v1.0 GOVERNANCE SUITE TESTS PASSED!")
    print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
