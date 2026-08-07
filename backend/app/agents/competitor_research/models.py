from sqlalchemy import Column, String, Integer, Float, JSON, DateTime
from datetime import datetime, timezone
from app.core.database import Base
import uuid

class CompetitorResearchModel(Base):
    __tablename__ = "competitor_researches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, nullable=True, index=True)
    business_name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    market_position_summary = Column(String, nullable=False)
    direct_competitors_json = Column(JSON, nullable=True)
    indirect_competitors_json = Column(JSON, nullable=True)
    market_gaps_json = Column(JSON, nullable=True)
    recommendations_json = Column(JSON, nullable=True)
    confidence_score = Column(Float, default=95.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
