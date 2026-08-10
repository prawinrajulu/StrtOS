from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.memory.models import MemoryRecordModel, MemoryType, OutcomeStatus

class MemoryRepository:
    """Repository enforcing multi-tenant database isolation on Memory Records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, memory: MemoryRecordModel) -> MemoryRecordModel:
        self.session.add(memory)
        await self.session.flush()
        return memory

    async def get_by_id_and_org(self, memory_id: str, org_id: str) -> Optional[MemoryRecordModel]:
        stmt = select(MemoryRecordModel).where(
            MemoryRecordModel.id == memory_id,
            MemoryRecordModel.organization_id == org_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_org(
        self,
        org_id: str,
        client_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        outcome_status: Optional[OutcomeStatus] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[MemoryRecordModel], int]:
        stmt = select(MemoryRecordModel).where(MemoryRecordModel.organization_id == org_id)

        if client_id:
            stmt = stmt.where(MemoryRecordModel.client_id == client_id)
        if workflow_id:
            stmt = stmt.where(MemoryRecordModel.workflow_id == workflow_id)
        if memory_type:
            stmt = stmt.where(MemoryRecordModel.memory_type == memory_type)
        if outcome_status:
            stmt = stmt.where(MemoryRecordModel.outcome_status == outcome_status)
        if search:
            stmt = stmt.where(
                or_(
                    MemoryRecordModel.title.ilike(f"%{search}%"),
                    MemoryRecordModel.content.ilike(f"%{search}%")
                )
            )

        # Count query
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0

        # Ordered query
        stmt = stmt.order_by(MemoryRecordModel.importance_score.desc(), MemoryRecordModel.created_at.desc()).offset(skip).limit(limit)
        results = await self.session.execute(stmt)
        memories = list(results.scalars().all())

        return memories, total

    async def update(self, memory: MemoryRecordModel) -> MemoryRecordModel:
        await self.session.flush()
        return memory

    async def delete(self, memory: MemoryRecordModel) -> None:
        await self.session.delete(memory)
        await self.session.flush()
