"""
Resource Capacity — mission resource requirement analysis.
Maps MissionStep types to resource requirements.
"""
from typing import List, Dict, Any, Optional
from app.resources.models import ResourceType
from app.resources.schemas import MissionResourceRequirement, MissionResourceRequirementsResponse


# Default resource requirements by action type
# These are defaults ONLY when no explicit requirements exist.
# Real requirements must come from mission step data.
ACTION_TYPE_REQUIREMENTS: Dict[str, List[Dict[str, Any]]] = {
    "RUN_SEO_AUDIT": [
        {"resource_type": ResourceType.AI_AGENT, "required_amount": 1.0, "estimated_duration_hours": 2.0, "priority": "HIGH", "is_mandatory": True},
        {"resource_type": ResourceType.TOOL, "required_amount": 1.0, "estimated_duration_hours": 2.0, "priority": "MEDIUM", "is_mandatory": True},
        {"resource_type": ResourceType.COMPUTE, "required_amount": 2.0, "estimated_duration_hours": 2.0, "priority": "MEDIUM", "is_mandatory": False},
    ],
    "CREATE_CAMPAIGN": [
        {"resource_type": ResourceType.BUDGET, "required_amount": 5000.0, "estimated_duration_hours": 168.0, "priority": "CRITICAL", "is_mandatory": True},
        {"resource_type": ResourceType.HUMAN, "required_amount": 1.0, "estimated_duration_hours": 8.0, "priority": "HIGH", "is_mandatory": True},
        {"resource_type": ResourceType.AI_AGENT, "required_amount": 2.0, "estimated_duration_hours": 24.0, "priority": "HIGH", "is_mandatory": True},
        {"resource_type": ResourceType.MARKETING_CAPACITY, "required_amount": 1.0, "estimated_duration_hours": 168.0, "priority": "HIGH", "is_mandatory": True},
    ],
    "GENERATE_REPORT": [
        {"resource_type": ResourceType.AI_AGENT, "required_amount": 1.0, "estimated_duration_hours": 1.0, "priority": "HIGH", "is_mandatory": True},
        {"resource_type": ResourceType.EXECUTION_CAPACITY, "required_amount": 1.0, "estimated_duration_hours": 1.0, "priority": "MEDIUM", "is_mandatory": True},
    ],
    "EXECUTE_WORKFLOW": [
        {"resource_type": ResourceType.EXECUTION_CAPACITY, "required_amount": 2.0, "estimated_duration_hours": 4.0, "priority": "HIGH", "is_mandatory": True},
        {"resource_type": ResourceType.AI_AGENT, "required_amount": 1.0, "estimated_duration_hours": 4.0, "priority": "HIGH", "is_mandatory": True},
    ],
    "HUMAN_REVIEW": [
        {"resource_type": ResourceType.HUMAN, "required_amount": 1.0, "estimated_duration_hours": 2.0, "priority": "CRITICAL", "is_mandatory": True},
    ],
    "DEFAULT": [
        {"resource_type": ResourceType.EXECUTION_CAPACITY, "required_amount": 1.0, "estimated_duration_hours": 1.0, "priority": "MEDIUM", "is_mandatory": True},
    ],
}


class MissionCapacityAnalyzer:
    """
    Analyzes resource requirements for missions based on their steps.
    Uses ACTION_TYPE_REQUIREMENTS as defaults; real step data takes precedence.
    """

    def analyze_mission_requirements(
        self,
        mission_id: str,
        steps: List[Dict[str, Any]],
        available_resources: List[Dict[str, Any]]
    ) -> MissionResourceRequirementsResponse:
        """
        Args:
          steps: list of {action_type, resource_requirements_json (optional)}
          available_resources: list of {resource_type, available_capacity, unit, cost_per_unit}
        """
        requirements: List[MissionResourceRequirement] = []
        total_cost: Optional[float] = 0.0
        cost_known = True

        for step in steps:
            action_type = step.get("action_type", "DEFAULT")

            # Use step-level explicit requirements if available
            explicit = step.get("resource_requirements_json") or []
            if explicit:
                for req in explicit:
                    requirements.append(MissionResourceRequirement(
                        resource_type=req.get("resource_type", ResourceType.EXECUTION_CAPACITY),
                        required_amount=req.get("required_amount", 1.0),
                        estimated_duration_hours=req.get("estimated_duration_hours"),
                        priority=req.get("priority", "MEDIUM"),
                        is_mandatory=req.get("is_mandatory", True),
                        dependency=req.get("dependency"),
                        notes=req.get("notes", f"Step: {step.get('title', action_type)}")
                    ))
            else:
                # Fall back to action type defaults
                defaults = ACTION_TYPE_REQUIREMENTS.get(action_type, ACTION_TYPE_REQUIREMENTS["DEFAULT"])
                for req in defaults:
                    requirements.append(MissionResourceRequirement(
                        resource_type=req["resource_type"],
                        required_amount=req["required_amount"],
                        estimated_duration_hours=req.get("estimated_duration_hours"),
                        priority=req.get("priority", "MEDIUM"),
                        is_mandatory=req.get("is_mandatory", True),
                        notes=f"Default requirement for step type '{action_type}'."
                    ))

        # Cost estimation
        cost_map = {r["resource_type"]: r.get("cost_per_unit") for r in available_resources}
        for req in requirements:
            rt = req.resource_type.value if hasattr(req.resource_type, 'value') else req.resource_type
            unit_cost = cost_map.get(rt)
            if unit_cost is None:
                cost_known = False
            elif total_cost is not None and unit_cost is not None:
                total_cost += req.required_amount * unit_cost

        if not cost_known:
            total_cost = None

        # Feasibility check
        resource_avail = {r["resource_type"]: r.get("available_capacity") for r in available_resources}
        aggregated: Dict[str, float] = {}
        for req in requirements:
            rt = req.resource_type.value if hasattr(req.resource_type, 'value') else req.resource_type
            aggregated[rt] = aggregated.get(rt, 0.0) + req.required_amount

        feasibility = "FEASIBLE"
        for rt, needed in aggregated.items():
            avail = resource_avail.get(rt)
            if avail is None:
                feasibility = "UNKNOWN"
                break
            if needed > avail:
                if any(r.is_mandatory and (r.resource_type.value if hasattr(r.resource_type, 'value') else r.resource_type) == rt for r in requirements):
                    feasibility = "INFEASIBLE"
                    break
                feasibility = "AT_RISK"

        return MissionResourceRequirementsResponse(
            mission_id=mission_id,
            requirements=requirements,
            total_estimated_cost=total_cost,
            feasibility=feasibility
        )
