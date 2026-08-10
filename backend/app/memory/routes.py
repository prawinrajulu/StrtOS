from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user, get_current_organization_id
from app.auth.models import UserModel
from app.memory.models import MemoryType, OutcomeStatus
from app.memory.schemas import (
    MemoryRecordCreate, MemoryRecordResponse, MemoryListResponse,
    OutcomeSubmissionRequest, OutcomeResponse
)
from app.memory.service import MemoryService

router = APIRouter(prefix="/api/v1/memory", tags=["Adaptive Memory Layer"])

@router.post("", response_model=MemoryRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_memory_record(
    payload: MemoryRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = MemoryService(db)
    return await service.create_memory(payload, org_id=org_id, creator_id=current_user.id)

@router.get("", response_model=MemoryListResponse)
async def list_memory_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    client_id: Optional[str] = Query(None),
    workflow_id: Optional[str] = Query(None),
    memory_type: Optional[MemoryType] = Query(None),
    outcome_status: Optional[OutcomeStatus] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = MemoryService(db)
    return await service.list_memories(
        org_id=org_id,
        page=page,
        page_size=page_size,
        client_id=client_id,
        workflow_id=workflow_id,
        memory_type=memory_type,
        outcome_status=outcome_status,
        search=search
    )

@router.get("/retrieve", response_model=List[MemoryRecordResponse])
async def retrieve_memories(
    client_id: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = MemoryService(db)
    return await service.retrieve_memories_for_context(
        org_id=org_id,
        client_id=client_id,
        query=query,
        limit=limit
    )

@router.get("/{id}", response_model=MemoryRecordResponse)
async def get_memory_record(
    id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = MemoryService(db)
    return await service.get_memory(id, org_id=org_id)

@router.post("/outcomes", response_model=OutcomeResponse, status_code=status.HTTP_201_CREATED)
async def submit_actual_outcome(
    payload: OutcomeSubmissionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = MemoryService(db)
    return await service.submit_outcome(payload, org_id=org_id, creator_id=current_user.id)

@router.get("/outcomes", response_model=MemoryListResponse)
async def list_outcomes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    client_id: Optional[str] = Query(None),
    workflow_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = MemoryService(db)
    return await service.list_memories(
        org_id=org_id,
        page=page,
        page_size=page_size,
        client_id=client_id,
        workflow_id=workflow_id,
        memory_type=MemoryType.OUTCOME
    )
