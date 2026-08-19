import pytest
from app.services.event_translation_layer import (
    translate_backend_task_to_user_task,
    translate_workflow_to_tasks
)

class MockTask:
    def __init__(self, task_id="t-real-001", workflow_id="wf-real-001", title="Business Performance Analysis", agent_name="BusinessAnalysisAgent", status="RUNNING"):
        self.id = task_id
        self.workflow_id = workflow_id
        self.title = title
        self.agent_name = agent_name
        self.status = status
        self.completed_at = "2026-08-19T20:00:00Z"
        self.started_at = "2026-08-19T19:55:00Z"
        self.created_at = "2026-08-19T19:50:00Z"
        self.output = {"summary": "Revenue increased by 14%"}

class MockWorkflow:
    def __init__(self, workflow_id="wf-real-001"):
        self.id = workflow_id
        self.organization_id = "org_real_tenant"
        self.client_id = "client_real_tenant"
        self.title = "Performance Directive"
        self.status = "RUNNING"

def test_agent_name_not_required_in_user_facing_model():
    task = MockTask()
    user_task = translate_backend_task_to_user_task(task)
    assert user_task is not None
    # User facing model contains business title and no required agentName attribute
    assert user_task["title"] == "Business Performance Analysis"
    assert "agentName" not in user_task or user_task.get("agentName") == "BusinessAnalysisAgent"

def test_internal_agent_events_translated_to_business_language():
    task_seo = MockTask(title="SEO Audit Agent", agent_name="SEOAuditAgent")
    user_task = translate_backend_task_to_user_task(task_seo)
    assert user_task["title"] == "Website Performance Analysis"

def test_missing_task_id_ignored():
    task = MockTask(task_id=None)
    user_task = translate_backend_task_to_user_task(task)
    assert user_task is None

def test_missing_workflow_id_ignored():
    wf = MockWorkflow(workflow_id=None)
    res = translate_workflow_to_tasks(wf, [MockTask()])
    assert res["activeTask"] is None

def test_single_active_task_enforced():
    wf = MockWorkflow()
    tasks = [
        MockTask(task_id="t-1", status="RUNNING"),
        MockTask(task_id="t-2", status="QUEUED"),
        MockTask(task_id="t-3", status="QUEUED")
    ]
    res = translate_workflow_to_tasks(wf, tasks)
    assert res["activeTask"] is not None
    assert res["activeTask"]["id"] == "t-1"
    assert len(res["upcomingTasks"]) == 2

def test_completed_tasks_from_backend_state_only():
    wf = MockWorkflow()
    tasks = [
        MockTask(task_id="t-1", status="COMPLETED"),
        MockTask(task_id="t-2", status="RUNNING")
    ]
    res = translate_workflow_to_tasks(wf, tasks)
    assert len(res["completedTasks"]) == 1
    assert res["completedTasks"][0]["id"] == "t-1"
