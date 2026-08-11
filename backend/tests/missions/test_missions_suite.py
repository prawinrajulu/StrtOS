import pytest
from app.core.database import AsyncSessionLocal
from app.missions.models import MissionStatus
from app.missions.service import MissionService
from app.missions.schemas import MissionCreate, MissionSuccessCriterionCreate, MissionReplanRequest

@pytest.mark.asyncio
async def test_missions_models_service_and_engines():
    async with AsyncSessionLocal() as session:
        service = MissionService(session)
        org_id = "test-mission-org-1"

        # 1. Create Mission
        m = await service.create_mission(
            MissionCreate(
                title="Q1 ARR Scaling & Conversion Recovery Mission",
                summary="Execute autonomous strategic steps to recover mid-funnel conversion yield.",
                criteria=[
                    MissionSuccessCriterionCreate(
                        metric_name="Quarterly ARR",
                        baseline_value=450000.0,
                        target_value=600000.0,
                        unit="USD"
                    )
                ]
            ),
            org_id=org_id
        )
        assert m.title == "Q1 ARR Scaling & Conversion Recovery Mission"
        assert m.status == MissionStatus.READY
        assert m.current_version == "v1.0.0"
        assert len(m.steps) == 4

        # 2. Start Mission
        active_m = await service.start_mission(m.id, org_id)
        assert active_m.status == MissionStatus.ACTIVE

        # 3. Evaluate Mission
        eval_res = await service.evaluate_mission(m.id, org_id)
        assert eval_res.mission_id == m.id
        assert eval_res.status.value in ["ON_TRACK", "AT_RISK", "COMPLETED"]

        # 4. Replanning & Bounded Adaptation (Max 10%)
        replan_m = await service.replan_mission(
            m.id,
            MissionReplanRequest(reason="Ad network CPM volatility shift", adaptation_delta_percentage=8.5),
            org_id=org_id
        )
        assert replan_m.current_version == "v1.1.0"
        assert len(replan_m.plans) >= 1

        # 5. Multi-Tenant Check
        try:
            await service.get_mission(m.id, org_id="unauthorized-org")
            assert False, "Should have failed multi-tenant check"
        except KeyError:
            pass
