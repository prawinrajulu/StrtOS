from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class CreativeRequirement(BaseModel):
    asset_type: str  # Video Ad, Search Copy, Carousel Image, Landing Page
    specs: str
    quantity: int
    target_channel: str
    priority: str

class WeeklyActivity(BaseModel):
    week_number: int
    focus_theme: str
    key_deliverables: List[str]
    target_milestone: str

class CampaignPlanningInput(BaseModel):
    marketing_strategy_result: dict
    business_analysis_result: Optional[dict] = Field(default_factory=dict)
    seo_audit_result: Optional[dict] = Field(default_factory=dict)
    competitor_research_result: Optional[dict] = Field(default_factory=dict)
    business_goal: Optional[str] = "Acquire high-intent customers"
    budget: Optional[str] = "$10,000 / mo"
    timeline: Optional[str] = "90 Days"

class CampaignPlanningResult(BaseModel):
    agent_name: str = "Campaign Planner Agent"
    campaign_summary: str
    campaign_timeline: str
    execution_plan: List[str]
    channel_allocation: Dict[str, str]
    creative_requirements: List[CreativeRequirement]
    budget_allocation: Dict[str, str]
    weekly_roadmap: List[WeeklyActivity]
    kpis: List[str]
    launch_checklist: List[str]
    optimization_plan: List[str]
    risk_assessment: List[str]
    expected_outcome: str
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = Field(default=95.0, ge=0.0, le=100.0)
    execution_time_seconds: float = 0.0
    status: str = "COMPLETED"
    latency_ms: Optional[int] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    token_usage: Optional[int] = None
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
