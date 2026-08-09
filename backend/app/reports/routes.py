from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.dependencies import get_current_user, RoleChecker
from app.auth.models import UserModel, UserRole
from app.schemas.all_schemas import SuccessResponse
from app.reports.schemas import (
    ReportCreateRequest, ReportUpdateRequest, ReportResponse, ReportListResponse, ReportMetricsResponse
)
from app.reports.service import ReportService

router = APIRouter(prefix="/reports", tags=["Executive Reports"])

@router.post("", response_model=SuccessResponse[ReportResponse], status_code=status.HTTP_201_CREATED)
async def create_report(
    payload: ReportCreateRequest,
    current_user: UserModel = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new Executive Report linked to workflow & client."""
    service = ReportService(db)
    dto = await service.create_report(payload, org_id=current_user.organization_id, creator_id=current_user.id)
    return SuccessResponse(data=dto, message="Executive report created successfully.")

@router.get("", response_model=SuccessResponse[ReportListResponse])
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    client_id: Optional[str] = Query(None),
    workflow_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists Executive Reports for the authenticated user's organization."""
    service = ReportService(db)
    result = await service.list_reports(
        org_id=current_user.organization_id,
        page=page,
        page_size=page_size,
        client_id=client_id,
        workflow_id=workflow_id,
        status_filter=status_filter,
        search=search
    )
    return SuccessResponse(data=result, message="Executive reports retrieved successfully.")

@router.get("/metrics", response_model=SuccessResponse[ReportMetricsResponse])
async def get_report_metrics(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets aggregate report metrics for the organization."""
    service = ReportService(db)
    metrics = await service.get_metrics(org_id=current_user.organization_id)
    return SuccessResponse(data=metrics, message="Report metrics calculated.")

@router.get("/{report_id}", response_model=SuccessResponse[ReportResponse])
async def get_report(
    report_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets single Executive Report with organization ownership check."""
    service = ReportService(db)
    dto = await service.get_report(report_id, org_id=current_user.organization_id)
    return SuccessResponse(data=dto, message="Executive report retrieved.")

@router.get("/workflow/{workflow_id}", response_model=SuccessResponse[ReportResponse])
async def get_workflow_report(
    workflow_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets Executive Report for a specific workflow."""
    service = ReportService(db)
    dto = await service.get_by_workflow(workflow_id, org_id=current_user.organization_id)
    return SuccessResponse(data=dto, message="Workflow report retrieved.")

@router.get("/client/{client_id}", response_model=SuccessResponse[ReportListResponse])
async def get_client_reports(
    client_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets Executive Reports for a specific client."""
    service = ReportService(db)
    result = await service.list_reports(org_id=current_user.organization_id, page=page, page_size=page_size, client_id=client_id)
    return SuccessResponse(data=result, message="Client reports retrieved.")

@router.patch("/{report_id}", response_model=SuccessResponse[ReportResponse])
async def update_report(
    report_id: str,
    payload: ReportUpdateRequest,
    current_user: UserModel = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """Updates an Executive Report."""
    service = ReportService(db)
    dto = await service.update_report(report_id, payload, org_id=current_user.organization_id)
    return SuccessResponse(data=dto, message="Executive report updated successfully.")

@router.delete("/{report_id}", response_model=SuccessResponse[ReportResponse])
async def archive_report(
    report_id: str,
    current_user: UserModel = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Archives an Executive Report."""
    service = ReportService(db)
    dto = await service.archive_report(report_id, org_id=current_user.organization_id)
    return SuccessResponse(data=dto, message="Executive report archived successfully.")

@router.get("/{report_id}/export")
async def export_report(
    report_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Exports structured report payload for download."""
    service = ReportService(db)
    export_payload = await service.export_report(report_id, org_id=current_user.organization_id)
    return SuccessResponse(data=export_payload, message="Report export payload generated.")
