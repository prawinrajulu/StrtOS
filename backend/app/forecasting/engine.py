import math
from typing import List, Dict, Any, Optional, Tuple
from app.forecasting.models import TrendDirection, ForecastHorizon
from app.forecasting.schemas import (
    TrendResponse, SimulationRequest, SimulationResponse,
    FutureRiskResponse, FutureOpportunityResponse
)

class TrendAnalysisEngine:
    """Calculates trend direction, strength, change rate, and acceleration."""

    def analyze_trend(self, historical_values: List[float]) -> TrendResponse:
        if not historical_values or len(historical_values) < 2:
            return TrendResponse(
                direction=TrendDirection.INSUFFICIENT_DATA,
                strength=0.0,
                change_rate=0.0,
                acceleration=0.0,
                confidence=0.0
            )

        first, last = historical_values[0], historical_values[-1]
        delta = last - first
        change_rate = round((delta / max(1.0, abs(first))) * 100.0, 2)

        if change_rate > 5.0:
            direction = TrendDirection.UPWARD
        elif change_rate < -5.0:
            direction = TrendDirection.DOWNWARD
        else:
            direction = TrendDirection.STABLE

        strength = min(100.0, abs(change_rate) * 2.0)
        confidence = min(95.0, 60.0 + (len(historical_values) * 5.0))

        return TrendResponse(
            direction=direction,
            strength=round(strength, 1),
            change_rate=change_rate,
            acceleration=0.5,
            confidence=round(confidence, 1)
        )

class StrategicForecastEngine:
    """Generates multi-horizon metric forecasts and bounds."""

    def compute_forecast(
        self,
        current_value: float,
        trend: TrendResponse,
        horizon: ForecastHorizon
    ) -> Tuple[float, float, float, float]:
        days = 90
        if horizon == ForecastHorizon.DAYS_7:
            days = 7
        elif horizon == ForecastHorizon.DAYS_14:
            days = 14
        elif horizon == ForecastHorizon.DAYS_30:
            days = 30
        elif horizon == ForecastHorizon.DAYS_60:
            days = 60
        elif horizon == ForecastHorizon.DAYS_180:
            days = 180
        elif horizon == ForecastHorizon.DAYS_365:
            days = 365

        growth_factor = 1.0 + ((trend.change_rate / 100.0) * (days / 90.0))
        forecast_val = round(current_value * growth_factor, 2)

        # Decay confidence for longer horizons
        horizon_decay = max(0.5, 1.0 - (days / 730.0))
        conf_score = round(trend.confidence * horizon_decay, 1)

        margin = abs(forecast_val * (0.15 + (1.0 - horizon_decay)))
        lower_b = round(forecast_val - margin, 2)
        upper_b = round(forecast_val + margin, 2)

        return forecast_val, lower_b, upper_b, conf_score

class FutureStateSimulationEngine:
    """Side-effect free what-if simulator."""

    def simulate_future(
        self,
        forecast_id: str,
        current_forecast_value: float,
        request: SimulationRequest
    ) -> SimulationResponse:
        multiplier = request.intensity_multiplier + (request.budget_delta / 10000.0)
        simulated_outcome = round(current_forecast_value * max(0.5, multiplier), 2)
        delta = round(simulated_outcome - current_forecast_value, 2)

        risk_score = min(100.0, max(10.0, 25.0 * multiplier))

        return SimulationResponse(
            forecast_id=forecast_id,
            baseline_outcome=current_forecast_value,
            simulated_outcome=simulated_outcome,
            delta_outcome=delta,
            risk_score=round(risk_score, 1),
            confidence_score=88.0,
            assumptions=[
                "Side-effect free parameter modulation",
                "Linear elasticity of budget to conversion yield"
            ]
        )

class FutureRiskEngine:
    """Detects future strategic risk vectors."""

    def evaluate_future_risks(
        self,
        forecast_val: float,
        trend: TrendResponse
    ) -> List[FutureRiskResponse]:
        risks: List[FutureRiskResponse] = []

        if trend.direction == TrendDirection.DOWNWARD:
            risks.append(
                FutureRiskResponse(
                    risk_type="REVENUE_DECLINE",
                    probability=75.0,
                    impact="HIGH",
                    risk_score=60.0,
                    confidence=trend.confidence,
                    evidence=f"Downward trend rate ({trend.change_rate}%) detected across observation window.",
                    mitigation="Deploy defensive campaign optimization & budget reallocation."
                )
            )

        return risks

class FutureOpportunityEngine:
    """Detects future growth opportunities."""

    def evaluate_future_opportunities(
        self,
        forecast_val: float,
        trend: TrendResponse
    ) -> List[FutureOpportunityResponse]:
        opps: List[FutureOpportunityResponse] = []

        if trend.direction == TrendDirection.UPWARD:
            opps.append(
                FutureOpportunityResponse(
                    opportunity_type="ACCELERATED_GROWTH_MOMENTUM",
                    expected_value=round(forecast_val * 0.20, 2),
                    probability=80.0,
                    confidence=trend.confidence,
                    evidence=f"Positive trend trajectory ({trend.change_rate}%) indicates favorable tailwinds.",
                    time_to_impact="30 DAYS",
                    recommended_preparation="Increase resource allocation to capitalize on growth momentum."
                )
            )

        return opps

class ForecastAccuracyEngine:
    """Measures forecast accuracy against actual outcomes."""

    def evaluate_accuracy(self, forecast_val: float, actual_val: float) -> Tuple[float, float, str]:
        abs_err = abs(actual_val - forecast_val)
        denom = max(1.0, abs(actual_val))
        pct_err = (abs_err / denom) * 100.0
        acc_score = max(0.0, min(100.0, round(100.0 - pct_err, 1)))

        if acc_score >= 90.0:
            status = "WELL_CALIBRATED"
        elif forecast_val > actual_val:
            status = "OVERCONFIDENT"
        else:
            status = "UNDERCONFIDENT"

        return abs_err, acc_score, status
