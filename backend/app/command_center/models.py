import enum
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.models.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class AutonomyLevel(str, enum.Enum):
    MANUAL = "MANUAL"
    ASSISTED = "ASSISTED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    AUTONOMOUS = "AUTONOMOUS"

class PrioritySeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class CommandCenterSnapshotModel(Base):
    __tablename__ = "command_center_snapshots"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    overall_health_score = Column(Float, nullable=False, default=88.0)
    health_status = Column(String, nullable=False, default="HEALTHY")
    business_health = Column(Float, nullable=False, default=85.0)
    strategy_health = Column(Float, nullable=False, default=90.0)
    execution_health = Column(Float, nullable=False, default=92.0)
    ai_health = Column(Float, nullable=False, default=94.0)
    governance_status = Column(String, nullable=False, default="CLEARED")
    active_alerts_count = Column(Integer, nullable=False, default=0)
    active_executions_count = Column(Integer, nullable=False, default=0)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

class StrategicDecisionSnapshotModel(Base):
    __tablename__ = "strategic_decision_snapshots"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    problem_statement = Column(Text, nullable=False)
    do_nothing_outcome = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    expected_value = Column(Float, nullable=False, default=0.0)
    risk_score = Column(Float, nullable=False, default=20.0)
    confidence_score = Column(Float, nullable=False, default=90.0)
    consensus_score = Column(Float, nullable=False, default=85.0)
    autonomy_level = Column(Enum(AutonomyLevel), nullable=False, default=AutonomyLevel.APPROVAL_REQUIRED)
    governance_status = Column(String, nullable=False, default="PENDING")
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
