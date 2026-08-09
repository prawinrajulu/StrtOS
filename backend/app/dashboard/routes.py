from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import UserModel
from app.schemas.all_schemas import SuccessResponse
from app.dashboard.schemas import (
    DashboardOverviewResponse, ClientKPIs, WorkflowKPIs, TaskKPIs, ReportKPIs,
    AgentPerformanceItem, IndustryAnalyticsItem, TrendPoint, RecentActivityItem
)
from app.dashboard.service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Executive Dashboard"])

@router.get("/overview", response_model=SuccessResponse[DashboardOverviewResponse])
async def get_dashboard_overview(
    days: int = Query(30, ge=7, le=90),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets complete Executive Analytics Dashboard Overview."""
    service = DashboardService(db)
    data = await service.get_overview(org_id=current_user.organization_id, days=days)
    return SuccessResponse(data=data, message="Dashboard overview retrieved successfully.")

@router.get("/kpis", response_model=SuccessResponse[Dict[str, Any]])
async def get_dashboard_kpis(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets top-level KPI metrics."""
    service = DashboardService(db)
    overview = await service.get_overview(org_id=current_user.organization_id)
    return SuccessResponse(data={
        "clients": overview.clients,
        "workflows": overview.workflows,
        "tasks": overview.tasks,
        "reports": overview.reports
    }, message="Dashboard KPIs retrieved.")

@router.get("/workflows", response_model=SuccessResponse[WorkflowKPIs])
async def get_workflow_metrics(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets workflow metrics."""
    service = DashboardService(db)
    overview = await service.get_overview(org_id=current_user.organization_id)
    return SuccessResponse(data=overview.workflows, message="Workflow KPIs retrieved.")

@router.get("/tasks", response_model=SuccessResponse[TaskKPIs])
async def get_task_metrics(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets task metrics."""
    service = DashboardService(db)
    overview = await service.get_overview(org_id=current_user.organization_id)
    return SuccessResponse(data=overview.tasks, message="Task KPIs retrieved.")

@router.get("/agents", response_model=SuccessResponse[List[AgentPerformanceItem]])
async def get_agent_metrics(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets agent performance metrics."""
    service = DashboardService(db)
    overview = await service.get_overview(org_id=current_user.organization_id)
    return SuccessResponse(data=overview.agent_performance, message="Agent metrics retrieved.")

@router.get("/clients", response_model=SuccessResponse[ClientKPIs])
async def get_client_metrics(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets client metrics."""
    service = DashboardService(db)
    overview = await service.get_overview(org_id=current_user.organization_id)
    return SuccessResponse(data=overview.clients, message="Client KPIs retrieved.")

@router.get("/reports", response_model=SuccessResponse[ReportKPIs])
async def get_report_metrics(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets report metrics."""
    service = DashboardService(db)
    overview = await service.get_overview(org_id=current_user.organization_id)
    return SuccessResponse(data=overview.reports, message="Report KPIs retrieved.")

@router.get("/trends", response_model=SuccessResponse[List[TrendPoint]])
async def get_trend_metrics(
    days: int = Query(30, ge=7, le=90),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets analytics time trends."""
    service = DashboardService(db)
    overview = await service.get_overview(org_id=current_user.organization_id, days=days)
    return SuccessResponse(data=overview.trends, message="Trends retrieved.")

@router.get("/insights", response_model=SuccessResponse[List[str]])
async def get_dashboard_insights(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets automated backend executive insights."""
    service = DashboardService(db)
    overview = await service.get_overview(org_id=current_user.organization_id)
    return SuccessResponse(data=overview.insights, message="Insights retrieved.")
