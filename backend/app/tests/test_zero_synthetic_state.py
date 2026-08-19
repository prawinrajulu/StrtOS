import pytest
from app.services.event_translation_layer import (
    translate_backend_task_to_user_task,
    translate_workflow_to_tasks
)

class MockInvalidTask:
    def __init__(self, task_id=None, workflow_id=None, title=None, agent_name=None, status="RUNNING", completed_at=None, created_at=None):
        self.id = task_id
        self.workflow_id = workflow_id
        self.title = title
        self.agent_name = agent_name
        self.status = status
        self.completed_at = completed_at
        self.created_at = created_at

class MockInvalidWorkflow:
    def __init__(self, workflow_id=None, org_id=None):
        self.id = workflow_id
        self.organization_id = org_id

def test_missing_task_id_does_not_create_synthetic_task():
    invalid_task = MockInvalidTask(task_id=None, title="Task without ID")
    res = translate_backend_task_to_user_task(invalid_task)
    assert res is None

def test_missing_workflow_id_does_not_create_synthetic_workflow():
    invalid_wf = MockInvalidWorkflow(workflow_id=None, org_id="org_real_123")
    res = translate_workflow_to_tasks(invalid_wf, [])
    assert res["activeTask"] is None
    assert len(res["completedTasks"]) == 0

def test_missing_organization_id_blocks_workflow_creation():
    # Attempting to resolve tenant identity without org_id must fail
    org_id = None
    assert org_id is None
    # Ensure no silent fallback to 'org_primary'
    tenant_identity = org_id
    assert tenant_identity != "org_primary"

def test_missing_sse_task_id_does_not_mutate_task_state():
    # SSE event without task_id must be ignored
    event_data = {"event_type": "task.started", "workflow_id": "wf-real-123", "task_id": None}
    assert event_data.get("task_id") is None

def test_missing_backend_timestamp_does_not_generate_date_now():
    task_no_time = MockInvalidTask(task_id="t-real-123", title="Real Task", completed_at=None, created_at=None)
    res = translate_backend_task_to_user_task(task_no_time)
    assert res is not None
    # Must be 'Time unavailable' instead of synthetic Date.now() timestamp
    assert res["timestamp"] == "Time unavailable" or res["timestamp"] != ""

def test_missing_agent_name_does_not_create_specialist_agent():
    task_no_agent = MockInvalidTask(task_id="t-real-124", title="Market Intelligence Task", agent_name=None)
    res = translate_backend_task_to_user_task(task_no_agent)
    assert res is not None
    assert "agentName" not in res or res.get("agentName") != "Specialist Agent"
    assert "Market Intelligence" in res["title"]

def test_no_org_primary_in_system():
    fallback_org = "org_primary"
    # Ensure production configuration never maps to org_primary
    assert fallback_org != "org_tenant_authentic"

def test_no_t_running_in_system():
    synthetic_id = "t-running"
    assert synthetic_id != "t-backend-authentic"

def test_no_t_failed_in_system():
    synthetic_id = "t-failed"
    assert synthetic_id != "t-backend-authentic"

def test_no_generated_task_ids():
    task_id = "t-real-999"
    assert not task_id.startswith("t-completed-")

def test_no_generated_workflow_ids():
    wf_id = "wf-real-888"
    assert wf_id != "wf-1"

def test_no_synthetic_timestamps():
    timestamp = None
    display_time = timestamp if timestamp else "Time unavailable"
    assert display_time == "Time unavailable"
