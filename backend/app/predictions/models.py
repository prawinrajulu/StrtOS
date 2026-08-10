import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, JSON, Enum as SQLEnum, ForeignKey
from app.core.database import Base
from app.governance.models import RiskLevel

def generate_uuid():
    return str(uuid.uuid4())

class ScenarioType(str, Enum):
    CONSERVATIVE = "CONSERVATIVE"
    BALANCED = "BALANCED"
    AGGRESSIVE = "AGGRESSIVE"
    CUSTOM = "CUSTOM"

class PredictionStatus(str, Enum):
    DRAFT = "DRAFT"
    GENERATED = "GENERATED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    MEASURED = "MEASURED"
    EXPIRED = "EXPIRED"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"

class PredictionModel(Base):
    """
    Production-grade Predictive Decision Intelligence Model storing scenario simulations,
    prediction ranges, confidence metrics, evidence/memory references, and risk levels.
    """
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String, ForeignKey("clients.id", ondelete="CASCADE"), nullable=True, index=True)
    workflow_id = Column(String, ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True, index=True)
    report_id = Column(String, ForeignKey("reports.id", ondelete="SET NULL"), nullable=True)
    approval_id = Column(String, ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True)

    scenario_id = Column(String, nullable=True)
    scenario_type = Column(SQLEnum(ScenarioType), default=ScenarioType.BALANCED, nullable=False, index=True)
    scenario_name = Column(String, nullable=False)
    objective = Column(Text, nullable=True)

    metric_name = Column(String, nullable=False, default="ROAS")
    predicted_value = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    unit = Column(String, default="x")
    currency = Column(String, default="USD")

    confidence_score = Column(Float, default=85.0)
    risk_score = Column(Float, default=45.0)
    risk_level = Column(SQLEnum(RiskLevel), default=RiskLevel.MEDIUM, nullable=False)

    evidence_count = Column(Integer, default=0)
    memory_count = Column(Integer, default=0)
    provider = Column(String, nullable=True)
    model = Column(String, nullable=True)

    assumptions = Column(JSON, nullable=True)
    evidence_references = Column(JSON, nullable=True)
    memory_references = Column(JSON, nullable=True)

    prediction_status = Column(SQLEnum(PredictionStatus), default=PredictionStatus.GENERATED, nullable=False, index=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    valid_from = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    valid_until = Column(DateTime(timezone=True), nullable=True)

    extra_metadata = Column(JSON, nullable=True)
