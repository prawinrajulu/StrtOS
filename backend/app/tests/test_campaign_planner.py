import asyncio
from app.agents.campaign_planner.schemas import CampaignPlanningInput, CampaignPlanningResult
from app.agents.campaign_planner.validator import CampaignPlannerValidator
from app.agents.campaign_planner.service import CampaignPlannerService
from app.agents.campaign_planner.interfaces import CampaignPlannerAgent
from app.agents.ceo.graph.state import CEOTaskItem, PriorityLevel, TaskStatus
from app.core.exceptions import ValidationException

async def test_validator_input():
    validator = CampaignPlannerValidator()
    valid_input = CampaignPlanningInput(
        marketing_strategy_result={"status": "COMPLETED"}
    )
    assert validator.validate_input(valid_input) is True

    try:
        invalid_input = CampaignPlanningInput(
            marketing_strategy_result={}
        )
        validator.validate_input(invalid_input)
        assert False, "Should have raised ValidationException for missing marketing_strategy_result"
    except ValidationException:
        pass

async def test_campaign_planner_service_execution():
    service = CampaignPlannerService()
    payload = CampaignPlanningInput(
        marketing_strategy_result={"status": "COMPLETED"},
        business_goal="Acquire 10k online customers",
        budget="$10,000 / mo",
        timeline="90 Days"
    )
    result = await service.build_plan(payload)
    assert isinstance(result, CampaignPlanningResult)
    assert "Actionable 90-day campaign flighting plan" in result.campaign_summary
    assert len(result.creative_requirements) == 3
    assert len(result.weekly_roadmap) == 3
    assert len(result.launch_checklist) == 4
    assert result.confidence_score >= 95.0

async def test_campaign_ceo_interface_delegation():
    agent = CampaignPlannerAgent()
    task = CEOTaskItem(
        task_id="test-camp-1",
        title="Kite & Loom holiday media mix",
        agent_name="Campaign Planner Agent",
        priority=PriorityLevel.MEDIUM,
        status=TaskStatus.WAITING
    )
    context = {
        "client_name": "Kite & Loom",
        "directive": "Acquire holiday shoppers",
        "marketing_strategy_result": {"status": "COMPLETED"}
    }
    response = await agent.execute_task(task, context)
    assert response["agent_name"] == "Campaign Planner Agent"
    assert response["status"] == "COMPLETED"
    assert "full_result" in response
    assert len(response["full_result"]["creative_requirements"]) == 3
