from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.resources.models import (
    ResourceType, ResourceStatus, AllocationPlanStatus,
    BottleneckSeverity, ConflictSeverity
)


# ─────────────────────── Resource CRUD Schemas ────────────────────────────────

class ResourceCreate(BaseModel):
    name: str
    resource_type: ResourceType
    description: Optional[str] = None
    total_capacity: Optional[float] = Field(None, ge=0.0)
    available_capacity: Optional[float] = Field(None, ge=0.0)
    unit: str = "UNITS"
    cost_per_unit: Optional[float] = None
    client_id: Optional[str] = None
    is_shared: bool = False
    metadata_json: Optional[Dict[str, Any]] = None


class ResourceUpdate(BaseModel):
    total_capacity: Optional[float] = Field(None, ge=0.0)
    available_capacity: Optional[float] = Field(None, ge=0.0)
    cost_per_unit: Optional[float] = None
    status: Optional[ResourceStatus] = None


class ResourceResponse(BaseModel):
    id: str
    organization_id: str
    client_id: Optional[str] = None
    name: str
    resource_type: ResourceType
    description: Optional[str] = None
    total_capacity: Optional[float] = None
    available_capacity: Optional[float] = None
    allocated_capacity: float
    utilization_percentage: float
    unit: str
    cost_per_unit: Optional[float] = None
    status: ResourceStatus
    is_shared: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────── Capacity Schemas ────────────────────────────────────

class CapacityResponse(BaseModel):
    resource_id: str
    resource_name: str
    resource_type: ResourceType
    total_capacity: Optional[float]
    available_capacity: Optional[float]
    allocated_capacity: float
    remaining_capacity: float
    utilization_percentage: float
    status: ResourceStatus
    is_measured: bool
    shortage_detected: bool
    shortage_amount: float


class UtilizationOverview(BaseModel):
    organization_id: str
    total_resources: int
    available_count: int
    limited_count: int
    exhausted_count: int
    unknown_count: int
    blocked_count: int
    degraded_count: int
    overall_utilization_pct: float
    highest_utilization_resource: Optional[str]
    highest_utilization_pct: float


# ─────────────────────── Bottleneck Schemas ──────────────────────────────────

class BottleneckResult(BaseModel):
    resource_id: str
    resource_name: str
    resource_type: ResourceType
    current_capacity: Optional[float]
    required_capacity: float
    shortage: float
    shortage_pct: float
    affected_mission_ids: List[str]
    severity: BottleneckSeverity
    recommended_action: str


class BottleneckResponse(BaseModel):
    organization_id: str
    bottlenecks: List[BottleneckResult]
    critical_count: int
    high_count: int
    total_count: int
    summary: str


# ─────────────────────── Conflict Schemas ────────────────────────────────────

class ConflictResult(BaseModel):
    conflict_id: str
    resource_id: str
    resource_name: str
    resource_type: ResourceType
    mission_ids: List[str]
    required_capacity: float
    available_capacity: float
    shortage: float
    severity: ConflictSeverity
    resolution_options: List[str]


class ConflictResponse(BaseModel):
    organization_id: str
    conflicts: List[ConflictResult]
    critical_count: int
    total_count: int
    summary: str


# ─────────────────────── Priority Schemas ────────────────────────────────────

class MissionResourcePriority(BaseModel):
    mission_id: str
    mission_title: str
    priority_score: float
    rank: int
    strategic_value: float
    urgency_score: float
    expected_value: float
    risk_penalty: float
    opportunity_cost_score: float
    reason: str
    tradeoffs: List[str]


class PriorityResponse(BaseModel):
    organization_id: str
    ranked_missions: List[MissionResourcePriority]
    explanation: str


# ─────────────────────── Opportunity Cost Schemas ────────────────────────────

class OpportunityCostResult(BaseModel):
    selected_mission_id: str
    alternative_mission_id: str
    expected_value_difference: float
    resource_difference: float
    risk_difference: float
    opportunity_cost_score: float
    explanation: str
    data_quality: str  # SUFFICIENT, INSUFFICIENT_DATA


# ─────────────────────── Simulation Schemas ──────────────────────────────────

class SimulationRequest(BaseModel):
    scenario_type: str = "CURRENT_CAPACITY"
    capacity_delta_pct: float = 0.0
    budget_delta_pct: float = 0.0
    additional_humans: int = 0
    additional_agents: int = 0
    custom_overrides: Optional[Dict[str, float]] = None


class SimulationScenarioResult(BaseModel):
    scenario_type: str
    feasible_mission_ids: List[str]
    blocked_mission_ids: List[str]
    bottleneck_count: int
    budget_utilization_pct: float
    capacity_utilization_pct: float
    expected_value: float
    opportunity_cost_score: float
    strategic_impact_summary: str


class SimulationResponse(BaseModel):
    portfolio_id: Optional[str] = None
    organization_id: str
    scenario: SimulationScenarioResult
    recommendation: str
    is_side_effect_free: bool = True


# ─────────────────────── Allocation Plan Schemas ─────────────────────────────

class AllocationEntryRequest(BaseModel):
    mission_id: str
    resource_id: str
    requested_amount: float = Field(..., ge=0.0)
    is_mandatory: bool = True
    priority_score: float = Field(default=50.0, ge=0.0, le=100.0)


class AllocationPlanCreate(BaseModel):
    title: str
    portfolio_id: Optional[str] = None
    entries: List[AllocationEntryRequest] = []


class AllocationPlanResponse(BaseModel):
    id: str
    organization_id: str
    portfolio_id: Optional[str]
    version: str
    status: AllocationPlanStatus
    title: str
    summary: Optional[str]
    resource_allocations_json: Optional[Dict[str, Any]]
    bottlenecks_json: Optional[Dict[str, Any]]
    conflicts_json: Optional[Dict[str, Any]]
    expected_value: float
    risk_score: float
    confidence_score: float
    explanation: Optional[str]
    governance_approval_id: Optional[str]
    approved_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────── Mission Resource Requirement Schemas ─────────────────

class MissionResourceRequirement(BaseModel):
    resource_type: ResourceType
    required_amount: float
    estimated_duration_hours: Optional[float] = None
    priority: str = "HIGH"
    is_mandatory: bool = True
    dependency: Optional[str] = None
    notes: Optional[str] = None


class MissionResourceRequirementsResponse(BaseModel):
    mission_id: str
    requirements: List[MissionResourceRequirement]
    total_estimated_cost: Optional[float]
    feasibility: str  # FEASIBLE, AT_RISK, INFEASIBLE, UNKNOWN


# ─────────────────────── Overview Schema ─────────────────────────────────────

class ResourceOverviewResponse(BaseModel):
    organization_id: str
    total_resources: int
    resources_available: int
    resources_limited: int
    resources_exhausted: int
    resources_unknown: int
    active_allocation_plans: int
    open_bottlenecks: int
    open_conflicts: int
    overall_capacity_health: str
    top_bottleneck_type: Optional[str]
    governance_pending_count: int
