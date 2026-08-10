import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, JSON, Enum as SQLEnum, ForeignKey
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class MemoryType(str, Enum):
    CLIENT_CONTEXT = "CLIENT_CONTEXT"
    DECISION = "DECISION"
    STRATEGY = "STRATEGY"
    APPROVAL = "APPROVAL"
    WORKFLOW = "WORKFLOW"
    OUTCOME = "OUTCOME"
    FEEDBACK = "FEEDBACK"
    LESSON = "LESSON"

class OutcomeStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"

class MemoryRecordModel(Base):
    """
    Unified Production Memory Record storing historical client context, executive decisions,
    strategy recommendations, approval events, measured outcomes, and lessons learned.
    """
    __tablename__ = "memory_records"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String, ForeignKey("clients.id", ondelete="CASCADE"), nullable=True, index=True)
    workflow_id = Column(String, ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True, index=True)
    report_id = Column(String, ForeignKey("reports.id", ondelete="SET NULL"), nullable=True)
    approval_id = Column(String, ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True)

    memory_type = Column(SQLEnum(MemoryType), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    structured_data = Column(JSON, nullable=True)

    source = Column(String, nullable=True)
    source_type = Column(String, nullable=True)
    confidence_score = Column(Float, default=90.0)
    importance_score = Column(Float, default=50.0, index=True)
    outcome_status = Column(SQLEnum(OutcomeStatus), default=OutcomeStatus.UNKNOWN, nullable=False)

    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    occurred_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)

    extra_metadata = Column(JSON, nullable=True)
