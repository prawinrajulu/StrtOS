from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.dependencies import get_current_user, RoleChecker
from app.auth.models import UserModel, UserRole
from app.schemas.all_schemas import SuccessResponse
from app.workflows.schemas import (
    WorkflowCreateRequest, WorkflowUpdateRequest, WorkflowDTO, WorkflowListResponse, TaskDTO, WorkflowEventDTO
)
from app.workflows.service import WorkflowService

router = APIRouter(prefix="/workflows", tags=["Workflow Management"])

@router.post("", response_model=SuccessResponse[WorkflowDTO], status_code=status.HTTP_201_CREATED)
async def create_workflow(
    payload: WorkflowCreateRequest,
    current_user: UserModel = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new Workflow securely scoped to the user's organization and client."""
    service = WorkflowService(db)
    dto = await service.create_workflow(payload, org_id=current_user.organization_id, creator_id=current_user.id)
    return SuccessResponse(data=dto, message="Workflow created successfully.")

@router.get("", response_model=SuccessResponse[WorkflowListResponse])
async def list_workflows(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    client_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists Workflows for the authenticated user's organization."""
    service = WorkflowService(db)
    result = await service.list_workflows(
        org_id=current_user.organization_id,
        page=page,
        page_size=page_size,
        client_id=client_id,
        status_filter=status_filter,
        search=search
    )
    return SuccessResponse(data=result, message="Workflows retrieved successfully.")

@router.get("/{workflow_id}", response_model=SuccessResponse[WorkflowDTO])
async def get_workflow(
    workflow_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets details for a specific Workflow with organization ownership check."""
    service = WorkflowService(db)
    dto = await service.get_workflow(workflow_id, org_id=current_user.organization_id)
    return SuccessResponse(data=dto, message="Workflow details retrieved.")

@router.post("/{workflow_id}/start", response_model=SuccessResponse[WorkflowDTO])
async def start_workflow(
    workflow_id: str,
    current_user: UserModel = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """Starts Workflow execution via CEO Orchestrator Engine."""
    service = WorkflowService(db)
    dto = await service.start_workflow(workflow_id, org_id=current_user.organization_id)
    return SuccessResponse(data=dto, message="Workflow started successfully.")

@router.post("/{workflow_id}/pause", response_model=SuccessResponse[WorkflowDTO])
async def pause_workflow(
    workflow_id: str,
    current_user: UserModel = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """Pauses a running Workflow."""
    service = WorkflowService(db)
    dto = await service.pause_workflow(workflow_id, org_id=current_user.organization_id)
    return SuccessResponse(data=dto, message="Workflow paused successfully.")

@router.post("/{workflow_id}/resume", response_model=SuccessResponse[WorkflowDTO])
async def resume_workflow(
    workflow_id: str,
    current_user: UserModel = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """Resumes a paused Workflow."""
    service = WorkflowService(db)
    dto = await service.resume_workflow(workflow_id, org_id=current_user.organization_id)
    return SuccessResponse(data=dto, message="Workflow resumed successfully.")

@router.post("/{workflow_id}/cancel", response_model=SuccessResponse[WorkflowDTO])
async def cancel_workflow(
    workflow_id: str,
    current_user: UserModel = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Cancels a Workflow."""
    service = WorkflowService(db)
    dto = await service.cancel_workflow(workflow_id, org_id=current_user.organization_id)
    return SuccessResponse(data=dto, message="Workflow cancelled successfully.")

@router.get("/{workflow_id}/tasks", response_model=SuccessResponse[List[TaskDTO]])
async def get_workflow_tasks(
    workflow_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves tasks generated for a specific Workflow."""
    service = WorkflowService(db)
    tasks = await service.get_tasks(workflow_id, org_id=current_user.organization_id)
    return SuccessResponse(data=tasks, message="Workflow tasks retrieved.")

@router.get("/{workflow_id}/events", response_model=SuccessResponse[List[WorkflowEventDTO]])
async def get_workflow_events(
    workflow_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves audit events for a specific Workflow."""
    service = WorkflowService(db)
    events = await service.get_events(workflow_id, org_id=current_user.organization_id)
    return SuccessResponse(data=events, message="Workflow events retrieved.")
