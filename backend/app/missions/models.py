import enum
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.models.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class MissionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    BLOCKED = "BLOCKED"
    ADAPTING = "ADAPTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class MissionStepStatus(str, enum.Enum):
    PENDING = "PENDING"
    READY = "READY"
    BLOCKED = "BLOCKED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class MissionEvaluationStatus(str, enum.Enum):
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    OFF_TRACK = "OFF_TRACK"
    LIKELY_TO_FAIL = "LIKELY_TO_FAIL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

class MissionCheckpointDecision(str, enum.Enum):
    CONTINUE = "CONTINUE"
    PAUSE = "PAUSE"
    REPLAN = "REPLAN"
    ESCALATE = "ESCALATE"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"

class MissionModel(Base):
    __tablename__ = "missions"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    objective_id = Column(String, nullable=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    status = Column(Enum(MissionStatus), nullable=False, default=MissionStatus.DRAFT, index=True)
    current_version = Column(String, nullable=False, default="v1.0.0")
    progress_percentage = Column(Float, nullable=False, default=0.0)
    risk_score = Column(Float, nullable=False, default=20.0)
    confidence_score = Column(Float, nullable=False, default=90.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    criteria = relationship("MissionSuccessCriterionModel", back_populates="mission", cascade="all, delete-orphan")
    plans = relationship("MissionPlanVersionModel", back_populates="mission", cascade="all, delete-orphan")
    steps = relationship("MissionStepModel", back_populates="mission", cascade="all, delete-orphan")
    checkpoints = relationship("MissionCheckpointModel", back_populates="mission", cascade="all, delete-orphan")

class MissionSuccessCriterionModel(Base):
    __tablename__ = "mission_success_criteria"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    mission_id = Column(String, ForeignKey("missions.id"), nullable=False, index=True)
    metric_name = Column(String, nullable=False)
    baseline_value = Column(Float, nullable=False, default=0.0)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False, default=0.0)
    unit = Column(String, nullable=False, default="USD")
    status = Column(String, nullable=False, default="PROGRESSING")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    mission = relationship("MissionModel", back_populates="criteria")

class MissionPlanVersionModel(Base):
    __tablename__ = "mission_plan_versions"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    mission_id = Column(String, ForeignKey("missions.id"), nullable=False, index=True)
    version = Column(String, nullable=False)
    parent_version = Column(String, nullable=True)
    adaptation_reason = Column(Text, nullable=True)
    delta_percentage = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    mission = relationship("MissionModel", back_populates="plans")

class MissionStepModel(Base):
    __tablename__ = "mission_steps"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    mission_id = Column(String, ForeignKey("missions.id"), nullable=False, index=True)
    step_order = Column(Integer, nullable=False, default=1)
    title = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    status = Column(Enum(MissionStepStatus), nullable=False, default=MissionStepStatus.PENDING, index=True)
    dependencies_json = Column(JSON, nullable=True) # list of step IDs
    risk_level = Column(String, nullable=False, default="LOW")
    autonomy_level = Column(String, nullable=False, default="AUTONOMOUS")
    result_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    mission = relationship("MissionModel", back_populates="steps")

class MissionCheckpointModel(Base):
    __tablename__ = "mission_checkpoints"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    mission_id = Column(String, ForeignKey("missions.id"), nullable=False, index=True)
    decision = Column(Enum(MissionCheckpointDecision), nullable=False, default=MissionCheckpointDecision.CONTINUE)
    progress_at_checkpoint = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    mission = relationship("MissionModel", back_populates="checkpoints")
