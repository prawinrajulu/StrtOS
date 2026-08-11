# Decision Optimization ORM models
"""SQLAlchemy models for decision optimization components.
These models reuse the existing Base from app.core.database and follow the
organization_id tenant isolation strategy used throughout the codebase.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum as SQLEnum, JSON, ForeignKey
from app.core.database import Base
from app.governance.models import RiskLevel

def generate_uuid() -> str:
    return str(uuid.uuid4())

class ActionCandidate(Base):
    """Represents a potential action generated from the ActionRegistry.
    All fields required by the specification are stored. Values are filled
    by the candidate engine; missing values remain NULL and are validated
    later in the pipeline.
    """
    __tablename__ = "action_candidates"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String, nullable=True, index=True)
    workflow_id = Column(String, nullable=True, index=True)
    decision_id = Column(String, nullable=True, index=True)
    action_type = Column(String, nullable=False, index=True)
    expected_value = Column(Float, nullable=True)
    expected_cost = Column(Float, nullable=True)
    expected_roi = Column(Float, nullable=True)
    expected_confidence = Column(Float, nullable=True)
    expected_risk = Column(String, nullable=True)  # stored as enum name from RiskLevel
    causal_support = Column(Float, nullable=True)
    historical_success = Column(Float, nullable=True)
    agent_reliability = Column(Float, nullable=True)
    reversibility = Column(String, nullable=True)
    time_to_impact = Column(Integer, nullable=True)  # minutes
    supporting_evidence = Column(JSON, nullable=True)
    supporting_memory = Column(JSON, nullable=True)
    prediction_id = Column(String, nullable=True)
    policy_version_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="PENDING")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ActionPlan(Base):
    """Represents an ordered execution plan container."""
    __tablename__ = "action_plans"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String, nullable=True, index=True)
    workflow_id = Column(String, nullable=True, index=True)
    decision_id = Column(String, nullable=True, index=True)
    status = Column(String, nullable=False, default="PENDING")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ActionPlanStep(Base):
    """A single step within an executable action plan.
    Dependency relationships are represented by the ``dependency`` column that
    holds the ``id`` of the predecessor step (or NULL for the first step).
    """
    __tablename__ = "action_plan_steps"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(String, ForeignKey("action_plans.id", ondelete="CASCADE"), nullable=True, index=True)
    client_id = Column(String, nullable=True, index=True)
    workflow_id = Column(String, nullable=True, index=True)
    decision_id = Column(String, nullable=True, index=True)
    action_id = Column(String, ForeignKey("action_candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    step_order = Column(Integer, nullable=False)
    dependency = Column(String, ForeignKey("action_plan_steps.id", ondelete="SET NULL"), nullable=True)
    estimated_cost = Column(Float, nullable=True)
    estimated_time = Column(Integer, nullable=True)  # minutes
    risk_level = Column(String, nullable=True)  # enum name from RiskLevel
    rollback_strategy = Column(String, nullable=True)
    success_metric = Column(String, nullable=True)
    status = Column(String, nullable=False, default="PENDING")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ActionEvaluation(Base):
    """Result of evaluating a candidate – includes risk and scoring.
    This table stores a snapshot of the deterministic optimizer output for
    auditability and later reporting.
    """
    __tablename__ = "action_evaluations"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String, nullable=True, index=True)
    workflow_id = Column(String, nullable=True, index=True)
    decision_id = Column(String, nullable=True, index=True)
    candidate_id = Column(String, ForeignKey("action_candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    score_breakdown = Column(JSON, nullable=True)
    total_score = Column(Float, nullable=True)
    recommendation = Column(String, nullable=True)
    risk_level = Column(String, nullable=True)
    status = Column(String, nullable=False, default="COMPLETED")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
