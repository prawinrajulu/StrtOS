from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.business_state.schemas import (
    StateSnapshotCreate, StateSnapshotResponse, SignalResponse, ChangeResponse,
    AlertResponse, OpportunityResponse, ThreatResponse, BusinessHealthResponse,
    BusinessExplanationResponse
)
from app.business_state.models import AlertStatus
from app.business_state.service import BusinessStateService

router = APIRouter(prefix="/business-state", tags=["Business State & Early-Warning Intelligence"])

@router.get("/overview")
async def get_business_state_overview(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    snapshot = await service.get_latest_snapshot(org_id)
    alerts = await service.list_alerts(org_id)
    opportunities = await service.list_opportunities(org_id)
    threats = await service.list_threats(org_id)

    return {
        "organization_id": org_id,
        "latest_snapshot": snapshot,
        "active_alerts_count": len([a for a in alerts if a.status != AlertStatus.RESOLVED]),
        "total_opportunities": len(opportunities),
        "total_threats": len(threats),
        "alerts_summary": [
            {"id": a.id, "title": a.title, "severity": a.severity, "status": a.status} for a in alerts[:5]
        ]
    }

@router.post("/snapshots", response_model=StateSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def create_snapshot(
    payload: StateSnapshotCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    return await service.create_snapshot(payload, org_id)

@router.get("/snapshots", response_model=List[StateSnapshotResponse])
async def list_snapshots(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    return await service.list_snapshots(org_id)

@router.get("/signals", response_model=List[SignalResponse])
async def list_signals(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    return await service.list_signals(org_id)

@router.get("/changes", response_model=List[ChangeResponse])
async def list_changes(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    return await service.list_changes(org_id)

@router.get("/opportunities", response_model=List[OpportunityResponse])
async def list_opportunities(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    return await service.list_opportunities(org_id)

@router.get("/threats", response_model=List[ThreatResponse])
async def list_threats(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    return await service.list_threats(org_id)

@router.get("/alerts", response_model=List[AlertResponse])
async def list_alerts(
    status: Optional[AlertStatus] = Query(None),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    return await service.list_alerts(org_id, status=status)

@router.get("/alerts/{id}", response_model=AlertResponse)
async def get_alert(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    try:
        return await service.get_alert(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/alerts/{id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    try:
        return await service.update_alert_status(id, org_id, AlertStatus.ACKNOWLEDGED)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/alerts/{id}/investigate", response_model=AlertResponse)
async def investigate_alert(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    try:
        return await service.update_alert_status(id, org_id, AlertStatus.INVESTIGATING)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/alerts/{id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    try:
        return await service.update_alert_status(id, org_id, AlertStatus.RESOLVED)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/alerts/{id}/dismiss", response_model=AlertResponse)
async def dismiss_alert(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    try:
        return await service.update_alert_status(id, org_id, AlertStatus.DISMISSED)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/alerts/{id}/explanation", response_model=BusinessExplanationResponse)
async def get_alert_explanation(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = BusinessStateService(db)
    try:
        return await service.get_alert_explanation(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
