from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.portfolio.models import (
    PortfolioStatus, PortfolioDecisionStatus, ResourceType,
    MissionPriority, PortfolioHealth, PortfolioCheckpointDecision,
    ConstraintStatus, RecommendationAction
)


# ─────────────────────── Resource Schemas ────────────────────────────────────

class PortfolioResourceCreate(BaseModel):
    resource_type: ResourceType
    available: float = Field(..., ge=0.0)
    unit: str = "USD"
    period: str = "MONTHLY"


class PortfolioResourceResponse(BaseModel):
    id: str
    organization_id: str
    portfolio_id: str
    resource_type: ResourceType
    available: float
    allocated: float
    remaining: float
    unit: str
    period: str
    utilization_pct: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────── Mission Entry Schemas ───────────────────────────────

class PortfolioMissionCreate(BaseModel):
    mission_id: str
    expected_value: float = 0.0
    success_probability: float = Field(default=80.0, ge=0.0, le=100.0)
    resource_requirement: float = Field(default=0.0, ge=0.0)


class PortfolioMissionResponse(BaseModel):
    id: str
    organization_id: str
    portfolio_id: str
    mission_id: str
    priority: MissionPriority
    priority_score: float
    expected_value: float
    success_probability: float
    resource_requirement: float
    selection_status: str
    selection_reason: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────── Constraint Schemas ──────────────────────────────────

class PortfolioConstraintResponse(BaseModel):
    id: str
    organization_id: str
    portfolio_id: str
    constraint_type: str
    limit_value: float
    current_usage: float
    is_hard_constraint: bool
    status: ConstraintStatus
    description: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────── Allocation Schemas ──────────────────────────────────

class PortfolioAllocationResponse(BaseModel):
    id: str
    organization_id: str
    portfolio_id: str
    portfolio_version: str
    mission_id: str
    resource_type: ResourceType
    requested: float
    allocated: float
    remaining: float
    reason: Optional[str] = None
    confidence: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────── Version & Checkpoint Schemas ────────────────────────

class PortfolioVersionResponse(BaseModel):
    id: str
    organization_id: str
    portfolio_id: str
    version: str
    parent_version: Optional[str] = None
    reason: Optional[str] = None
    risk_change: float
    expected_value_change: float
    approved_by: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PortfolioCheckpointResponse(BaseModel):
    id: str
    organization_id: str
    portfolio_id: str
    decision: PortfolioCheckpointDecision
    health_at_checkpoint: PortfolioHealth
    risk_at_checkpoint: float
    progress_at_checkpoint: float
    notes: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────── Decision Schemas ────────────────────────────────────

class PortfolioDecisionResponse(BaseModel):
    id: str
    organization_id: str
    portfolio_id: str
    decision_type: str
    status: PortfolioDecisionStatus
    title: str
    rationale: Optional[str] = None
    risk_score: float
    requires_governance: bool
    approved_by: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────── Evaluation Schemas ──────────────────────────────────

class PortfolioEvaluationResponse(BaseModel):
    portfolio_id: str
    health: PortfolioHealth
    health_score: float
    expected_value: float
    actual_value: float
    portfolio_roi: float
    mission_success_rate: float
    resource_efficiency: float
    risk_score: float
    confidence_score: float
    summary: str
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────── Main Portfolio Schemas ──────────────────────────────

class PortfolioCreate(BaseModel):
    title: str
    summary: Optional[str] = None
    objective_id: Optional[str] = None
    total_budget: float = Field(default=0.0, ge=0.0)
    scenario_type: str = "BALANCED"
    resources: List[PortfolioResourceCreate] = []
    missions: List[PortfolioMissionCreate] = []


class PortfolioResponse(BaseModel):
    id: str
    organization_id: str
    objective_id: Optional[str] = None
    title: str
    summary: Optional[str] = None
    status: PortfolioStatus
    current_version: str
    health: PortfolioHealth
    expected_value: float
    actual_value: float
    portfolio_risk_score: float
    confidence_score: float
    total_budget: float
    allocated_budget: float
    scenario_type: str
    created_at: datetime
    updated_at: datetime
    missions: List[PortfolioMissionResponse] = []
    resources: List[PortfolioResourceResponse] = []
    constraints: List[PortfolioConstraintResponse] = []
    versions: List[PortfolioVersionResponse] = []
    checkpoints: List[PortfolioCheckpointResponse] = []
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────── Optimization Schemas ────────────────────────────────

class OptimizationRequest(BaseModel):
    scenario_type: str = "BALANCED"  # CONSERVATIVE, BALANCED, AGGRESSIVE, CUSTOM
    budget_delta_pct: float = 0.0    # What-if budget change %
    capacity_delta_pct: float = 0.0  # What-if capacity change %


class MissionOptimizationResult(BaseModel):
    mission_id: str
    title: str
    priority_score: float
    expected_value: float
    success_probability: float
    resource_requirement: float
    value_cost_ratio: float
    status: str  # SELECTED, DEFERRED, PAUSED
    reason: str


class OptimizationResponse(BaseModel):
    portfolio_id: str
    scenario_type: str
    selected_missions: List[MissionOptimizationResult]
    deferred_missions: List[MissionOptimizationResult]
    paused_missions: List[MissionOptimizationResult]
    expected_portfolio_value: float
    portfolio_risk_score: float
    confidence: float
    budget_utilization_pct: float
    capacity_utilization_pct: float
    explanation: str


# ─────────────────────── Simulation Schemas ──────────────────────────────────

class ScenarioResult(BaseModel):
    scenario_type: str
    expected_value: float
    risk_score: float
    budget_utilization_pct: float
    capacity_utilization_pct: float
    selected_mission_count: int
    deferred_mission_count: int
    confidence: float


class SimulationResponse(BaseModel):
    portfolio_id: str
    scenarios: List[ScenarioResult]
    recommendation: str


# ─────────────────────── Rebalance Schemas ───────────────────────────────────

class RebalanceRequest(BaseModel):
    reason: str
    force: bool = False


class RebalanceResponse(BaseModel):
    portfolio_id: str
    new_version: str
    parent_version: str
    requires_governance: bool
    governance_approval_id: Optional[str] = None
    risk_change: float
    expected_value_change: float
    summary: str


# ─────────────────────── Approve Schemas ─────────────────────────────────────

class ApproveDecisionRequest(BaseModel):
    decision_id: str
    approved_by: str
    comment: Optional[str] = None


# ─────────────────────── Overview Schema ─────────────────────────────────────

class PortfolioOverviewResponse(BaseModel):
    organization_id: str
    total_portfolios: int
    active_portfolios: int
    total_expected_value: float
    total_allocated_budget: float
    missions_selected: int
    missions_deferred: int
    missions_at_risk: int
    portfolios_requiring_rebalance: int
    overall_health: str


# ─────────────────────── v2.7.0 Initiative & Trade-Off Schemas ───────────────

class PortfolioInitiativeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    strategic_objective_id: Optional[str] = None
    priority: MissionPriority = MissionPriority.MEDIUM
    expected_value: float = Field(default=0.0, ge=0.0)
    expected_roi: float = Field(default=0.0)
    success_probability: float = Field(default=80.0, ge=0.0, le=100.0)
    risk_score: float = Field(default=20.0, ge=0.0, le=100.0)
    time_to_impact_days: int = Field(default=90, ge=1)
    resource_cost: float = Field(default=0.0, ge=0.0)
    capital_budget: float = Field(default=0.0, ge=0.0)


class PortfolioInitiativeResponse(BaseModel):
    id: str
    organization_id: str
    portfolio_id: str
    title: str
    description: Optional[str] = None
    strategic_objective_id: Optional[str] = None
    priority: MissionPriority
    priority_score: float
    expected_value: float
    expected_roi: float
    success_probability: float
    risk_score: float
    time_to_impact_days: int
    resource_cost: float
    capital_budget: float
    status: str
    selection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PortfolioRecommendationResponse(BaseModel):
    id: str
    organization_id: str
    portfolio_id: str
    initiative_id: Optional[str] = None
    mission_id: Optional[str] = None
    recommendation_type: RecommendationAction
    title: str
    reason: str
    expected_impact: Optional[str] = None
    risk_level: str
    requires_governance: bool
    governance_approval_id: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CapitalAllocationResponse(BaseModel):
    portfolio_id: str
    total_budget: Optional[float]
    current_spend: float
    allocated_budget: float
    unused_budget: Optional[float]
    budget_shortage: float
    expected_portfolio_roi: Optional[float]
    allocation_breakdown: List[Dict[str, Any]]
    data_quality: str  # SUFFICIENT or INSUFFICIENT_DATA
    explanation: str


class TradeoffResult(BaseModel):
    option_a_id: str
    option_a_title: str
    option_b_id: str
    option_b_title: str
    prioritize_a_tradeoffs: List[str]
    prioritize_b_tradeoffs: List[str]
    expected_value_delta: float
    risk_delta: float
    resource_efficiency_delta: float
    recommendation: str


class TradeoffResponse(BaseModel):
    portfolio_id: str
    tradeoffs: List[TradeoffResult]
    summary: str


class DoNothingScenarioResult(BaseModel):
    scenario_type: str  # CURRENT_PORTFOLIO, OPTIMIZED_PORTFOLIO, DO_NOTHING
    expected_value: float
    expected_roi: float
    risk_score: float
    resource_utilization_pct: float
    budget_utilization_pct: float
    mission_completion_rate: float
    strategic_progress_pct: float
    summary: str


class DoNothingSimulationResponse(BaseModel):
    portfolio_id: str
    current: DoNothingScenarioResult
    optimized: DoNothingScenarioResult
    do_nothing: DoNothingScenarioResult
    recommendation: str
    is_side_effect_free: bool = True
