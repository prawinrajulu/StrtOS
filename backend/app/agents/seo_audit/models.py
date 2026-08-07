from sqlalchemy import Column, String, Integer, Float, JSON, DateTime
from datetime import datetime, timezone
from app.core.database import Base
import uuid

class SEOAuditModel(Base):
    __tablename__ = "seo_audits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, nullable=True, index=True)
    website_url = Column(String, nullable=False)
    overall_seo_score = Column(Integer, default=88)
    technical_seo_score = Column(Integer, default=90)
    on_page_seo_score = Column(Integer, default=85)
    performance_score = Column(Integer, default=92)
    accessibility_score = Column(Integer, default=94)
    core_web_vitals_json = Column(JSON, nullable=True)
    critical_issues_json = Column(JSON, nullable=True)
    warnings_json = Column(JSON, nullable=True)
    recommendations_json = Column(JSON, nullable=True)
    confidence_score = Column(Float, default=95.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
