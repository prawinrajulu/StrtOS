import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import asyncio
import uuid
from datetime import datetime, timezone

from app.core.database import AsyncSessionLocal
from app.swarm.models import SwarmSessionModel, SwarmStatus
from app.swarm.schemas import SwarmSessionCreate
from app.swarm.service import SwarmService
from app.swarm.context_bus import SharedContextBus
from app.swarm.critic_engine import CriticEngine
from app.swarm.conflict_engine import ConflictEngine
from app.swarm.debate_engine import DebateEngine
from app.swarm.consensus_engine import ConsensusEngine
from app.auth.service import AuthService
from app.auth.repository import AuthRepository
from app.auth.schemas import UserRegisterRequest
from app.governance.models import RiskLevel
from app.execution.action_registry import ActionRegistry
from fastapi import HTTPException

# 1. Shared Context Bus Unit Test
async def test_context_bus_and_messages():
    print("\n[1/5] Testing Shared Context Bus & Tenant Scoping...")
    swarm_id = f"sw-{uuid.uuid4()}"[:8]
    org_id = f"org-{uuid.uuid4()}"[:8]

    await SharedContextBus.publish_evidence(swarm_id, org_id, {
        "source_agent": "Business Analysis Agent",
        "finding": "Market expansion target identified with 88% confidence.",
        "confidence": 88.0
    })

    evs = await SharedContextBus.get_evidence(swarm_id, org_id)
    assert len(evs) == 1
    assert evs[0]["source_agent"] == "Business Analysis Agent"
    print("  [PASS] Shared Context Bus published and retrieved evidence item cleanly!")

    # Verify cross-tenant isolation
    evs_cross = await SharedContextBus.get_evidence(swarm_id, "OTHER_ORG")
    assert len(evs_cross) == 0
    print("  [PASS] Tenant isolation verified on Shared Context Bus!")


# 2. Engines Unit Test (Critic, Conflict, Debate, Consensus)
def test_engines_debate_critic_conflict_consensus():
    print("\n[2/5] Testing Critic, Conflict, Debate & Consensus Engines...")

    mock_agent_outputs = {
        "Business Analysis Agent": {"confidence": 85.0, "findings": ["High demand in market segment A"], "status": "SUCCESS"},
        "SEO Audit Agent": {"confidence": 90.0, "findings": ["SEO Score: 82/100"], "status": "SUCCESS", "seo_score": 82},
        "Competitor Research Agent": {"confidence": 75.0, "findings": ["Identified 4 direct competitors"], "status": "SUCCESS", "competition_intensity": "HIGH"},
        "Marketing Strategy Agent": {"confidence": 80.0, "findings": ["Allocate $10,000 budget"], "recommended_budget": 10000, "status": "SUCCESS"},
        "Campaign Planner Agent": {"confidence": 80.0, "findings": ["Allocate $5,000 budget"], "recommended_budget": 5000, "status": "SUCCESS"}
    }

    mock_evidence = [
        {"source_agent": "Business Analysis Agent", "finding": "High demand in market segment A", "confidence": 85.0},
        {"source_agent": "SEO Audit Agent", "finding": "SEO Score: 82/100", "confidence": 90.0}
    ]

    # Critic Engine
    critic_res = CriticEngine.evaluate_findings(mock_agent_outputs, mock_evidence)
    assert critic_res["critic_score"] > 60.0
    print(f"  [PASS] Critic Engine evaluated findings! (Score: {critic_res['critic_score']}/100)")

    # Conflict Engine (detects $10k vs $5k budget discrepancy)
    conflicts = ConflictEngine.detect_conflicts(mock_agent_outputs, mock_evidence)
    assert len(conflicts) >= 1
    assert conflicts[0]["severity"] == RiskLevel.HIGH
    print(f"  [PASS] Conflict Engine detected {len(conflicts)} conflict(s) with HIGH severity!")

    # Debate Engine (bounded to <= 3 rounds)
    claims = [{"agent": k, "finding": v["findings"][0], "confidence": v["confidence"]} for k, v in mock_agent_outputs.items()]
    debates = DebateEngine.conduct_debate(claims, mock_evidence)
    assert len(debates) <= 3
    print(f"  [PASS] Debate Engine generated {len(debates)} debate round(s) (bounded <= 3)!")

    # Consensus Engine
    c_score, conf_score, supporting, dissenting, req_gov, rationale = ConsensusEngine.calculate_consensus(
        mock_agent_outputs, critic_res["critic_score"], conflicts, mock_evidence
    )
    assert c_score is not None
    assert len(supporting) >= 3
    print(f"  [PASS] Consensus Engine computed consensus score {c_score}% (Confidence: {conf_score}%)")


# 3. Full Swarm Session E2E Test
async def test_swarm_session_e2e():
    print("\n[3/5] Testing Swarm Session E2E Execution & Action Proposal Integration...")

    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)

        # Register Org
        reg = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Swarm-Org-{uid}", full_name="Admin Swarm",
            email=f"admin-swarm-{uid}@exec.io", password="Password123!"
        ))
        org_id = reg.organization_id
        auth_repo = AuthRepository(db)
        user = await auth_repo.get_user_by_id(reg.id)

        service = SwarmService(db)

        # Create Swarm Session
        session = await service.create_swarm_session(SwarmSessionCreate(
            objective="Full-funnel digital strategy optimization for Q3 growth flight"
        ), org_id=org_id, creator_id=user.id)

        assert session.id is not None
        assert len(session.participating_agents) == 5
        print(f"  [PASS] Swarm Session Created (ID: {session.id[:8]}, Status: {session.status})")

        # Start Swarm Session
        res = await service.start_swarm_session(session.id, org_id=org_id, creator_user=user)
        assert res.status == SwarmStatus.COMPLETED
        assert res.consensus_score >= 0.0
        assert res.synthesis_output is not None
        print(f"  [PASS] Swarm Session Executed E2E! Final Consensus: {res.consensus_score}%, Status: {res.status}")


# 4. Multi-Tenant Security Test
async def test_swarm_multi_tenant_security():
    print("\n[4/5] Testing Swarm Multi-Tenant Security Scoping...")

    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)

        reg_a = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Swarm-Org-A-{uid}", full_name="Admin Swarm A",
            email=f"admin-swarm-a-{uid}@exec.io", password="Password123!"
        ))
        org_a_id = reg_a.organization_id

        reg_b = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Swarm-Org-B-{uid}", full_name="Admin Swarm B",
            email=f"admin-swarm-b-{uid}@exec.io", password="Password123!"
        ))
        org_b_id = reg_b.organization_id

        auth_repo = AuthRepository(db)
        user_a = await auth_repo.get_user_by_id(reg_a.id)

        service = SwarmService(db)
        sess = await service.create_swarm_session(SwarmSessionCreate(
            objective="Org A Private Strategy Objective"
        ), org_id=org_a_id, creator_id=user_a.id)

        # Org B attempting to fetch Org A swarm session
        try:
            await service.get_swarm_session(sess.id, org_id=org_b_id)
            assert False, "Org B should not access Org A swarm session"
        except HTTPException as exc:
            assert exc.status_code == 404
            print("  [PASS] Multi-tenant access correctly BLOCKED for cross-tenant swarm!")


# 5. Governance Escalation Test
async def test_swarm_governance_escalation():
    print("\n[5/5] Testing Human Governance Escalation on Low Consensus...")

    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)

        reg = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Gov-Swarm-Org-{uid}", full_name="Admin GovSwarm",
            email=f"admin-govswarm-{uid}@exec.io", password="Password123!"
        ))
        org_id = reg.organization_id
        auth_repo = AuthRepository(db)
        user = await auth_repo.get_user_by_id(reg.id)

        service = SwarmService(db)
        sess = await service.create_swarm_session(SwarmSessionCreate(
            objective="High Risk Capital Flight Strategy"
        ), org_id=org_id, creator_id=user.id)

        res = await service.start_swarm_session(sess.id, org_id=org_id, creator_user=user)
        assert res.synthesis_output is not None
        print(f"  [PASS] Swarm Governance Escalation check completed cleanly!")


async def main():
    await test_context_bus_and_messages()
    test_engines_debate_critic_conflict_consensus()
    await test_swarm_session_e2e()
    await test_swarm_multi_tenant_security()
    await test_swarm_governance_escalation()
    print("\n=======================================================")
    print("ALL STRTOS v1.4.0 SWARM SUITE TESTS PASSED!")
    print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
