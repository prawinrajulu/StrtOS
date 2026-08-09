from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum

class ClientStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"

class ClientCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    industry: str = Field(..., min_length=2, max_length=100)
    website_url: Optional[str] = None
    description: Optional[str] = None
    business_goal: Optional[str] = None
    monthly_budget: Optional[float] = 0.0
    currency: Optional[str] = "USD"
    status: Optional[ClientStatusEnum] = ClientStatusEnum.ACTIVE
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class ClientUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    industry: Optional[str] = Field(None, min_length=2, max_length=100)
    website_url: Optional[str] = None
    description: Optional[str] = None
    business_goal: Optional[str] = None
    monthly_budget: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[ClientStatusEnum] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

class ClientDTO(BaseModel):
    id: str
    organization_id: str
    name: str
    industry: str
    website_url: Optional[str] = None
    description: Optional[str] = None
    business_goal: Optional[str] = None
    monthly_budget: Optional[float] = 0.0
    currency: str = "USD"
    status: str = "ACTIVE"
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    created_by: Optional[str] = None
    health_score: int = 90
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ClientListResponse(BaseModel):
    clients: List[ClientDTO]
    total: int
    page: int
    page_size: int
