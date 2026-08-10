from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

class CoreWebVitals(BaseModel):
    lcp: str = "1.1s"  # Largest Contentful Paint
    fid: str = "14ms"   # First Input Delay
    cls: str = "0.02"   # Cumulative Layout Shift

class SEOIssue(BaseModel):
    issue_type: str
    severity: str  # CRITICAL, WARNING, INFO
    description: str
    impact: str
    recommended_fix: str

class SEOAuditInput(BaseModel):
    website_url: str
    business_context: Optional[str] = "General Business"
    industry: Optional[str] = "Commercial"
    target_audience: Optional[str] = None
    business_analysis_result: Optional[dict] = Field(default_factory=dict)

class SEOAuditResult(BaseModel):
    agent_name: str = "SEO Audit Agent"
    website_url: str
    overall_seo_score: int = Field(ge=0, le=100)
    technical_seo_score: int = Field(ge=0, le=100)
    on_page_seo_score: int = Field(ge=0, le=100)
    performance_score: int = Field(ge=0, le=100)
    accessibility_score: int = Field(ge=0, le=100)
    core_web_vitals: CoreWebVitals
    critical_issues: List[SEOIssue] = Field(default_factory=list)
    warnings: List[SEOIssue] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    priority_fixes: List[str] = Field(default_factory=list)
    estimated_seo_impact: str = "High (+35% organic traffic expected within 60 days)"
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = Field(default=95.0, ge=0.0, le=100.0)
    execution_time_seconds: float = 0.0
    status: str = "COMPLETED"
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
