from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.agent_intelligence.models import (
    AgentHealthStatus, AgentTrendStatus, WeaknessSeverity, RecommendationStatus
)

class AgentMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    agent_name: str
    policy_version: str
    execution_count: int
    successful_execution_count: int
    failed_execution_count: int
    degraded_execution_count: int
    success_rate: float
    failure_rate: float
    average_latency_ms: float
    p95_latency_ms: float
    average_confidence: float
    evidence_quality_score: float
    tool_success_rate: float
    llm_success_rate: float
    prediction_accuracy: float
    outcome_success_rate: float
    policy_score: float
    average_token_usage: int
    estimated_cost: float
    regression_score: float
    overall_agent_score: float
    health_status: AgentHealthStatus
    trend: AgentTrendStatus
    recorded_at: datetime

class AgentBenchmarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    agent_name: str
    rank: int
    overall_score: float
    reliability_score: float
    accuracy_score: float
    evidence_quality: float
    execution_speed_ms: float
    outcome_success: float
    confidence: float
    sample_count: int
    trend: AgentTrendStatus
    evaluated_at: datetime

class AgentAnomalyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    agent_name: str
    anomaly_type: str
    severity: WeaknessSeverity
    baseline_value: float
    observed_value: float
    deviation_percent: float
    explanation: Optional[str] = None
    detected_at: datetime

class AgentWeaknessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    agent_name: str
    weakness_type: str
    severity: WeaknessSeverity
    metric_name: str
    current_value: float
    baseline_value: float
    deviation: float
    sample_count: int
    explanation: str
    detected_at: datetime

class AgentOptimizationRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    agent_name: str
    target_metric: str
    current_value: float
    target_value: float
    expected_improvement: float
    risk_score: float
    risk_level: str
    recommended_policy_change: Dict[str, Any]
    reason: str
    evidence_summary: Optional[Dict[str, Any]] = None
    status: RecommendationStatus
    governance_approval_id: Optional[str] = None
    candidate_policy_id: Optional[str] = None
    created_at: datetime

class AgentIntelligenceOverviewResponse(BaseModel):
    total_agents: int
    healthy_agents: int
    at_risk_agents: int
    critical_agents: int
    average_agent_score: float
    average_accuracy: float
    average_reliability: float
    optimization_recommendations_count: int
    agents: List[AgentMetricResponse]
    benchmarks: List[AgentBenchmarkResponse]
    recent_anomalies: List[AgentAnomalyResponse]
    recent_weaknesses: List[AgentWeaknessResponse]

class AgentAnalyzeRequest(BaseModel):
    agent_name: Optional[str] = Field(None, description="Optional target specialist agent")
    force_recalculate: bool = Field(default=False)
