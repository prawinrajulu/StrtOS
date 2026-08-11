import enum
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.models.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class ObjectiveLifecycle(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    AT_RISK = "AT_RISK"
    ON_TRACK = "ON_TRACK"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"

class HorizonType(str, enum.Enum):
    DAYS_30 = "30_DAYS"
    DAYS_60 = "60_DAYS"
    DAYS_90 = "90_DAYS"
    DAYS_180 = "180_DAYS"
    DAYS_365 = "365_DAYS"

class ScenarioType(str, enum.Enum):
    CONSERVATIVE = "CONSERVATIVE"
    BALANCED = "BALANCED"
    AGGRESSIVE = "AGGRESSIVE"
    CUSTOM = "CUSTOM"

class StrategicObjectiveModel(Base):
    __tablename__ = "strategic_objectives"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False, default="Growth") # Revenue, Acquisition, Conversion, SEO, Efficiency
    status = Column(Enum(ObjectiveLifecycle), nullable=False, default=ObjectiveLifecycle.DRAFT)
    target_horizon = Column(Enum(HorizonType), nullable=False, default=HorizonType.DAYS_90)
    baseline_value = Column(Float, nullable=False, default=0.0)
    target_value = Column(Float, nullable=False, default=100.0)
    current_value = Column(Float, nullable=False, default=0.0)
    unit = Column(String, nullable=False, default="USD")
    confidence_score = Column(Float, nullable=False, default=90.0)
    risk_level = Column(String, nullable=False, default="LOW")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    metrics = relationship("StrategicMetricModel", back_populates="objective", cascade="all, delete-orphan")
    constraints = relationship("StrategicConstraintModel", back_populates="objective", cascade="all, delete-orphan")
    plans = relationship("StrategicPlanModel", back_populates="objective", cascade="all, delete-orphan")

class StrategicMetricModel(Base):
    __tablename__ = "strategic_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    objective_id = Column(String, ForeignKey("strategic_objectives.id"), nullable=False, index=True)
    metric_name = Column(String, nullable=False)
    baseline = Column(Float, nullable=False, default=0.0)
    target = Column(Float, nullable=False, default=0.0)
    actual = Column(Float, nullable=True)
    unit = Column(String, nullable=False, default="USD")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    objective = relationship("StrategicObjectiveModel", back_populates="metrics")

class StrategicConstraintModel(Base):
    __tablename__ = "strategic_constraints"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    objective_id = Column(String, ForeignKey("strategic_objectives.id"), nullable=False, index=True)
    constraint_type = Column(String, nullable=False) # Budget, Timeline, Capacity, Risk, Policy
    limit_value = Column(Float, nullable=False)
    current_usage = Column(Float, nullable=False, default=0.0)
    is_hard_constraint = Column(Boolean, default=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    objective = relationship("StrategicObjectiveModel", back_populates="constraints")

class StrategicPlanModel(Base):
    __tablename__ = "strategic_plans"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    objective_id = Column(String, ForeignKey("strategic_objectives.id"), nullable=False, index=True)
    version = Column(String, nullable=False, default="1.0.0")
    scenario_type = Column(Enum(ScenarioType), nullable=False, default=ScenarioType.BALANCED)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    horizon = Column(Enum(HorizonType), nullable=False, default=HorizonType.DAYS_90)
    expected_value = Column(Float, nullable=False, default=0.0)
    confidence_score = Column(Float, nullable=False, default=90.0)
    risk_score = Column(Float, nullable=False, default=15.0)
    risk_level = Column(String, nullable=False, default="LOW")
    status = Column(String, nullable=False, default="DRAFT") # DRAFT, ACTIVE, EVALUATED, COMPLETED, ARCHIVED
    action_plan_id = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    objective = relationship("StrategicObjectiveModel", back_populates="plans")
    milestones = relationship("StrategicMilestoneModel", back_populates="plan", cascade="all, delete-orphan")
    versions = relationship("StrategicPlanVersionModel", back_populates="plan", cascade="all, delete-orphan")

class StrategicMilestoneModel(Base):
    __tablename__ = "strategic_milestones"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    plan_id = Column(String, ForeignKey("strategic_plans.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    horizon_day = Column(Integer, nullable=False, default=30)
    target_metric_value = Column(Float, nullable=False, default=0.0)
    actual_metric_value = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="PENDING")
    expected_outcome = Column(String, nullable=True)
    confidence_score = Column(Float, default=90.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    plan = relationship("StrategicPlanModel", back_populates="milestones")

class StrategicPlanVersionModel(Base):
    __tablename__ = "strategic_plan_versions"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    plan_id = Column(String, ForeignKey("strategic_plans.id"), nullable=False, index=True)
    version = Column(String, nullable=False)
    parent_version = Column(String, nullable=True)
    change_reason = Column(Text, nullable=False)
    performance_before = Column(Float, nullable=False, default=0.0)
    performance_after = Column(Float, nullable=False, default=0.0)
    risk_before = Column(Float, nullable=False, default=0.0)
    risk_after = Column(Float, nullable=False, default=0.0)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    plan = relationship("StrategicPlanModel", back_populates="versions")
