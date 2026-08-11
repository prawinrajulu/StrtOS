from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.command_center.models import CommandCenterSnapshotModel, StrategicDecisionSnapshotModel

class CommandCenterRepository:
    """Tenant-isolated repository for Command Center read-models."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_snapshot(self, snapshot: CommandCenterSnapshotModel) -> CommandCenterSnapshotModel:
        self.session.add(snapshot)
        await self.session.commit()
        await self.session.refresh(snapshot)
        return snapshot

    async def get_latest_snapshot(self, org_id: str) -> Optional[CommandCenterSnapshotModel]:
        stmt = (
            select(CommandCenterSnapshotModel)
            .where(CommandCenterSnapshotModel.organization_id == org_id)
            .order_by(CommandCenterSnapshotModel.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def create_decision_snapshot(self, decision: StrategicDecisionSnapshotModel) -> StrategicDecisionSnapshotModel:
        self.session.add(decision)
        await self.session.commit()
        await self.session.refresh(decision)
        return decision

    async def list_decisions(self, org_id: str) -> List[StrategicDecisionSnapshotModel]:
        stmt = (
            select(StrategicDecisionSnapshotModel)
            .where(StrategicDecisionSnapshotModel.organization_id == org_id)
            .order_by(StrategicDecisionSnapshotModel.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_decision_by_id(self, decision_id: str, org_id: str) -> Optional[StrategicDecisionSnapshotModel]:
        stmt = select(StrategicDecisionSnapshotModel).where(
            StrategicDecisionSnapshotModel.id == decision_id,
            StrategicDecisionSnapshotModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()
