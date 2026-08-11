# Decision Optimization Planner
"""ActionPlanEngine creates ordered execution plans from candidate actions.
It validates dependencies, detects cycles, and assigns step metadata.
"""

from typing import List, Dict, Set, Tuple
import uuid

from app.decision_optimization.models import ActionPlan, ActionPlanStep, ActionCandidate
from app.decision_optimization.repository import DecisionOptimizationRepository

class CycleError(Exception):
    pass

class ActionPlanEngine:
    """Builds a DAG of ActionPlanStep objects inside an ActionPlan container.
    Steps are persisted via the repository. Dependency cycles raise CycleError.
    """

    def __init__(self, repo: DecisionOptimizationRepository):
        self.repo = repo

    def _detect_cycle(self, dependencies: Dict[str, List[str]]) -> None:
        """Raise CycleError if a cycle exists in the dependency graph.
        dependencies: mapping candidate_id -> list of predecessor candidate_ids.
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    raise CycleError(f"Dependency cycle detected involving {neighbor}")
            rec_stack.remove(node)

        for n in dependencies:
            if n not in visited:
                dfs(n)

    async def create_plan(
        self,
        organization_id: str,
        candidate_ids: List[str],
        dependencies: Dict[str, List[str]] | None = None,
        client_id: str | None = None,
        workflow_id: str | None = None,
        decision_id: str | None = None,
    ) -> Tuple[ActionPlan, List[ActionPlanStep]]:
        """Create ActionPlan and ActionPlanStep records respecting dependencies.
        Returns a tuple of (ActionPlan, List[ActionPlanStep]).
        """
        deps = dependencies or {}
        # Validate candidate IDs exist and belong to organization.
        candidates = []
        for cid in candidate_ids:
            cand = await self.repo.get_candidate(cid, organization_id)
            candidates.append(cand)
        # Detect cycles.
        self._detect_cycle(deps)
        # Topological sort to determine execution order.
        ordered_ids = self._topological_sort(candidate_ids, deps)
        
        # Persist parent plan container first
        plan = ActionPlan(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            client_id=client_id,
            workflow_id=workflow_id,
            decision_id=decision_id,
            status="PENDING",
        )
        plan = await self.repo.create_plan(plan)

        steps: List[ActionPlanStep] = []
        # Mapping candidate_id to step_id for predecessor dependency foreign keys
        cand_to_step_id: Dict[str, str] = {}

        for order, cand_id in enumerate(ordered_ids, start=1):
            preds = deps.get(cand_id, [])
            dependency_step_id = cand_to_step_id.get(preds[0]) if preds and preds[0] in cand_to_step_id else None
            
            step_id = str(uuid.uuid4())
            cand_to_step_id[cand_id] = step_id

            step = ActionPlanStep(
                id=step_id,
                organization_id=organization_id,
                plan_id=plan.id,
                client_id=client_id,
                workflow_id=workflow_id,
                decision_id=decision_id,
                action_id=cand_id,
                step_order=order,
                dependency=dependency_step_id,
                risk_level="LOW",
                status="PENDING",
            )
            persisted = await self.repo.create_plan_step(step)
            steps.append(persisted)

        return plan, steps

    def _topological_sort(self, nodes: List[str], deps: Dict[str, List[str]]) -> List[str]:
        """Return a list of node IDs sorted respecting dependencies using Kahn's algorithm."""
        indegree: Dict[str, int] = {n: 0 for n in nodes}
        for child, parents in deps.items():
            for p in parents:
                if p in indegree:
                    indegree[child] = indegree.get(child, 0) + 1
        queue: List[str] = [n for n, d in indegree.items() if d == 0]
        result: List[str] = []
        while queue:
            n = queue.pop(0)
            result.append(n)
            for child, parents in deps.items():
                if n in parents:
                    indegree[child] -= 1
                    if indegree[child] == 0:
                        queue.append(child)
        if len(result) != len(nodes):
            raise CycleError("Unable to resolve a full topological order – possible cycle or missing nodes.")
        return result
