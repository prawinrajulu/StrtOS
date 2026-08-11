import enum
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.models.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class ForecastType(str, enum.Enum):
    BUSINESS_HEALTH = "BUSINESS_HEALTH"
    REVENUE = "REVENUE"
    CUSTOMER_GROWTH = "CUSTOMER_GROWTH"
    LEAD_GENERATION = "LEAD_GENERATION"
    CONVERSION = "CONVERSION"
    TRAFFIC = "TRAFFIC"
    SEO = "SEO"
    CAMPAIGN = "CAMPAIGN"
    EXECUTION = "EXECUTION"
    PREDICTION_ACCURACY = "PREDICTION_ACCURACY"
    AGENT_RELIABILITY = "AGENT_RELIABILITY"
    STRATEGIC_OBJECTIVE = "STRATEGIC_OBJECTIVE"

class ForecastHorizon(str, enum.Enum):
    DAYS_7 = "7_DAYS"
    DAYS_14 = "14_DAYS"
    DAYS_30 = "30_DAYS"
    DAYS_60 = "60_DAYS"
    DAYS_90 = "90_DAYS"
    DAYS_180 = "180_DAYS"
    DAYS_365 = "365_DAYS"

class ForecastStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    GENERATED = "GENERATED"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    EXPIRED = "EXPIRED"
    MEASURED = "MEASURED"

class TrendDirection(str, enum.Enum):
    UPWARD = "UPWARD"
    DOWNWARD = "DOWNWARD"
    STABLE = "STABLE"
    VOLATILE = "VOLATILE"
    REVERSING = "REVERSING"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

class ForecastModel(Base):
    __tablename__ = "forecasts"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    forecast_type = Column(Enum(ForecastType), nullable=False, default=ForecastType.BUSINESS_HEALTH, index=True)
    horizon = Column(Enum(ForecastHorizon), nullable=False, default=ForecastHorizon.DAYS_90, index=True)
    status = Column(Enum(ForecastStatus), nullable=False, default=ForecastStatus.GENERATED, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=False, default=85.0)
    trend_direction = Column(Enum(TrendDirection), nullable=False, default=TrendDirection.STABLE)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    metrics = relationship("ForecastMetricModel", back_populates="forecast", cascade="all, delete-orphan")
    scenarios = relationship("ForecastScenarioModel", back_populates="forecast", cascade="all, delete-orphan")
    impacts = relationship("ForecastImpactModel", back_populates="forecast", cascade="all, delete-orphan")
    evaluations = relationship("ForecastEvaluationModel", back_populates="forecast", cascade="all, delete-orphan")

class ForecastMetricModel(Base):
    __tablename__ = "forecast_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    forecast_id = Column(String, ForeignKey("forecasts.id"), nullable=False, index=True)
    metric_name = Column(String, nullable=False)
    current_value = Column(Float, nullable=False, default=0.0)
    forecast_value = Column(Float, nullable=True)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)
    unit = Column(String, nullable=False, default="USD")
    confidence_score = Column(Float, nullable=False, default=85.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    forecast = relationship("ForecastModel", back_populates="metrics")

class ForecastScenarioModel(Base):
    __tablename__ = "forecast_scenarios"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    forecast_id = Column(String, ForeignKey("forecasts.id"), nullable=False, index=True)
    scenario_type = Column(String, nullable=False) # CONSERVATIVE, BALANCED, AGGRESSIVE, CUSTOM
    expected_outcome = Column(Float, nullable=False, default=0.0)
    lower_bound = Column(Float, nullable=False, default=0.0)
    upper_bound = Column(Float, nullable=False, default=0.0)
    confidence_score = Column(Float, nullable=False, default=85.0)
    risk_score = Column(Float, nullable=False, default=20.0)
    required_budget = Column(Float, nullable=False, default=0.0)
    time_to_impact_days = Column(Integer, nullable=False, default=90)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    forecast = relationship("ForecastModel", back_populates="scenarios")

class ForecastImpactModel(Base):
    __tablename__ = "forecast_impacts"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    forecast_id = Column(String, ForeignKey("forecasts.id"), nullable=False, index=True)
    objective_id = Column(String, nullable=True)
    financial_impact = Column(Float, nullable=False, default=0.0)
    customer_impact = Column(Float, nullable=False, default=0.0)
    timeline_impact_days = Column(Integer, nullable=False, default=0)
    risk_level = Column(String, nullable=False, default="LOW")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    forecast = relationship("ForecastModel", back_populates="impacts")

class ForecastEvaluationModel(Base):
    __tablename__ = "forecast_evaluations"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    forecast_id = Column(String, ForeignKey("forecasts.id"), nullable=False, index=True)
    actual_value = Column(Float, nullable=False)
    forecast_value = Column(Float, nullable=False)
    absolute_error = Column(Float, nullable=False)
    accuracy_score = Column(Float, nullable=False)
    calibration_status = Column(String, nullable=False, default="WELL_CALIBRATED") # OVERCONFIDENT, UNDERCONFIDENT, WELL_CALIBRATED
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    forecast = relationship("ForecastModel", back_populates="evaluations")
