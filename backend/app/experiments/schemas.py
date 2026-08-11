from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.experiments.models import ExperimentStatus, ExperimentResult, VariantType

class ExperimentBase(BaseModel):
    experiment_name: str = Field(..., description="Human readable experiment title")
    objective: str = Field(..., description="Business goal for experiment")
    hypothesis: str = Field(..., description="Tested hypothesis")
    metric_name: str = Field(default="conversion_rate")
    baseline_value: float = Field(default=0.0)
    target_value: float = Field(default=10.0)
    minimum_detectable_effect: float = Field(default=5.0, description="Minimum % change needed")
    confidence_threshold: float = Field(default=95.0, description="Target confidence %")

class ExperimentCreate(ExperimentBase):
    client_id: Optional[str] = None
    workflow_id: Optional[str] = None
    prediction_id: Optional[str] = None
    baseline_policy_id: str = Field(..., description="ID of active control policy")
    variant_policy_id: str = Field(..., description="ID of proposed variant policy")

class ExperimentDesignRequest(BaseModel):
    available_sample_size: int = Field(default=100)
    measurement_window_days: int = Field(default=14)
    max_budget_impact_percent: float = Field(default=10.0)

class ExperimentVariantSchema(BaseModel):
    id: str
    experiment_id: str
    organization_id: str
    variant_type: VariantType
    variant_name: str
    policy_id: str
    configuration: Dict[str, Any]
    sample_size: int
    success_count: int
    failure_count: int
    average_kpi: float
    average_latency_ms: float
    average_cost: float
    average_confidence: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ExperimentMeasurementCreate(BaseModel):
    execution_id: str
    kpi_value: float = Field(default=0.0)
    success: bool = Field(default=True)
    confidence: float = Field(default=80.0)
    latency_ms: float = Field(default=0.0)
    cost: float = Field(default=0.0)
    human_approved: bool = Field(default=True)
    prediction_error: float = Field(default=0.0)
    metadata_json: Optional[Dict[str, Any]] = None

class ExperimentMeasurementSchema(BaseModel):
    id: str
    experiment_id: str
    variant_id: str
    organization_id: str
    execution_id: str
    variant_type: VariantType
    kpi_value: float
    success: int
    confidence: float
    latency_ms: float
    cost: float
    human_approved: int
    prediction_error: float
    metadata_json: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ExperimentSchema(ExperimentBase):
    id: str
    organization_id: str
    client_id: Optional[str]
    workflow_id: Optional[str]
    prediction_id: Optional[str]
    baseline_policy_id: Optional[str]
    variant_policy_id: Optional[str]
    control_sample_size: int
    variant_sample_size: int
    status: ExperimentStatus
    result: ExperimentResult
    winner: Optional[VariantType]
    confidence: float
    created_by: Optional[str]
    approved_by: Optional[str]
    approval_id: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ExperimentEvaluationSchema(BaseModel):
    experiment_id: str
    metric_name: str
    control_sample_size: int
    variant_sample_size: int
    control_mean_kpi: float
    variant_mean_kpi: float
    absolute_difference: float
    percentage_improvement: float
    confidence_level: float
    statistically_significant: bool
    result: ExperimentResult
    winner: Optional[VariantType]
    recommendation: str
    details: Dict[str, Any]

class OptimizationProposalSchema(BaseModel):
    experiment_id: str
    organization_id: str
    winning_variant: VariantType
    baseline_policy_id: str
    winning_policy_id: str
    proposed_new_policy_version: str
    confidence: float
    improvement_percent: float
    requires_governance: bool
    status: str
