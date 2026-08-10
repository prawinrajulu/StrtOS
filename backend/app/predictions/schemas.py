from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.predictions.models import ScenarioType, PredictionStatus
from app.governance.models import RiskLevel

class PredictionCreate(BaseModel):
    client_id: Optional[str] = None
    workflow_id: Optional[str] = None
    report_id: Optional[str] = None
    approval_id: Optional[str] = None
    scenario_type: ScenarioType = ScenarioType.BALANCED
    scenario_name: str = Field(..., min_length=2, max_length=150)
    objective: Optional[str] = None
    metric_name: str = Field(default="ROAS", min_length=2, max_length=100)
    predicted_value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    unit: str = Field(default="x", max_length=20)
    currency: str = Field(default="USD", max_length=10)
    confidence_score: float = Field(default=85.0, ge=0.0, le=100.0)
    risk_score: float = Field(default=45.0, ge=0.0, le=100.0)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    evidence_count: int = 0
    memory_count: int = 0
    provider: Optional[str] = None
    model: Optional[str] = None
    assumptions: Optional[List[str]] = None
    evidence_references: Optional[List[Dict[str, Any]]] = None
    memory_references: Optional[List[Dict[str, Any]]] = None
    extra_metadata: Optional[Dict[str, Any]] = None

class PredictionResponse(BaseModel):
    id: str
    organization_id: str
    client_id: Optional[str] = None
    workflow_id: Optional[str] = None
    report_id: Optional[str] = None
    approval_id: Optional[str] = None
    scenario_id: Optional[str] = None
    scenario_type: ScenarioType
    scenario_name: str
    objective: Optional[str] = None
    metric_name: str
    predicted_value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    unit: str
    currency: str
    confidence_score: float
    risk_score: float
    risk_level: RiskLevel
    evidence_count: int
    memory_count: int
    provider: Optional[str] = None
    model: Optional[str] = None
    assumptions: Optional[List[str]] = None
    evidence_references: Optional[List[Dict[str, Any]]] = None
    memory_references: Optional[List[Dict[str, Any]]] = None
    prediction_status: PredictionStatus
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    valid_from: datetime
    valid_until: Optional[datetime] = None
    extra_metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class PredictionListResponse(BaseModel):
    predictions: List[PredictionResponse]
    total: int
    page: int
    page_size: int

class ScenarioGenerateRequest(BaseModel):
    client_id: Optional[str] = None
    workflow_id: Optional[str] = None
    metric_name: str = Field(default="ROAS", min_length=2, max_length=100)
    monthly_budget: float = Field(default=10000.0, ge=0.0)
    timeline_days: int = Field(default=90, ge=7, le=365)
    objective: Optional[str] = None

class ScenarioListResponse(BaseModel):
    scenarios: List[PredictionResponse]
    recommended_scenario_type: ScenarioType
    summary: str

class WhatIfSimulationRequest(BaseModel):
    client_id: Optional[str] = None
    metric_name: str = Field(default="ROAS", min_length=2, max_length=100)
    current_budget: float = Field(..., ge=0.0)
    simulated_budget: float = Field(..., ge=0.0)
    timeline_days: int = Field(default=90, ge=7, le=365)

class WhatIfSimulationResponse(BaseModel):
    baseline: Dict[str, Any]
    simulated_scenario: Dict[str, Any]
    delta: Dict[str, Any]
    confidence_score: float
    risk_score: float
    risk_level: RiskLevel
    assumptions: List[str]

class AccuracyAssessmentResponse(BaseModel):
    prediction_id: str
    metric_name: str
    predicted_value: float
    actual_value: float
    unit: str
    absolute_error: float
    percentage_error: float
    accuracy_score: float
    accuracy_status: str
    lesson_summary: Optional[str] = None
