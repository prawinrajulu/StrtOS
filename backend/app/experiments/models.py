import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON, Enum as SQLEnum, ForeignKey
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ExperimentStatus(str, Enum):
    DRAFT = "DRAFT"
    DESIGNED = "DESIGNED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    RUNNING = "RUNNING"
    MEASURING = "MEASURING"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

class ExperimentResult(str, Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    NEUTRAL = "NEUTRAL"
    INCONCLUSIVE = "INCONCLUSIVE"
    FAILED = "FAILED"

class VariantType(str, Enum):
    CONTROL = "CONTROL"
    VARIANT_A = "VARIANT_A"
    VARIANT_B = "VARIANT_B"

class ExperimentModel(Base):
    """
    Tracks A/B and multivariate experiments for continuous optimization & experimentation.
    """
    __tablename__ = "experiments"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String, ForeignKey("clients.id", ondelete="CASCADE"), nullable=True, index=True)
    workflow_id = Column(String, nullable=True, index=True)
    prediction_id = Column(String, ForeignKey("predictions.id", ondelete="SET NULL"), nullable=True, index=True)
    baseline_policy_id = Column(String, ForeignKey("agent_policies.id", ondelete="SET NULL"), nullable=True)
    variant_policy_id = Column(String, ForeignKey("agent_policies.id", ondelete="SET NULL"), nullable=True)

    experiment_name = Column(String, nullable=False, index=True)
    objective = Column(Text, nullable=False)
    hypothesis = Column(Text, nullable=False)
    metric_name = Column(String, nullable=False, default="conversion_rate")

    baseline_value = Column(Float, default=0.0)
    target_value = Column(Float, default=0.0)
    minimum_detectable_effect = Column(Float, default=5.0)
    confidence_threshold = Column(Float, default=95.0)

    control_sample_size = Column(Integer, default=0)
    variant_sample_size = Column(Integer, default=0)

    status = Column(SQLEnum(ExperimentStatus), default=ExperimentStatus.DRAFT, nullable=False, index=True)
    result = Column(SQLEnum(ExperimentResult), default=ExperimentResult.INCONCLUSIVE, nullable=False)
    winner = Column(SQLEnum(VariantType), nullable=True)
    confidence = Column(Float, default=0.0)

    created_by = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    approval_id = Column(String, ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ExperimentVariantModel(Base):
    """
    Defines control vs variant configurations bound to versioned policies.
    """
    __tablename__ = "experiment_variants"

    id = Column(String, primary_key=True, default=generate_uuid)
    experiment_id = Column(String, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    variant_type = Column(SQLEnum(VariantType), nullable=False)
    variant_name = Column(String, nullable=False)
    policy_id = Column(String, ForeignKey("agent_policies.id", ondelete="RESTRICT"), nullable=False)
    configuration = Column(JSON, nullable=False)

    sample_size = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    average_kpi = Column(Float, default=0.0)
    average_latency_ms = Column(Float, default=0.0)
    average_cost = Column(Float, default=0.0)
    average_confidence = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ExperimentMeasurementModel(Base):
    """
    Tracks individual execution telemetry assigned to an active experiment variant.
    """
    __tablename__ = "experiment_measurements"

    id = Column(String, primary_key=True, default=generate_uuid)
    experiment_id = Column(String, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_id = Column(String, ForeignKey("experiment_variants.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    execution_id = Column(String, nullable=False, index=True)

    variant_type = Column(SQLEnum(VariantType), nullable=False)
    kpi_value = Column(Float, default=0.0)
    success = Column(Integer, default=1)  # 1 = True, 0 = False
    confidence = Column(Float, default=80.0)
    latency_ms = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    human_approved = Column(Integer, default=1)

    prediction_error = Column(Float, default=0.0)
    metadata_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
