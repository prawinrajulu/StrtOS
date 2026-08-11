from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func

from app.knowledge.models import (
    KnowledgeNodeModel, KnowledgeRelationModel, CausalObservationModel,
    NodeTypeEnum, RelationTypeEnum, CausalStatusEnum
)

class KnowledgeRepository:
    """
    Data access repository for Causal Knowledge Graph with strict tenant isolation.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_node(self, node: KnowledgeNodeModel) -> KnowledgeNodeModel:
        self.session.add(node)
        await self.session.commit()
        await self.session.refresh(node)
        return node

    async def get_node(self, node_id: str, org_id: str) -> Optional[KnowledgeNodeModel]:
        stmt = select(KnowledgeNodeModel).where(
            KnowledgeNodeModel.id == node_id,
            KnowledgeNodeModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_node_by_entity(self, entity_id: str, node_type: NodeTypeEnum, org_id: str) -> Optional[KnowledgeNodeModel]:
        stmt = select(KnowledgeNodeModel).where(
            KnowledgeNodeModel.entity_id == entity_id,
            KnowledgeNodeModel.node_type == node_type,
            KnowledgeNodeModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_nodes(self, org_id: str, limit: int = 100) -> List[KnowledgeNodeModel]:
        stmt = select(KnowledgeNodeModel).where(
            KnowledgeNodeModel.organization_id == org_id
        ).order_by(KnowledgeNodeModel.created_at.desc()).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_relation(self, relation: KnowledgeRelationModel) -> KnowledgeRelationModel:
        self.session.add(relation)
        await self.session.commit()
        await self.session.refresh(relation)
        return relation

    async def list_relations(self, org_id: str, limit: int = 200) -> List[KnowledgeRelationModel]:
        stmt = select(KnowledgeRelationModel).where(
            KnowledgeRelationModel.organization_id == org_id
        ).order_by(KnowledgeRelationModel.created_at.desc()).limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def list_node_relations(self, node_id: str, org_id: str) -> List[KnowledgeRelationModel]:
        stmt = select(KnowledgeRelationModel).where(
            KnowledgeRelationModel.organization_id == org_id,
            or_(
                KnowledgeRelationModel.source_node_id == node_id,
                KnowledgeRelationModel.target_node_id == node_id
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_observation(self, obs: CausalObservationModel) -> CausalObservationModel:
        self.session.add(obs)
        await self.session.commit()
        await self.session.refresh(obs)
        return obs

    async def list_relation_observations(self, relation_id: str, org_id: str) -> List[CausalObservationModel]:
        stmt = select(CausalObservationModel).where(
            CausalObservationModel.relation_id == relation_id,
            CausalObservationModel.organization_id == org_id
        ).order_by(CausalObservationModel.observed_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
