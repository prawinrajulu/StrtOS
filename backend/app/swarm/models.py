import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON, Enum as SQLEnum, ForeignKey
from app.core.database import Base
from app.governance.models import RiskLevel

def generate_uuid():
    return str(uuid.uuid4())

class SwarmStatus(str, Enum):
    DRAFT = "DRAFT"
    PLANNING = "PLANNING"
    RUNNING = "RUNNING"
    DEBATING = "DEBATING"
    CRITIQUING = "CRITIQUING"
    CONSENSUS = "CONSENSUS"
    COMPLETED = "COMPLETED"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class SwarmMessageType(str, Enum):
    FINDING = "FINDING"
    EVIDENCE = "EVIDENCE"
    QUESTION = "QUESTION"
    CRITIQUE = "CRITIQUE"
    RECOMMENDATION = "RECOMMENDATION"
    CONFLICT = "CONFLICT"
    CONSENSUS = "CONSENSUS"
    DECISION = "DECISION"

class SwarmSessionModel(Base):
    """
    Multi-Agent Swarm Orchestration Session tracking parallel specialist agents,
    shared context, agent debate rounds, conflict matrices, and consensus scoring.
    """
    __tablename__ = "swarm_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String, ForeignKey("clients.id", ondelete="CASCADE"), nullable=True, index=True)
    workflow_id = Column(String, ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True, index=True)
    prediction_id = Column(String, ForeignKey("predictions.id", ondelete="SET NULL"), nullable=True, index=True)

    status = Column(SQLEnum(SwarmStatus), default=SwarmStatus.DRAFT, nullable=False, index=True)
    objective = Column(Text, nullable=False)
    strategy = Column(Text, nullable=True)

    participating_agents = Column(JSON, default=list)
    active_agents = Column(JSON, default=list)
    completed_agents = Column(JSON, default=list)
    failed_agents = Column(JSON, default=list)

    consensus_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    conflict_count = Column(Integer, default=0)
    debate_rounds = Column(Integer, default=0)

    synthesis_output = Column(JSON, nullable=True)
    created_by = Column(String, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    extra_metadata = Column(JSON, nullable=True)


class SwarmMessageModel(Base):
    """
    Structured message contract between agents in a Swarm Session.
    """
    __tablename__ = "swarm_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    swarm_id = Column(String, ForeignKey("swarm_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    source_agent = Column(String, nullable=False)
    target_agent = Column(String, nullable=True)
    message_type = Column(SQLEnum(SwarmMessageType), nullable=False)
    content = Column(Text, nullable=False)

    evidence_refs = Column(JSON, default=list)
    confidence = Column(Float, default=80.0)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class SwarmConflictModel(Base):
    """
    Tracks cross-agent findings contradictions and conflict resolutions.
    """
    __tablename__ = "swarm_conflicts"

    id = Column(String, primary_key=True, default=generate_uuid)
    swarm_id = Column(String, ForeignKey("swarm_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    subject = Column(String, nullable=False)
    agent_a = Column(String, nullable=False)
    agent_b = Column(String, nullable=False)
    claim_a = Column(Text, nullable=False)
    claim_b = Column(Text, nullable=False)

    evidence_a = Column(JSON, default=list)
    evidence_b = Column(JSON, default=list)
    severity = Column(SQLEnum(RiskLevel), default=RiskLevel.MEDIUM, nullable=False)

    resolution = Column(Text, nullable=True)
    resolved_by = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class SwarmDebateModel(Base):
    """
    Bounded Agent-to-Agent debate rounds record.
    """
    __tablename__ = "swarm_debates"

    id = Column(String, primary_key=True, default=generate_uuid)
    swarm_id = Column(String, ForeignKey("swarm_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    round_number = Column(Integer, nullable=False)
    claim = Column(Text, nullable=False)
    challenge = Column(Text, nullable=False)

    supporting_evidence = Column(JSON, default=list)
    counter_evidence = Column(JSON, default=list)
    resolution = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
