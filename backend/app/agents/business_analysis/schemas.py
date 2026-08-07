from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SWOTAnalysis(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)

class CustomerPersona(BaseModel):
    name: str
    demographics: str
    pain_points: List[str]
    buying_motivations: List[str]

class BusinessAnalysisInput(BaseModel):
    business_name: str
    industry: str
    description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = "Global / Remote"
    target_audience: Optional[str] = None
    budget: Optional[str] = None
    business_goal: Optional[str] = None
    additional_context: Optional[dict] = Field(default_factory=dict)

class BusinessAnalysisResult(BaseModel):
    agent_name: str = "Business Analysis Agent"
    business_name: str
    industry: str
    business_summary: str
    industry_analysis: str
    swot: SWOTAnalysis
    digital_maturity_score: int = Field(ge=0, le=100)
    business_maturity_score: int = Field(ge=0, le=100)
    target_audience: str
    customer_personas: List[CustomerPersona]
    growth_opportunities: List[str]
    business_risks: List[str]
    recommendations: List[str]
    confidence_score: float = Field(default=95.0, ge=0.0, le=100.0)
    execution_time_seconds: float = 0.0
    status: str = "COMPLETED"
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
