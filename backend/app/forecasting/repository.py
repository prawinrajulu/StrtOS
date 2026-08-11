from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.forecasting.models import (
    ForecastModel, ForecastMetricModel, ForecastScenarioModel,
    ForecastImpactModel, ForecastEvaluationModel, ForecastStatus, ForecastType
)

class ForecastingRepository:
    """Tenant-isolated repository for all Forecasting entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_forecast(self, forecast: ForecastModel) -> ForecastModel:
        self.session.add(forecast)
        await self.session.commit()
        return await self.get_forecast_by_id(forecast.id, forecast.organization_id)

    async def get_forecast_by_id(self, forecast_id: str, org_id: str) -> Optional[ForecastModel]:
        stmt = (
            select(ForecastModel)
            .options(
                selectinload(ForecastModel.metrics),
                selectinload(ForecastModel.scenarios),
                selectinload(ForecastModel.impacts),
                selectinload(ForecastModel.evaluations)
            )
            .where(
                ForecastModel.id == forecast_id,
                ForecastModel.organization_id == org_id
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_forecasts(self, org_id: str, forecast_type: Optional[ForecastType] = None) -> List[ForecastModel]:
        stmt = (
            select(ForecastModel)
            .options(
                selectinload(ForecastModel.metrics),
                selectinload(ForecastModel.scenarios),
                selectinload(ForecastModel.impacts),
                selectinload(ForecastModel.evaluations)
            )
            .where(ForecastModel.organization_id == org_id)
        )
        if forecast_type:
            stmt = stmt.where(ForecastModel.forecast_type == forecast_type)
        stmt = stmt.order_by(ForecastModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def add_evaluation(self, eval_model: ForecastEvaluationModel) -> ForecastEvaluationModel:
        self.session.add(eval_model)
        await self.session.commit()
        await self.session.refresh(eval_model)
        return eval_model
