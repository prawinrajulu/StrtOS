from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import UserModel
from app.resources.schemas import (
    ResourceCreate, ResourceResponse, CapacityResponse, UtilizationOverview,
    BottleneckResponse, ConflictResponse, SimulationRequest, SimulationResponse,
    AllocationPlanCreate, AllocationPlanResponse, MissionResourceRequirementsResponse,
    ResourceOverviewResponse
)
from app.resources.models import ResourceType
from app.resources.service import ResourceService

router = APIRouter(prefix="/resources", tags=["Autonomous Resource & Capacity Intelligence"])


def org_id(user: UserModel) -> str:
    return user.organization_id


# ─────────────────────────── Overview ────────────────────────────────────────

@router.get("/overview", response_model=ResourceOverviewResponse)
async def get_resource_overview(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Resource & Capacity Command Center overview."""
    svc = ResourceService(db)
    return await svc.get_overview(org_id(current_user))


# ─────────────────────────── Resources ───────────────────────────────────────

@router.get("/resources", response_model=List[ResourceResponse])
async def list_resources(
    resource_type: Optional[ResourceType] = Query(None),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all resources for the organization."""
    svc = ResourceService(db)
    return await svc.list_resources(org_id(current_user), resource_type=resource_type)


@router.post("/resources", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    payload: ResourceCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Register a new organizational resource."""
    svc = ResourceService(db)
    return await svc.create_resource(payload, org_id(current_user))


@router.get("/resources/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific resource with full utilization details."""
    svc = ResourceService(db)
    try:
        return await svc.get_resource(resource_id, org_id(current_user))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─────────────────────────── Capacity & Utilization ──────────────────────────

@router.get("/capacity", response_model=List[CapacityResponse])
async def get_capacity_overview(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Capacity availability for all resources."""
    svc = ResourceService(db)
    return await svc.get_capacity_overview(org_id(current_user))


@router.get("/utilization", response_model=UtilizationOverview)
async def get_utilization_overview(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Utilization summary across all resources."""
    svc = ResourceService(db)
    return await svc.get_utilization_overview(org_id(current_user))


# ─────────────────────────── Bottlenecks & Conflicts ─────────────────────────

@router.get("/bottlenecks", response_model=BottleneckResponse)
async def get_bottlenecks(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Detect and classify all resource bottlenecks."""
    svc = ResourceService(db)
    return await svc.detect_bottlenecks(org_id(current_user))


@router.get("/conflicts", response_model=ConflictResponse)
async def get_conflicts(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Detect all active resource conflicts between missions."""
    svc = ResourceService(db)
    return await svc.detect_conflicts(org_id(current_user))


# ─────────────────────────── Allocation Plans ────────────────────────────────

@router.get("/allocations", response_model=List[AllocationPlanResponse])
async def list_allocation_plans(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all resource allocation plans."""
    svc = ResourceService(db)
    return await svc.list_allocation_plans(org_id(current_user))


@router.post("/allocations/simulate", response_model=SimulationResponse)
async def simulate_allocation(
    payload: SimulationRequest,
    missions: List[Dict[str, Any]] = Body(default=[]),
    requirements: List[Dict[str, Any]] = Body(default=[]),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Side-effect free resource allocation simulation."""
    svc = ResourceService(db)
    return await svc.simulate(payload, org_id(current_user), missions, requirements)


@router.post("/allocations/recommend")
async def recommend_allocation(
    missions: List[Dict[str, Any]] = Body(default=[]),
    requirements: List[Dict[str, Any]] = Body(default=[]),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate deterministic resource allocation recommendation."""
    svc = ResourceService(db)
    return await svc.recommend_allocation(org_id(current_user), missions, requirements)


@router.post("/allocations/plan", response_model=AllocationPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_allocation_plan(
    payload: AllocationPlanCreate,
    missions: List[Dict[str, Any]] = Body(default=[]),
    requirements: List[Dict[str, Any]] = Body(default=[]),
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a full resource allocation plan with governance routing."""
    svc = ResourceService(db)
    return await svc.create_allocation_plan(payload, org_id(current_user), missions, requirements)


@router.get("/allocations/{plan_id}", response_model=AllocationPlanResponse)
async def get_allocation_plan(
    plan_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific allocation plan."""
    svc = ResourceService(db)
    try:
        return await svc.get_allocation_plan(plan_id, org_id(current_user))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/allocations/{plan_id}/explanation")
async def get_plan_explanation(
    plan_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get full causal explanation of an allocation plan."""
    svc = ResourceService(db)
    try:
        plan = await svc.get_allocation_plan(plan_id, org_id(current_user))
        return {
            "plan_id": plan_id,
            "explanation": plan.explanation,
            "risk_score": plan.risk_score,
            "confidence_score": plan.confidence_score,
            "expected_value": plan.expected_value,
            "causal_chain": [
                "EVIDENCE: Resource capacity measured from registered resource pool.",
                "MEMORY: Historical allocation patterns consulted.",
                "KNOWLEDGE: Mission-resource dependency graph applied.",
                "FORECAST: Future capacity trends incorporated.",
                "PRIORITY: Missions ranked by strategic value, urgency, and expected outcome.",
                "ALLOCATION: Greedy priority allocation under capacity constraints.",
                "GOVERNANCE: Risk-based governance gate applied.",
                f"DECISION: Plan status = {plan.status.value}. {plan.explanation}"
            ]
        }
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/allocations/{plan_id}/submit-governance")
async def submit_plan_for_governance(
    plan_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit an allocation plan for governance review."""
    svc = ResourceService(db)
    try:
        return await svc.submit_governance(plan_id, org_id(current_user), current_user.id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/allocations/{plan_id}/approve")
async def approve_allocation_plan(
    plan_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve an allocation plan (governance-authorized users only)."""
    from app.auth.models import UserRole
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Insufficient role to approve allocation plans.")
    svc = ResourceService(db)
    try:
        return await svc.approve_plan(plan_id, org_id(current_user), current_user.id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/allocations/{plan_id}/activate")
async def activate_allocation_plan(
    plan_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Activate an approved allocation plan."""
    svc = ResourceService(db)
    try:
        return await svc.activate_plan(plan_id, org_id(current_user))
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─────────────────────────── Mission Resources ───────────────────────────────

@router.get("/missions/{mission_id}/resources", response_model=MissionResourceRequirementsResponse)
async def get_mission_resources(
    mission_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get resource requirements for a mission based on its step types."""
    svc = ResourceService(db)
    return await svc.get_mission_resources(mission_id, org_id(current_user))
