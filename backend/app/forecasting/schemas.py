from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.forecasting.models import ForecastType, ForecastHorizon, ForecastStatus, TrendDirection

class ForecastMetricCreate(BaseModel):
    metric_name: str
    current_value: float
    forecast_value: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    unit: str = "USD"
    confidence_score: float = 85.0

class ForecastMetricResponse(BaseModel):
    id: str
    organization_id: str
    forecast_id: str
    metric_name: str
    current_value: float
    forecast_value: Optional[float] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    unit: str
    confidence_score: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ForecastScenarioResponse(BaseModel):
    id: str
    organization_id: str
    forecast_id: str
    scenario_type: str
    expected_outcome: float
    lower_bound: float
    upper_bound: float
    confidence_score: float
    risk_score: float
    required_budget: float
    time_to_impact_days: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ForecastImpactResponse(BaseModel):
    id: str
    organization_id: str
    forecast_id: str
    objective_id: Optional[str] = None
    financial_impact: float
    customer_impact: float
    timeline_impact_days: int
    risk_level: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ForecastEvaluationResponse(BaseModel):
    id: str
    organization_id: str
    forecast_id: str
    actual_value: float
    forecast_value: float
    absolute_error: float
    accuracy_score: float
    calibration_status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ForecastCreate(BaseModel):
    forecast_type: ForecastType = ForecastType.BUSINESS_HEALTH
    horizon: ForecastHorizon = ForecastHorizon.DAYS_90
    title: str
    metrics: List[ForecastMetricCreate] = []

class ForecastResponse(BaseModel):
    id: str
    organization_id: str
    forecast_type: ForecastType
    horizon: ForecastHorizon
    status: ForecastStatus
    title: str
    summary: Optional[str] = None
    confidence_score: float
    trend_direction: TrendDirection
    created_at: datetime
    metrics: List[ForecastMetricResponse] = []
    scenarios: List[ForecastScenarioResponse] = []
    impacts: List[ForecastImpactResponse] = []
    evaluations: List[ForecastEvaluationResponse] = []
    model_config = ConfigDict(from_attributes=True)

class TrendResponse(BaseModel):
    direction: TrendDirection
    strength: float
    change_rate: float
    acceleration: float
    confidence: float

class SimulationRequest(BaseModel):
    budget_delta: float = 0.0
    timeline_days_delta: int = 0
    intensity_multiplier: float = 1.0

class SimulationResponse(BaseModel):
    forecast_id: str
    baseline_outcome: float
    simulated_outcome: float
    delta_outcome: float
    risk_score: float
    confidence_score: float
    assumptions: List[str]

class FutureRiskResponse(BaseModel):
    risk_type: str
    probability: float
    impact: str
    risk_score: float
    confidence: float
    evidence: str
    mitigation: str

class FutureOpportunityResponse(BaseModel):
    opportunity_type: str
    expected_value: float
    probability: float
    confidence: float
    evidence: str
    time_to_impact: str
    recommended_preparation: str
