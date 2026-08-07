import json
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.agents.ceo.orchestrator import ceo_orchestrator
from app.agents.ceo.graph.state import WorkflowState
from app.core.redis import redis_manager
from app.schemas.all_schemas import SuccessResponse
from pydantic import BaseModel

router = APIRouter(prefix="/ceo", tags=["CEO Agent"])

class DirectiveRequest(BaseModel):
    directive: str
    client_name: str = "Arcadia Ventures"

@router.post("/directive", response_model=SuccessResponse[dict])
async def submit_directive(request: DirectiveRequest):
    """
    Submits a new executive directive to the CEO Agent Orchestrator.
    """
    state = await ceo_orchestrator.execute_directive(request.directive, request.client_name)
    return SuccessResponse(
        data={"workflow_id": state.workflow_id, "status": state.status},
        message="Executive directive accepted and workflow initialized."
    )

@router.get("/workflow/{workflow_id}", response_model=SuccessResponse[dict])
async def get_workflow_status(workflow_id: str):
    """
    Retrieves the current execution status and task queue of a specific workflow.
    """
    state = ceo_orchestrator.active_workflows.get(workflow_id)
    if not state:
        # Return current state as fallback if ID matches default
        state = list(ceo_orchestrator.active_workflows.values())[-1] if ceo_orchestrator.active_workflows else None
    if not state:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return SuccessResponse(data=state.model_dump())

@router.get("/report/{workflow_id}", response_model=SuccessResponse[dict])
async def get_executive_report(workflow_id: str):
    """
    Retrieves the synthesized Executive Report for a completed workflow.
    """
    state = ceo_orchestrator.active_workflows.get(workflow_id)
    if not state and ceo_orchestrator.active_workflows:
        state = list(ceo_orchestrator.active_workflows.values())[-1]
    if not state:
        raise HTTPException(status_code=404, detail="Workflow report not found")
    
    report = state.executive_report
    if not report:
        report = await ceo_orchestrator.reporter.generate_report(state)
    return SuccessResponse(data=report)

@router.get("/stream")
async def stream_events():
    """
    Server-Sent Events (SSE) streaming endpoint for real-time dashboard updates.
    Streams current thoughts, task queue updates, and confidence metrics.
    """
    async def event_generator():
        # Stream active workflow state first if available
        if ceo_orchestrator.active_workflows:
            latest_state = list(ceo_orchestrator.active_workflows.values())[-1]
            yield f"data: {json.dumps({'type': 'STATE_UPDATE', 'data': latest_state.model_dump()})}\n\n"
        
        # Subscribe to Redis channels for real-time events
        async for msg in redis_manager.subscribe_channel("strtos_events"):
            yield f"data: {msg}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
