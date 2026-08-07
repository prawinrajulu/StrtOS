from sqlalchemy import Column, String, Integer, Float, JSON, DateTime
from datetime import datetime, timezone
from app.core.database import Base
import uuid

class MarketingStrategyModel(Base):
    __tablename__ = "marketing_strategies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, nullable=True, index=True)
    brand_positioning = Column(String, nullable=False)
    unique_value_proposition = Column(String, nullable=False)
    roi_projection = Column(String, nullable=False)
    channel_recommendations_json = Column(JSON, nullable=True)
    budget_allocation_json = Column(JSON, nullable=True)
    growth_roadmap_json = Column(JSON, nullable=True)
    recommendations_json = Column(JSON, nullable=True)
    confidence_score = Column(Float, default=95.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
