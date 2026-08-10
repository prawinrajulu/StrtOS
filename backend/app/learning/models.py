import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON, Enum as SQLEnum, ForeignKey
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ReliabilityClass(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    MODERATE = "MODERATE"
    LOW = "LOW"
    CRITICAL = "CRITICAL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

class PolicyStatus(str, Enum):
    DRAFT = "DRAFT"
    TESTING = "TESTING"
    ACTIVE = "ACTIVE"
    ROLLED_BACK = "ROLLED_BACK"
    DEPRECATED = "DEPRECATED"

class AdaptationStatus(str, Enum):
    PROPOSED = "PROPOSED"
    PENDING_GOVERNANCE = "PENDING_GOVERNANCE"
    APPROVED = "APPROVED"
    ACTIVATED = "ACTIVATED"
    REJECTED = "REJECTED"
    ROLLED_BACK = "ROLLED_BACK"

class AgentPerformanceModel(Base):
    """
    Tracks performance telemetry and deterministic reliability scoring for specialist agents.
    """
    __tablename__ = "agent_performance"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String, ForeignKey("clients.id", ondelete="CASCADE"), nullable=True, index=True)

    agent_name = Column(String, nullable=False, index=True)
    agent_version = Column(String, default="1.0.0", nullable=False)

    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    degraded_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)

    average_confidence = Column(Float, default=80.0)
    average_latency_ms = Column(Float, default=0.0)
    average_token_usage = Column(Integer, default=0)

    prediction_accuracy = Column(Float, default=80.0)
    outcome_success_rate = Column(Float, default=80.0)
    human_approval_rate = Column(Float, default=90.0)
    human_rejection_rate = Column(Float, default=10.0)
    swarm_consensus_rate = Column(Float, default=85.0)
    tool_success_rate = Column(Float, default=95.0)
    evidence_quality_score = Column(Float, default=85.0)

    current_reliability_score = Column(Float, default=80.0)
    reliability_class = Column(SQLEnum(ReliabilityClass), default=ReliabilityClass.INSUFFICIENT_DATA, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ToolReliabilityModel(Base):
    """
    Tracks external tool reliability, availability, evidence quality, and latency metrics.
    """
    __tablename__ = "tool_reliability"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_name = Column(String, nullable=False, index=True)

    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    timeout_count = Column(Integer, default=0)

    average_latency_ms = Column(Float, default=0.0)
    availability_rate = Column(Float, default=100.0)
    evidence_quality = Column(Float, default=85.0)
    reliability_score = Column(Float, default=90.0)

    last_successful_execution = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class LLMProviderPerformanceModel(Base):
    """
    Tracks LLM provider latency, cost efficiency, structured output accuracy, and retries.
    """
    __tablename__ = "llm_provider_performance"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    provider = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False)
    agent_name = Column(String, nullable=True)

    average_latency_ms = Column(Float, default=0.0)
    average_token_usage = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)

    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    fallback_count = Column(Integer, default=0)

    structured_output_success_rate = Column(Float, default=95.0)
    confidence_score = Column(Float, default=90.0)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class AgentPolicyModel(Base):
    """
    Versioned Agent Policies ensuring deterministic, auditable, and reversible agent configurations.
    """
    __tablename__ = "agent_policies"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    agent_name = Column(String, nullable=False, index=True)
    policy_version = Column(String, nullable=False)
    configuration = Column(JSON, nullable=False)

    reason = Column(Text, nullable=False)
    evidence_count = Column(Integer, default=0)
    confidence = Column(Float, default=80.0)
    status = Column(SQLEnum(PolicyStatus), default=PolicyStatus.ACTIVE, nullable=False, index=True)

    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class AgentAdaptationModel(Base):
    """
    Tracks grounded adaptation proposals derived from verified outcomes and human governance approvals.
    """
    __tablename__ = "agent_adaptations"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    agent_name = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    previous_performance = Column(JSON, nullable=True)
    expected_improvement = Column(JSON, nullable=True)
    adaptation_delta = Column(Float, default=5.0)

    status = Column(SQLEnum(AdaptationStatus), default=AdaptationStatus.PROPOSED, nullable=False, index=True)
    approval_id = Column(String, ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True)
    policy_id = Column(String, ForeignKey("agent_policies.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
