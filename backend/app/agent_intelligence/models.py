import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class AgentHealthStatus(str, enum.Enum):
    EXCELLENT = "EXCELLENT"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    AT_RISK = "AT_RISK"
    CRITICAL = "CRITICAL"

class AgentTrendStatus(str, enum.Enum):
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

class WeaknessSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RecommendationStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    EVALUATING = "EVALUATING"
    PENDING_GOVERNANCE = "PENDING_GOVERNANCE"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"
    ROLLED_BACK = "ROLLED_BACK"

class AgentIntelligenceMetricModel(Base):
    """
    Detailed, un-fabricated execution performance telemetry per agent and organization.
    """
    __tablename__ = "agent_intelligence_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String, nullable=False, index=True)
    policy_version = Column(String, default="1.0.0", nullable=False)

    execution_count = Column(Integer, default=0)
    successful_execution_count = Column(Integer, default=0)
    failed_execution_count = Column(Integer, default=0)
    degraded_execution_count = Column(Integer, default=0)

    success_rate = Column(Float, default=100.0)
    failure_rate = Column(Float, default=0.0)
    average_latency_ms = Column(Float, default=0.0)
    p95_latency_ms = Column(Float, default=0.0)

    average_confidence = Column(Float, default=85.0)
    evidence_quality_score = Column(Float, default=85.0)
    tool_success_rate = Column(Float, default=95.0)
    llm_success_rate = Column(Float, default=95.0)

    prediction_accuracy = Column(Float, default=80.0)
    outcome_success_rate = Column(Float, default=80.0)
    policy_score = Column(Float, default=80.0)

    average_token_usage = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    regression_score = Column(Float, default=0.0)
    overall_agent_score = Column(Float, default=82.5)

    health_status = Column(SQLEnum(AgentHealthStatus), default=AgentHealthStatus.HEALTHY, nullable=False, index=True)
    trend = Column(SQLEnum(AgentTrendStatus), default=AgentTrendStatus.STABLE, nullable=False, index=True)

    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class AgentBenchmarkModel(Base):
    """
    Normalized cross-agent performance benchmarks.
    """
    __tablename__ = "agent_benchmarks"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String, nullable=False, index=True)

    rank = Column(Integer, default=1)
    overall_score = Column(Float, default=80.0)
    reliability_score = Column(Float, default=85.0)
    accuracy_score = Column(Float, default=80.0)
    evidence_quality = Column(Float, default=85.0)
    execution_speed_ms = Column(Float, default=1200.0)
    outcome_success = Column(Float, default=85.0)
    confidence = Column(Float, default=85.0)

    sample_count = Column(Integer, default=1)
    trend = Column(SQLEnum(AgentTrendStatus), default=AgentTrendStatus.STABLE, nullable=False)

    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

class AgentAnomalyModel(Base):
    """
    Empirical anomaly detection logs tracking unexpected metric shifts against baselines.
    """
    __tablename__ = "agent_anomalies"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String, nullable=False, index=True)

    anomaly_type = Column(String, nullable=False, index=True)  # LATENCY_SPIKE, FAILURE_RATE_SPIKE, CONFIDENCE_DROP, EVIDENCE_DROP
    severity = Column(SQLEnum(WeaknessSeverity), default=WeaknessSeverity.MEDIUM, nullable=False, index=True)

    baseline_value = Column(Float, nullable=False)
    observed_value = Column(Float, nullable=False)
    deviation_percent = Column(Float, nullable=False)

    explanation = Column(Text, nullable=True)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

class AgentWeaknessModel(Base):
    """
    Detected agent operational and analytical weaknesses.
    """
    __tablename__ = "agent_weaknesses"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String, nullable=False, index=True)

    weakness_type = Column(String, nullable=False, index=True)  # LOW_ACCURACY, LOW_EVIDENCE_QUALITY, HIGH_FAILURE_RATE, HIGH_LATENCY, REPEATED_TOOL_FAILURES
    severity = Column(SQLEnum(WeaknessSeverity), default=WeaknessSeverity.MEDIUM, nullable=False, index=True)
    metric_name = Column(String, nullable=False)

    current_value = Column(Float, nullable=False)
    baseline_value = Column(Float, nullable=False)
    deviation = Column(Float, nullable=False)
    sample_count = Column(Integer, default=1)

    explanation = Column(Text, nullable=False)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

class AgentOptimizationRecommendationModel(Base):
    """
    Grounded optimization recommendations linking detected weaknesses to policy parameter adjustments.
    """
    __tablename__ = "agent_optimization_recommendations"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String, nullable=False, index=True)

    target_metric = Column(String, nullable=False)
    current_value = Column(Float, nullable=False)
    target_value = Column(Float, nullable=False)
    expected_improvement = Column(Float, default=5.0)

    risk_score = Column(Float, default=25.0)
    risk_level = Column(String, default="LOW", nullable=False)

    recommended_policy_change = Column(JSON, nullable=False, default=dict)
    reason = Column(Text, nullable=False)
    evidence_summary = Column(JSON, nullable=True)

    status = Column(SQLEnum(RecommendationStatus), default=RecommendationStatus.DRAFT, nullable=False, index=True)
    governance_approval_id = Column(String, ForeignKey("approval_requests.id", ondelete="SET NULL"), nullable=True)
    candidate_policy_id = Column(String, ForeignKey("policies.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
