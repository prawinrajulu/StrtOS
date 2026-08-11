from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.portfolio.models import (
    StrategicPortfolioModel, PortfolioMissionModel, PortfolioResourceModel,
    PortfolioConstraintModel, PortfolioAllocationModel, PortfolioEvaluationModel,
    PortfolioDecisionModel, PortfolioVersionModel, PortfolioCheckpointModel,
    PortfolioStatus, PortfolioDecisionStatus
)


class PortfolioRepository:
    """Tenant-isolated repository for all Portfolio entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ──────────────────── Portfolio CRUD ────────────────────────────────────

    async def create_portfolio(self, portfolio: StrategicPortfolioModel) -> StrategicPortfolioModel:
        self.session.add(portfolio)
        await self.session.commit()
        return await self.get_portfolio_by_id(portfolio.id, portfolio.organization_id)

    async def get_portfolio_by_id(self, portfolio_id: str, org_id: str) -> Optional[StrategicPortfolioModel]:
        stmt = (
            select(StrategicPortfolioModel)
            .options(
                selectinload(StrategicPortfolioModel.missions),
                selectinload(StrategicPortfolioModel.resources),
                selectinload(StrategicPortfolioModel.constraints),
                selectinload(StrategicPortfolioModel.allocations),
                selectinload(StrategicPortfolioModel.evaluations),
                selectinload(StrategicPortfolioModel.decisions),
                selectinload(StrategicPortfolioModel.versions),
                selectinload(StrategicPortfolioModel.checkpoints),
            )
            .where(
                StrategicPortfolioModel.id == portfolio_id,
                StrategicPortfolioModel.organization_id == org_id
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_portfolios(
        self, org_id: str, status: Optional[PortfolioStatus] = None
    ) -> List[StrategicPortfolioModel]:
        stmt = (
            select(StrategicPortfolioModel)
            .options(
                selectinload(StrategicPortfolioModel.missions),
                selectinload(StrategicPortfolioModel.resources),
                selectinload(StrategicPortfolioModel.constraints),
                selectinload(StrategicPortfolioModel.allocations),
                selectinload(StrategicPortfolioModel.evaluations),
                selectinload(StrategicPortfolioModel.decisions),
                selectinload(StrategicPortfolioModel.versions),
                selectinload(StrategicPortfolioModel.checkpoints),
            )
            .where(StrategicPortfolioModel.organization_id == org_id)
        )
        if status:
            stmt = stmt.where(StrategicPortfolioModel.status == status)
        stmt = stmt.order_by(StrategicPortfolioModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_portfolio_status(
        self, portfolio_id: str, org_id: str, new_status: PortfolioStatus
    ) -> Optional[StrategicPortfolioModel]:
        stmt = (
            update(StrategicPortfolioModel)
            .where(
                StrategicPortfolioModel.id == portfolio_id,
                StrategicPortfolioModel.organization_id == org_id
            )
            .values(status=new_status)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_portfolio_by_id(portfolio_id, org_id)

    async def update_portfolio_fields(
        self, portfolio_id: str, org_id: str, **kwargs
    ) -> Optional[StrategicPortfolioModel]:
        stmt = (
            update(StrategicPortfolioModel)
            .where(
                StrategicPortfolioModel.id == portfolio_id,
                StrategicPortfolioModel.organization_id == org_id
            )
            .values(**kwargs)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_portfolio_by_id(portfolio_id, org_id)

    # ──────────────────── Relationship Mutations ─────────────────────────────

    async def add_portfolio_mission(self, pm: PortfolioMissionModel) -> PortfolioMissionModel:
        self.session.add(pm)
        await self.session.commit()
        await self.session.refresh(pm)
        return pm

    async def add_resource(self, resource: PortfolioResourceModel) -> PortfolioResourceModel:
        self.session.add(resource)
        await self.session.commit()
        await self.session.refresh(resource)
        return resource

    async def add_constraint(self, constraint: PortfolioConstraintModel) -> PortfolioConstraintModel:
        self.session.add(constraint)
        await self.session.commit()
        await self.session.refresh(constraint)
        return constraint

    async def add_allocation(self, allocation: PortfolioAllocationModel) -> PortfolioAllocationModel:
        self.session.add(allocation)
        await self.session.commit()
        await self.session.refresh(allocation)
        return allocation

    async def add_version(self, version: PortfolioVersionModel) -> PortfolioVersionModel:
        self.session.add(version)
        await self.session.commit()
        await self.session.refresh(version)
        return version

    async def add_checkpoint(self, checkpoint: PortfolioCheckpointModel) -> PortfolioCheckpointModel:
        self.session.add(checkpoint)
        await self.session.commit()
        await self.session.refresh(checkpoint)
        return checkpoint

    async def add_evaluation(self, evaluation: PortfolioEvaluationModel) -> PortfolioEvaluationModel:
        self.session.add(evaluation)
        await self.session.commit()
        await self.session.refresh(evaluation)
        return evaluation

    async def add_decision(self, decision: PortfolioDecisionModel) -> PortfolioDecisionModel:
        self.session.add(decision)
        await self.session.commit()
        await self.session.refresh(decision)
        return decision

    async def update_decision_status(
        self, decision_id: str, org_id: str, new_status: PortfolioDecisionStatus, **kwargs
    ) -> Optional[PortfolioDecisionModel]:
        stmt = (
            update(PortfolioDecisionModel)
            .where(
                PortfolioDecisionModel.id == decision_id,
                PortfolioDecisionModel.organization_id == org_id
            )
            .values(status=new_status, **kwargs)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        res = await self.session.execute(
            select(PortfolioDecisionModel).where(PortfolioDecisionModel.id == decision_id)
        )
        return res.scalars().first()
