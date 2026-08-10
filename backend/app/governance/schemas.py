from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.governance.models import ApprovalStatus, RiskLevel, DecisionType

class ApprovalRequestCreate(BaseModel):
    workflow_id: Optional[str] = None
    client_id: Optional[str] = None
    report_id: Optional[str] = None
    title: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None
    decision_type: DecisionType = DecisionType.WORKFLOW_EXECUTION
    requested_action: Optional[str] = None
    ai_recommendation: Optional[str] = None
    ai_confidence_score: float = Field(default=95.0, ge=0.0, le=100.0)
    evidence_count: int = 0
    provider: Optional[str] = None
    model: Optional[str] = None
    is_reversible: bool = True
    has_unavailable_evidence: bool = False
    extra_metadata: Optional[Dict[str, Any]] = None

class ApprovalRequestUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    requested_action: Optional[str] = None

class ApprovalActionRequest(BaseModel):
    comment: Optional[str] = None
    rejection_reason: Optional[str] = None

class ApprovalResponse(BaseModel):
    id: str
    organization_id: str
    workflow_id: Optional[str] = None
    client_id: Optional[str] = None
    report_id: Optional[str] = None
    requested_by: str
    reviewed_by: Optional[str] = None
    title: str
    description: Optional[str] = None
    decision_type: DecisionType
    risk_level: RiskLevel
    risk_score: float
    status: ApprovalStatus
    requested_action: Optional[str] = None
    ai_recommendation: Optional[str] = None
    ai_confidence_score: float
    evidence_count: int
    provider: Optional[str] = None
    model: Optional[str] = None
    requested_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer_comment: Optional[str] = None
    rejection_reason: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ApprovalListResponse(BaseModel):
    approvals: List[ApprovalResponse]
    total: int
    page: int
    page_size: int

class RiskAssessmentResponse(BaseModel):
    risk_level: RiskLevel
    risk_score: float
    reasons: List[str]
