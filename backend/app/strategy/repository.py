from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.strategy.models import (
    StrategicObjectiveModel, StrategicMetricModel, StrategicConstraintModel,
    StrategicPlanModel, StrategicMilestoneModel, StrategicPlanVersionModel
)

class StrategyRepository:
    """Tenant-isolated repository for all Strategy domain entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ---------------------------------------------------------------------------
    # OBJECTIVE CRUD
    # ---------------------------------------------------------------------------
    async def create_objective(self, obj: StrategicObjectiveModel) -> StrategicObjectiveModel:
        self.session.add(obj)
        await self.session.commit()
        return await self.get_objective_by_id(obj.id, obj.organization_id)

    async def get_objective_by_id(self, obj_id: str, org_id: str) -> Optional[StrategicObjectiveModel]:
        stmt = (
            select(StrategicObjectiveModel)
            .options(
                selectinload(StrategicObjectiveModel.metrics),
                selectinload(StrategicObjectiveModel.constraints)
            )
            .where(
                StrategicObjectiveModel.id == obj_id,
                StrategicObjectiveModel.organization_id == org_id
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_objectives(self, org_id: str, status: Optional[str] = None) -> List[StrategicObjectiveModel]:
        stmt = (
            select(StrategicObjectiveModel)
            .options(
                selectinload(StrategicObjectiveModel.metrics),
                selectinload(StrategicObjectiveModel.constraints)
            )
            .where(StrategicObjectiveModel.organization_id == org_id)
        )
        if status:
            stmt = stmt.where(StrategicObjectiveModel.status == status)
        stmt = stmt.order_by(StrategicObjectiveModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    # ---------------------------------------------------------------------------
    # PLAN CRUD
    # ---------------------------------------------------------------------------
    async def create_plan(self, plan: StrategicPlanModel) -> StrategicPlanModel:
        self.session.add(plan)
        await self.session.commit()
        return await self.get_plan_by_id(plan.id, plan.organization_id)

    async def get_plan_by_id(self, plan_id: str, org_id: str) -> Optional[StrategicPlanModel]:
        stmt = (
            select(StrategicPlanModel)
            .options(
                selectinload(StrategicPlanModel.milestones),
                selectinload(StrategicPlanModel.versions)
            )
            .where(
                StrategicPlanModel.id == plan_id,
                StrategicPlanModel.organization_id == org_id
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_plans(self, org_id: str, objective_id: Optional[str] = None) -> List[StrategicPlanModel]:
        stmt = (
            select(StrategicPlanModel)
            .options(
                selectinload(StrategicPlanModel.milestones),
                selectinload(StrategicPlanModel.versions)
            )
            .where(StrategicPlanModel.organization_id == org_id)
        )
        if objective_id:
            stmt = stmt.where(StrategicPlanModel.objective_id == objective_id)
        stmt = stmt.order_by(StrategicPlanModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_version(self, version: StrategicPlanVersionModel) -> StrategicPlanVersionModel:
        self.session.add(version)
        await self.session.commit()
        await self.session.refresh(version)
        return version
