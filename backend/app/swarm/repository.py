from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.swarm.models import SwarmSessionModel, SwarmMessageModel, SwarmConflictModel, SwarmDebateModel, SwarmStatus

class SwarmRepository:
    """Async Repository managing database persistence for Swarm Sessions with multi-tenant isolation."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(self, swarm_session: SwarmSessionModel) -> SwarmSessionModel:
        self.session.add(swarm_session)
        await self.session.flush()
        return swarm_session

    async def get_session_by_id_and_org(self, session_id: str, org_id: str) -> Optional[SwarmSessionModel]:
        stmt = select(SwarmSessionModel).where(
            SwarmSessionModel.id == session_id,
            SwarmSessionModel.organization_id == org_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_sessions_by_org(
        self,
        org_id: str,
        client_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        status_filter: Optional[SwarmStatus] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[SwarmSessionModel], int]:
        stmt = select(SwarmSessionModel).where(SwarmSessionModel.organization_id == org_id)

        if client_id:
            stmt = stmt.where(SwarmSessionModel.client_id == client_id)
        if workflow_id:
            stmt = stmt.where(SwarmSessionModel.workflow_id == workflow_id)
        if status_filter:
            stmt = stmt.where(SwarmSessionModel.status == status_filter)
        if search:
            stmt = stmt.where(SwarmSessionModel.objective.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0

        stmt = stmt.order_by(SwarmSessionModel.created_at.desc()).offset(skip).limit(limit)
        results = await self.session.execute(stmt)
        sessions = list(results.scalars().all())

        return sessions, total

    async def update_session(self, swarm_session: SwarmSessionModel) -> SwarmSessionModel:
        await self.session.flush()
        return swarm_session

    async def create_message(self, message: SwarmMessageModel) -> SwarmMessageModel:
        self.session.add(message)
        await self.session.flush()
        return message

    async def list_messages_by_swarm(self, swarm_id: str, org_id: str) -> List[SwarmMessageModel]:
        stmt = select(SwarmMessageModel).where(
            SwarmMessageModel.swarm_id == swarm_id,
            SwarmMessageModel.organization_id == org_id
        ).order_by(SwarmMessageModel.created_at.asc())
        results = await self.session.execute(stmt)
        return list(results.scalars().all())

    async def create_conflict(self, conflict: SwarmConflictModel) -> SwarmConflictModel:
        self.session.add(conflict)
        await self.session.flush()
        return conflict

    async def list_conflicts_by_swarm(self, swarm_id: str, org_id: str) -> List[SwarmConflictModel]:
        stmt = select(SwarmConflictModel).where(
            SwarmConflictModel.swarm_id == swarm_id,
            SwarmConflictModel.organization_id == org_id
        ).order_by(SwarmConflictModel.created_at.asc())
        results = await self.session.execute(stmt)
        return list(results.scalars().all())

    async def create_debate(self, debate: SwarmDebateModel) -> SwarmDebateModel:
        self.session.add(debate)
        await self.session.flush()
        return debate

    async def list_debates_by_swarm(self, swarm_id: str, org_id: str) -> List[SwarmDebateModel]:
        stmt = select(SwarmDebateModel).where(
            SwarmDebateModel.swarm_id == swarm_id,
            SwarmDebateModel.organization_id == org_id
        ).order_by(SwarmDebateModel.round_number.asc())
        results = await self.session.execute(stmt)
        return list(results.scalars().all())
