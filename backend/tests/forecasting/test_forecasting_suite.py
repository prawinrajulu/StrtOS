import pytest
from app.core.database import AsyncSessionLocal
from app.forecasting.models import ForecastType, ForecastHorizon, ForecastStatus, TrendDirection
from app.forecasting.service import ForecastingService
from app.forecasting.schemas import ForecastCreate, ForecastMetricCreate, SimulationRequest

@pytest.mark.asyncio
async def test_forecasting_models_service_and_engines():
    async with AsyncSessionLocal() as session:
        service = ForecastingService(session)
        org_id = "test-forecast-org-1"

        # 1. Create Strategic Forecast
        fc = await service.create_forecast(
            ForecastCreate(
                forecast_type=ForecastType.REVENUE,
                horizon=ForecastHorizon.DAYS_90,
                title="Q2 Strategic Revenue Forecast",
                metrics=[
                    ForecastMetricCreate(
                        metric_name="Quarterly Revenue",
                        current_value=500000.0,
                        unit="USD",
                        confidence_score=90.0
                    )
                ]
            ),
            org_id=org_id
        )
        assert fc.title == "Q2 Strategic Revenue Forecast"
        assert fc.status == ForecastStatus.GENERATED
        assert len(fc.metrics) == 1
        assert fc.metrics[0].forecast_value is not None

        # 2. Run What-If Simulation
        sim_res = await service.simulate_forecast(
            fc.id,
            SimulationRequest(budget_delta=2500.0, intensity_multiplier=1.2),
            org_id=org_id
        )
        assert sim_res.forecast_id == fc.id
        assert sim_res.simulated_outcome > sim_res.baseline_outcome

        # 3. Discover Future Risks & Opportunities
        risks = await service.get_future_risks(fc.id, org_id)
        opps = await service.get_future_opportunities(fc.id, org_id)
        assert isinstance(risks, list)
        assert isinstance(opps, list)

        # 4. Measure Forecast Accuracy & Calibration
        eval_res = await service.evaluate_accuracy(fc.id, actual_value=510000.0, org_id=org_id)
        assert eval_res.forecast_id == fc.id
        assert eval_res.accuracy_score >= 80.0
        assert eval_res.calibration_status in ["WELL_CALIBRATED", "OVERCONFIDENT", "UNDERCONFIDENT"]

        # 5. Multi-Tenant Check
        try:
            await service.get_forecast(fc.id, org_id="unauthorized-org")
            assert False, "Should have failed multi-tenant check"
        except KeyError:
            pass
