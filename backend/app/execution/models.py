import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, Enum as SQLEnum, ForeignKey
from app.core.database import Base
from app.governance.models import RiskLevel

def generate_uuid():
    return str(uuid.uuid4())

class AutonomyMode(str, Enum):
    MANUAL = "MANUAL"
    ASSISTED = "ASSISTED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    AUTONOMOUS = "AUTONOMOUS"

class PolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    EXPIRED = "EXPIRED"

class ActionStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_POLICY = "PENDING_POLICY"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ROLLED_BACK = "ROLLED_BACK"
    EXPIRED = "EXPIRED"
    DEGRADED = "DEGRADED"

class ActionModel(Base):
    """
    Production-grade Autonomous Execution Action Model tracking action proposals,
    policy evaluation decisions, autonomy modes, tool execution payloads, and state transitions.
    """
    __tablename__ = "actions"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String, ForeignKey("clients.id", ondelete="CASCADE"), nullable=True, index=True)
    workflow_id = Column(String, ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True, index=True)
    prediction_id = Column(String, ForeignKey("predictions.id", ondelete="SET NULL"), nullable=True, index=True)
    approval_id = Column(String, ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True, index=True)
    created_by = Column(String, nullable=True)

    action_type = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    status = Column(SQLEnum(ActionStatus), default=ActionStatus.DRAFT, nullable=False, index=True)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.LOW, nullable=False)
    autonomy_mode = Column(SQLEnum(AutonomyMode), default=AutonomyMode.APPROVAL_REQUIRED, nullable=False)
    policy_decision = Column(SQLEnum(PolicyDecision), default=PolicyDecision.REQUIRE_APPROVAL, nullable=False)

    input_payload = Column(JSON, nullable=True)
    validated_payload = Column(JSON, nullable=True)
    output_payload = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    idempotency_key = Column(String, nullable=True, index=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    extra_metadata = Column(JSON, nullable=True)
