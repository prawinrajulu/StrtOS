import enum
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Column, String, Float, Boolean, JSON, DateTime, ForeignKey, Enum, Text, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


# ─────────────────────────── Enumerations ────────────────────────────────────

class PortfolioStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    ACTIVE = "ACTIVE"
    REBALANCING = "REBALANCING"
    AT_RISK = "AT_RISK"
    BLOCKED = "BLOCKED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


class PortfolioDecisionStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    EVALUATING = "EVALUATING"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"
    ROLLED_BACK = "ROLLED_BACK"


class ResourceType(str, enum.Enum):
    BUDGET = "BUDGET"
    TIME = "TIME"
    TEAM_CAPACITY = "TEAM_CAPACITY"
    AGENT_CAPACITY = "AGENT_CAPACITY"
    EXECUTION_CAPACITY = "EXECUTION_CAPACITY"


class MissionPriority(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class PortfolioHealth(str, enum.Enum):
    EXCELLENT = "EXCELLENT"
    HEALTHY = "HEALTHY"
    WATCH = "WATCH"
    AT_RISK = "AT_RISK"
    CRITICAL = "CRITICAL"


class PortfolioCheckpointDecision(str, enum.Enum):
    CONTINUE = "CONTINUE"
    REBALANCE = "REBALANCE"
    PAUSE = "PAUSE"
    ESCALATE = "ESCALATE"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


class ConstraintStatus(str, enum.Enum):
    VALID = "VALID"
    WARNING = "WARNING"
    VIOLATION = "VIOLATION"


class RecommendationAction(str, enum.Enum):
    CONTINUE = "CONTINUE"
    ACCELERATE = "ACCELERATE"
    MAINTAIN = "MAINTAIN"
    DELAY = "DELAY"
    REDUCE = "REDUCE"
    STOP = "STOP"
    REVIEW = "REVIEW"



# ─────────────────────────── ORM Models ──────────────────────────────────────

class StrategicPortfolioModel(Base):
    __tablename__ = "portfolios"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    objective_id = Column(String, ForeignKey("strategic_objectives.id"), nullable=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    status = Column(Enum(PortfolioStatus), nullable=False, default=PortfolioStatus.DRAFT, index=True)
    current_version = Column(String, nullable=False, default="v1.0.0")
    health = Column(Enum(PortfolioHealth), nullable=False, default=PortfolioHealth.HEALTHY)
    expected_value = Column(Float, nullable=False, default=0.0)
    actual_value = Column(Float, nullable=False, default=0.0)
    portfolio_risk_score = Column(Float, nullable=False, default=20.0)
    confidence_score = Column(Float, nullable=False, default=90.0)
    total_budget = Column(Float, nullable=False, default=0.0)
    allocated_budget = Column(Float, nullable=False, default=0.0)
    scenario_type = Column(String, nullable=False, default="BALANCED")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    missions = relationship("PortfolioMissionModel", back_populates="portfolio", cascade="all, delete-orphan")
    resources = relationship("PortfolioResourceModel", back_populates="portfolio", cascade="all, delete-orphan")
    constraints = relationship("PortfolioConstraintModel", back_populates="portfolio", cascade="all, delete-orphan")
    allocations = relationship("PortfolioAllocationModel", back_populates="portfolio", cascade="all, delete-orphan")
    evaluations = relationship("PortfolioEvaluationModel", back_populates="portfolio", cascade="all, delete-orphan")
    decisions = relationship("PortfolioDecisionModel", back_populates="portfolio", cascade="all, delete-orphan")
    versions = relationship("PortfolioVersionModel", back_populates="portfolio", cascade="all, delete-orphan")
    checkpoints = relationship("PortfolioCheckpointModel", back_populates="portfolio", cascade="all, delete-orphan")
    initiatives = relationship("PortfolioInitiativeModel", back_populates="portfolio", cascade="all, delete-orphan")
    recommendations = relationship("PortfolioRecommendationModel", back_populates="portfolio", cascade="all, delete-orphan")


class PortfolioMissionModel(Base):
    """M2M join: Portfolio ↔ Mission with portfolio-level metadata."""
    __tablename__ = "portfolio_missions"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    mission_id = Column(String, ForeignKey("missions.id"), nullable=False, index=True)
    priority = Column(Enum(MissionPriority), nullable=False, default=MissionPriority.MEDIUM)
    priority_score = Column(Float, nullable=False, default=50.0)
    expected_value = Column(Float, nullable=False, default=0.0)
    success_probability = Column(Float, nullable=False, default=80.0)
    resource_requirement = Column(Float, nullable=False, default=0.0)  # budget units
    selection_status = Column(String, nullable=False, default="SELECTED")  # SELECTED, DEFERRED, PAUSED
    selection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    portfolio = relationship("StrategicPortfolioModel", back_populates="missions")


class PortfolioResourceModel(Base):
    __tablename__ = "portfolio_resources"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    resource_type = Column(Enum(ResourceType), nullable=False)
    available = Column(Float, nullable=False, default=0.0)
    allocated = Column(Float, nullable=False, default=0.0)
    remaining = Column(Float, nullable=False, default=0.0)
    unit = Column(String, nullable=False, default="USD")
    period = Column(String, nullable=False, default="MONTHLY")
    utilization_pct = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    portfolio = relationship("StrategicPortfolioModel", back_populates="resources")


class PortfolioConstraintModel(Base):
    __tablename__ = "portfolio_constraints"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    constraint_type = Column(String, nullable=False)  # BUDGET, TIMELINE, CAPACITY, POLICY
    limit_value = Column(Float, nullable=False)
    current_usage = Column(Float, nullable=False, default=0.0)
    is_hard_constraint = Column(Boolean, default=True)
    status = Column(Enum(ConstraintStatus), nullable=False, default=ConstraintStatus.VALID)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    portfolio = relationship("StrategicPortfolioModel", back_populates="constraints")


class PortfolioAllocationModel(Base):
    """Immutable allocation record per resource per mission per version."""
    __tablename__ = "portfolio_allocations"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    portfolio_version = Column(String, nullable=False)
    mission_id = Column(String, nullable=False, index=True)
    resource_type = Column(Enum(ResourceType), nullable=False)
    requested = Column(Float, nullable=False, default=0.0)
    allocated = Column(Float, nullable=False, default=0.0)
    remaining = Column(Float, nullable=False, default=0.0)
    reason = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False, default=90.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    portfolio = relationship("StrategicPortfolioModel", back_populates="allocations")


class PortfolioEvaluationModel(Base):
    __tablename__ = "portfolio_evaluations"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    health = Column(Enum(PortfolioHealth), nullable=False, default=PortfolioHealth.HEALTHY)
    health_score = Column(Float, nullable=False, default=80.0)
    expected_value = Column(Float, nullable=False, default=0.0)
    actual_value = Column(Float, nullable=False, default=0.0)
    portfolio_roi = Column(Float, nullable=False, default=0.0)
    mission_success_rate = Column(Float, nullable=False, default=0.0)
    resource_efficiency = Column(Float, nullable=False, default=0.0)
    risk_score = Column(Float, nullable=False, default=20.0)
    confidence_score = Column(Float, nullable=False, default=90.0)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    portfolio = relationship("StrategicPortfolioModel", back_populates="evaluations")


class PortfolioDecisionModel(Base):
    __tablename__ = "portfolio_decisions"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    decision_type = Column(String, nullable=False)  # OPTIMIZE, REBALANCE, PAUSE, APPROVE
    status = Column(Enum(PortfolioDecisionStatus), nullable=False, default=PortfolioDecisionStatus.PROPOSED)
    title = Column(String, nullable=False)
    rationale = Column(Text, nullable=True)
    risk_score = Column(Float, nullable=False, default=20.0)
    requires_governance = Column(Boolean, default=False)
    governance_approval_id = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    portfolio = relationship("StrategicPortfolioModel", back_populates="decisions")


class PortfolioVersionModel(Base):
    """Immutable version history — never mutated after creation."""
    __tablename__ = "portfolio_versions"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    version = Column(String, nullable=False)
    parent_version = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    resource_changes_json = Column(JSON, nullable=True)
    mission_changes_json = Column(JSON, nullable=True)
    risk_change = Column(Float, nullable=False, default=0.0)
    expected_value_change = Column(Float, nullable=False, default=0.0)
    approved_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    portfolio = relationship("StrategicPortfolioModel", back_populates="versions")


class PortfolioCheckpointModel(Base):
    __tablename__ = "portfolio_checkpoints"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    decision = Column(Enum(PortfolioCheckpointDecision), nullable=False,
                      default=PortfolioCheckpointDecision.CONTINUE)
    health_at_checkpoint = Column(Enum(PortfolioHealth), nullable=False, default=PortfolioHealth.HEALTHY)
    risk_at_checkpoint = Column(Float, nullable=False, default=20.0)
    progress_at_checkpoint = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    portfolio = relationship("StrategicPortfolioModel", back_populates="checkpoints")


class PortfolioInitiativeModel(Base):
    """Strategic initiative belonging to a portfolio."""
    __tablename__ = "portfolio_initiatives"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    strategic_objective_id = Column(String, nullable=True, index=True)
    priority = Column(Enum(MissionPriority), nullable=False, default=MissionPriority.MEDIUM)
    priority_score = Column(Float, nullable=False, default=50.0)
    expected_value = Column(Float, nullable=False, default=0.0)
    expected_roi = Column(Float, nullable=False, default=0.0)
    success_probability = Column(Float, nullable=False, default=80.0)
    risk_score = Column(Float, nullable=False, default=20.0)
    time_to_impact_days = Column(Integer, nullable=False, default=90)
    resource_cost = Column(Float, nullable=False, default=0.0)
    capital_budget = Column(Float, nullable=False, default=0.0)
    status = Column(String, nullable=False, default="PROPOSED")  # PROPOSED, ACTIVE, DEFERRED, PAUSED, STOPPED, COMPLETED
    selection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    portfolio = relationship("StrategicPortfolioModel", back_populates="initiatives")


class PortfolioRecommendationModel(Base):
    """Actionable portfolio recommendation (CONTINUE, ACCELERATE, MAINTAIN, DELAY, REDUCE, STOP, REVIEW)."""
    __tablename__ = "portfolio_recommendations"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    initiative_id = Column(String, nullable=True, index=True)
    mission_id = Column(String, nullable=True, index=True)
    recommendation_type = Column(Enum(RecommendationAction), nullable=False, default=RecommendationAction.REVIEW)
    title = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    expected_impact = Column(Text, nullable=True)
    risk_level = Column(String, nullable=False, default="MEDIUM")
    requires_governance = Column(Boolean, default=False)
    governance_approval_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="PROPOSED")  # PROPOSED, SUBMITTED, APPROVED, REJECTED, APPLIED
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    portfolio = relationship("StrategicPortfolioModel", back_populates="recommendations")
