from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.database import Client as ClientModel
from app.clients.schemas import ClientCreateRequest, ClientUpdateRequest, ClientDTO, ClientListResponse
from app.clients.repository import ClientRepository
from app.clients.validator import ClientValidator

class ClientService:
    """Core Service layer handling tenant-isolated Client operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ClientRepository(session)

    async def create_client(self, payload: ClientCreateRequest, org_id: str, creator_id: str) -> ClientDTO:
        ClientValidator.validate_create_payload(payload.name, payload.industry)
        if payload.monthly_budget:
            ClientValidator.validate_budget(payload.monthly_budget)

        client = ClientModel(
            organization_id=org_id,
            name=payload.name.strip(),
            industry=payload.industry.strip(),
            website_url=payload.website_url,
            description=payload.description,
            business_goal=payload.business_goal,
            monthly_budget=payload.monthly_budget or 0.0,
            currency=payload.currency or "USD",
            status=payload.status.value if payload.status else "ACTIVE",
            contact_name=payload.contact_name,
            contact_email=payload.contact_email,
            contact_phone=payload.contact_phone,
            created_by=creator_id
        )

        created = await self.repo.create(client)
        await self.session.commit()
        await self.session.refresh(created)
        return ClientDTO.model_validate(created)

    async def get_client(self, client_id: str, org_id: str) -> ClientDTO:
        client = await self.repo.get_by_id_and_org(client_id, org_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found or does not belong to your organization."
            )
        return ClientDTO.model_validate(client)

    async def list_clients(
        self,
        org_id: str,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        industry: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> ClientListResponse:
        skip = (page - 1) * page_size
        clients, total = await self.repo.list_by_org(
            org_id=org_id,
            skip=skip,
            limit=page_size,
            search=search,
            industry=industry,
            status=status_filter
        )
        client_dtos = [ClientDTO.model_validate(c) for c in clients]
        return ClientListResponse(
            clients=client_dtos,
            total=total,
            page=page,
            page_size=page_size
        )

    async def update_client(self, client_id: str, org_id: str, payload: ClientUpdateRequest) -> ClientDTO:
        client = await self.repo.get_by_id_and_org(client_id, org_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found or does not belong to your organization."
            )

        update_data = payload.model_dump(exclude_unset=True)
        if "monthly_budget" in update_data and update_data["monthly_budget"] is not None:
            ClientValidator.validate_budget(update_data["monthly_budget"])

        for key, value in update_data.items():
            if key == "status" and value is not None:
                setattr(client, key, value.value if hasattr(value, "value") else str(value))
            elif value is not None:
                setattr(client, key, value)

        client.updated_at = datetime.now(timezone.utc)
        updated = await self.repo.update(client)
        await self.session.commit()
        await self.session.refresh(updated)
        return ClientDTO.model_validate(updated)

    async def archive_client(self, client_id: str, org_id: str) -> ClientDTO:
        client = await self.repo.get_by_id_and_org(client_id, org_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found or does not belong to your organization."
            )

        archived = await self.repo.soft_delete_archive(client)
        await self.session.commit()
        await self.session.refresh(archived)
        return ClientDTO.model_validate(archived)
