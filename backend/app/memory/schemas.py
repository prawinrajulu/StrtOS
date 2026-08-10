from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.memory.models import MemoryType, OutcomeStatus

class MemoryRecordCreate(BaseModel):
    client_id: Optional[str] = None
    workflow_id: Optional[str] = None
    report_id: Optional[str] = None
    approval_id: Optional[str] = None
    memory_type: MemoryType = MemoryType.CLIENT_CONTEXT
    title: str = Field(..., min_length=2, max_length=200)
    content: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    source: Optional[str] = "system"
    source_type: Optional[str] = "internal"
    confidence_score: float = Field(default=90.0, ge=0.0, le=100.0)
    importance_score: float = Field(default=50.0, ge=0.0, le=100.0)
    outcome_status: OutcomeStatus = OutcomeStatus.UNKNOWN
    occurred_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    extra_metadata: Optional[Dict[str, Any]] = None

class MemoryRecordUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    content: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    importance_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    outcome_status: Optional[OutcomeStatus] = None

class MemoryRecordResponse(BaseModel):
    id: str
    organization_id: str
    client_id: Optional[str] = None
    workflow_id: Optional[str] = None
    report_id: Optional[str] = None
    approval_id: Optional[str] = None
    memory_type: MemoryType
    title: str
    content: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    source_type: Optional[str] = None
    confidence_score: float
    importance_score: float
    outcome_status: OutcomeStatus
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    occurred_at: datetime
    expires_at: Optional[datetime] = None
    extra_metadata: Optional[Dict[str, Any]] = None
    relevance_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class MemoryListResponse(BaseModel):
    memories: List[MemoryRecordResponse]
    total: int
    page: int
    page_size: int

class OutcomeSubmissionRequest(BaseModel):
    client_id: Optional[str] = None
    workflow_id: Optional[str] = None
    metric_name: str = Field(..., min_length=2, max_length=100)
    predicted_value: float
    actual_value: float
    unit: str = Field(default="ROAS", max_length=20)
    measurement_period: Optional[str] = Field(default="30_DAYS", max_length=50)
    notes: Optional[str] = None

class OutcomeResponse(BaseModel):
    outcome_memory_id: str
    lesson_memory_id: Optional[str] = None
    metric_name: str
    predicted_value: float
    actual_value: float
    unit: str
    absolute_variance: float
    percentage_variance: float
    outcome_status: OutcomeStatus
    lesson_summary: Optional[str] = None
