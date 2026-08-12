"""
Resource Simulation Engine — side-effect free.

All scenario computations are in-memory only.
No database mutations during simulation.
"""
from typing import List, Dict, Any, Optional
from app.resources.allocator import AllocationPool, ResourceAllocationEngine
from app.resources.engine import ResourceBottleneckEngine, ResourceConflictEngine
from app.resources.schemas import SimulationScenarioResult, SimulationResponse


SCENARIO_CAPACITY_FACTORS = {
    "CURRENT_CAPACITY": 1.00,
    "+10_PERCENT_CAPACITY": 1.10,
    "-10_PERCENT_CAPACITY": 0.90,
    "+20_PERCENT_BUDGET": 1.00,       # budget-specific handled separately
    "-20_PERCENT_BUDGET": 1.00,
    "ADDITIONAL_HUMAN_CAPACITY": 1.00,
    "ADDITIONAL_AGENT_CAPACITY": 1.00,
    "REDUCED_EXECUTION_CAPACITY": 0.80,
    "CUSTOM": 1.00,
}


class ResourceSimulationEngine:
    """
    Side-effect free resource simulation.
    Applies scenario modifications to in-memory copies of resources only.
    """

    def simulate(
        self,
        scenario_type: str,
        resources: List[Dict[str, Any]],
        missions: List[Dict[str, Any]],
        requirements: List[Dict[str, Any]],
        org_id: str,
        capacity_delta_pct: float = 0.0,
        budget_delta_pct: float = 0.0,
        additional_humans: int = 0,
        additional_agents: int = 0,
        custom_overrides: Optional[Dict[str, float]] = None
    ) -> SimulationResponse:
        """
        Returns SimulationResponse. No DB mutations.
        """
        import copy
        sim_resources = copy.deepcopy(resources)
        cap_factor = SCENARIO_CAPACITY_FACTORS.get(scenario_type, 1.00)

        # Apply scenario modifications to in-memory copy
        for r in sim_resources:
            rt = r.get("resource_type", "")
            current_total = r.get("total_capacity") or 0.0

            # General capacity delta
            if capacity_delta_pct != 0:
                r["total_capacity"] = round(current_total * (1.0 + capacity_delta_pct / 100.0), 2)

            # Budget-specific delta
            if scenario_type in ("+20_PERCENT_BUDGET", "-20_PERCENT_BUDGET") and rt == "BUDGET":
                delta = 0.20 if "+" in scenario_type else -0.20
                r["total_capacity"] = round(current_total * (1.0 + delta), 2)

            # Additional humans
            if rt == "HUMAN" and additional_humans > 0:
                r["total_capacity"] = round(current_total + float(additional_humans), 2)

            # Additional agents
            if rt == "AI_AGENT" and additional_agents > 0:
                r["total_capacity"] = round(current_total + float(additional_agents), 2)

            # Reduced execution capacity
            if scenario_type == "REDUCED_EXECUTION_CAPACITY" and rt == "EXECUTION_CAPACITY":
                r["total_capacity"] = round(current_total * 0.80, 2)

            # General capacity factor (for +/-10%)
            if scenario_type in ("+10_PERCENT_CAPACITY", "-10_PERCENT_CAPACITY"):
                r["total_capacity"] = round(current_total * cap_factor, 2)

            # Custom overrides
            if custom_overrides and rt in custom_overrides:
                r["total_capacity"] = custom_overrides[rt]

        # Run allocation engine on simulated resources
        alloc_engine = ResourceAllocationEngine()
        alloc_result = alloc_engine.allocate(missions, sim_resources, requirements, org_id)

        # Bottleneck detection on simulated state
        bottleneck_engine = ResourceBottleneckEngine()
        btk_result = bottleneck_engine.detect_bottlenecks(sim_resources, requirements)

        # Feasible vs blocked missions
        constrained = set(alloc_result["constrained_missions"])
        all_ids = {m["mission_id"] for m in missions}
        feasible = list(all_ids - constrained)
        blocked = list(constrained)

        # Utilization averages
        pool_snap = alloc_result.get("pool_snapshot", {})
        budget_util = 0.0
        cap_util_sum = 0.0
        cap_count = 0
        for rid, snap in pool_snap.items():
            cap_util_sum += snap.get("utilization_pct", 0.0)
            cap_count += 1
        cap_util = round(cap_util_sum / max(1, cap_count), 1)

        # Strategic impact
        n_feasible = len(feasible)
        n_total = len(missions)
        ev = alloc_result.get("total_expected_value", 0.0)
        impact = (
            f"Scenario '{scenario_type}': {n_feasible}/{n_total} missions feasible. "
            f"Expected value: {ev:,.0f}. {btk_result.summary}"
        )

        opp_cost = round(
            (len(blocked) / max(1, n_total)) * 100.0, 1
        ) if blocked else 0.0

        scenario_result = SimulationScenarioResult(
            scenario_type=scenario_type,
            feasible_mission_ids=feasible,
            blocked_mission_ids=blocked,
            bottleneck_count=btk_result.total_count,
            budget_utilization_pct=cap_util,
            capacity_utilization_pct=cap_util,
            expected_value=ev,
            opportunity_cost_score=opp_cost,
            strategic_impact_summary=impact
        )

        recommendation = self._recommend(scenario_type, feasible, blocked, btk_result.critical_count)

        return SimulationResponse(
            portfolio_id=None,
            organization_id=org_id,
            scenario=scenario_result,
            recommendation=recommendation,
            is_side_effect_free=True
        )

    def _recommend(
        self,
        scenario_type: str,
        feasible: List[str],
        blocked: List[str],
        critical_bottlenecks: int
    ) -> str:
        if not blocked and not critical_bottlenecks:
            return f"Scenario '{scenario_type}' is viable — all missions feasible with no critical bottlenecks."
        if critical_bottlenecks >= 2:
            return (
                f"Scenario '{scenario_type}': {critical_bottlenecks} critical bottlenecks detected. "
                "Request governance approval for emergency resource reallocation."
            )
        if blocked:
            return (
                f"Scenario '{scenario_type}': {len(blocked)} mission(s) blocked by resource constraints. "
                "Defer lower-priority missions or request additional capacity."
            )
        return f"Scenario '{scenario_type}': Proceed with monitoring. Minor bottlenecks detected."
