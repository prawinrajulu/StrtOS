from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.execution.models import AutonomyMode, PolicyDecision, ActionStatus
from app.governance.models import RiskLevel

class ActionCreate(BaseModel):
    client_id: Optional[str] = None
    workflow_id: Optional[str] = None
    prediction_id: Optional[str] = None
    approval_id: Optional[str] = None
    action_type: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    autonomy_mode: AutonomyMode = AutonomyMode.APPROVAL_REQUIRED
    input_payload: Optional[Dict[str, Any]] = None
    idempotency_key: Optional[str] = None
    max_retries: int = Field(default=3, ge=0, le=10)
    extra_metadata: Optional[Dict[str, Any]] = None

class ActionResponse(BaseModel):
    id: str
    organization_id: str
    client_id: Optional[str] = None
    workflow_id: Optional[str] = None
    prediction_id: Optional[str] = None
    approval_id: Optional[str] = None
    created_by: Optional[str] = None
    action_type: str
    name: str
    description: Optional[str] = None
    status: ActionStatus
    risk_level: RiskLevel
    autonomy_mode: AutonomyMode
    policy_decision: PolicyDecision
    input_payload: Optional[Dict[str, Any]] = None
    validated_payload: Optional[Dict[str, Any]] = None
    output_payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int
    max_retries: int
    idempotency_key: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    extra_metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class ActionListResponse(BaseModel):
    actions: List[ActionResponse]
    total: int
    page: int
    page_size: int

class ActionEvaluateResponse(BaseModel):
    action_id: str
    action_type: str
    policy_decision: PolicyDecision
    required_approval: bool
    allowed_execution: bool
    explanation: str

class ActionExecutePayload(BaseModel):
    force_retry: bool = False

class OutcomeMeasurementRequest(BaseModel):
    actual_metric_value: float = Field(..., description="Actual performance KPI value")

class ClosedLoopOptimizationResponse(BaseModel):
    action_id: str
    prediction_id: Optional[str] = None
    metric_name: str
    predicted_value: float
    actual_value: float
    accuracy_score: float
    percentage_error: float
    outcome_status: str
    lesson_memory_id: str
    lesson_summary: str
