from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.resources.models import (
    ResourceModel, ResourceCapacityModel, ResourceAllocationModel,
    ResourceConstraintModel, ResourceConflictModel, ResourceUtilizationModel,
    ResourceAllocationPlanModel, ResourceAllocationPlanVersionModel,
    ResourceStatus, AllocationPlanStatus
)


class ResourceRepository:
    """Tenant-isolated repository for all Resource entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ──────────────────── Resource CRUD ─────────────────────────────────────

    async def create_resource(self, resource: ResourceModel) -> ResourceModel:
        self.session.add(resource)
        await self.session.commit()
        return await self.get_resource_by_id(resource.id, resource.organization_id)

    async def get_resource_by_id(self, resource_id: str, org_id: str) -> Optional[ResourceModel]:
        stmt = (
            select(ResourceModel)
            .options(
                selectinload(ResourceModel.capacities),
                selectinload(ResourceModel.allocations),
                selectinload(ResourceModel.constraints),
                selectinload(ResourceModel.conflicts),
                selectinload(ResourceModel.utilizations),
            )
            .where(ResourceModel.id == resource_id, ResourceModel.organization_id == org_id)
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_resources(
        self, org_id: str, resource_type=None, status=None
    ) -> List[ResourceModel]:
        stmt = (
            select(ResourceModel)
            .options(
                selectinload(ResourceModel.capacities),
                selectinload(ResourceModel.allocations),
                selectinload(ResourceModel.constraints),
                selectinload(ResourceModel.conflicts),
                selectinload(ResourceModel.utilizations),
            )
            .where(ResourceModel.organization_id == org_id)
        )
        if resource_type:
            stmt = stmt.where(ResourceModel.resource_type == resource_type)
        if status:
            stmt = stmt.where(ResourceModel.status == status)
        stmt = stmt.order_by(ResourceModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_resource_fields(self, resource_id: str, org_id: str, **kwargs) -> Optional[ResourceModel]:
        stmt = (
            update(ResourceModel)
            .where(ResourceModel.id == resource_id, ResourceModel.organization_id == org_id)
            .values(**kwargs)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_resource_by_id(resource_id, org_id)

    # ──────────────────── Capacity ──────────────────────────────────────────

    async def add_capacity_snapshot(self, snap: ResourceCapacityModel) -> ResourceCapacityModel:
        self.session.add(snap)
        await self.session.commit()
        await self.session.refresh(snap)
        return snap

    # ──────────────────── Allocations ───────────────────────────────────────

    async def add_allocation(self, alloc: ResourceAllocationModel) -> ResourceAllocationModel:
        self.session.add(alloc)
        await self.session.commit()
        await self.session.refresh(alloc)
        return alloc

    async def list_allocations_for_mission(self, mission_id: str, org_id: str) -> List[ResourceAllocationModel]:
        stmt = select(ResourceAllocationModel).where(
            ResourceAllocationModel.mission_id == mission_id,
            ResourceAllocationModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    # ──────────────────── Conflicts ─────────────────────────────────────────

    async def add_conflict(self, conflict: ResourceConflictModel) -> ResourceConflictModel:
        self.session.add(conflict)
        await self.session.commit()
        await self.session.refresh(conflict)
        return conflict

    async def list_open_conflicts(self, org_id: str) -> List[ResourceConflictModel]:
        stmt = select(ResourceConflictModel).where(
            ResourceConflictModel.organization_id == org_id,
            ResourceConflictModel.is_resolved == False
        ).order_by(ResourceConflictModel.detected_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    # ──────────────────── Utilization ───────────────────────────────────────

    async def add_utilization_snapshot(self, util: ResourceUtilizationModel) -> ResourceUtilizationModel:
        self.session.add(util)
        await self.session.commit()
        await self.session.refresh(util)
        return util

    # ──────────────────── Allocation Plans ──────────────────────────────────

    async def create_plan(self, plan: ResourceAllocationPlanModel) -> ResourceAllocationPlanModel:
        self.session.add(plan)
        await self.session.commit()
        return await self.get_plan_by_id(plan.id, plan.organization_id)

    async def get_plan_by_id(self, plan_id: str, org_id: str) -> Optional[ResourceAllocationPlanModel]:
        stmt = (
            select(ResourceAllocationPlanModel)
            .options(selectinload(ResourceAllocationPlanModel.versions))
            .where(
                ResourceAllocationPlanModel.id == plan_id,
                ResourceAllocationPlanModel.organization_id == org_id
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_plans(self, org_id: str, status: Optional[AllocationPlanStatus] = None) -> List[ResourceAllocationPlanModel]:
        stmt = (
            select(ResourceAllocationPlanModel)
            .options(selectinload(ResourceAllocationPlanModel.versions))
            .where(ResourceAllocationPlanModel.organization_id == org_id)
        )
        if status:
            stmt = stmt.where(ResourceAllocationPlanModel.status == status)
        stmt = stmt.order_by(ResourceAllocationPlanModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_plan_status(
        self, plan_id: str, org_id: str, new_status: AllocationPlanStatus, **kwargs
    ) -> Optional[ResourceAllocationPlanModel]:
        stmt = (
            update(ResourceAllocationPlanModel)
            .where(
                ResourceAllocationPlanModel.id == plan_id,
                ResourceAllocationPlanModel.organization_id == org_id
            )
            .values(status=new_status, **kwargs)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_plan_by_id(plan_id, org_id)

    async def add_plan_version(self, ver: ResourceAllocationPlanVersionModel) -> ResourceAllocationPlanVersionModel:
        self.session.add(ver)
        await self.session.commit()
        await self.session.refresh(ver)
        return ver
