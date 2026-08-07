import asyncio
from app.agents.seo_audit.schemas import SEOAuditInput, SEOAuditResult
from app.agents.seo_audit.validator import SEOAuditValidator
from app.agents.seo_audit.service import SEOAuditService
from app.agents.seo_audit.interfaces import SEOAuditAgent
from app.agents.ceo.graph.state import CEOTaskItem, PriorityLevel, TaskStatus
from app.core.exceptions import ValidationException

async def test_validator_input():
    validator = SEOAuditValidator()
    valid_input = SEOAuditInput(website_url="https://orbitalabs.io")
    assert validator.validate_input(valid_input) is True

    try:
        invalid_input = SEOAuditInput(website_url="invalid-url-without-protocol")
        validator.validate_input(invalid_input)
        assert False, "Should have raised ValidationException for invalid URL"
    except ValidationException:
        pass

async def test_seo_audit_service_execution():
    service = SEOAuditService()
    payload = SEOAuditInput(
        website_url="https://orbitalabs.io",
        business_context="Orbitalabs FinTech",
        industry="FinTech"
    )
    result = await service.run_audit(payload)
    assert isinstance(result, SEOAuditResult)
    assert result.website_url == "https://orbitalabs.io"
    assert result.overall_seo_score == 88
    assert result.technical_seo_score == 90
    assert result.core_web_vitals.lcp == "1.1s"
    assert len(result.critical_issues) > 0
    assert len(result.recommendations) > 0

async def test_seo_ceo_interface_delegation():
    agent = SEOAuditAgent()
    task = CEOTaskItem(
        task_id="test-seo-1",
        title="SEO Technical Audit - orbitalabs.io",
        agent_name="SEO Audit Agent",
        priority=PriorityLevel.HIGH,
        status=TaskStatus.WAITING
    )
    context = {"client_name": "Orbitalabs", "website_url": "https://orbitalabs.io", "industry": "FinTech"}
    response = await agent.execute_task(task, context)
    assert response["agent_name"] == "SEO Audit Agent"
    assert response["status"] == "COMPLETED"
    assert "full_result" in response
    assert response["full_result"]["overall_seo_score"] == 88
