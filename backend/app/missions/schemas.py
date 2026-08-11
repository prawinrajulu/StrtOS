from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.missions.models import (
    MissionStatus, MissionStepStatus, MissionEvaluationStatus, MissionCheckpointDecision
)

class MissionSuccessCriterionCreate(BaseModel):
    metric_name: str
    baseline_value: float = 0.0
    target_value: float
    unit: str = "USD"

class MissionSuccessCriterionResponse(BaseModel):
    id: str
    organization_id: str
    mission_id: str
    metric_name: str
    baseline_value: float
    target_value: float
    current_value: float
    unit: str
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MissionStepResponse(BaseModel):
    id: str
    organization_id: str
    mission_id: str
    step_order: int
    title: str
    action_type: str
    status: MissionStepStatus
    dependencies_json: Optional[List[str]] = None
    risk_level: str
    autonomy_level: str
    result_summary: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MissionPlanVersionResponse(BaseModel):
    id: str
    organization_id: str
    mission_id: str
    version: str
    parent_version: Optional[str] = None
    adaptation_reason: Optional[str] = None
    delta_percentage: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MissionCheckpointResponse(BaseModel):
    id: str
    organization_id: str
    mission_id: str
    decision: MissionCheckpointDecision
    progress_at_checkpoint: float
    notes: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MissionCreate(BaseModel):
    title: str
    summary: Optional[str] = None
    objective_id: Optional[str] = None
    criteria: List[MissionSuccessCriterionCreate] = []

class MissionResponse(BaseModel):
    id: str
    organization_id: str
    objective_id: Optional[str] = None
    title: str
    summary: Optional[str] = None
    status: MissionStatus
    current_version: str
    progress_percentage: float
    risk_score: float
    confidence_score: float
    created_at: datetime
    updated_at: datetime
    criteria: List[MissionSuccessCriterionResponse] = []
    plans: List[MissionPlanVersionResponse] = []
    steps: List[MissionStepResponse] = []
    checkpoints: List[MissionCheckpointResponse] = []
    model_config = ConfigDict(from_attributes=True)

class MissionEvaluationResponse(BaseModel):
    mission_id: str
    status: MissionEvaluationStatus
    progress_percentage: float
    risk_score: float
    confidence_score: float
    summary: str

class MissionReplanRequest(BaseModel):
    reason: str
    adaptation_delta_percentage: float = Field(..., le=10.0, ge=0.0) # Bounded max 10%
