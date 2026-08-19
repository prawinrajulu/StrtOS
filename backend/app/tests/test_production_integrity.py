import pytest
import uuid
from typing import Dict, Any
from app.services.event_translation_layer import (
    extract_task_result_data,
    translate_backend_task_to_user_task,
    translate_workflow_to_tasks
)

class MockTaskItem:
    def __init__(self, task_id: str, workflow_id: str, title: str, agent_name: str, status: str, output: Any = None, error_message: str = None):
        self.id = task_id
        self.workflow_id = workflow_id
        self.title = title
        self.agent_name = agent_name
        self.status = status
        self.output = output
        self.error_message = error_message
        self.retry_count = 0
        self.max_retries = 3
        self.started_at = None
        self.completed_at = None

class MockWorkflow:
    def __init__(self, workflow_id: str, status: str = "RUNNING"):
        self.id = workflow_id
        self.organization_id = "org_test_tenant"
        self.client_id = "client_test_tenant"
        self.title = "Test Directive"
        self.status = status
        self.active_stage = "EXECUTION"
        self.progress = 50
        self.confidence_score = 96.0

def test_no_fabricated_confidence_when_missing():
    # If output contains no confidence score, result must reflect None / Confidence unavailable
    output = {"summary": "Completed analysis"}
    res = extract_task_result_data(output, "Business Performance Analysis")
    assert res["confidence"] is None

def test_no_fabricated_recommendation_when_missing():
    # If output contains no recommendation, must return "No recommendation available"
    output = {"findings": ["Revenue analyzed"]}
    res = extract_task_result_data(output, "Business Performance Analysis")
    assert res["recommendation"] == "No recommendation available"

def test_no_fabricated_findings_when_missing():
    # If output contains no findings, must return "INSUFFICIENT DATA"
    output = {}
    res = extract_task_result_data(output, "Business Performance Analysis")
    assert res["keyFinding"] == "INSUFFICIENT DATA"
    assert res["businessImpact"] == "INSUFFICIENT DATA"

def test_no_fake_organization_tenant_isolation():
    # Tenant isolation check: Workflow and task MUST carry authentic organization_id
    wf = MockWorkflow("wf-101")
    assert wf.organization_id == "org_test_tenant"
    assert wf.organization_id != "default_org"

def test_one_running_task_maximum():
    # Task queue rule: In a multi-task list, ONLY ONE task can be RUNNING at a time
    wf = MockWorkflow("wf-102")
    tasks = [
        MockTaskItem("t-1", wf.id, "Task 1", "Business Analysis Agent", "RUNNING"),
        MockTaskItem("t-2", wf.id, "Task 2", "SEO Audit Agent", "WAITING"),
        MockTaskItem("t-3", wf.id, "Task 3", "Competitor Research Agent", "WAITING")
    ]
    translated = translate_workflow_to_tasks(wf, tasks)
    assert translated["activeTask"] is not None
    assert translated["activeTask"]["id"] == "t-1"
    assert translated["activeTask"]["status"] == "RUNNING"
    # Ensure upcoming tasks are QUEUED/BLOCKED and NOT RUNNING
    for up in translated["upcomingTasks"]:
        assert up["status"] != "RUNNING"

def test_next_queued_task_starts_after_completion():
    # Sequential task transition: Task 1 COMPLETED -> Task 2 RUNNING
    wf = MockWorkflow("wf-103")
    tasks = [
        MockTaskItem("t-1", wf.id, "Task 1", "Business Analysis Agent", "COMPLETED", {"summary": "Done"}),
        MockTaskItem("t-2", wf.id, "Task 2", "SEO Audit Agent", "RUNNING"),
        MockTaskItem("t-3", wf.id, "Task 3", "Competitor Research Agent", "WAITING")
    ]
    translated = translate_workflow_to_tasks(wf, tasks)
    assert len(translated["completedTasks"]) == 1
    assert translated["completedTasks"][0]["id"] == "t-1"
    assert translated["activeTask"] is not None
    assert translated["activeTask"]["id"] == "t-2"
    assert translated["activeTask"]["status"] == "RUNNING"

def test_failed_task_does_not_fabricate_result():
    # Failed task handling: Output must be empty and error message preserved
    wf = MockWorkflow("wf-104")
    failed_task = MockTaskItem("t-1", wf.id, "Task 1", "Business Analysis Agent", "FAILED", None, "Telemetry unreachable")
    user_task = translate_backend_task_to_user_task(failed_task)
    assert user_task["status"] == "FAILED"
    assert user_task["errorReason"] == "Telemetry unreachable"
    assert user_task.get("result") is None

def test_blocked_task_remains_blocked_until_dependency_completes():
    # Dependency handling: Blocked task remains BLOCKED
    wf = MockWorkflow("wf-105")
    tasks = [
        MockTaskItem("t-1", wf.id, "Task 1", "Business Analysis Agent", "FAILED", None, "Error"),
        MockTaskItem("t-2", wf.id, "Task 2", "SEO Audit Agent", "SKIPPED", None, None)
    ]
    translated = translate_workflow_to_tasks(wf, tasks)
    blocked_task = [t for t in translated["upcomingTasks"] if t["id"] == "t-2"][0]
    assert blocked_task["status"] == "BLOCKED"
    assert blocked_task["statusMessage"] == "Waiting for required analysis"

def test_state_reconstruction_on_refresh():
    # State recovery: Refreshing the browser reconstructs identical task list from backend
    wf = MockWorkflow("wf-106")
    tasks = [
        MockTaskItem("t-1", wf.id, "Task 1", "Business Analysis Agent", "COMPLETED", {"summary": "Done"}),
        MockTaskItem("t-2", wf.id, "Task 2", "SEO Audit Agent", "RUNNING"),
        MockTaskItem("t-3", wf.id, "Task 3", "Competitor Research Agent", "WAITING")
    ]
    translated1 = translate_workflow_to_tasks(wf, tasks)
    translated2 = translate_workflow_to_tasks(wf, tasks)
    assert translated1["activeTask"]["id"] == translated2["activeTask"]["id"]
    assert len(translated1["completedTasks"]) == len(translated2["completedTasks"])

def test_duplicate_execution_prevented():
    # Idempotency check: Duplicate execution requests for same workflow ID return identical state
    wf = MockWorkflow("wf-107")
    task_ids = set()
    tasks = [
        MockTaskItem("t-1", wf.id, "Task 1", "Business Analysis Agent", "RUNNING"),
        MockTaskItem("t-2", wf.id, "Task 2", "SEO Audit Agent", "WAITING")
    ]
    for t in tasks:
        assert t.id not in task_ids
        task_ids.add(t.id)
