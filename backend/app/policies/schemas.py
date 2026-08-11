from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.policies.models import PolicyStatus

class PolicyBase(BaseModel):
    agent_name: str = Field(..., description="Name of target specialist agent")
    policy_name: str = Field(..., description="Human-readable policy name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Strategy parameters")
    change_reason: Optional[str] = Field(None, description="Reason for policy creation/change")

class PolicyCreate(PolicyBase):
    pass

class PolicyVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    policy_id: str
    organization_id: str
    agent_name: str
    version: str
    status: PolicyStatus
    parameters: Dict[str, Any]
    performance_score: float
    confidence_score: float
    risk_score: float
    adaptation_delta: float
    parent_version: Optional[str] = None
    change_reason: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    created_at: datetime
    activated_at: Optional[datetime] = None
    retired_at: Optional[datetime] = None

class PolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    agent_name: str
    policy_name: str
    current_version: str
    status: PolicyStatus
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    active_version: Optional[PolicyVersionResponse] = None

class PolicyEvaluationInput(BaseModel):
    predicted_kpi: float = Field(..., description="Predicted KPI value")
    actual_kpi: float = Field(..., description="Actual outcome KPI value")
    prediction_accuracy: float = Field(default=80.0, ge=0.0, le=100.0)
    confidence: float = Field(default=85.0, ge=0.0, le=100.0)
    outcome_status: str = Field(default="SUCCESS")
    agent_execution_success: bool = Field(default=True)
    evidence_quality: float = Field(default=85.0, ge=0.0, le=100.0)
    sample_count: int = Field(default=1, ge=1)

class PolicyEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    policy_id: str
    version: str
    agent_name: str
    accuracy_score: float
    reliability_score: float
    outcome_score: float
    confidence_score: float
    evidence_score: float
    overall_policy_score: float
    sample_count: int
    evaluated_at: datetime

class PolicyOptimizeRequest(BaseModel):
    target_performance_score: float = Field(default=90.0, ge=0.0, le=100.0)
    proposed_parameters: Optional[Dict[str, Any]] = Field(None, description="Optional custom parameter adjustments")
    reason: Optional[str] = Field(None, description="Context or trigger reason for optimization")

class PolicyOptimizeResponse(BaseModel):
    status: str  # CANDIDATE_CREATED, REJECTED
    reason: Optional[str] = None
    candidate_version: Optional[PolicyVersionResponse] = None
    expected_improvement: Optional[float] = None
    risk_level: Optional[str] = None
    governance_approval_id: Optional[str] = None

class PolicyRollbackRequest(BaseModel):
    target_version: Optional[str] = Field(None, description="Specific target version to rollback to, defaults to previous known-good")
    reason: str = Field(..., description="Mandatory reason for rollback")

class PolicyRollbackResponse(BaseModel):
    status: str
    policy_id: str
    active_version: str
    previous_version: str
    reason: str
    rolled_back_at: datetime

class AgentPerformanceMetricItem(BaseModel):
    agent_name: str
    current_policy_version: str
    performance_score: float
    accuracy_score: float
    reliability_score: float
    success_rate: float
    sample_count: int
    trend: str  # IMPROVING, STABLE, DEGRADING
    last_evaluated_at: datetime

class PolicyAnalyticsResponse(BaseModel):
    total_policies: int
    active_policies: int
    candidate_policies: int
    average_policy_score: float
    policy_improvement_percent: float
    total_rollbacks: int
    governance_pending_count: int
    agents_performance: List[AgentPerformanceMetricItem]
