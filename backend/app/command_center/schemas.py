from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.command_center.models import AutonomyLevel, PrioritySeverity

class ExecutiveHealthResponse(BaseModel):
    overall_score: float
    status: str
    business_health: float
    strategy_health: float
    execution_health: float
    ai_health: float
    prediction_health: float
    governance_health: float
    learning_health: float
    breakdown: Dict[str, float]

class StrategicPriorityResponse(BaseModel):
    id: str
    severity: PrioritySeverity
    title: str
    why_it_matters: str
    evidence: str
    affected_objective: str
    expected_impact: str
    risk: str
    recommended_next_step: str

class DecisionAlternativeResponse(BaseModel):
    option_type: str  # DO_NOTHING, RECOMMENDED_ACTION, CONSERVATIVE, BALANCED, AGGRESSIVE
    title: str
    expected_value: float
    confidence: float
    risk_score: float
    cost: float
    time_to_impact: str
    probability_of_success: float

class MultiAgentConsensusResponse(BaseModel):
    consensus_score: float
    status: str  # CONSENSUS_ACHIEVED, DEBATE_REQUIRED, HUMAN_REVIEW_REQUIRED
    supporting_agents: List[str]
    dissenting_agents: List[str]
    agent_contributions: List[Dict[str, Any]]

class StrategicDecisionResponse(BaseModel):
    id: str
    organization_id: str
    title: str
    problem_statement: str
    do_nothing_outcome: str
    recommended_action: str
    expected_value: float
    risk_score: float
    confidence_score: float
    consensus_score: float
    autonomy_level: AutonomyLevel
    governance_status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DecisionExplanationResponse(BaseModel):
    decision_id: str
    why_this_decision: str
    verified_evidence: List[str]
    historical_memory: List[str]
    causal_support: str
    forecast_summary: str
    agent_consensus_summary: str
    risk_breakdown: str
    assumptions: List[str]
    uncertainties: List[str]

class CommandCenterOverviewResponse(BaseModel):
    organization_id: str
    executive_health: ExecutiveHealthResponse
    top_priorities: List[StrategicPriorityResponse]
    active_decisions: List[StrategicDecisionResponse]
    active_alerts_count: int
    active_executions_count: int
    summary: str
