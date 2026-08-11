from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.missions.schemas import (
    MissionCreate, MissionResponse, MissionEvaluationResponse, MissionReplanRequest
)
from app.missions.models import MissionStatus
from app.missions.service import MissionService

router = APIRouter(prefix="/missions", tags=["Autonomous Strategic Mission Execution"])

@router.get("/overview")
async def get_missions_overview(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = MissionService(db)
    missions = await service.list_missions(org_id)
    return {
        "organization_id": org_id,
        "total_missions": len(missions),
        "missions": missions
    }

@router.post("", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
async def create_mission(
    payload: MissionCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = MissionService(db)
    return await service.create_mission(payload, org_id)

@router.get("", response_model=List[MissionResponse])
async def list_missions(
    status: Optional[MissionStatus] = Query(None),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = MissionService(db)
    return await service.list_missions(org_id, status=status)

@router.get("/{id}", response_model=MissionResponse)
async def get_mission(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = MissionService(db)
    try:
        return await service.get_mission(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{id}/start", response_model=MissionResponse)
async def start_mission(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = MissionService(db)
    try:
        return await service.start_mission(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{id}/replan", response_model=MissionResponse)
async def replan_mission(
    id: str,
    payload: MissionReplanRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = MissionService(db)
    try:
        return await service.replan_mission(id, payload, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{id}/evaluation", response_model=MissionEvaluationResponse)
async def evaluate_mission(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = MissionService(db)
    try:
        return await service.evaluate_mission(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
