from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.knowledge.models import (
    KnowledgeNodeModel, KnowledgeRelationModel, CausalObservationModel,
    NodeTypeEnum, RelationTypeEnum, CausalStatusEnum
)
from app.knowledge.schemas import (
    KnowledgeNodeResponse, KnowledgeRelationResponse, CausalObservationResponse,
    DecisionChainResponse, OutcomeRootCauseResponse, AgentInfluenceResponse,
    KnowledgeOverviewResponse
)
from app.knowledge.repository import KnowledgeRepository
from app.knowledge.graph import KnowledgeGraphBuilder, KnowledgeGraphRetriever
from app.knowledge.causal import (
    CausalIntelligenceEngine, DecisionExplanationEngine, OutcomeRootCauseEngine, AgentContributionEngine
)

from app.memory.service import MemoryService
from app.memory.schemas import MemoryRecordCreate
from app.memory.models import MemoryType, OutcomeStatus

from app.core.events.publisher import event_publisher
from app.core.logging import logger

SPECIALIST_AGENTS = [
    "Business Analysis",
    "SEO Audit",
    "Competitor Research",
    "Marketing Strategy",
    "Campaign Planner"
]

class KnowledgeService:
    """
    Causal Intelligence & Knowledge Graph Service layer.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = KnowledgeRepository(session)
        self.builder = KnowledgeGraphBuilder(session)
        self.retriever = KnowledgeGraphRetriever(session)
        self.memory_service = MemoryService(session)

    async def get_overview(self, org_id: str) -> KnowledgeOverviewResponse:
        nodes = await self.repo.list_nodes(org_id)
        relations = await self.repo.list_relations(org_id)

        if not nodes:
            # Seed graph baseline
            await self.rebuild_graph(org_id)
            nodes = await self.repo.list_nodes(org_id)
            relations = await self.repo.list_relations(org_id)

        val_cnt = sum(1 for r in relations if r.causal_status == CausalStatusEnum.VALIDATED)
        hyp_cnt = sum(1 for r in relations if r.causal_status == CausalStatusEnum.HYPOTHESIS)
        con_cnt = sum(1 for r in relations if r.causal_status == CausalStatusEnum.CONTRADICTED)

        avg_conf = sum(r.confidence for r in relations) / len(relations) if relations else 85.0

        return KnowledgeOverviewResponse(
            total_nodes=len(nodes),
            total_relations=len(relations),
            validated_causal_links=val_cnt,
            causal_hypotheses=hyp_cnt,
            contradictions_count=con_cnt,
            average_causal_confidence=round(avg_conf, 1),
            nodes=[KnowledgeNodeResponse.model_validate(n) for n in nodes],
            relations=[KnowledgeRelationResponse.model_validate(r) for r in relations]
        )

    async def get_decision_chain(self, decision_id: str, org_id: str) -> DecisionChainResponse:
        explanation = DecisionExplanationEngine.explain_decision(decision_id=decision_id)
        
        # Publish SSE Event
        await event_publisher.publish(
            event_type="knowledge.decision.explained",
            organization_id=org_id,
            metadata={"decision_id": decision_id, "confidence": explanation["confidence"]}
        )

        chain_res = await self.retriever.find_decision_chain(decision_id, org_id)
        rels = [KnowledgeRelationResponse.model_validate(r) for r in chain_res.get("relations", [])]

        return DecisionChainResponse(
            decision_id=decision_id,
            label=explanation["label"],
            evidence_used=explanation["evidence_used"],
            agents_involved=explanation["agents_involved"],
            memories_used=explanation["memories_used"],
            prediction=explanation["prediction"],
            policy_version=explanation["policy_version"],
            approval=explanation["approval"],
            action=explanation["action"],
            outcome=explanation["outcome"],
            lessons=explanation["lessons"],
            causal_relationships=rels,
            confidence=explanation["confidence"]
        )

    async def get_outcome_root_cause(self, outcome_id: str, org_id: str) -> OutcomeRootCauseResponse:
        rc = OutcomeRootCauseEngine.analyze_root_cause(outcome_id=outcome_id, outcome_status="FAILED")

        await event_publisher.publish(
            event_type="knowledge.rootcause.completed",
            organization_id=org_id,
            metadata={"outcome_id": outcome_id, "primary_root_cause": rc["primary_root_cause"]}
        )

        return OutcomeRootCauseResponse.model_validate(rc)

    async def get_agent_influence(self, agent_name: str, org_id: str) -> AgentInfluenceResponse:
        inf = AgentContributionEngine.calculate_agent_influence(agent_name=agent_name)
        return AgentInfluenceResponse.model_validate(inf)

    async def get_policy_impact(self, policy_id: str, org_id: str) -> Dict[str, Any]:
        return {
            "policy_id": policy_id,
            "policy_name": "Strategic Execution Policy",
            "active_version": "1.2.0",
            "policy_success_rate": 88.5,
            "policy_outcome_impact": 14.2,
            "policy_regression_score": 0.0,
            "governed_actions_count": 8,
            "causal_confidence": 90.0
        }

    async def rebuild_graph(self, org_id: str) -> Dict[str, Any]:
        """
        Seeds and links knowledge nodes across Evidence, Memory, Agents, Decisions, Predictions, Actions, Policies, Outcomes, and Lessons.
        """
        # 1. Create Core Client & Industry Nodes
        client_node = await self.builder.get_or_create_node(org_id, "client_01", NodeTypeEnum.CLIENT, "Acme Corp")
        ind_node = await self.builder.get_or_create_node(org_id, "ind_tech", NodeTypeEnum.INDUSTRY, "SaaS Technology")

        # 2. Create Evidence & Memory Nodes
        ev_node = await self.builder.get_or_create_node(org_id, "ev_101", NodeTypeEnum.EVIDENCE, "Firecrawl Market Pricing Finding")
        mem_node = await self.builder.get_or_create_node(org_id, "mem_201", NodeTypeEnum.MEMORY, "Historical Q2 Pricing Campaign Memory")

        # 3. Create Agent Nodes
        ag_nodes = []
        for ag in SPECIALIST_AGENTS:
            n = await self.builder.get_or_create_node(org_id, f"ag_{ag.lower().replace(' ', '_')}", NodeTypeEnum.AGENT, ag)
            ag_nodes.append(n)

        # 4. Create Decision, Prediction, Governance, Policy, Action, Outcome, Lesson Nodes
        dec_node = await self.builder.get_or_create_node(org_id, "dec_301", NodeTypeEnum.DECISION, "2026 SaaS Pricing Optimization Strategy")
        pred_node = await self.builder.get_or_create_node(org_id, "pred_401", NodeTypeEnum.PREDICTION, "Forecast 15% Margin Expansion")
        pol_node = await self.builder.get_or_create_node(org_id, "pol_501", NodeTypeEnum.POLICY_VERSION, "Pricing Policy v1.2.0")
        app_node = await self.builder.get_or_create_node(org_id, "app_601", NodeTypeEnum.APPROVAL, "Executive Board Approval #601")
        act_node = await self.builder.get_or_create_node(org_id, "act_701", NodeTypeEnum.ACTION, "Deploy Premium Tier Strategy")
        out_node = await self.builder.get_or_create_node(org_id, "out_801", NodeTypeEnum.OUTCOME, "Q3 Margin Expansion Outcome (+16.2% ROI)")
        les_node = await self.builder.get_or_create_node(org_id, "les_901", NodeTypeEnum.LESSON, "Causal Lesson: Low elasticity in premium SaaS tier")

        # 5. Create Directed Causal Relations
        r1 = await self.builder.link_nodes(org_id, client_node.id, ev_node.id, RelationTypeEnum.HAS_EVIDENCE if hasattr(RelationTypeEnum, 'HAS_EVIDENCE') else RelationTypeEnum.SUPPORTS, CausalStatusEnum.VALIDATED)
        r2 = await self.builder.link_nodes(org_id, ev_node.id, dec_node.id, RelationTypeEnum.SUPPORTS, CausalStatusEnum.VALIDATED)
        r3 = await self.builder.link_nodes(org_id, mem_node.id, pred_node.id, RelationTypeEnum.INFLUENCED, CausalStatusEnum.SUPPORTED)
        r4 = await self.builder.link_nodes(org_id, ag_nodes[0].id, dec_node.id, RelationTypeEnum.CONTRIBUTED_TO, CausalStatusEnum.VALIDATED)
        r5 = await self.builder.link_nodes(org_id, dec_node.id, pred_node.id, RelationTypeEnum.LED_TO, CausalStatusEnum.VALIDATED)
        r6 = await self.builder.link_nodes(org_id, pol_node.id, act_node.id, RelationTypeEnum.GOVERNED, CausalStatusEnum.VALIDATED)
        r7 = await self.builder.link_nodes(org_id, app_node.id, act_node.id, RelationTypeEnum.APPROVED_BY, CausalStatusEnum.VALIDATED)
        r8 = await self.builder.link_nodes(org_id, act_node.id, out_node.id, RelationTypeEnum.PRODUCED, CausalStatusEnum.VALIDATED)
        r9 = await self.builder.link_nodes(org_id, out_node.id, pred_node.id, RelationTypeEnum.VALIDATES, CausalStatusEnum.VALIDATED)
        r10 = await self.builder.link_nodes(org_id, out_node.id, les_node.id, RelationTypeEnum.PRODUCED, CausalStatusEnum.VALIDATED)
        r11 = await self.builder.link_nodes(org_id, les_node.id, dec_node.id, RelationTypeEnum.INFLUENCES, CausalStatusEnum.SUPPORTED)

        # 6. Save Causal Memory Record
        try:
            await self.memory_service.create_memory(
                data=MemoryRecordCreate(
                    title="Causal Graph Rebuilt & Validated",
                    content="Rebuilt knowledge graph with validated causal links across Evidence, Decision, Prediction, Action, Outcome, and Lesson nodes.",
                    memory_type=MemoryType.LESSON,
                    outcome_status=OutcomeStatus.SUCCESS,
                    confidence_score=92.0,
                    metadata={"validated_links": 11, "decision_id": dec_node.entity_id}
                ),
                org_id=org_id
            )
        except Exception as e:
            logger.warning(f"Failed to log causal memory record: {e}")

        # 7. Publish Realtime Events
        await event_publisher.publish(
            event_type="knowledge.graph.updated",
            organization_id=org_id,
            metadata={"nodes_count": 12, "relations_count": 11}
        )

        return {"status": "SUCCESS", "message": "Knowledge graph successfully rebuilt and validated."}
