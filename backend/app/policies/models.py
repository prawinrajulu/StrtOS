import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class PolicyStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    CANDIDATE = "CANDIDATE"
    TESTING = "TESTING"
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    ROLLED_BACK = "ROLLED_BACK"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"

class PolicyModel(Base):
    """
    Root Policy representation tracking agent decision strategies across tenant organizations.
    """
    __tablename__ = "policies"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String, nullable=False, index=True)
    policy_name = Column(String, nullable=False, index=True)
    current_version = Column(String, nullable=False, default="1.0.0")
    status = Column(SQLEnum(PolicyStatus), default=PolicyStatus.ACTIVE, nullable=False, index=True)
    
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    versions = relationship("PolicyVersionModel", back_populates="policy", cascade="all, delete-orphan")
    evaluations = relationship("PolicyEvaluationModel", back_populates="policy", cascade="all, delete-orphan")

class PolicyVersionModel(Base):
    """
    Immutable version snapshot of an agent policy decision strategy.
    """
    __tablename__ = "policy_versions"

    id = Column(String, primary_key=True, default=generate_uuid)
    policy_id = Column(String, ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String, nullable=False, index=True)
    
    version = Column(String, nullable=False, index=True)
    status = Column(SQLEnum(PolicyStatus), default=PolicyStatus.DRAFT, nullable=False, index=True)
    
    parameters = Column(JSON, nullable=False, default=dict)
    performance_score = Column(Float, default=80.0)
    confidence_score = Column(Float, default=85.0)
    risk_score = Column(Float, default=30.0)
    adaptation_delta = Column(Float, default=0.0)
    
    parent_version = Column(String, nullable=True)
    change_reason = Column(Text, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    retired_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    policy = relationship("PolicyModel", back_populates="versions")

class PolicyEvaluationModel(Base):
    """
    Deterministic performance evaluation logs for policy versions.
    """
    __tablename__ = "policy_evaluations"

    id = Column(String, primary_key=True, default=generate_uuid)
    policy_id = Column(String, ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(String, nullable=False)
    agent_name = Column(String, nullable=False, index=True)

    accuracy_score = Column(Float, nullable=False, default=80.0)
    reliability_score = Column(Float, nullable=False, default=80.0)
    outcome_score = Column(Float, nullable=False, default=80.0)
    confidence_score = Column(Float, nullable=False, default=85.0)
    evidence_score = Column(Float, nullable=False, default=80.0)
    overall_policy_score = Column(Float, nullable=False, default=81.0)
    
    sample_count = Column(Integer, default=1)
    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    policy = relationship("PolicyModel", back_populates="evaluations")

class PolicyABTestModel(Base):
    """
    Deterministic A/B comparison records for policy candidate evaluation.
    """
    __tablename__ = "policy_ab_tests"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String, nullable=False, index=True)

    control_policy_id = Column(String, ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    control_version = Column(String, nullable=False)
    candidate_policy_id = Column(String, ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    candidate_version = Column(String, nullable=False)

    control_score = Column(Float, default=80.0)
    candidate_score = Column(Float, default=85.0)
    improvement_percent = Column(Float, default=6.25)
    
    status = Column(String, default="PENDING", nullable=False, index=True)  # PENDING, PASSED, FAILED
    sample_count = Column(Integer, default=5)
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
