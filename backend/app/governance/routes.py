from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user, get_current_organization_id
from app.auth.models import UserModel
from app.governance.schemas import (
    ApprovalRequestCreate, ApprovalActionRequest, ApprovalResponse, ApprovalListResponse
)
from app.governance.service import GovernanceService

router = APIRouter(prefix="/api/v1/governance/approvals", tags=["Governance Approvals"])

@router.post("", response_model=ApprovalResponse, status_code=status.HTTP_201_CREATED)
async def create_approval_request(
    payload: ApprovalRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = GovernanceService(db)
    return await service.create_approval_request(payload, org_id=org_id, creator_id=current_user.id)

@router.get("", response_model=ApprovalListResponse)
async def list_approval_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    risk_level: Optional[str] = Query(None),
    workflow_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = GovernanceService(db)
    return await service.list_approval_requests(
        org_id=org_id,
        page=page,
        page_size=page_size,
        status_filter=status_filter,
        risk_level=risk_level,
        workflow_id=workflow_id,
        client_id=client_id,
        search=search
    )

@router.get("/{id}", response_model=ApprovalResponse)
async def get_approval_request(
    id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = GovernanceService(db)
    return await service.get_approval_request(id, org_id=org_id)

@router.post("/{id}/approve", response_model=ApprovalResponse)
async def approve_request(
    id: str,
    payload: ApprovalActionRequest = ApprovalActionRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = GovernanceService(db)
    return await service.approve_request(id, payload=payload, org_id=org_id, reviewer_user=current_user)

@router.post("/{id}/reject", response_model=ApprovalResponse)
async def reject_request(
    id: str,
    payload: ApprovalActionRequest = ApprovalActionRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = GovernanceService(db)
    return await service.reject_request(id, payload=payload, org_id=org_id, reviewer_user=current_user)

@router.post("/{id}/request-changes", response_model=ApprovalResponse)
async def request_changes(
    id: str,
    payload: ApprovalActionRequest = ApprovalActionRequest(),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = GovernanceService(db)
    return await service.request_changes(id, payload=payload, org_id=org_id, reviewer_user=current_user)

@router.post("/{id}/cancel", response_model=ApprovalResponse)
async def cancel_request(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = GovernanceService(db)
    return await service.cancel_request(id, org_id=org_id, user_id=current_user.id)
