import asyncio
from app.agents.business_analysis.schemas import BusinessAnalysisInput, BusinessAnalysisResult
from app.agents.business_analysis.validator import BusinessAnalysisValidator
from app.agents.business_analysis.service import BusinessAnalysisService
from app.agents.business_analysis.interfaces import BusinessAnalysisAgent
from app.agents.ceo.graph.state import CEOTaskItem, PriorityLevel, TaskStatus
from app.core.exceptions import ValidationException

async def test_validator_input():
    validator = BusinessAnalysisValidator()
    valid_input = BusinessAnalysisInput(business_name="Northwind Capital", industry="FinTech")
    assert validator.validate_input(valid_input) is True

    try:
        invalid_input = BusinessAnalysisInput(business_name="", industry="FinTech")
        validator.validate_input(invalid_input)
        assert False, "Should have raised ValidationException"
    except ValidationException:
        pass

async def test_business_analysis_service_execution():
    service = BusinessAnalysisService()
    payload = BusinessAnalysisInput(
        business_name="Lumen Studios",
        industry="D2C SKINCARE",
        target_audience="Beauty Consumers",
        business_goal="Acquire 10k online customers"
    )
    result = await service.run_analysis(payload)
    assert isinstance(result, BusinessAnalysisResult)
    assert result.business_name == "Lumen Studios"
    assert result.digital_maturity_score == 78
    assert len(result.swot.strengths) > 0
    assert len(result.customer_personas) == 2
    assert result.confidence_score > 90.0

async def test_ceo_interface_delegation():
    agent = BusinessAnalysisAgent()
    task = CEOTaskItem(
        task_id="test-1",
        title="Analyze D2C Skincare TAM",
        agent_name="Business Analysis Agent",
        priority=PriorityLevel.HIGH,
        status=TaskStatus.WAITING
    )
    context = {"client_name": "Lumen Studios", "industry": "D2C SKINCARE", "directive": "Growth"}
    response = await agent.execute_task(task, context)
    assert response["agent_name"] == "Business Analysis Agent"
    assert response["status"] == "COMPLETED"
    assert "full_result" in response
    assert response["full_result"]["digital_maturity_score"] == 78
