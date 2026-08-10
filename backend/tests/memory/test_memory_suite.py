import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import asyncio
import uuid
import time
from datetime import datetime, timezone

from app.core.database import AsyncSessionLocal
from app.memory.models import MemoryRecordModel, MemoryType, OutcomeStatus
from app.memory.schemas import MemoryRecordCreate, OutcomeSubmissionRequest
from app.memory.service import MemoryService
from app.memory.retrieval import MemoryRetrievalEngine
from app.memory.outcome_engine import evaluate_outcome_variance, extract_deterministic_lesson
from app.auth.service import AuthService
from app.auth.repository import AuthRepository
from app.auth.schemas import UserRegisterRequest
from app.clients.service import ClientService
from app.clients.schemas import ClientCreateRequest
from app.governance.service import GovernanceService
from app.governance.schemas import ApprovalRequestCreate, ApprovalActionRequest
from app.governance.models import DecisionType
from fastapi import HTTPException

# 1. Deterministic Outcome Variance Engine Unit Tests
def test_outcome_engine():
    print("\n[1/5] Testing Outcome Variance Engine & Lesson Extractor...")
    
    # Success case (variance <= 10%)
    res_succ = evaluate_outcome_variance(predicted_value=4.0, actual_value=4.2, metric_name="ROAS", unit="x")
    assert res_succ["outcome_status"] == OutcomeStatus.SUCCESS
    assert res_succ["percentage_variance"] <= 10.0
    print(f"  [PASS] Outcome SUCCESS verified (Variance: {res_succ['percentage_variance']}%)")

    # Partial case (variance 10-30%)
    res_part = evaluate_outcome_variance(predicted_value=4.0, actual_value=3.2, metric_name="ROAS", unit="x")
    assert res_part["outcome_status"] == OutcomeStatus.PARTIAL
    print(f"  [PASS] Outcome PARTIAL verified (Variance: {res_part['percentage_variance']}%)")

    # Failed case (variance > 30%)
    res_fail = evaluate_outcome_variance(predicted_value=4.0, actual_value=2.2, metric_name="ROAS", unit="x")
    assert res_fail["outcome_status"] == OutcomeStatus.FAILED
    assert res_fail["percentage_variance"] > 30.0
    print(f"  [PASS] Outcome FAILED verified (Variance: {res_fail['percentage_variance']}%)")

    # Lesson Extractor
    lesson = extract_deterministic_lesson(
        metric_name="ROAS", predicted_value=4.0, actual_value=2.2, unit="x",
        outcome_status=OutcomeStatus.FAILED, pct_var=res_fail["percentage_variance"]
    )
    assert "forecast" in lesson.lower() and "45.0%" in lesson
    print(f"  [PASS] Deterministic Lesson Extracted: '{lesson}'")


# 2. Database Memory CRUD & Multi-Tenant Security Tests
async def test_memory_crud_and_security():
    print("\n[2/5] Testing Memory CRUD, Retrieval Ranking & Multi-Tenant Isolation...")
    
    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)

        # Setup Org A & Org B
        reg_a = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Mem-Org-A-{uid}", full_name="Admin Mem A",
            email=f"admin-mem-a-{uid}@mem.io", password="Password123!"
        ))
        org_a_id = reg_a.organization_id

        reg_b = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Mem-Org-B-{uid}", full_name="Admin Mem B",
            email=f"admin-mem-b-{uid}@mem.io", password="Password123!"
        ))
        org_b_id = reg_b.organization_id

        service = MemoryService(db)

        # Create Memories in Org A
        mem_a1 = await service.create_memory(MemoryRecordCreate(
            title="Google Search ROAS Calibration",
            content="Historical Google Search ROAS predicted 4.2x actual 4.1x.",
            memory_type=MemoryType.LESSON,
            confidence_score=95.0,
            importance_score=85.0,
            outcome_status=OutcomeStatus.SUCCESS,
            extra_metadata={"industry": "Healthcare"}
        ), org_id=org_a_id, creator_id=reg_a.id)

        mem_a2 = await service.create_memory(MemoryRecordCreate(
            title="LinkedIn Campaign Audience Penalty",
            content="LinkedIn ad CPC exceeded target by 35%.",
            memory_type=MemoryType.LESSON,
            confidence_score=88.0,
            importance_score=70.0,
            outcome_status=OutcomeStatus.FAILED,
            extra_metadata={"industry": "Healthcare"}
        ), org_id=org_a_id, creator_id=reg_a.id)

        assert mem_a1.id is not None
        assert mem_a2.id is not None
        print(f"  [PASS] Created 2 Memory Records in Org A (ID: {mem_a1.id[:8]}, {mem_a2.id[:8]})")

        # TEST: Multi-Tenant Isolation (Org B requesting Org A memory)
        print("  [TEST] Verifying Multi-Tenant Memory Access Block...")
        try:
            await service.get_memory(mem_a1.id, org_id=org_b_id)
            assert False, "Org B should not access Org A memory record"
        except HTTPException as exc:
            assert exc.status_code == 404
            print("  [PASS] Multi-tenant memory access correctly BLOCKED!")

        # TEST: Memory Retrieval & Ranking Algorithm
        print("  [TEST] Testing Deterministic Memory Retrieval & Scoring...")
        retrieved = await service.retrieve_memories_for_context(
            org_id=org_a_id, query="Google Search ROAS", limit=5
        )
        assert len(retrieved) >= 1
        assert retrieved[0].id == mem_a1.id
        assert retrieved[0].relevance_score > 0
        print(f"  [PASS] Memory Retrieval Ranked Top Result: '{retrieved[0].title}' (Score: {retrieved[0].relevance_score})")


# 3. Outcome Submission & Lesson Engine Test
async def test_outcome_submission_workflow():
    print("\n[3/5] Testing Outcome Submission API & Automated Lesson Generation...")
    
    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)

        reg = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Mem-Out-Org-{uid}", full_name="Admin Out",
            email=f"admin-out-{uid}@mem.io", password="Password123!"
        ))
        org_id = reg.organization_id

        service = MemoryService(db)

        # Submit Actual Outcome
        outcome_resp = await service.submit_outcome(OutcomeSubmissionRequest(
            metric_name="Customer Acquisition Cost (CAC)",
            predicted_value=45.0,
            actual_value=42.0,
            unit="$",
            notes="Q3 Paid Search Campaign Results"
        ), org_id=org_id, creator_id=reg.id)

        assert outcome_resp.outcome_status == OutcomeStatus.SUCCESS
        assert outcome_resp.outcome_memory_id is not None
        assert outcome_resp.lesson_memory_id is not None
        print(f"  [PASS] Outcome & Lesson Created! Outcome Status: {outcome_resp.outcome_status.value}, Variance: {outcome_resp.percentage_variance}%")

        # Verify database records
        out_mem = await service.get_memory(outcome_resp.outcome_memory_id, org_id=org_id)
        assert out_mem.memory_type == MemoryType.OUTCOME
        assert out_mem.structured_data["actual_value"] == 42.0

        les_mem = await service.get_memory(outcome_resp.lesson_memory_id, org_id=org_id)
        assert les_mem.memory_type == MemoryType.LESSON
        print(f"  [PASS] Outcome & Lesson Database Records Verified Successfully!")


# 4. Governance & Approval Decision Memory Test
async def test_governance_decision_memory():
    print("\n[4/5] Testing Automated Decision & Approval Memory Hooks...")

    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)
        auth_repo = AuthRepository(db)

        reg = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Gov-Mem-Org-{uid}", full_name="Admin GovMem",
            email=f"admin-govmem-{uid}@mem.io", password="Password123!"
        ))
        org_id = reg.organization_id
        admin = await auth_repo.get_user_by_id(reg.id)

        gov_service = GovernanceService(db)
        mem_service = MemoryService(db)

        # Create Approval Request
        req_create = ApprovalRequestCreate(
            title="Strategic Repositioning Flight",
            description="Authorize 90-Day positioning shift",
            decision_type=DecisionType.STRATEGY_CHANGE,
            ai_confidence_score=94.0,
            evidence_count=5
        )
        app_res = await gov_service.create_approval_request(req_create, org_id=org_id, creator_id=admin.id)

        # Check DECISION Memory creation
        mems, total = await mem_service.repo.list_by_org(org_id, memory_type=MemoryType.DECISION)
        assert total >= 1
        print(f"  [PASS] Automated DECISION Memory created for approval request (Total: {total})")


async def main():
    test_outcome_engine()
    await test_memory_crud_and_security()
    await test_outcome_submission_workflow()
    await test_governance_decision_memory()
    print("\n=======================================================")
    print("ALL STRTOS v1.1.0 MEMORY SUITE TESTS PASSED!")
    print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
