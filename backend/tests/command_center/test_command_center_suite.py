import pytest
from app.core.database import AsyncSessionLocal
from app.command_center.service import CommandCenterService

@pytest.mark.asyncio
async def test_command_center_models_service_and_engines():
    async with AsyncSessionLocal() as session:
        service = CommandCenterService(session)
        org_id = "test-cc-org-1"

        # 1. Get Overview & Executive Health
        overview = await service.get_overview(org_id)
        assert overview.organization_id == org_id
        assert overview.executive_health.overall_score >= 80.0
        assert len(overview.top_priorities) >= 1
        assert len(overview.active_decisions) >= 1

        decision_id = overview.active_decisions[0].id

        # 2. Test Alternatives & Do Nothing Simulation
        alternatives = await service.get_decision_alternatives(decision_id, org_id)
        assert len(alternatives) == 4
        types = [a.option_type for a in alternatives]
        assert "DO_NOTHING" in types
        assert "RECOMMENDED_ACTION" in types

        # 3. Test Decision Explanation Graph
        exp = await service.get_decision_explanation(decision_id, org_id)
        assert exp.decision_id == decision_id
        assert len(exp.verified_evidence) >= 1

        # 4. Multi-Agent Swarm Consensus
        consensus = await service.get_multi_agent_consensus(decision_id, org_id)
        assert consensus.consensus_score >= 80.0
        assert len(consensus.supporting_agents) >= 1

        # 5. Multi-Tenant Check
        try:
            await service.get_decision(decision_id, org_id="unauthorized-org")
            assert False, "Should have failed multi-tenant check"
        except KeyError:
            pass
