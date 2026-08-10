from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.predictions.models import PredictionModel, ScenarioType, PredictionStatus

class PredictionRepository:
    """Async Repository managing database persistence for Decision Predictions with multi-tenant isolation."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, prediction: PredictionModel) -> PredictionModel:
        self.session.add(prediction)
        await self.session.flush()
        return prediction

    async def get_by_id_and_org(self, prediction_id: str, org_id: str) -> Optional[PredictionModel]:
        stmt = select(PredictionModel).where(
            PredictionModel.id == prediction_id,
            PredictionModel.organization_id == org_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_org(
        self,
        org_id: str,
        client_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        scenario_type: Optional[ScenarioType] = None,
        prediction_status: Optional[PredictionStatus] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[PredictionModel], int]:
        stmt = select(PredictionModel).where(PredictionModel.organization_id == org_id)

        if client_id:
            stmt = stmt.where(PredictionModel.client_id == client_id)
        if workflow_id:
            stmt = stmt.where(PredictionModel.workflow_id == workflow_id)
        if scenario_type:
            stmt = stmt.where(PredictionModel.scenario_type == scenario_type)
        if prediction_status:
            stmt = stmt.where(PredictionModel.prediction_status == prediction_status)
        if search:
            stmt = stmt.where(
                or_(
                    PredictionModel.scenario_name.ilike(f"%{search}%"),
                    PredictionModel.objective.ilike(f"%{search}%")
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0

        # Paginated results
        stmt = stmt.order_by(PredictionModel.created_at.desc()).offset(skip).limit(limit)
        results = await self.session.execute(stmt)
        predictions = list(results.scalars().all())

        return predictions, total

    async def update(self, prediction: PredictionModel) -> PredictionModel:
        await self.session.flush()
        return prediction

    async def delete(self, prediction: PredictionModel) -> None:
        await self.session.delete(prediction)
        await self.session.flush()
