from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import UserModel
from app.clients.service import ClientService
from app.agents.ceo.orchestrator import ceo_orchestrator
from app.agents.ceo.graph.state import WorkflowState
from app.core.redis import redis_manager
from app.schemas.all_schemas import SuccessResponse
from pydantic import BaseModel

router = APIRouter(prefix="/ceo", tags=["CEO Agent"])

class DirectiveRequest(BaseModel):
    directive: str
    client_id: Optional[str] = None
    client_name: Optional[str] = "Arcadia Ventures"

@router.post("/directive", response_model=SuccessResponse[dict])
async def submit_directive(
    request: DirectiveRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a new executive directive to the CEO Agent Orchestrator.
    If client_id is provided, loads full Client context from the authenticated user's organization.
    """
    client_name = request.client_name or "Arcadia Ventures"
    client_context = None

    if request.client_id:
        client_service = ClientService(db)
        client_dto = await client_service.get_client(request.client_id, org_id=current_user.organization_id)
        client_name = client_dto.name
        client_context = {
            "client_id": client_dto.id,
            "organization_id": client_dto.organization_id,
            "client_name": client_dto.name,
            "industry": client_dto.industry,
            "website_url": client_dto.website_url,
            "business_goal": client_dto.business_goal,
            "monthly_budget": client_dto.monthly_budget,
            "currency": client_dto.currency
        }

    state = await ceo_orchestrator.execute_directive(request.directive, client_name=client_name, client_context=client_context)
    return SuccessResponse(
        data={"workflow_id": state.workflow_id, "status": state.status, "client_name": client_name},
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
