from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.dependencies import get_current_user, RoleChecker
from app.auth.models import UserModel, UserRole
from app.schemas.all_schemas import SuccessResponse
from app.clients.schemas import (
    ClientCreateRequest, ClientUpdateRequest, ClientDTO, ClientListResponse
)
from app.clients.service import ClientService

router = APIRouter(prefix="/clients", tags=["Client Management"])

@router.post("", response_model=SuccessResponse[ClientDTO], status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreateRequest,
    current_user: UserModel = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """Creates a new Client securely scoped to the user's organization."""
    service = ClientService(db)
    client_dto = await service.create_client(payload, org_id=current_user.organization_id, creator_id=current_user.id)
    return SuccessResponse(data=client_dto, message="Client created successfully.")

@router.get("", response_model=SuccessResponse[ClientListResponse])
async def list_clients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lists all Clients belonging exclusively to the user's organization."""
    service = ClientService(db)
    result = await service.list_clients(
        org_id=current_user.organization_id,
        page=page,
        page_size=page_size,
        search=search,
        industry=industry,
        status_filter=status_filter
    )
    return SuccessResponse(data=result, message="Clients retrieved successfully.")

@router.get("/{client_id}", response_model=SuccessResponse[ClientDTO])
async def get_client(
    client_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Gets details for a specific Client, verifying organization ownership."""
    service = ClientService(db)
    client_dto = await service.get_client(client_id, org_id=current_user.organization_id)
    return SuccessResponse(data=client_dto, message="Client details retrieved.")

@router.patch("/{client_id}", response_model=SuccessResponse[ClientDTO])
async def update_client(
    client_id: str,
    payload: ClientUpdateRequest,
    current_user: UserModel = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """Updates a Client record with organization ownership check."""
    service = ClientService(db)
    client_dto = await service.update_client(client_id, org_id=current_user.organization_id, payload=payload)
    return SuccessResponse(data=client_dto, message="Client updated successfully.")

@router.delete("/{client_id}", response_model=SuccessResponse[ClientDTO])
async def archive_client(
    client_id: str,
    current_user: UserModel = Depends(RoleChecker([UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    """Soft-deletes (archives) a Client record with organization ownership check."""
    service = ClientService(db)
    client_dto = await service.archive_client(client_id, org_id=current_user.organization_id)
    return SuccessResponse(data=client_dto, message="Client archived successfully.")
