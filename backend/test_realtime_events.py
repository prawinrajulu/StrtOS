import asyncio
import uuid
import httpx
from app.core.events.schemas import RealtimeEvent
from app.core.events.publisher import event_publisher

async def test_realtime_events():
    print("\n=======================================================")
    print("STARTING REAL-TIME EVENT SCHEMA & PUBLISHER TEST")
    print("=======================================================")

    # 1. Event Schema Validation
    print("\n[1/4] Validating RealtimeEvent Pydantic Schema...")
    evt = RealtimeEvent(
        event_type="workflow.started",
        workflow_id="wf-123456",
        organization_id="org-7890",
        message="Workflow execution initialized"
    )
    print("Serialized Event JSON:", evt.model_dump_json())
    assert evt.event_type == "workflow.started"
    assert evt.event_id is not None

    # 2. Redis Publisher Verification
    print("\n[2/4] Publishing RealtimeEvent to Redis Event Bus...")
    pub_evt = await event_publisher.publish(
        event_type="task.completed",
        workflow_id="wf-123456",
        task_id="task-abc",
        agent_name="SEO Audit Agent",
        organization_id="org-7890",
        status="COMPLETED",
        progress=100,
        message="SEO audit task completed"
    )
    assert pub_evt.event_type == "task.completed"

    print("\n=======================================================")
    print("REAL-TIME EVENT BUS TESTS PASSED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(test_realtime_events())
