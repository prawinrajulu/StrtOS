from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.swarm.models import SwarmSessionModel, SwarmMessageModel, SwarmConflictModel, SwarmDebateModel, SwarmStatus, SwarmMessageType
from app.swarm.schemas import (
    SwarmSessionCreate, SwarmSessionResponse, SwarmSessionListResponse,
    SwarmMessageResponse, SwarmConflictResponse, SwarmDebateResponse
)
from app.swarm.repository import SwarmRepository
from app.swarm.context_bus import SharedContextBus
from app.swarm.coordinator import SwarmCoordinator
from app.swarm.critic_engine import CriticEngine
from app.swarm.conflict_engine import ConflictEngine
from app.swarm.debate_engine import DebateEngine
from app.swarm.consensus_engine import ConsensusEngine

from app.governance.service import GovernanceService
from app.governance.schemas import ApprovalRequestCreate
from app.governance.models import DecisionType, RiskLevel

from app.execution.service import ExecutionService
from app.execution.schemas import ActionCreate
from app.execution.models import AutonomyMode

from app.memory.service import MemoryService
from app.memory.schemas import MemoryRecordCreate
from app.memory.models import MemoryType, OutcomeStatus

from app.core.events.publisher import event_publisher
from app.core.logging import logger

FIVE_SPECIALIST_AGENTS = [
    "Business Analysis Agent",
    "SEO Audit Agent",
    "Competitor Research Agent",
    "Marketing Strategy Agent",
    "Campaign Planner Agent"
]

class SwarmService:
    """
    High-level Swarm Service managing multi-agent collaboration, parallel execution,
    debate rounds, critic evaluations, conflict resolution, consensus calculation,
    governance escalation, and proposal routing to v1.3 Action Execution Engine.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SwarmRepository(session)

    async def create_swarm_session(
        self,
        payload: SwarmSessionCreate,
        org_id: str,
        creator_id: str
    ) -> SwarmSessionResponse:
        session_model = SwarmSessionModel(
            organization_id=org_id,
            client_id=payload.client_id,
            workflow_id=payload.workflow_id,
            prediction_id=payload.prediction_id,
            objective=payload.objective.strip(),
            strategy=payload.strategy,
            participating_agents=FIVE_SPECIALIST_AGENTS,
            status=SwarmStatus.DRAFT,
            created_by=creator_id,
            extra_metadata=payload.extra_metadata or {}
        )
        created = await self.repo.create_session(session_model)
        await self.session.commit()
        await self.session.refresh(created)

        await event_publisher.publish(
            event_type="swarm.created",
            workflow_id=created.workflow_id,
            organization_id=org_id,
            status=created.status.value,
            metadata={"swarm_id": created.id, "objective": created.objective}
        )

        return SwarmSessionResponse.model_validate(created)

    async def get_swarm_session(self, session_id: str, org_id: str) -> SwarmSessionResponse:
        session = await self.repo.get_session_by_id_and_org(session_id, org_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Swarm session not found.")
        return SwarmSessionResponse.model_validate(session)

    async def list_swarm_sessions(
        self,
        org_id: str,
        page: int = 1,
        page_size: int = 20,
        client_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        status_filter: Optional[SwarmStatus] = None,
        search: Optional[str] = None
    ) -> SwarmSessionListResponse:
        skip = (page - 1) * page_size
        sessions, total = await self.repo.list_sessions_by_org(
            org_id=org_id,
            client_id=client_id,
            workflow_id=workflow_id,
            status_filter=status_filter,
            search=search,
            skip=skip,
            limit=page_size
        )
        dtos = [SwarmSessionResponse.model_validate(s) for s in sessions]
        return SwarmSessionListResponse(sessions=dtos, total=total, page=page, page_size=page_size)

    async def start_swarm_session(
        self,
        session_id: str,
        org_id: str,
        creator_user: Any
    ) -> SwarmSessionResponse:
        session = await self.repo.get_session_by_id_and_org(session_id, org_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Swarm session not found.")

        if session.status in [SwarmStatus.RUNNING, SwarmStatus.COMPLETED]:
            return SwarmSessionResponse.model_validate(session)

        # Update to RUNNING
        session.status = SwarmStatus.RUNNING
        session.started_at = datetime.now(timezone.utc)
        await self.repo.update_session(session)
        await self.session.commit()

        await event_publisher.publish(
            event_type="swarm.planning",
            workflow_id=session.workflow_id,
            organization_id=org_id,
            status="RUNNING",
            metadata={"swarm_id": session.id}
        )

        # 1. Parallel Specialist Agent Execution via SwarmCoordinator
        coordinator = SwarmCoordinator(self.session)
        agent_outputs = await coordinator.execute_swarm_graph(
            swarm_id=session.id,
            org_id=org_id,
            client_domain="example-client.com",
            objective=session.objective
        )

        evidence_bus = await SharedContextBus.get_evidence(session.id, org_id)

        # 2. Critic Evaluation
        session.status = SwarmStatus.CRITIQUING
        critic_res = CriticEngine.evaluate_findings(agent_outputs, evidence_bus)
        critic_score = critic_res["critic_score"]

        # 3. Conflict Detection
        session.status = SwarmStatus.DEBATING
        conflicts_list = ConflictEngine.detect_conflicts(agent_outputs, evidence_bus)
        for c in conflicts_list:
            conf_model = SwarmConflictModel(
                swarm_id=session.id,
                organization_id=org_id,
                subject=c["subject"],
                agent_a=c["agent_a"],
                agent_b=c["agent_b"],
                claim_a=c["claim_a"],
                claim_b=c["claim_b"],
                severity=c.get("severity", RiskLevel.MEDIUM),
                resolution=c.get("resolution")
            )
            await self.repo.create_conflict(conf_model)

            await event_publisher.publish(
                event_type="swarm.conflict.detected",
                workflow_id=session.workflow_id,
                organization_id=org_id,
                status="DEBATING",
                metadata={"swarm_id": session.id, "subject": c["subject"]}
            )

        # 4. Bounded Agent Debate Rounds
        claims_list = []
        for name, out in agent_outputs.items():
            for f in out.get("findings", []):
                claims_list.append({"agent": name, "finding": f, "confidence": out.get("confidence", 80.0)})

        debates_list = DebateEngine.conduct_debate(claims_list, evidence_bus)
        for d in debates_list:
            deb_model = SwarmDebateModel(
                swarm_id=session.id,
                organization_id=org_id,
                round_number=d["round_number"],
                claim=d["claim"],
                challenge=d["challenge"],
                supporting_evidence=d["supporting_evidence"],
                counter_evidence=d["counter_evidence"],
                resolution=d["resolution"]
            )
            await self.repo.create_debate(deb_model)

        session.debate_rounds = len(debates_list)
        session.conflict_count = len(conflicts_list)

        # 5. Deterministic Consensus Calculation
        session.status = SwarmStatus.CONSENSUS
        c_score, o_conf, supporting, dissenting, req_gov, rationale = ConsensusEngine.calculate_consensus(
            agent_outputs, critic_score, conflicts_list, evidence_bus
        )

        session.consensus_score = c_score
        session.confidence_score = o_conf
        session.completed_agents = supporting
        session.failed_agents = dissenting

        await event_publisher.publish(
            event_type="swarm.consensus.calculated",
            workflow_id=session.workflow_id,
            organization_id=org_id,
            status="CONSENSUS",
            metadata={"swarm_id": session.id, "consensus_score": c_score, "confidence_score": o_conf}
        )

        # 6. CEO Synthesis Generation
        ceo_synthesis = {
            "swarm_id": session.id,
            "objective": session.objective,
            "consensus_score": c_score,
            "confidence_score": o_conf,
            "critic_score": critic_score,
            "supporting_agents": supporting,
            "dissenting_agents": dissenting,
            "conflicts_count": len(conflicts_list),
            "requires_governance": req_gov,
            "rationale": rationale,
            "recommended_action": "GENERATE_REPORT"
        }
        session.synthesis_output = ceo_synthesis

        # 7. Human Governance Escalation
        if req_gov:
            gov_svc = GovernanceService(self.session)
            app_req = await gov_svc.create_approval_request(
                payload=ApprovalRequestCreate(
                    workflow_id=session.workflow_id,
                    client_id=session.client_id,
                    title=f"Swarm Governance Approval: {session.objective[:40]}...",
                    description=f"Swarm consensus score is {c_score}% (<60%) or critical conflict detected. Review required.",
                    decision_type=DecisionType.WORKFLOW_EXECUTION,
                    requested_action="Approve Swarm Recommendation",
                    ai_recommendation=rationale,
                    ai_confidence_score=o_conf
                ),
                org_id=org_id,
                creator_id=creator_user.id
            )
            await event_publisher.publish(
                event_type="swarm.human_review.required",
                workflow_id=session.workflow_id,
                organization_id=org_id,
                status="PENDING_APPROVAL",
                metadata={"swarm_id": session.id, "approval_id": app_req.id}
            )

        # 8. Submit Action Proposal to v1.3 Action Execution Engine
        exec_svc = ExecutionService(self.session)
        action_prop = await exec_svc.create_action(
            payload=ActionCreate(
                client_id=session.client_id,
                workflow_id=session.workflow_id,
                prediction_id=session.prediction_id,
                action_type="GENERATE_REPORT",
                name=f"Swarm Executive Report: {session.objective[:30]}",
                risk_level=RiskLevel.MEDIUM if req_gov else RiskLevel.LOW,
                autonomy_mode=AutonomyMode.APPROVAL_REQUIRED if req_gov else AutonomyMode.AUTONOMOUS,
                input_payload=ceo_synthesis
            ),
            org_id=org_id,
            current_user=creator_user
        )

        # 9. Persist Swarm Memory Record
        mem_svc = MemoryService(self.session)
        await mem_svc.create_memory(
            payload=MemoryRecordCreate(
                client_id=session.client_id,
                workflow_id=session.workflow_id,
                memory_type=MemoryType.STRATEGY,
                title=f"Swarm Synthesis: {session.objective[:40]}",
                content=rationale,
                confidence_score=o_conf,
                importance_score=85.0,
                outcome_status=OutcomeStatus.SUCCESS if c_score >= 70.0 else OutcomeStatus.PARTIAL,
                extra_metadata={"swarm_id": session.id, "consensus_score": c_score, "action_id": action_prop.id}
            ),
            org_id=org_id,
            creator_id=creator_user.id
        )

        # Finish Session
        session.status = SwarmStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)
        updated = await self.repo.update_session(session)
        await self.session.commit()

        await event_publisher.publish(
            event_type="swarm.completed",
            workflow_id=updated.workflow_id,
            organization_id=org_id,
            status="COMPLETED",
            metadata={"swarm_id": updated.id, "consensus_score": c_score}
        )

        return SwarmSessionResponse.model_validate(updated)

    async def list_messages(self, swarm_id: str, org_id: str) -> List[SwarmMessageResponse]:
        msgs = await self.repo.list_messages_by_swarm(swarm_id, org_id)
        return [SwarmMessageResponse.model_validate(m) for m in msgs]

    async def list_conflicts(self, swarm_id: str, org_id: str) -> List[SwarmConflictResponse]:
        confs = await self.repo.list_conflicts_by_swarm(swarm_id, org_id)
        return [SwarmConflictResponse.model_validate(c) for c in confs]

    async def list_debates(self, swarm_id: str, org_id: str) -> List[SwarmDebateResponse]:
        debs = await self.repo.list_debates_by_swarm(swarm_id, org_id)
        return [SwarmDebateResponse.model_validate(d) for d in debs]
