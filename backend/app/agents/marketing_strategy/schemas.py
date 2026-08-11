from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class ChannelStrategyItem(BaseModel):
    channel: str  # Organic Search, Paid Search, Social Video, Email, etc.
    objective: str
    allocation_percentage: float
    tactics: List[str]
    target_kpi: str

class MarketingFunnelStage(BaseModel):
    stage_name: str  # TOFU (Awareness), MOFU (Consideration), BOFU (Conversion)
    focus: str
    key_channels: List[str]
    conversion_metric: str

class MarketingStrategyInput(BaseModel):
    business_analysis_result: dict
    seo_audit_result: dict
    competitor_research_result: dict
    business_goal: Optional[str] = "Acquire high-intent customers"
    budget: Optional[str] = "$10,000 / mo"
    target_audience: Optional[str] = "General Commercial Audience"
    priority: Optional[str] = "HIGH"

class MarketingStrategyResult(BaseModel):
    agent_name: str = "Marketing Strategy Agent"
    executive_marketing_summary: str
    brand_positioning: str
    unique_value_proposition: str
    marketing_objectives: List[str]
    target_personas: List[Dict[str, Any]]
    channel_recommendations: List[ChannelStrategyItem]
    content_pillars: List[str]
    customer_journey: List[str]
    marketing_funnel: List[MarketingFunnelStage]
    budget_allocation: Dict[str, str]
    kpis: List[str]
    roi_projection: str
    growth_roadmap: List[str]
    implementation_timeline_days: int = 90
    risks: List[str]
    recommendations: List[str]
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = Field(default=95.0, ge=0.0, le=100.0)
    execution_time_seconds: float = 0.0
    status: str = "COMPLETED"
    latency_ms: Optional[int] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    token_usage: Optional[int] = None
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
