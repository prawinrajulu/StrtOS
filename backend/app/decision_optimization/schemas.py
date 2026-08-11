# Decision Optimization Pydantic Schemas (v1.9.0)
"""Schemas for request and response payloads used by the decision optimization
pipeline. All models are Pydantic v2 and enforce strict validation. Enums are
derived from the existing system where possible.
"""

from __future__ import annotations

from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, model_validator

# Import existing enums where appropriate to avoid duplication
from app.governance.models import RiskLevel as GovRiskLevel
from app.execution.models import AutonomyMode
from app.auth.models import UserRole

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ActionTypeEnum(str, Enum):
    """Allowed action types – must match the ActionRegistry entries.
    The values are dynamically populated at runtime from the registry, but we
    keep a static fallback list for validation. The list should be kept in sync
    with `app.execution.action_registry.ActionRegistry`.
    """
    GENERATE_REPORT = "GENERATE_REPORT"
    RUN_WEBSITE_AUDIT = "RUN_WEBSITE_AUDIT"
    RUN_SEO_AUDIT = "RUN_SEO_AUDIT"
    RUN_COMPETITOR_RESEARCH = "RUN_COMPETITOR_RESEARCH"
    RUN_PAGESPEED_ANALYSIS = "RUN_PAGESPEED_ANALYSIS"
    COLLECT_BUSINESS_DATA = "COLLECT_BUSINESS_DATA"
    REFRESH_CLIENT_ANALYSIS = "REFRESH_CLIENT_ANALYSIS"
    CREATE_CAMPAIGN_DRAFT = "CREATE_CAMPAIGN_DRAFT"
    GENERATE_MARKETING_PLAN = "GENERATE_MARKETING_PLAN"
    RECORD_OUTCOME = "RECORD_OUTCOME"

class CandidateStatusEnum(str, Enum):
    PENDING = "PENDING"
    ENRICHED = "ENRICHED"
    EVALUATED = "EVALUATED"
    REJECTED = "REJECTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

class RiskLevelEnum(str, Enum):
    LOW = GovRiskLevel.LOW.value
    MEDIUM = GovRiskLevel.MEDIUM.value
    HIGH = GovRiskLevel.HIGH.value
    CRITICAL = GovRiskLevel.CRITICAL.value

class PlanStepStatusEnum(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED_BY_DEPENDENCY = "BLOCKED_BY_DEPENDENCY"
    CANCELLED = "CANCELLED"

# ---------------------------------------------------------------------------
# Base models for common fields
# ---------------------------------------------------------------------------

class OrganizationScopedBase(BaseModel):
    organization_id: str = Field(..., description="Tenant identifier, enforced by all services.")
    client_id: Optional[str] = Field(None, description="Optional client identifier.")
    workflow_id: Optional[str] = Field(None, description="Optional workflow identifier.")
    decision_id: Optional[str] = Field(None, description="Optional decision context identifier.")

    model_config = ConfigDict(extra="forbid")

# ---------------------------------------------------------------------------
# Action Candidate Schemas
# ---------------------------------------------------------------------------

class ActionCandidateCreate(OrganizationScopedBase):
    action_type: ActionTypeEnum = Field(..., description="Action type – must be registered in the ActionRegistry.")
    supporting_evidence: Optional[Dict[str, Any]] = Field(None, description="Evidence JSON from the Knowledge Graph.")
    supporting_memory: Optional[Dict[str, Any]] = Field(None, description="Memory records related to the candidate.")

class ActionCandidateResponse(OrganizationScopedBase):
    id: str = Field(..., description="UUID of the candidate record.")
    action_type: ActionTypeEnum
    expected_value: Optional[float] = None
    expected_cost: Optional[float] = None
    expected_roi: Optional[float] = None
    expected_confidence: Optional[float] = None
    expected_risk: Optional[RiskLevelEnum] = None
    causal_support: Optional[float] = None
    historical_success: Optional[float] = None
    agent_reliability: Optional[float] = None
    reversibility: Optional[str] = None
    time_to_impact: Optional[int] = None
    status: CandidateStatusEnum = Field(default=CandidateStatusEnum.PENDING)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

    model_config = ConfigDict(from_attributes=True)

class ActionCandidateListResponse(BaseModel):
    candidates: List[ActionCandidateResponse]
    total: int

# ---------------------------------------------------------------------------
# Action Evaluation Schemas
# ---------------------------------------------------------------------------

class ActionEvaluationRequest(OrganizationScopedBase):
    candidate_id: str = Field(..., description="The candidate to be evaluated.")
    overrides: Optional[Dict[str, Any]] = Field(None, description="Optional overrides for deterministic optimizer.")

class ActionEvaluationResponse(BaseModel):
    id: str
    candidate_id: str
    score_breakdown: Dict[str, float]
    total_score: float
    recommendation: Optional[str] = None
    risk_level: RiskLevelEnum
    status: Literal["COMPLETED"] = "COMPLETED"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Action Comparison Schemas
# ---------------------------------------------------------------------------

class ActionComparisonRequest(OrganizationScopedBase):
    candidate_ids: List[str] = Field(..., min_items=2, description="At least two candidate IDs to compare.")

class ActionComparisonResponse(BaseModel):
    compared: List[ActionEvaluationResponse]
    best_candidate_id: Optional[str] = None
    explanation: str

# ---------------------------------------------------------------------------
# Simulation Schemas
# ---------------------------------------------------------------------------

class SimulationRequest(OrganizationScopedBase):
    candidate_ids: List[str] = Field(..., description="Candidates to simulate together.")
    horizon_minutes: Optional[int] = Field(60, description="Planning horizon for simulation.")

class SimulationResponse(BaseModel):
    simulation_id: str
    outcomes: Dict[str, Any]
    explanation: str
    created_at: datetime

# ---------------------------------------------------------------------------
# Action Plan Schemas
# ---------------------------------------------------------------------------

class ActionPlanCreate(OrganizationScopedBase):
    candidates: List[str] = Field(..., description="Ordered list of candidate IDs to include in the plan.")
    dependencies: Optional[Dict[str, List[str]]] = Field(
        None,
        description="Mapping of candidate_id -> list of predecessor candidate_ids.",
    )

class ActionPlanStepResponse(BaseModel):
    id: str
    action_id: str
    step_order: int
    dependency: Optional[str] = None
    estimated_cost: Optional[float] = None
    estimated_time: Optional[int] = None
    risk_level: RiskLevelEnum
    rollback_strategy: Optional[str] = None
    success_metric: Optional[str] = None
    status: PlanStepStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ActionPlanResponse(BaseModel):
    plan_id: str
    steps: List[ActionPlanStepResponse]
    status: Literal["PENDING", "READY", "RUNNING", "COMPLETED", "FAILED"]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Recommendation Schemas
# ---------------------------------------------------------------------------

class RecommendationResponse(BaseModel):
    decision_id: str
    recommended_action: ActionCandidateResponse
    alternatives: List[ActionCandidateResponse]
    score_breakdown: Dict[str, float]
    explanation: str
    risk_level: RiskLevelEnum
    governance_required: bool

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Governance Submission Schemas
# ---------------------------------------------------------------------------

class GovernanceSubmissionResponse(BaseModel):
    governance_id: str
    decision_id: str
    approved: bool
    reviewer_user_id: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Execution Schemas
# ---------------------------------------------------------------------------

class ExecutionResponse(BaseModel):
    execution_id: str
    action_id: str
    status: Literal["STARTED", "COMPLETED", "FAILED"]
    result: Optional[Dict[str, Any]] = None
    started_at: datetime
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Decision Explanation Schemas
# ---------------------------------------------------------------------------

class DecisionExplanationResponse(BaseModel):
    decision_id: str
    explanation: str
    evidence: List[Dict[str, Any]]
    memory_links: List[Dict[str, Any]]
    causal_links: List[Dict[str, Any]]
    prediction_links: List[Dict[str, Any]]
    agent_contributions: List[Dict[str, Any]]
    policy_version: Optional[str] = None
    risk_analysis: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------------------------
# Overview Schemas
# ---------------------------------------------------------------------------

class DecisionOptimizationOverviewResponse(BaseModel):
    total_candidates: int
    recommended_actions: int
    pending_approvals: int
    executed_actions: int
    success_rate: float
    expected_roi: float
    decision_confidence: float
    recent_decisions: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)

# End of schemas
