import pytest
import pytest_asyncio
from app.core.database import AsyncSessionLocal
from app.strategy.models import (
    StrategicObjectiveModel, StrategicMetricModel, StrategicConstraintModel,
    StrategicPlanModel, StrategicMilestoneModel, StrategicPlanVersionModel,
    ObjectiveLifecycle, HorizonType, ScenarioType
)
from app.strategy.engine import StrategicPlanningEngine, MAX_ADAPTATION_DELTA
from app.strategy.service import StrategyService
from app.strategy.schemas import (
    StrategicObjectiveCreate, StrategicPlanCreate, StrategyAdaptationRequest
)

@pytest.mark.asyncio
async def test_strategy_models_and_repository():
    async with AsyncSessionLocal() as session:
        service = StrategyService(session)
        org_id = "test-strategy-org-1"

        # 1. Create Objective
        obj = await service.create_objective(
            StrategicObjectiveCreate(
                title="Expand SaaS ARR to $10M",
                description="Scale enterprise ARR via performance marketing & SEO.",
                category="Revenue Growth",
                target_horizon=HorizonType.DAYS_90,
                baseline_value=2000000.0,
                target_value=10000000.0,
                unit="USD"
            ),
            org_id=org_id
        )
        assert obj.title == "Expand SaaS ARR to $10M"
        assert obj.status == ObjectiveLifecycle.DRAFT

        # 2. Generate Scenarios
        scenarios = await service.generate_scenarios(obj.id, org_id)
        assert len(scenarios) == 3
        types = [s.scenario_type for s in scenarios]
        assert ScenarioType.CONSERVATIVE in types
        assert ScenarioType.BALANCED in types
        assert ScenarioType.AGGRESSIVE in types

        # 3. Create Plan
        plan = await service.create_plan(
            StrategicPlanCreate(
                objective_id=obj.id,
                title="Balanced SaaS Scaling Plan",
                scenario_type=ScenarioType.BALANCED,
                horizon=HorizonType.DAYS_90
            ),
            org_id=org_id
        )
        assert plan.objective_id == obj.id
        assert len(plan.milestones) == 3
        assert len(plan.versions) == 1
        assert plan.version == "1.0.0"

        # 4. Evaluate Plan Constraints
        eval_res = await service.evaluate_plan(plan.id, org_id)
        assert eval_res.is_valid is True
        assert eval_res.evaluation_status == "PASSED"

        # 5. Get Plan Explanation
        explanation = await service.get_explanation(plan.id, org_id)
        assert explanation.plan_id == plan.id
        assert "Expand SaaS ARR to $10M" in explanation.why_objective

        # 6. Bounded Adaptation
        adaptation = await service.adapt_plan(
            plan.id,
            StrategyAdaptationRequest(
                actual_performance=11000000.0,
                adaptation_reason="Outperformed Q1 milestone target"
            ),
            org_id=org_id
        )
        assert adaptation.new_version == "1.1.0"
        assert adaptation.bounded is True or adaptation.adaptation_delta_pct == 10.0
        assert adaptation.adaptation_delta_pct <= (MAX_ADAPTATION_DELTA * 100.0)

        # 7. Multi-Tenant Isolation Verification
        try:
            await service.get_plan(plan.id, org_id="unauthorized-org")
            assert False, "Should have failed multi-tenant check"
        except KeyError:
            pass
