from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.execution.models import ActionModel, ActionStatus

class ActionRepository:
    """Async Repository managing database persistence for Execution Actions with multi-tenant isolation."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, action: ActionModel) -> ActionModel:
        self.session.add(action)
        await self.session.flush()
        return action

    async def get_by_id_and_org(self, action_id: str, org_id: str) -> Optional[ActionModel]:
        stmt = select(ActionModel).where(
            ActionModel.id == action_id,
            ActionModel.organization_id == org_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_idempotency_key(self, idempotency_key: str, org_id: str) -> Optional[ActionModel]:
        stmt = select(ActionModel).where(
            ActionModel.idempotency_key == idempotency_key,
            ActionModel.organization_id == org_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_org(
        self,
        org_id: str,
        client_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        prediction_id: Optional[str] = None,
        status_filter: Optional[ActionStatus] = None,
        action_type: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[ActionModel], int]:
        stmt = select(ActionModel).where(ActionModel.organization_id == org_id)

        if client_id:
            stmt = stmt.where(ActionModel.client_id == client_id)
        if workflow_id:
            stmt = stmt.where(ActionModel.workflow_id == workflow_id)
        if prediction_id:
            stmt = stmt.where(ActionModel.prediction_id == prediction_id)
        if status_filter:
            stmt = stmt.where(ActionModel.status == status_filter)
        if action_type:
            stmt = stmt.where(ActionModel.action_type == action_type)
        if search:
            stmt = stmt.where(
                or_(
                    ActionModel.name.ilike(f"%{search}%"),
                    ActionModel.action_type.ilike(f"%{search}%")
                )
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0

        stmt = stmt.order_by(ActionModel.created_at.desc()).offset(skip).limit(limit)
        results = await self.session.execute(stmt)
        actions = list(results.scalars().all())

        return actions, total

    async def update(self, action: ActionModel) -> ActionModel:
        await self.session.flush()
        return action

    async def delete(self, action: ActionModel) -> None:
        await self.session.delete(action)
        await self.session.flush()
