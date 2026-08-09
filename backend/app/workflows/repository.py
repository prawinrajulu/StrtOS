from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.database import Workflow as WorkflowModel, Task as TaskModel, WorkflowEvent as WorkflowEventModel, Report as ReportModel

class WorkflowRepository:
    """Async SQLAlchemy Repository for Workflow entity."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_and_org(self, workflow_id: str, org_id: str) -> Optional[WorkflowModel]:
        stmt = select(WorkflowModel).where(
            WorkflowModel.id == workflow_id,
            WorkflowModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_org(
        self,
        org_id: str,
        skip: int = 0,
        limit: int = 50,
        client_id: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[WorkflowModel], int]:
        stmt = select(WorkflowModel).where(WorkflowModel.organization_id == org_id)
        count_stmt = select(func.count(WorkflowModel.id)).where(WorkflowModel.organization_id == org_id)

        if client_id:
            stmt = stmt.where(WorkflowModel.client_id == client_id)
            count_stmt = count_stmt.where(WorkflowModel.client_id == client_id)

        if status:
            stmt = stmt.where(WorkflowModel.status == status)
            count_stmt = count_stmt.where(WorkflowModel.status == status)

        if search:
            search_filter = WorkflowModel.title.ilike(f"%{search}%")
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        stmt = stmt.order_by(WorkflowModel.created_at.desc()).offset(skip).limit(limit)

        res = await self.session.execute(stmt)
        workflows = res.scalars().all()

        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0

        return list(workflows), total

    async def create(self, workflow: WorkflowModel) -> WorkflowModel:
        self.session.add(workflow)
        await self.session.flush()
        return workflow

    async def update(self, workflow: WorkflowModel) -> WorkflowModel:
        await self.session.flush()
        return workflow

    async def create_event(self, event: WorkflowEventModel) -> WorkflowEventModel:
        self.session.add(event)
        await self.session.flush()
        return event

    async def get_tasks_by_workflow(self, workflow_id: str, org_id: str) -> List[TaskModel]:
        stmt = select(TaskModel).where(
            TaskModel.workflow_id == workflow_id,
            TaskModel.organization_id == org_id
        ).order_by(TaskModel.created_at.asc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_events_by_workflow(self, workflow_id: str, org_id: str) -> List[WorkflowEventModel]:
        stmt = select(WorkflowEventModel).where(
            WorkflowEventModel.workflow_id == workflow_id,
            WorkflowEventModel.organization_id == org_id
        ).order_by(WorkflowEventModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
