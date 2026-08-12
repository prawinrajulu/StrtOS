"""
Resource Service — orchestration layer.

Coordinates: ResourceRepository, engines, GovernanceService, EventPublisher.
Integrates with: MissionService, PortfolioService, AgentIntelligenceService.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.resources.models import (
    ResourceModel, ResourceCapacityModel, ResourceAllocationModel,
    ResourceConflictModel, ResourceUtilizationModel,
    ResourceAllocationPlanModel, ResourceAllocationPlanVersionModel,
    ResourceStatus, AllocationPlanStatus, ResourceType
)
from app.resources.schemas import (
    ResourceCreate, ResourceResponse, CapacityResponse, UtilizationOverview,
    BottleneckResponse, ConflictResponse, PriorityResponse,
    OpportunityCostResult, SimulationRequest, SimulationResponse,
    AllocationPlanCreate, AllocationPlanResponse, MissionResourceRequirementsResponse,
    ResourceOverviewResponse
)
from app.resources.repository import ResourceRepository
from app.resources.engine import (
    ResourceCapacityEngine, ResourceBottleneckEngine, ResourceConflictEngine,
    ResourcePriorityEngine, OpportunityCostEngine
)
from app.resources.allocator import ResourceAllocationEngine
from app.resources.capacity import MissionCapacityAnalyzer
from app.resources.simulation import ResourceSimulationEngine
from app.core.events.publisher import event_publisher
from app.core.logging import logger


GOVERNANCE_RISK_THRESHOLD = 70.0
GOVERNANCE_BUDGET_THRESHOLD = 0.90


class ResourceService:
    """Orchestrates all resource intelligence operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ResourceRepository(session)
        self.capacity_engine = ResourceCapacityEngine()
        self.bottleneck_engine = ResourceBottleneckEngine()
        self.conflict_engine = ResourceConflictEngine()
        self.priority_engine = ResourcePriorityEngine()
        self.opportunity_engine = OpportunityCostEngine()
        self.alloc_engine = ResourceAllocationEngine()
        self.mission_analyzer = MissionCapacityAnalyzer()
        self.sim_engine = ResourceSimulationEngine()

    # ─────────────────────────────────────────────────────────────────────────
    # RESOURCE CRUD
    # ─────────────────────────────────────────────────────────────────────────

    async def create_resource(self, payload: ResourceCreate, org_id: str) -> ResourceResponse:
        resource = ResourceModel(
            organization_id=org_id,
            client_id=payload.client_id,
            name=payload.name,
            resource_type=payload.resource_type,
            description=payload.description,
            total_capacity=payload.total_capacity,
            available_capacity=payload.available_capacity,
            allocated_capacity=0.0,
            utilization_percentage=0.0,
            unit=payload.unit,
            cost_per_unit=payload.cost_per_unit,
            is_shared=payload.is_shared,
            status=ResourceStatus.UNKNOWN if payload.total_capacity is None else ResourceStatus.AVAILABLE,
            metadata_json=payload.metadata_json
        )
        saved = await self.repo.create_resource(resource)

        # Recalculate utilization
        util_pct, _, _, status = self.capacity_engine.compute_utilization(
            saved.total_capacity, saved.allocated_capacity
        )
        await self.repo.update_resource_fields(saved.id, org_id, utilization_percentage=util_pct, status=status)
        saved = await self.repo.get_resource_by_id(saved.id, org_id)

        await event_publisher.publish(
            event_type="resource.created",
            organization_id=org_id,
            message=f"Resource '{saved.name}' ({saved.resource_type.value}) created.",
            metadata={"resource_id": saved.id, "resource_type": saved.resource_type.value}
        )

        return ResourceResponse.model_validate(saved)

    async def list_resources(self, org_id: str, resource_type=None) -> List[ResourceResponse]:
        resources = await self.repo.list_resources(org_id, resource_type=resource_type)
        return [ResourceResponse.model_validate(r) for r in resources]

    async def get_resource(self, resource_id: str, org_id: str) -> ResourceResponse:
        r = await self.repo.get_resource_by_id(resource_id, org_id)
        if not r:
            raise KeyError(f"Resource '{resource_id}' not found.")
        return ResourceResponse.model_validate(r)

    # ─────────────────────────────────────────────────────────────────────────
    # CAPACITY
    # ─────────────────────────────────────────────────────────────────────────

    async def get_capacity_overview(self, org_id: str) -> List[CapacityResponse]:
        resources = await self.repo.list_resources(org_id)
        return [
            self.capacity_engine.build_capacity_response(
                resource_id=r.id,
                resource_name=r.name,
                resource_type=r.resource_type,
                total_capacity=r.total_capacity,
                allocated_capacity=r.allocated_capacity,
                is_measured=bool(r.capacities and any(c.is_measured for c in r.capacities))
            )
            for r in resources
        ]

    async def get_utilization_overview(self, org_id: str) -> UtilizationOverview:
        resources = await self.repo.list_resources(org_id)
        counts = {s: 0 for s in ResourceStatus}
        total_util = 0.0
        highest_util = 0.0
        highest_name = None

        for r in resources:
            counts[r.status] = counts.get(r.status, 0) + 1
            total_util += r.utilization_percentage
            if r.utilization_percentage > highest_util:
                highest_util = r.utilization_percentage
                highest_name = r.name

        avg_util = round(total_util / max(1, len(resources)), 1) if resources else 0.0

        return UtilizationOverview(
            organization_id=org_id,
            total_resources=len(resources),
            available_count=counts.get(ResourceStatus.AVAILABLE, 0),
            limited_count=counts.get(ResourceStatus.LIMITED, 0),
            exhausted_count=counts.get(ResourceStatus.EXHAUSTED, 0),
            unknown_count=counts.get(ResourceStatus.UNKNOWN, 0),
            blocked_count=counts.get(ResourceStatus.BLOCKED, 0),
            degraded_count=counts.get(ResourceStatus.DEGRADED, 0),
            overall_utilization_pct=avg_util,
            highest_utilization_resource=highest_name,
            highest_utilization_pct=highest_util
        )

    # ─────────────────────────────────────────────────────────────────────────
    # BOTTLENECKS
    # ─────────────────────────────────────────────────────────────────────────

    async def detect_bottlenecks(
        self,
        org_id: str,
        mission_requirements: Optional[List[Dict[str, Any]]] = None
    ) -> BottleneckResponse:
        resources = await self.repo.list_resources(org_id)
        resource_dicts = [
            {
                "resource_id": r.id,
                "resource_name": r.name,
                "resource_type": r.resource_type,
                "total_capacity": r.total_capacity,
                "allocated_capacity": r.allocated_capacity
            }
            for r in resources
        ]
        reqs = mission_requirements or []
        result = self.bottleneck_engine.detect_bottlenecks(resource_dicts, reqs)
        result.organization_id = org_id

        if result.critical_count > 0:
            await event_publisher.publish(
                event_type="resource.bottleneck.detected",
                organization_id=org_id,
                message=f"CRITICAL bottleneck detected: {result.critical_count} resources critically constrained.",
                metadata={"critical_count": result.critical_count, "total": result.total_count}
            )

        return result

    # ─────────────────────────────────────────────────────────────────────────
    # CONFLICTS
    # ─────────────────────────────────────────────────────────────────────────

    async def detect_conflicts(
        self,
        org_id: str,
        mission_requirements: Optional[List[Dict[str, Any]]] = None
    ) -> ConflictResponse:
        resources = await self.repo.list_resources(org_id)
        resource_dicts = [
            {
                "resource_id": r.id,
                "resource_name": r.name,
                "resource_type": r.resource_type,
                "total_capacity": r.total_capacity,
                "allocated_capacity": r.allocated_capacity
            }
            for r in resources
        ]
        reqs = mission_requirements or []
        result = self.conflict_engine.detect_conflicts(resource_dicts, reqs)
        result.organization_id = org_id

        for conflict in result.conflicts:
            await self.repo.add_conflict(ResourceConflictModel(
                organization_id=org_id,
                resource_id=conflict.resource_id,
                mission_ids_json=conflict.mission_ids,
                required_capacity=conflict.required_capacity,
                available_capacity=conflict.available_capacity,
                shortage=conflict.shortage,
                severity=conflict.severity,
                resolution_options_json=conflict.resolution_options
            ))

        if result.conflicts:
            await event_publisher.publish(
                event_type="resource.conflict.detected",
                organization_id=org_id,
                message=f"{result.total_count} resource conflict(s) detected.",
                metadata={"total": result.total_count, "critical": result.critical_count}
            )

        return result

    # ─────────────────────────────────────────────────────────────────────────
    # SIMULATION (side-effect free)
    # ─────────────────────────────────────────────────────────────────────────

    async def simulate(
        self,
        payload: SimulationRequest,
        org_id: str,
        missions: List[Dict[str, Any]],
        requirements: List[Dict[str, Any]]
    ) -> SimulationResponse:
        resources = await self.repo.list_resources(org_id)
        resource_dicts = [
            {
                "resource_id": r.id,
                "resource_name": r.name,
                "resource_type": r.resource_type.value,
                "total_capacity": r.total_capacity,
                "allocated_capacity": r.allocated_capacity
            }
            for r in resources
        ]
        result = self.sim_engine.simulate(
            scenario_type=payload.scenario_type,
            resources=resource_dicts,
            missions=missions,
            requirements=requirements,
            org_id=org_id,
            capacity_delta_pct=payload.capacity_delta_pct,
            budget_delta_pct=payload.budget_delta_pct,
            additional_humans=payload.additional_humans,
            additional_agents=payload.additional_agents,
            custom_overrides=payload.custom_overrides
        )
        await event_publisher.publish(
            event_type="resource.allocation.simulated",
            organization_id=org_id,
            message=f"Resource simulation '{payload.scenario_type}' completed.",
            metadata={"scenario": payload.scenario_type, "is_side_effect_free": True}
        )
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # RECOMMENDATION
    # ─────────────────────────────────────────────────────────────────────────

    async def recommend_allocation(
        self,
        org_id: str,
        missions: List[Dict[str, Any]],
        requirements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        resources = await self.repo.list_resources(org_id)
        resource_dicts = [
            {
                "resource_id": r.id,
                "resource_name": r.name,
                "resource_type": r.resource_type.value,
                "total_capacity": r.total_capacity,
                "allocated_capacity": r.allocated_capacity
            }
            for r in resources
        ]
        result = self.alloc_engine.allocate(missions, resource_dicts, requirements, org_id)

        await event_publisher.publish(
            event_type="resource.allocation.recommended",
            organization_id=org_id,
            message=f"Resource allocation recommendation generated. {len(result['constrained_missions'])} mission(s) constrained.",
            metadata={"constrained_count": len(result["constrained_missions"])}
        )
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # ALLOCATION PLAN
    # ─────────────────────────────────────────────────────────────────────────

    async def create_allocation_plan(
        self,
        payload: AllocationPlanCreate,
        org_id: str,
        missions: List[Dict[str, Any]],
        requirements: List[Dict[str, Any]]
    ) -> AllocationPlanResponse:
        # Run bottleneck and conflict detection
        btk = await self.detect_bottlenecks(org_id, requirements)
        conflicts = await self.detect_conflicts(org_id, requirements)

        # Run allocation recommendation
        resources = await self.repo.list_resources(org_id)
        resource_dicts = [
            {
                "resource_id": r.id,
                "resource_name": r.name,
                "resource_type": r.resource_type.value,
                "total_capacity": r.total_capacity,
                "allocated_capacity": r.allocated_capacity
            }
            for r in resources
        ]
        alloc = self.alloc_engine.allocate(missions, resource_dicts, requirements, org_id)

        risk_score = round(alloc["risk_score"], 1)
        needs_governance = risk_score >= GOVERNANCE_RISK_THRESHOLD or btk.critical_count > 0

        plan = ResourceAllocationPlanModel(
            organization_id=org_id,
            portfolio_id=payload.portfolio_id,
            version="v1.0.0",
            status=AllocationPlanStatus.SIMULATED,
            title=payload.title,
            summary=alloc["explanation"],
            resource_allocations_json={"entries": alloc["allocated"], "pool": alloc["pool_snapshot"]},
            bottlenecks_json={"count": btk.total_count, "critical": btk.critical_count,
                              "items": [b.model_dump() for b in btk.bottlenecks]},
            conflicts_json={"count": conflicts.total_count,
                            "items": [c.model_dump() for c in conflicts.conflicts]},
            expected_value=alloc["total_expected_value"],
            risk_score=risk_score,
            confidence_score=alloc["confidence"],
            explanation=alloc["explanation"]
        )

        saved_plan = await self.repo.create_plan(plan)

        # Add initial version
        await self.repo.add_plan_version(ResourceAllocationPlanVersionModel(
            organization_id=org_id,
            plan_id=saved_plan.id,
            version="v1.0.0",
            change_reason="Initial plan creation.",
            snapshot_json={"allocations": alloc["allocated"]},
            risk_change=0.0,
            value_change=0.0
        ))

        # Governance gate
        if needs_governance:
            await self.repo.update_plan_status(
                saved_plan.id, org_id, AllocationPlanStatus.PENDING_GOVERNANCE
            )
            await event_publisher.publish(
                event_type="resource.allocation.governance_pending",
                organization_id=org_id,
                message=f"Allocation plan '{payload.title}' requires governance approval (risk={risk_score}).",
                metadata={"plan_id": saved_plan.id, "risk_score": risk_score}
            )
        else:
            await event_publisher.publish(
                event_type="resource.allocation.recommended",
                organization_id=org_id,
                message=f"Allocation plan '{payload.title}' recommended.",
                metadata={"plan_id": saved_plan.id}
            )

        refreshed = await self.repo.get_plan_by_id(saved_plan.id, org_id)
        return AllocationPlanResponse.model_validate(refreshed)

    async def get_allocation_plan(self, plan_id: str, org_id: str) -> AllocationPlanResponse:
        plan = await self.repo.get_plan_by_id(plan_id, org_id)
        if not plan:
            raise KeyError(f"Plan '{plan_id}' not found.")
        return AllocationPlanResponse.model_validate(plan)

    async def list_allocation_plans(self, org_id: str) -> List[AllocationPlanResponse]:
        plans = await self.repo.list_plans(org_id)
        return [AllocationPlanResponse.model_validate(p) for p in plans]

    async def submit_governance(self, plan_id: str, org_id: str, creator_id: str) -> AllocationPlanResponse:
        plan = await self.repo.get_plan_by_id(plan_id, org_id)
        if not plan:
            raise KeyError(f"Plan '{plan_id}' not found.")

        try:
            from app.governance.service import GovernanceService
            from app.governance.schemas import ApprovalRequestCreate
            from app.governance.models import DecisionType
            gov = GovernanceService(self.session)
            approval = await gov.create_approval_request(
                payload=ApprovalRequestCreate(
                    title=f"Resource Allocation Plan Approval — {plan.title}",
                    description=plan.explanation,
                    decision_type=DecisionType.STRATEGY_CHANGE,
                    requested_action=f"Activate resource allocation plan '{plan.title}' v{plan.version}.",
                    ai_recommendation=plan.explanation,
                    ai_confidence_score=plan.confidence_score,
                    evidence_count=len(plan.resource_allocations_json.get("entries", []) if plan.resource_allocations_json else []),
                    is_reversible=True,
                    has_unavailable_evidence=False
                ),
                org_id=org_id,
                creator_id=creator_id
            )
            updated = await self.repo.update_plan_status(
                plan_id, org_id, AllocationPlanStatus.PENDING_GOVERNANCE,
                governance_approval_id=approval.id
            )
        except Exception as e:
            logger.warning(f"Governance submission warning: {e}")
            updated = plan

        return AllocationPlanResponse.model_validate(updated)

    async def approve_plan(self, plan_id: str, org_id: str, approved_by: str) -> AllocationPlanResponse:
        updated = await self.repo.update_plan_status(
            plan_id, org_id, AllocationPlanStatus.APPROVED, approved_by=approved_by
        )
        if not updated:
            raise KeyError(f"Plan '{plan_id}' not found.")
        await event_publisher.publish(
            event_type="resource.allocation.approved",
            organization_id=org_id,
            message=f"Allocation plan approved by {approved_by}.",
            metadata={"plan_id": plan_id}
        )
        return AllocationPlanResponse.model_validate(updated)

    async def activate_plan(self, plan_id: str, org_id: str) -> AllocationPlanResponse:
        plan = await self.repo.get_plan_by_id(plan_id, org_id)
        if not plan:
            raise KeyError(f"Plan '{plan_id}' not found.")
        if plan.status not in (AllocationPlanStatus.APPROVED, AllocationPlanStatus.SIMULATED):
            raise ValueError(f"Cannot activate plan in status '{plan.status.value}'.")

        updated = await self.repo.update_plan_status(plan_id, org_id, AllocationPlanStatus.ACTIVE)
        await event_publisher.publish(
            event_type="resource.allocation.activated",
            organization_id=org_id,
            message=f"Allocation plan '{plan.title}' activated.",
            metadata={"plan_id": plan_id}
        )
        return AllocationPlanResponse.model_validate(updated)

    # ─────────────────────────────────────────────────────────────────────────
    # MISSION RESOURCES
    # ─────────────────────────────────────────────────────────────────────────

    async def get_mission_resources(
        self,
        mission_id: str,
        org_id: str,
        steps: Optional[List[Dict[str, Any]]] = None
    ) -> MissionResourceRequirementsResponse:
        resources = await self.repo.list_resources(org_id)
        resource_dicts = [
            {
                "resource_type": r.resource_type.value,
                "available_capacity": r.available_capacity,
                "cost_per_unit": r.cost_per_unit
            }
            for r in resources
        ]
        return self.mission_analyzer.analyze_mission_requirements(
            mission_id=mission_id,
            steps=steps or [],
            available_resources=resource_dicts
        )

    # ─────────────────────────────────────────────────────────────────────────
    # OVERVIEW
    # ─────────────────────────────────────────────────────────────────────────

    async def get_overview(self, org_id: str) -> ResourceOverviewResponse:
        resources = await self.repo.list_resources(org_id)
        plans = await self.repo.list_plans(org_id)
        conflicts = await self.repo.list_open_conflicts(org_id)

        status_counts = {s: 0 for s in ResourceStatus}
        for r in resources:
            status_counts[r.status] = status_counts.get(r.status, 0) + 1

        active_plans = [p for p in plans if p.status == AllocationPlanStatus.ACTIVE]
        pending_gov = [p for p in plans if p.status == AllocationPlanStatus.PENDING_GOVERNANCE]

        # Health classification
        if status_counts.get(ResourceStatus.EXHAUSTED, 0) >= 2:
            health = "CRITICAL"
        elif status_counts.get(ResourceStatus.EXHAUSTED, 0) >= 1:
            health = "AT_RISK"
        elif status_counts.get(ResourceStatus.LIMITED, 0) >= 2:
            health = "WATCH"
        elif status_counts.get(ResourceStatus.UNKNOWN, 0) == len(resources):
            health = "UNKNOWN"
        else:
            health = "HEALTHY"

        # Top bottleneck type (most constrained)
        top_bottleneck = None
        worst_util = 0.0
        for r in resources:
            if r.utilization_percentage > worst_util:
                worst_util = r.utilization_percentage
                top_bottleneck = r.resource_type.value if r.resource_type else None

        return ResourceOverviewResponse(
            organization_id=org_id,
            total_resources=len(resources),
            resources_available=status_counts.get(ResourceStatus.AVAILABLE, 0),
            resources_limited=status_counts.get(ResourceStatus.LIMITED, 0),
            resources_exhausted=status_counts.get(ResourceStatus.EXHAUSTED, 0),
            resources_unknown=status_counts.get(ResourceStatus.UNKNOWN, 0),
            active_allocation_plans=len(active_plans),
            open_bottlenecks=len(conflicts),
            open_conflicts=len([c for c in conflicts if not c.is_resolved]),
            overall_capacity_health=health,
            top_bottleneck_type=top_bottleneck,
            governance_pending_count=len(pending_gov)
        )
