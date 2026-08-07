from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class CompetitorProfile(BaseModel):
    name: str
    competitor_type: str  # DIRECT or INDIRECT
    website: str
    market_share_estimate: str
    pricing_tier: str  # LOW, MEDIUM, PREMIUM
    digital_presence_score: int = Field(ge=0, le=100)
    seo_visibility_score: int = Field(ge=0, le=100)
    key_strengths: List[str]
    key_weaknesses: List[str]

class MarketGapItem(BaseModel):
    gap_category: str
    description: str
    opportunity_level: str  # HIGH, MEDIUM, LOW
    actionable_strategy: str

class CompetitorResearchInput(BaseModel):
    business_name: str
    industry: str
    location: Optional[str] = "Global / Remote"
    website: Optional[str] = None
    business_analysis_result: Optional[dict] = Field(default_factory=dict)
    seo_audit_result: Optional[dict] = Field(default_factory=dict)

class CompetitorResearchResult(BaseModel):
    agent_name: str = "Competitor Research Agent"
    business_name: str
    industry: str
    direct_competitors: List[CompetitorProfile] = Field(default_factory=list)
    indirect_competitors: List[CompetitorProfile] = Field(default_factory=list)
    market_position_summary: str
    pricing_comparison_summary: str
    strength_matrix: Dict[str, List[str]] = Field(default_factory=dict)
    weakness_matrix: Dict[str, List[str]] = Field(default_factory=dict)
    market_gaps: List[MarketGapItem] = Field(default_factory=list)
    competitive_opportunities: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=95.0, ge=0.0, le=100.0)
    execution_time_seconds: float = 0.0
    status: str = "COMPLETED"
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
