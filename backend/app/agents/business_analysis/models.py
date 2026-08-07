from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, ForeignKey
from datetime import datetime, timezone
from app.core.database import Base
import uuid

class BusinessAnalysisModel(Base):
    __tablename__ = "business_analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, nullable=True, index=True)
    business_name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    business_summary = Column(String, nullable=False)
    digital_maturity_score = Column(Integer, default=85)
    business_maturity_score = Column(Integer, default=80)
    swot_json = Column(JSON, nullable=True)
    personas_json = Column(JSON, nullable=True)
    growth_opportunities_json = Column(JSON, nullable=True)
    recommendations_json = Column(JSON, nullable=True)
    confidence_score = Column(Float, default=95.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
