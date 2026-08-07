from typing import Optional, List, Any, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

T = TypeVar("T")

# Base API Response Wrappers
class ResponseBase(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"

class SuccessResponse(ResponseBase, Generic[T]):
    data: Optional[T] = None

class ErrorResponse(ResponseBase):
    success: bool = False
    error_code: str
    details: Optional[dict] = None

# Organization Schemas
class OrganizationBase(BaseModel):
    name: str
    slug: str
    tier: str = "ENTERPRISE"

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationRead(OrganizationBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# User & Authentication Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "FOUNDER"

class UserCreate(UserBase):
    password: str
    organization_id: Optional[str] = None

class UserRead(UserBase):
    id: str
    organization_id: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Client Schemas
class ClientBase(BaseModel):
    name: str
    industry: str

class ClientCreate(ClientBase):
    organization_id: str

class ClientRead(ClientBase):
    id: str
    organization_id: str
    health_score: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Task Schemas
class TaskBase(BaseModel):
    title: str
    agent_name: str
    priority: str = "HIGH"
    status: str = "WAITING"
    eta: Optional[str] = None

class TaskCreate(TaskBase):
    workflow_id: str

class TaskRead(TaskBase):
    id: str
    workflow_id: str
    retry_count: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Workflow Schemas
class WorkflowBase(BaseModel):
    title: str
    status: str = "RUNNING"
    confidence_score: float = 92.0

class WorkflowCreate(WorkflowBase):
    client_id: str

class WorkflowRead(WorkflowBase):
    id: str
    client_id: str
    total_stages: int
    completed_stages: int
    created_at: datetime
    tasks: List[TaskRead] = []
    model_config = ConfigDict(from_attributes=True)

# Report Schemas
class ReportBase(BaseModel):
    title: str
    summary_json: Optional[dict] = None

class ReportCreate(ReportBase):
    workflow_id: str

class ReportRead(ReportBase):
    id: str
    workflow_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
