import asyncio
from app.agents.marketing_strategy.schemas import MarketingStrategyInput, MarketingStrategyResult
from app.agents.marketing_strategy.validator import MarketingStrategyValidator
from app.agents.marketing_strategy.service import MarketingStrategyService
from app.agents.marketing_strategy.interfaces import MarketingStrategyAgent
from app.agents.ceo.graph.state import CEOTaskItem, PriorityLevel, TaskStatus
from app.core.exceptions import ValidationException

async def test_validator_input():
    validator = MarketingStrategyValidator()
    valid_input = MarketingStrategyInput(
        business_analysis_result={"status": "COMPLETED"},
        seo_audit_result={"status": "COMPLETED"},
        competitor_research_result={"status": "COMPLETED"}
    )
    assert validator.validate_input(valid_input) is True

    try:
        invalid_input = MarketingStrategyInput(
            business_analysis_result={},
            seo_audit_result={"status": "COMPLETED"},
            competitor_research_result={"status": "COMPLETED"}
        )
        validator.validate_input(invalid_input)
        assert False, "Should have raised ValidationException for missing business_analysis_result"
    except ValidationException:
        pass

async def test_marketing_strategy_service_execution():
    service = MarketingStrategyService()
    payload = MarketingStrategyInput(
        business_analysis_result={"status": "COMPLETED"},
        seo_audit_result={"status": "COMPLETED"},
        competitor_research_result={"status": "COMPLETED"},
        business_goal="Acquire 10k online customers",
        budget="$10,000 / mo"
    )
    result = await service.create_strategy(payload)
    assert isinstance(result, MarketingStrategyResult)
    assert "Synthesized multi-channel growth strategy" in result.executive_marketing_summary
    assert len(result.channel_recommendations) == 3
    assert len(result.marketing_funnel) == 3
    assert len(result.growth_roadmap) == 3
    assert result.confidence_score >= 95.0

async def test_marketing_ceo_interface_delegation():
    agent = MarketingStrategyAgent()
    task = CEOTaskItem(
        task_id="test-mkt-1",
        title="Draft Lumen Studios Q1 narrative",
        agent_name="Marketing Strategy Agent",
        priority=PriorityLevel.HIGH,
        status=TaskStatus.WAITING
    )
    context = {
        "client_name": "Lumen Studios",
        "directive": "Acquire 10k online customers",
        "business_analysis_result": {"status": "COMPLETED"},
        "seo_audit_result": {"status": "COMPLETED"},
        "competitor_research_result": {"status": "COMPLETED"}
    }
    response = await agent.execute_task(task, context)
    assert response["agent_name"] == "Marketing Strategy Agent"
    assert response["status"] == "COMPLETED"
    assert "full_result" in response
    assert len(response["full_result"]["channel_recommendations"]) == 3
