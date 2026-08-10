from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user, get_current_organization_id
from app.auth.models import UserModel
from app.execution.models import ActionStatus
from app.execution.schemas import (
    ActionCreate, ActionResponse, ActionListResponse, ActionEvaluateResponse,
    OutcomeMeasurementRequest, ClosedLoopOptimizationResponse
)
from app.execution.service import ExecutionService

router = APIRouter(prefix="/api/v1/execution", tags=["Autonomous Execution & Closed-Loop Optimization"])

@router.post("/actions", response_model=ActionResponse, status_code=status.HTTP_201_CREATED)
async def create_action(
    payload: ActionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = ExecutionService(db)
    return await service.create_action(payload, org_id=org_id, current_user=current_user)

@router.get("/actions", response_model=ActionListResponse)
async def list_actions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    client_id: Optional[str] = Query(None),
    workflow_id: Optional[str] = Query(None),
    prediction_id: Optional[str] = Query(None),
    status_filter: Optional[ActionStatus] = Query(None, alias="status"),
    action_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = ExecutionService(db)
    return await service.list_actions(
        org_id=org_id,
        page=page,
        page_size=page_size,
        client_id=client_id,
        workflow_id=workflow_id,
        prediction_id=prediction_id,
        status_filter=status_filter,
        action_type=action_type,
        search=search
    )

@router.get("/actions/{id}", response_model=ActionResponse)
async def get_action(
    id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = ExecutionService(db)
    return await service.get_action(id, org_id=org_id)

@router.post("/actions/{id}/evaluate", response_model=ActionEvaluateResponse)
async def evaluate_action_policy(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = ExecutionService(db)
    return await service.evaluate_action_policy(id, org_id=org_id, current_user=current_user)

@router.post("/actions/{id}/approve", response_model=ActionResponse)
async def submit_action_for_approval(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = ExecutionService(db)
    return await service.submit_action_for_approval(id, org_id=org_id, current_user=current_user)

@router.post("/actions/{id}/execute", response_model=ActionResponse)
async def execute_action(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = ExecutionService(db)
    return await service.execute_action(id, org_id=org_id, current_user=current_user)

@router.post("/actions/{id}/cancel", response_model=ActionResponse)
async def cancel_action(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = ExecutionService(db)
    return await service.cancel_action(id, org_id=org_id, current_user=current_user)

@router.post("/actions/{id}/retry", response_model=ActionResponse)
async def retry_action(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = ExecutionService(db)
    return await service.retry_action(id, org_id=org_id, current_user=current_user)

@router.post("/actions/{id}/measure", response_model=ClosedLoopOptimizationResponse)
async def measure_action_outcome(
    id: str,
    payload: OutcomeMeasurementRequest,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = ExecutionService(db)
    return await service.measure_action_outcome(id, payload=payload, org_id=org_id)
