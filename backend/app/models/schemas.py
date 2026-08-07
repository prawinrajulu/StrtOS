from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class StatusType(str, Enum):
    THINKING = "THINKING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    WAITING = "WAITING"
    IDLE = "IDLE"

class PriorityType(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Task(BaseModel):
    task_id: str
    title: str
    priority: PriorityType
    agent_name: str
    status: StatusType = StatusType.WAITING
    eta: str
    dependencies: List[str] = Field(default_factory=list)
    confidence: float = 0.90
    retry_count: int = 0
    max_retries: int = 1
    result_summary: Optional[str] = None

class DirectiveRequest(BaseModel):
    directive: str
    client_name: str = "Arcadia Ventures"
    client_type: str = "D2C SKINCARE"

class WorkflowStage(BaseModel):
    id: str
    name: str
    agent_name: str
    status: StatusType = StatusType.WAITING

class ExecutionState(BaseModel):
    workflow_id: str
    client_name: str
    current_thought: str
    overall_confidence: int = 92
    stages: List[WorkflowStage] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    completed_count: int = 0
    running_count: int = 0
    waiting_count: int = 0
    is_active: bool = True

class SpecialistOutput(BaseModel):
    agent_name: str
    title: str
    findings: List[str]
    metrics: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.95
    warning: Optional[str] = None

class ExecutiveReport(BaseModel):
    workflow_id: str
    client_name: str
    directive: str
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    overall_confidence: int
    business_summary: SpecialistOutput
    seo_summary: SpecialistOutput
    competitor_summary: SpecialistOutput
    marketing_summary: SpecialistOutput
    campaign_summary: SpecialistOutput
    analytics_summary: SpecialistOutput
    ceo_final_recommendations: List[str]
