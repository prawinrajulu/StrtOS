from typing import List, Dict, Any, Tuple
from app.missions.models import MissionStepModel, MissionStepStatus

class DependencyGraphEngine:
    """DAG validation, cycle detection, and topological sorting engine."""

    def validate_and_sort_steps(self, steps: List[MissionStepModel]) -> Tuple[bool, List[MissionStepModel], str]:
        # Step map
        step_dict = {s.id: s for s in steps}
        graph: Dict[str, List[str]] = {}
        in_degree: Dict[str, int] = {s.id: 0 for s in steps}

        for s in steps:
            deps = s.dependencies_json or []
            graph[s.id] = []
            for dep_id in deps:
                if dep_id in step_dict:
                    in_degree[s.id] += 1

        # Kahn's algorithm for topological sort
        queue = [s_id for s_id, deg in in_degree.items() if deg == 0]
        sorted_ids = []

        while queue:
            curr = queue.pop(0)
            sorted_ids.append(curr)

            # Decrement dependent degrees
            for s in steps:
                deps = s.dependencies_json or []
                if curr in deps:
                    in_degree[s.id] -= 1
                    if in_degree[s.id] == 0:
                        queue.append(s.id)

        if len(sorted_ids) != len(steps):
            return False, [], "Cycle detected in Mission step dependencies."

        sorted_steps = [step_dict[s_id] for s_id in sorted_ids]
        return True, sorted_steps, "DAG validated cleanly."

class MissionPlanningEngine:
    """Generates ordered mission steps and DAG dependency graphs."""

    def create_default_steps(self, org_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "step_order": 1,
                "title": "Business State Telemetry & Baseline Sync",
                "action_type": "TELEMETRY_SYNC",
                "dependencies_json": [],
                "risk_level": "LOW",
                "autonomy_level": "AUTONOMOUS"
            },
            {
                "step_order": 2,
                "title": "Specialist Agent Swarm Consensus Audit",
                "action_type": "AGENT_SWARM_AUDIT",
                "dependencies_json": [],
                "risk_level": "LOW",
                "autonomy_level": "AUTONOMOUS"
            },
            {
                "step_order": 3,
                "title": "Multi-Horizon Strategic Decision Optimization",
                "action_type": "DECISION_OPTIMIZATION",
                "dependencies_json": [],
                "risk_level": "MEDIUM",
                "autonomy_level": "ASSISTED"
            },
            {
                "step_order": 4,
                "title": "Governed Action Execution",
                "action_type": "GOVERNED_EXECUTION",
                "dependencies_json": [],
                "risk_level": "HIGH",
                "autonomy_level": "APPROVAL_REQUIRED"
            }
        ]
