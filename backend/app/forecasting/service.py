import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.forecasting.models import (
    ForecastModel, ForecastMetricModel, ForecastScenarioModel,
    ForecastImpactModel, ForecastEvaluationModel, ForecastStatus,
    ForecastType, ForecastHorizon, TrendDirection
)
from app.forecasting.schemas import (
    ForecastCreate, ForecastResponse, TrendResponse, SimulationRequest,
    SimulationResponse, FutureRiskResponse, FutureOpportunityResponse,
    ForecastEvaluationResponse
)
from app.forecasting.repository import ForecastingRepository
from app.forecasting.engine import (
    TrendAnalysisEngine, StrategicForecastEngine, FutureStateSimulationEngine,
    FutureRiskEngine, FutureOpportunityEngine, ForecastAccuracyEngine
)
from app.core.events.publisher import event_publisher

class ForecastingService:
    """Core Service orchestrating Strategic Forecasting & Simulation workflows."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ForecastingRepository(session)
        self.trend_engine = TrendAnalysisEngine()
        self.forecast_engine = StrategicForecastEngine()
        self.simulation_engine = FutureStateSimulationEngine()
        self.risk_engine = FutureRiskEngine()
        self.opportunity_engine = FutureOpportunityEngine()
        self.accuracy_engine = ForecastAccuracyEngine()

    async def create_forecast(self, payload: ForecastCreate, org_id: str) -> ForecastResponse:
        # Standard dummy trend analysis from metric inputs
        current_vals = [m.current_value for m in payload.metrics] if payload.metrics else [10000.0, 10500.0]
        trend_resp = self.trend_engine.analyze_trend(current_vals)

        forecast = ForecastModel(
            organization_id=org_id,
            forecast_type=payload.forecast_type,
            horizon=payload.horizon,
            status=ForecastStatus.GENERATED,
            title=payload.title,
            summary=f"Strategic forecast for '{payload.title}' across {payload.horizon.value} horizon.",
            confidence_score=trend_resp.confidence,
            trend_direction=trend_resp.direction
        )

        for m_in in payload.metrics:
            f_val, l_b, u_b, c_score = self.forecast_engine.compute_forecast(
                current_value=m_in.current_value,
                trend=trend_resp,
                horizon=payload.horizon
            )
            forecast.metrics.append(
                ForecastMetricModel(
                    organization_id=org_id,
                    metric_name=m_in.metric_name,
                    current_value=m_in.current_value,
                    forecast_value=f_val,
                    lower_bound=l_b,
                    upper_bound=u_b,
                    unit=m_in.unit,
                    confidence_score=c_score
                )
            )

        saved = await self.repo.create_forecast(forecast)

        await event_publisher.publish(
            event_type="forecast.created",
            organization_id=org_id,
            message=f"Strategic Forecast '{saved.title}' generated.",
            metadata={"forecast_id": saved.id, "horizon": saved.horizon.value}
        )

        return ForecastResponse.model_validate(saved)

    async def get_forecast(self, forecast_id: str, org_id: str) -> ForecastResponse:
        fc = await self.repo.get_forecast_by_id(forecast_id, org_id)
        if not fc:
            raise KeyError(f"Strategic Forecast '{forecast_id}' not found.")
        return ForecastResponse.model_validate(fc)

    async def list_forecasts(self, org_id: str, forecast_type: Optional[ForecastType] = None) -> List[ForecastResponse]:
        forecasts = await self.repo.list_forecasts(org_id, forecast_type=forecast_type)
        return [ForecastResponse.model_validate(f) for f in forecasts]

    async def simulate_forecast(self, forecast_id: str, request: SimulationRequest, org_id: str) -> SimulationResponse:
        fc = await self.repo.get_forecast_by_id(forecast_id, org_id)
        if not fc:
            raise KeyError(f"Strategic Forecast '{forecast_id}' not found.")

        base_val = fc.metrics[0].forecast_value if fc.metrics and fc.metrics[0].forecast_value else 10000.0
        return self.simulation_engine.simulate_future(forecast_id, base_val, request)

    async def get_future_risks(self, forecast_id: str, org_id: str) -> List[FutureRiskResponse]:
        fc = await self.repo.get_forecast_by_id(forecast_id, org_id)
        if not fc:
            raise KeyError(f"Strategic Forecast '{forecast_id}' not found.")
        trend = TrendResponse(
            direction=fc.trend_direction,
            strength=80.0,
            change_rate=-10.0 if fc.trend_direction == TrendDirection.DOWNWARD else 5.0,
            acceleration=0.5,
            confidence=fc.confidence_score
        )
        base_val = fc.metrics[0].forecast_value if fc.metrics and fc.metrics[0].forecast_value else 10000.0
        return self.risk_engine.evaluate_future_risks(base_val, trend)

    async def get_future_opportunities(self, forecast_id: str, org_id: str) -> List[FutureOpportunityResponse]:
        fc = await self.repo.get_forecast_by_id(forecast_id, org_id)
        if not fc:
            raise KeyError(f"Strategic Forecast '{forecast_id}' not found.")
        trend = TrendResponse(
            direction=fc.trend_direction,
            strength=80.0,
            change_rate=15.0 if fc.trend_direction == TrendDirection.UPWARD else -5.0,
            acceleration=0.5,
            confidence=fc.confidence_score
        )
        base_val = fc.metrics[0].forecast_value if fc.metrics and fc.metrics[0].forecast_value else 10000.0
        return self.opportunity_engine.evaluate_future_opportunities(base_val, trend)

    async def evaluate_accuracy(self, forecast_id: str, actual_value: float, org_id: str) -> ForecastEvaluationResponse:
        fc = await self.repo.get_forecast_by_id(forecast_id, org_id)
        if not fc:
            raise KeyError(f"Strategic Forecast '{forecast_id}' not found.")

        f_val = fc.metrics[0].forecast_value if fc.metrics and fc.metrics[0].forecast_value else 10000.0
        abs_err, acc_score, cal_status = self.accuracy_engine.evaluate_accuracy(f_val, actual_value)

        eval_model = ForecastEvaluationModel(
            organization_id=org_id,
            forecast_id=forecast_id,
            actual_value=actual_value,
            forecast_value=f_val,
            absolute_error=abs_err,
            accuracy_score=acc_score,
            calibration_status=cal_status
        )
        saved = await self.repo.add_evaluation(eval_model)

        await event_publisher.publish(
            event_type="forecast.accuracy.measured",
            organization_id=org_id,
            message=f"Measured forecast accuracy for '{fc.title}'. Score: {acc_score}%.",
            metadata={"forecast_id": forecast_id, "accuracy_score": acc_score}
        )

        return ForecastEvaluationResponse.model_validate(saved)
