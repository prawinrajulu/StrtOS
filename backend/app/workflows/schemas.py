from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum

class WorkflowStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TaskStatusEnum(str, Enum):
    WAITING = "WAITING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class WorkflowCreateRequest(BaseModel):
    client_id: str
    title: str = Field(..., min_length=2, max_length=150)
    directive: Optional[str] = None

class WorkflowUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=150)
    directive: Optional[str] = None
    status: Optional[WorkflowStatusEnum] = None

class TaskDTO(BaseModel):
    id: str
    workflow_id: str
    organization_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    agent_name: str
    priority: str = "HIGH"
    status: str = "WAITING"
    dependencies: Optional[List[str]] = None
    eta: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkflowEventDTO(BaseModel):
    id: str
    workflow_id: str
    organization_id: Optional[str] = None
    event_type: str
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkflowDTO(BaseModel):
    id: str
    organization_id: str
    client_id: str
    created_by: Optional[str] = None
    title: str
    directive: Optional[str] = None
    status: str = "DRAFT"
    active_stage: Optional[str] = "INITIALIZATION"
    progress: int = 0
    confidence_score: float = 92.0
    total_stages: int = 9
    completed_stages: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkflowListResponse(BaseModel):
    workflows: List[WorkflowDTO]
    total: int
    page: int
    page_size: int
