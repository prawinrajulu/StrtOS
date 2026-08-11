from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.strategy.models import ObjectiveLifecycle, HorizonType, ScenarioType

class OrganizationScopedBase(BaseModel):
    organization_id: Optional[str] = None

# Strategic Metric Schemas
class StrategicMetricCreate(BaseModel):
    metric_name: str
    baseline: float = 0.0
    target: float = 0.0
    unit: str = "USD"

class StrategicMetricResponse(BaseModel):
    id: str
    organization_id: str
    objective_id: str
    metric_name: str
    baseline: float
    target: float
    actual: Optional[float] = None
    unit: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Strategic Constraint Schemas
class StrategicConstraintCreate(BaseModel):
    constraint_type: str  # Budget, Timeline, Capacity, Risk, Policy
    limit_value: float
    current_usage: float = 0.0
    is_hard_constraint: bool = True
    description: Optional[str] = None

class StrategicConstraintResponse(BaseModel):
    id: str
    organization_id: str
    objective_id: str
    constraint_type: str
    limit_value: float
    current_usage: float
    is_hard_constraint: bool
    description: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Strategic Objective Schemas
class StrategicObjectiveCreate(OrganizationScopedBase):
    title: str
    description: Optional[str] = None
    category: str = "Growth"
    target_horizon: HorizonType = HorizonType.DAYS_90
    baseline_value: float = 0.0
    target_value: float = 100.0
    unit: str = "USD"

class StrategicObjectiveResponse(BaseModel):
    id: str
    organization_id: str
    title: str
    description: Optional[str] = None
    category: str
    status: ObjectiveLifecycle
    target_horizon: HorizonType
    baseline_value: float
    target_value: float
    current_value: float
    unit: str
    confidence_score: float
    risk_level: str
    created_at: datetime
    updated_at: datetime
    metrics: List[StrategicMetricResponse] = []
    constraints: List[StrategicConstraintResponse] = []
    model_config = ConfigDict(from_attributes=True)

# Strategic Milestone Schemas
class StrategicMilestoneResponse(BaseModel):
    id: str
    organization_id: str
    plan_id: str
    title: str
    horizon_day: int
    target_metric_value: float
    actual_metric_value: Optional[float] = None
    status: str
    expected_outcome: Optional[str] = None
    confidence_score: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Strategic Plan & Version Schemas
class StrategicPlanVersionResponse(BaseModel):
    id: str
    organization_id: str
    plan_id: str
    version: str
    parent_version: Optional[str] = None
    change_reason: str
    performance_before: float
    performance_after: float
    risk_before: float
    risk_after: float
    created_by: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StrategicPlanCreate(OrganizationScopedBase):
    objective_id: str
    title: str
    scenario_type: ScenarioType = ScenarioType.BALANCED
    horizon: HorizonType = HorizonType.DAYS_90

class StrategicPlanResponse(BaseModel):
    id: str
    organization_id: str
    objective_id: str
    version: str
    scenario_type: ScenarioType
    title: str
    summary: Optional[str] = None
    horizon: HorizonType
    expected_value: float
    confidence_score: float
    risk_score: float
    risk_level: str
    status: str
    action_plan_id: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    milestones: List[StrategicMilestoneResponse] = []
    versions: List[StrategicPlanVersionResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ScenarioResponse(BaseModel):
    scenario_type: ScenarioType
    expected_value: float
    confidence_score: float
    risk_score: float
    risk_level: str
    cost: float
    time_to_impact_days: int
    resource_requirement: str
    dependency_count: int
    upside_potential: str
    downside_risk: str

class StrategyEvaluationResponse(BaseModel):
    plan_id: str
    objective_id: str
    is_valid: bool
    evaluation_status: str
    violated_constraints: List[str] = []
    risk_score: float
    risk_level: str
    recommendation: str

class StrategyAdaptationRequest(OrganizationScopedBase):
    actual_performance: float
    adaptation_reason: str

class StrategyAdaptationResponse(BaseModel):
    plan_id: str
    new_version: str
    previous_performance: float
    new_performance_target: float
    adaptation_delta_pct: float
    bounded: bool
    message: str

class StrategyExplanationResponse(BaseModel):
    plan_id: str
    why_objective: str
    why_target: str
    why_horizon: str
    why_scenario: str
    why_risk_score: str
    evidence_sources: List[Dict[str, Any]] = []
    memory_references: List[Dict[str, Any]] = []
    assumptions: List[str] = []
    invalidation_factors: List[str] = []
