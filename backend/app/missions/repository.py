from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.missions.models import (
    MissionModel, MissionSuccessCriterionModel, MissionPlanVersionModel,
    MissionStepModel, MissionCheckpointModel, MissionStatus, MissionStepStatus
)

class MissionRepository:
    """Tenant-isolated repository for Mission entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_mission(self, mission: MissionModel) -> MissionModel:
        self.session.add(mission)
        await self.session.commit()
        return await self.get_mission_by_id(mission.id, mission.organization_id)

    async def get_mission_by_id(self, mission_id: str, org_id: str) -> Optional[MissionModel]:
        stmt = (
            select(MissionModel)
            .options(
                selectinload(MissionModel.criteria),
                selectinload(MissionModel.plans),
                selectinload(MissionModel.steps),
                selectinload(MissionModel.checkpoints)
            )
            .where(
                MissionModel.id == mission_id,
                MissionModel.organization_id == org_id
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_missions(self, org_id: str, status: Optional[MissionStatus] = None) -> List[MissionModel]:
        stmt = (
            select(MissionModel)
            .options(
                selectinload(MissionModel.criteria),
                selectinload(MissionModel.plans),
                selectinload(MissionModel.steps),
                selectinload(MissionModel.checkpoints)
            )
            .where(MissionModel.organization_id == org_id)
        )
        if status:
            stmt = stmt.where(MissionModel.status == status)
        stmt = stmt.order_by(MissionModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_mission_status(self, mission_id: str, org_id: str, new_status: MissionStatus) -> Optional[MissionModel]:
        stmt = (
            update(MissionModel)
            .where(MissionModel.id == mission_id, MissionModel.organization_id == org_id)
            .values(status=new_status)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_mission_by_id(mission_id, org_id)

    async def add_checkpoint(self, checkpoint: MissionCheckpointModel) -> MissionCheckpointModel:
        self.session.add(checkpoint)
        await self.session.commit()
        await self.session.refresh(checkpoint)
        return checkpoint

    async def add_plan_version(self, plan: MissionPlanVersionModel) -> MissionPlanVersionModel:
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan
