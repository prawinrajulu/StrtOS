from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user, get_current_organization_id
from app.auth.models import UserModel
from app.swarm.models import SwarmStatus
from app.swarm.schemas import (
    SwarmSessionCreate, SwarmSessionResponse, SwarmSessionListResponse,
    SwarmMessageResponse, SwarmConflictResponse, SwarmDebateResponse
)
from app.swarm.service import SwarmService

router = APIRouter(prefix="/api/v1/swarm", tags=["Multi-Agent Swarm Orchestration"])

@router.post("/sessions", response_model=SwarmSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_swarm_session(
    payload: SwarmSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = SwarmService(db)
    return await service.create_swarm_session(payload, org_id=org_id, creator_id=current_user.id)

@router.get("/sessions", response_model=SwarmSessionListResponse)
async def list_swarm_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    client_id: Optional[str] = Query(None),
    workflow_id: Optional[str] = Query(None),
    status_filter: Optional[SwarmStatus] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = SwarmService(db)
    return await service.list_swarm_sessions(
        org_id=org_id,
        page=page,
        page_size=page_size,
        client_id=client_id,
        workflow_id=workflow_id,
        status_filter=status_filter,
        search=search
    )

@router.get("/sessions/{id}", response_model=SwarmSessionResponse)
async def get_swarm_session(
    id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = SwarmService(db)
    return await service.get_swarm_session(id, org_id=org_id)

@router.post("/sessions/{id}/start", response_model=SwarmSessionResponse)
async def start_swarm_session(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = SwarmService(db)
    return await service.start_swarm_session(id, org_id=org_id, creator_user=current_user)

@router.get("/sessions/{id}/messages", response_model=List[SwarmMessageResponse])
async def list_swarm_messages(
    id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = SwarmService(db)
    return await service.list_messages(id, org_id=org_id)

@router.get("/sessions/{id}/conflicts", response_model=List[SwarmConflictResponse])
async def list_swarm_conflicts(
    id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = SwarmService(db)
    return await service.list_conflicts(id, org_id=org_id)

@router.get("/sessions/{id}/debates", response_model=List[SwarmDebateResponse])
async def list_swarm_debates(
    id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = SwarmService(db)
    return await service.list_debates(id, org_id=org_id)
