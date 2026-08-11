# Decision Optimization Candidate Engine
"""Engine that generates ActionCandidate records from the ActionRegistry
and enriches them with data from existing StrtOS components.
The engine does NOT fabricate values – missing data is stored as None.
"""

from typing import List, Optional, Any
import uuid

from app.execution.action_registry import ActionRegistry
from app.decision_optimization.models import ActionCandidate
from app.decision_optimization.repository import DecisionOptimizationRepository
from app.core.events.publisher import event_publisher

class ActionCandidateEngine:
    """Generates and enriches action candidates.

    The engine pulls data from existing services when provided. Missing data is left as None.
    """

    def __init__(
        self,
        repo: DecisionOptimizationRepository,
        knowledge_service: Optional[Any] = None,
        memory_service: Optional[Any] = None,
        prediction_service: Optional[Any] = None,
        agent_intelligence_service: Optional[Any] = None,
    ):
        self.repo = repo
        self.knowledge_service = knowledge_service
        self.memory_service = memory_service
        self.prediction_service = prediction_service
        self.agent_intelligence_service = agent_intelligence_service

    async def _generate_base_candidates(
        self,
        organization_id: str,
        client_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        decision_id: Optional[str] = None,
    ) -> List[ActionCandidate]:
        """Create a candidate for every allow‑listed action in ActionRegistry."""
        candidates: List[ActionCandidate] = []
        for definition in ActionRegistry.list_actions():
            action_type = definition["action_type"]
            candidate = ActionCandidate(
                id=str(uuid.uuid4()),
                organization_id=organization_id,
                client_id=client_id,
                workflow_id=workflow_id,
                decision_id=decision_id,
                action_type=action_type,
                status="PENDING",
            )
            candidates.append(candidate)
        return candidates

    async def enrich_candidate(self, candidate: ActionCandidate) -> ActionCandidate:
        """Enrich a candidate from available service instances.
        Missing data remains None (no fabricated values).
        """
        if self.knowledge_service and hasattr(self.knowledge_service, "get_evidence"):
            try:
                ev = await self.knowledge_service.get_evidence(candidate.action_type)
                candidate.supporting_evidence = ev
            except Exception:
                candidate.supporting_evidence = None

        if self.memory_service and hasattr(self.memory_service, "get_historical_performance"):
            try:
                mem = await self.memory_service.get_historical_performance(candidate.action_type)
                candidate.historical_success = mem.get("success_rate") if isinstance(mem, dict) else None
                candidate.supporting_memory = mem if isinstance(mem, dict) else None
            except Exception:
                candidate.historical_success = None

        if self.prediction_service and hasattr(self.prediction_service, "predict_outcome"):
            try:
                pred = await self.prediction_service.predict_outcome(candidate.action_type)
                if isinstance(pred, dict):
                    candidate.expected_value = pred.get("expected_value")
                    candidate.expected_cost = pred.get("expected_cost")
                    candidate.expected_roi = pred.get("expected_roi")
                    candidate.expected_confidence = pred.get("confidence")
            except Exception:
                pass

        if self.agent_intelligence_service and hasattr(self.agent_intelligence_service, "get_reliability"):
            try:
                rel = await self.agent_intelligence_service.get_reliability(candidate.action_type)
                if isinstance(rel, dict):
                    candidate.agent_reliability = rel.get("reliability")
            except Exception:
                pass

        candidate.status = "ENRICHED"
        return candidate

    async def generate_and_persist(
        self,
        organization_id: str,
        client_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        decision_id: Optional[str] = None,
    ) -> List[ActionCandidate]:
        """Create candidates for all registered actions, enrich them, persist, and publish events."""
        base = await self._generate_base_candidates(
            organization_id, client_id, workflow_id, decision_id
        )
        persisted: List[ActionCandidate] = []
        for cand in base:
            enriched = await self.enrich_candidate(cand)
            saved = await self.repo.create_candidate(enriched)
            persisted.append(saved)
            
            # Real-time event publishing
            await event_publisher.publish(
                topic="decision.candidate.created",
                payload={
                    "candidate_id": saved.id,
                    "organization_id": saved.organization_id,
                    "action_type": saved.action_type,
                    "status": saved.status,
                }
            )

        return persisted
