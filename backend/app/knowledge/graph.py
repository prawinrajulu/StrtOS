from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.knowledge.models import (
    KnowledgeNodeModel, KnowledgeRelationModel, NodeTypeEnum, RelationTypeEnum, CausalStatusEnum
)
from app.knowledge.repository import KnowledgeRepository

class KnowledgeGraphBuilder:
    """
    Constructs and links Knowledge Nodes and directed Knowledge Relations in the graph.
    """
    def __init__(self, session: AsyncSession):
        self.repo = KnowledgeRepository(session)

    async def get_or_create_node(
        self,
        org_id: str,
        entity_id: str,
        node_type: NodeTypeEnum,
        label: str,
        confidence: float = 85.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> KnowledgeNodeModel:
        existing = await self.repo.get_node_by_entity(entity_id, node_type, org_id)
        if existing:
            return existing

        node = KnowledgeNodeModel(
            organization_id=org_id,
            node_type=node_type,
            entity_id=entity_id,
            label=label,
            confidence=confidence,
            node_metadata=metadata or {}
        )
        return await self.repo.create_node(node)

    async def link_nodes(
        self,
        org_id: str,
        source_node_id: str,
        target_node_id: str,
        relation_type: RelationTypeEnum,
        causal_status: CausalStatusEnum = CausalStatusEnum.OBSERVED,
        confidence: float = 80.0,
        weight: float = 1.0,
        evidence_summary: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> KnowledgeRelationModel:
        relation = KnowledgeRelationModel(
            organization_id=org_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relation_type=relation_type,
            causal_status=causal_status,
            confidence=confidence,
            weight=weight,
            evidence_summary=evidence_summary or {},
            relation_metadata=metadata or {}
        )
        return await self.repo.create_relation(relation)

class KnowledgeGraphRetriever:
    """
    Graph Traversal and Search Retriever enforcing strict organization_id tenant boundaries.
    """
    def __init__(self, session: AsyncSession):
        self.repo = KnowledgeRepository(session)

    async def find_related_nodes(self, node_id: str, org_id: str) -> Dict[str, Any]:
        node = await self.repo.get_node(node_id, org_id)
        if not node:
            return {"node": None, "relations": []}

        relations = await self.repo.list_node_relations(node_id, org_id)
        return {
            "node": node,
            "relations": relations
        }

    async def find_decision_chain(self, decision_id: str, org_id: str) -> Dict[str, Any]:
        dec_node = await self.repo.get_node_by_entity(decision_id, NodeTypeEnum.DECISION, org_id)
        if not dec_node:
            # Fallback mock node for unindexed decisions
            dec_node = KnowledgeNodeModel(
                id=f"node_dec_{decision_id[:8]}",
                organization_id=org_id,
                node_type=NodeTypeEnum.DECISION,
                entity_id=decision_id,
                label=f"Strategic Execution Decision #{decision_id[:8]}",
                confidence=88.0
            )

        relations = await self.repo.list_node_relations(dec_node.id, org_id)
        return {
            "decision_node": dec_node,
            "relations": relations
        }

    async def find_outcome_chain(self, outcome_id: str, org_id: str) -> Dict[str, Any]:
        out_node = await self.repo.get_node_by_entity(outcome_id, NodeTypeEnum.OUTCOME, org_id)
        if not out_node:
            out_node = KnowledgeNodeModel(
                id=f"node_out_{outcome_id[:8]}",
                organization_id=org_id,
                node_type=NodeTypeEnum.OUTCOME,
                entity_id=outcome_id,
                label=f"Actual Outcome Record #{outcome_id[:8]}",
                confidence=85.0
            )

        relations = await self.repo.list_node_relations(out_node.id, org_id)
        return {
            "outcome_node": out_node,
            "relations": relations
        }
