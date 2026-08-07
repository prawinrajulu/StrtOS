from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class TaskStatus(str, Enum):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"

class WorkflowStatus(str, Enum):
    CREATED = "CREATED"
    STARTED = "STARTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class PriorityLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class StructuredIntent(BaseModel):
    directive: str
    business_type: str
    industry: str
    primary_goal: str
    priority: PriorityLevel = PriorityLevel.HIGH
    urgency: str = "NORMAL"
    target_audience: str = "GENERAL"

class WorkflowDecision(BaseModel):
    workflow_type: str
    required_agents: List[str]
    execution_order: List[List[str]]  # Supports parallel stages as lists
    priority: PriorityLevel = PriorityLevel.HIGH
    estimated_duration_minutes: int = 15
    risk_assessment: str = "LOW"
    confidence_score: float = 95.0

class CEOTaskItem(BaseModel):
    task_id: str
    title: str
    agent_name: str
    priority: PriorityLevel = PriorityLevel.HIGH
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.WAITING
    retry_count: int = 0
    max_retries: int = 2
    eta: str = "ETA 2 MIN"
    result: Optional[Dict[str, Any]] = None

class WorkflowState(BaseModel):
    workflow_id: str
    client_name: str
    directive: str
    intent: Optional[StructuredIntent] = None
    decision: Optional[WorkflowDecision] = None
    current_thought: str = "Initializing CEO Decision Pipeline..."
    overall_confidence: float = 92.0
    status: WorkflowStatus = WorkflowStatus.CREATED
    stages: List[Dict[str, Any]] = Field(default_factory=list)
    tasks: List[CEOTaskItem] = Field(default_factory=list)
    agent_outputs: Dict[str, Any] = Field(default_factory=dict)
    completed_count: int = 0
    running_count: int = 0
    waiting_count: int = 0
    is_completed: bool = False
    executive_report: Optional[Dict[str, Any]] = None
