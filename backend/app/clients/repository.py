from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.database import Client as ClientModel

class ClientRepository:
    """Async SQLAlchemy Repository for Client entity."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_and_org(self, client_id: str, org_id: str) -> Optional[ClientModel]:
        stmt = select(ClientModel).where(
            ClientModel.id == client_id,
            ClientModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_org(
        self,
        org_id: str,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        industry: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[ClientModel], int]:
        stmt = select(ClientModel).where(ClientModel.organization_id == org_id)
        count_stmt = select(func.count(ClientModel.id)).where(ClientModel.organization_id == org_id)

        if search:
            search_filter = ClientModel.name.ilike(f"%{search}%")
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)
        
        if industry:
            stmt = stmt.where(ClientModel.industry.ilike(f"%{industry}%"))
            count_stmt = count_stmt.where(ClientModel.industry.ilike(f"%{industry}%"))

        if status:
            stmt = stmt.where(ClientModel.status == status)
            count_stmt = count_stmt.where(ClientModel.status == status)

        stmt = stmt.order_by(ClientModel.created_at.desc()).offset(skip).limit(limit)

        res = await self.session.execute(stmt)
        clients = res.scalars().all()

        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0

        return list(clients), total

    async def create(self, client: ClientModel) -> ClientModel:
        self.session.add(client)
        await self.session.flush()
        return client

    async def update(self, client: ClientModel) -> ClientModel:
        await self.session.flush()
        return client

    async def soft_delete_archive(self, client: ClientModel) -> ClientModel:
        client.status = "ARCHIVED"
        await self.session.flush()
        return client
