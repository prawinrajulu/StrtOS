"""
Resource Allocation Engine.

Deterministic per-mission resource allocation.
Never silently exceeds capacity.
On insufficient resources: returns RESOURCE_CONSTRAINED + recommendation.
"""
from typing import List, Dict, Any, Tuple
from app.portfolio.models import ResourceType


RECOMMENDATION_MAP = {
    "BUDGET": "DEFER or REDUCE_SCOPE — budget insufficient for this mission.",
    "TEAM_CAPACITY": "QUEUE or REASSIGN — team capacity exhausted.",
    "AGENT_CAPACITY": "DEFER or REASSIGN — specialist agent capacity exhausted.",
    "EXECUTION_CAPACITY": "QUEUE — execution pipeline at limit.",
    "TIME": "DEFER — timeline constraint prevents this mission.",
}


class ResourcePool:
    """Mutable in-memory resource pool for allocation computation (no DB)."""

    def __init__(self, resources: List[Dict[str, Any]]):
        # resources: list of {resource_type, available, unit, period}
        self._pool: Dict[str, float] = {}
        self._allocated: Dict[str, float] = {}
        for r in resources:
            rt = r["resource_type"] if isinstance(r["resource_type"], str) else r["resource_type"].value
            self._pool[rt] = float(r.get("available", 0.0))
            self._allocated[rt] = float(r.get("allocated", 0.0))

    def available(self, resource_type: str) -> float:
        allocated = self._allocated.get(resource_type, 0.0)
        total = self._pool.get(resource_type, 0.0)
        return max(0.0, total - allocated)

    def allocate(self, resource_type: str, amount: float) -> bool:
        """Returns True if allocation succeeded, False if insufficient."""
        avail = self.available(resource_type)
        if amount > avail:
            return False
        self._allocated[resource_type] = self._allocated.get(resource_type, 0.0) + amount
        return True

    def snapshot(self) -> Dict[str, Dict[str, float]]:
        result = {}
        for rt in self._pool:
            total = self._pool[rt]
            alloc = self._allocated.get(rt, 0.0)
            result[rt] = {
                "available": total,
                "allocated": alloc,
                "remaining": max(0.0, total - alloc),
                "utilization_pct": round((alloc / max(1.0, total)) * 100.0, 1)
            }
        return result


class ResourceAllocationEngine:
    """
    Deterministic per-mission resource allocator.

    For each mission, attempts to allocate requested resources from the pool.
    On failure: marks mission as RESOURCE_CONSTRAINED and returns recommendation.
    """

    def allocate_for_missions(
        self,
        portfolio_id: str,
        missions: List[Dict[str, Any]],
        resource_pool: ResourcePool,
        portfolio_version: str,
        org_id: str
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Returns:
          allocation_records: list of allocation dicts (to be persisted)
          constrained_missions: list of missions that could not be fully allocated
        """
        allocation_records: List[Dict[str, Any]] = []
        constrained_missions: List[Dict[str, Any]] = []

        for mission in missions:
            mission_id = mission["mission_id"]
            budget_req = mission.get("resource_requirement", 0.0)
            mission_constrained = False

            # Budget allocation
            if budget_req > 0:
                success = resource_pool.allocate("BUDGET", budget_req)
                avail = resource_pool.available("BUDGET") + (budget_req if success else 0.0)
                allocation_records.append({
                    "organization_id": org_id,
                    "portfolio_id": portfolio_id,
                    "portfolio_version": portfolio_version,
                    "mission_id": mission_id,
                    "resource_type": ResourceType.BUDGET,
                    "requested": budget_req,
                    "allocated": budget_req if success else 0.0,
                    "remaining": resource_pool.available("BUDGET"),
                    "reason": (
                        f"Budget allocated: {budget_req:,.0f} units."
                        if success else
                        f"RESOURCE_CONSTRAINED: {budget_req:,.0f} budget requested but only "
                        f"{avail:,.0f} available. {RECOMMENDATION_MAP['BUDGET']}"
                    ),
                    "confidence": 95.0 if success else 0.0
                })
                if not success:
                    mission_constrained = True

            # Execution capacity: 1 unit per mission
            cap_success = resource_pool.allocate("EXECUTION_CAPACITY", 1.0)
            allocation_records.append({
                "organization_id": org_id,
                "portfolio_id": portfolio_id,
                "portfolio_version": portfolio_version,
                "mission_id": mission_id,
                "resource_type": ResourceType.EXECUTION_CAPACITY,
                "requested": 1.0,
                "allocated": 1.0 if cap_success else 0.0,
                "remaining": resource_pool.available("EXECUTION_CAPACITY"),
                "reason": (
                    "Execution slot allocated."
                    if cap_success else
                    f"RESOURCE_CONSTRAINED: execution pipeline at limit. {RECOMMENDATION_MAP['EXECUTION_CAPACITY']}"
                ),
                "confidence": 95.0 if cap_success else 0.0
            })
            if not cap_success:
                mission_constrained = True

            if mission_constrained:
                constrained_missions.append({
                    **mission,
                    "constraint_reason": "RESOURCE_CONSTRAINED",
                    "recommendation": RECOMMENDATION_MAP.get("BUDGET", "DEFER")
                })

        return allocation_records, constrained_missions

    def compute_agent_capacity_status(
        self, agent_name: str, total_capacity: int, active_tasks: int
    ) -> Dict[str, Any]:
        remaining = total_capacity - active_tasks
        if remaining <= 0:
            status = "EXHAUSTED"
            recommendation = "QUEUE, DEFER, or REASSIGN this agent's tasks."
        elif remaining <= 2:
            status = "NEAR_LIMIT"
            recommendation = "Monitor closely — capacity nearly exhausted."
        else:
            status = "AVAILABLE"
            recommendation = "Capacity available."

        return {
            "agent_name": agent_name,
            "total_capacity": total_capacity,
            "active_tasks": active_tasks,
            "remaining": max(0, remaining),
            "utilization_pct": round((active_tasks / max(1, total_capacity)) * 100.0, 1),
            "status": status,
            "recommendation": recommendation
        }
