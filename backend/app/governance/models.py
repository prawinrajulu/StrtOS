import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ApprovalStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class DecisionType(str, enum.Enum):
    WORKFLOW_EXECUTION = "WORKFLOW_EXECUTION"
    CAMPAIGN_LAUNCH = "CAMPAIGN_LAUNCH"
    BUDGET_CHANGE = "BUDGET_CHANGE"
    STRATEGY_CHANGE = "STRATEGY_CHANGE"
    REPORT_PUBLICATION = "REPORT_PUBLICATION"
    OTHER = "OTHER"

class ApprovalRequestModel(Base):
    __tablename__ = "approval_requests"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    workflow_id = Column(String, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=True, index=True)
    client_id = Column(String, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True)
    report_id = Column(String, ForeignKey("reports.id", ondelete="SET NULL"), nullable=True, index=True)
    requested_by = Column(String, nullable=False, index=True)
    reviewed_by = Column(String, nullable=True, index=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    decision_type = Column(SQLEnum(DecisionType), default=DecisionType.WORKFLOW_EXECUTION, nullable=False)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.MEDIUM, nullable=False, index=True)
    risk_score = Column(Float, default=50.0)
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING_APPROVAL, nullable=False, index=True)
    requested_action = Column(Text, nullable=True)
    
    ai_recommendation = Column(Text, nullable=True)
    ai_confidence_score = Column(Float, default=95.0)
    evidence_count = Column(Integer, default=0)
    provider = Column(String, nullable=True)
    model = Column(String, nullable=True)
    
    requested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewer_comment = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    extra_metadata = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
