import asyncio
from app.agents.competitor_research.schemas import CompetitorResearchInput, CompetitorResearchResult
from app.agents.competitor_research.validator import CompetitorResearchValidator
from app.agents.competitor_research.service import CompetitorResearchService
from app.agents.competitor_research.interfaces import CompetitorResearchAgent
from app.agents.ceo.graph.state import CEOTaskItem, PriorityLevel, TaskStatus
from app.core.exceptions import ValidationException

async def test_validator_input():
    validator = CompetitorResearchValidator()
    valid_input = CompetitorResearchInput(business_name="Arcadia Ventures", industry="FinTech")
    assert validator.validate_input(valid_input) is True

    try:
        invalid_input = CompetitorResearchInput(business_name="", industry="FinTech")
        validator.validate_input(invalid_input)
        assert False, "Should have raised ValidationException"
    except ValidationException:
        pass

async def test_competitor_research_service_execution():
    service = CompetitorResearchService()
    payload = CompetitorResearchInput(
        business_name="Lumen Studios",
        industry="D2C SKINCARE",
        location="North America"
    )
    result = await service.run_research(payload)
    assert isinstance(result, CompetitorResearchResult)
    assert result.business_name == "Lumen Studios"
    assert len(result.direct_competitors) == 2
    assert len(result.indirect_competitors) == 1
    assert len(result.market_gaps) > 0
    assert result.confidence_score >= 95.0

async def test_competitor_ceo_interface_delegation():
    agent = CompetitorResearchAgent()
    task = CEOTaskItem(
        task_id="test-comp-1",
        title="Synthesize Northwind competitive matrix",
        agent_name="Competitor Research Agent",
        priority=PriorityLevel.HIGH,
        status=TaskStatus.WAITING
    )
    context = {"client_name": "Northwind Capital", "industry": "FinTech", "location": "EMEA"}
    response = await agent.execute_task(task, context)
    assert response["agent_name"] == "Competitor Research Agent"
    assert response["status"] == "COMPLETED"
    assert "full_result" in response
    assert len(response["full_result"]["direct_competitors"]) == 2
