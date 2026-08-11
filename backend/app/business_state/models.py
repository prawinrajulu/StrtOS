import enum
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.models.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class SnapshotType(str, enum.Enum):
    CURRENT = "CURRENT"
    BASELINE = "BASELINE"
    HISTORICAL = "HISTORICAL"

class AlertSeverity(str, enum.Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertStatus(str, enum.Enum):
    DETECTED = "DETECTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    ACTION_RECOMMENDED = "ACTION_RECOMMENDED"
    GOVERNANCE_PENDING = "GOVERNANCE_PENDING"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"

class MetricDirection(str, enum.Enum):
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"
    STABLE = "STABLE"
    UNKNOWN = "UNKNOWN"

class BusinessStateSnapshotModel(Base):
    __tablename__ = "business_state_snapshots"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    snapshot_type = Column(Enum(SnapshotType), nullable=False, default=SnapshotType.CURRENT)
    health_score = Column(Float, nullable=False, default=85.0)
    health_status = Column(String, nullable=False, default="HEALTHY") # EXCELLENT, HEALTHY, WATCH, AT_RISK, CRITICAL
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    metrics = relationship("BusinessMetricSnapshotModel", back_populates="snapshot", cascade="all, delete-orphan")

class BusinessMetricSnapshotModel(Base):
    __tablename__ = "business_metric_snapshots"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    snapshot_id = Column(String, ForeignKey("business_state_snapshots.id"), nullable=False, index=True)
    metric_name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, default="General") # Revenue, Acquisition, SEO, Agent, Execution, Prediction
    value = Column(Float, nullable=False, default=0.0)
    unit = Column(String, nullable=False, default="USD")
    confidence_score = Column(Float, nullable=False, default=95.0)
    source = Column(String, nullable=False, default="SystemTelemetry")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    snapshot = relationship("BusinessStateSnapshotModel", back_populates="metrics")

class BusinessSignalModel(Base):
    __tablename__ = "business_signals"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    metric_name = Column(String, nullable=False, index=True)
    previous_value = Column(Float, nullable=False, default=0.0)
    current_value = Column(Float, nullable=False, default=0.0)
    delta = Column(Float, nullable=False, default=0.0)
    percentage_change = Column(Float, nullable=False, default=0.0)
    direction = Column(Enum(MetricDirection), nullable=False, default=MetricDirection.STABLE)
    confidence = Column(Float, nullable=False, default=90.0)
    evidence_ref = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

class BusinessChangeModel(Base):
    __tablename__ = "business_changes"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    metric_name = Column(String, nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False, default=AlertSeverity.LOW)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    previous_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    percentage_change = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False, default=90.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

class BusinessAlertModel(Base):
    __tablename__ = "business_alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    alert_type = Column(String, nullable=False) # STRATEGIC_RISK, STRATEGIC_OPPORTUNITY, PERFORMANCE_DEGRADATION, etc.
    severity = Column(Enum(AlertSeverity), nullable=False, default=AlertSeverity.MEDIUM, index=True)
    status = Column(Enum(AlertStatus), nullable=False, default=AlertStatus.DETECTED, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    affected_objective_id = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=False, default=90.0)
    recommended_action = Column(Text, nullable=True)
    governance_required = Column(Boolean, default=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
