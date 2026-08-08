import asyncio
from app.agents.ceo.orchestrator import ceo_orchestrator
from app.agents.ceo.graph.state import WorkflowStatus, TaskStatus

async def test_end_to_end_integration_pipeline():
    directive = "I own a fine-dining Italian restaurant and need to double our online dinner reservations and customer acquisition."
    client_name = "Bella Italia Restaurant"

    state = await ceo_orchestrator.execute_directive(directive, client_name)
    assert state.workflow_id is not None
    assert state.client_name == client_name
    assert state.intent.business_type == "Restaurant & Hospitality"
    assert state.intent.industry == "Food & Beverage"

    # Allow async execution background task to run to completion
    await asyncio.sleep(12.0)

    active_state = ceo_orchestrator.active_workflows[state.workflow_id]
    assert active_state.status == WorkflowStatus.COMPLETED
    assert active_state.is_completed is True

    # Verify all 5 tasks executed and completed sequentially
    assert len(active_state.tasks) == 5
    for task in active_state.tasks:
        assert task.status == TaskStatus.COMPLETED
        assert task.result is not None

    # Verify Shared Context Data Propagation across all 5 Agent Outputs
    outputs = active_state.agent_outputs
    assert "Business Analysis Agent" in outputs
    assert "SEO Audit Agent" in outputs
    assert "Competitor Research Agent" in outputs
    assert "Marketing Strategy Agent" in outputs
    assert "Campaign Planner Agent" in outputs

    # Verify Executive Summary Report Aggregation
    report = active_state.executive_report
    assert report is not None
    assert report["client_name"] == client_name
    assert "business_summary" in report
    assert "seo_summary" in report
    assert "competitor_summary" in report
    assert "marketing_summary" in report
    assert "campaign_summary" in report
    assert len(report["ceo_final_recommendations"]) == 3
