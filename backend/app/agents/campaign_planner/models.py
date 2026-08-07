from sqlalchemy import Column, String, Integer, Float, JSON, DateTime
from datetime import datetime, timezone
from app.core.database import Base
import uuid

class CampaignPlannerModel(Base):
    __tablename__ = "campaign_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, nullable=True, index=True)
    campaign_timeline = Column(String, nullable=False)
    expected_outcome = Column(String, nullable=False)
    channel_allocation_json = Column(JSON, nullable=True)
    creative_requirements_json = Column(JSON, nullable=True)
    weekly_roadmap_json = Column(JSON, nullable=True)
    launch_checklist_json = Column(JSON, nullable=True)
    confidence_score = Column(Float, default=95.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
