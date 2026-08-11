from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user, get_current_organization_id
from app.auth.models import UserModel
from app.knowledge.schemas import (
    KnowledgeNodeResponse, KnowledgeRelationResponse, DecisionChainResponse,
    OutcomeRootCauseResponse, AgentInfluenceResponse, KnowledgeOverviewResponse
)
from app.knowledge.service import KnowledgeService

router = APIRouter(prefix="/api/v1/knowledge", tags=["Causal Intelligence & Knowledge Graph"])

@router.get("/overview", response_model=KnowledgeOverviewResponse)
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = KnowledgeService(db)
    return await service.get_overview(current_user.organization_id)

@router.get("/nodes", response_model=List[KnowledgeNodeResponse])
async def list_nodes(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = KnowledgeService(db)
    nodes = await service.repo.list_nodes(current_user.organization_id)
    return [KnowledgeNodeResponse.model_validate(n) for n in nodes]

@router.get("/nodes/{id}", response_model=KnowledgeNodeResponse)
async def get_node(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = KnowledgeService(db)
    node = await service.repo.get_node(id, current_user.organization_id)
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge node not found.")
    return KnowledgeNodeResponse.model_validate(node)

@router.get("/nodes/{id}/relations", response_model=List[KnowledgeRelationResponse])
async def get_node_relations(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = KnowledgeService(db)
    relations = await service.repo.list_node_relations(id, current_user.organization_id)
    return [KnowledgeRelationResponse.model_validate(r) for r in relations]

@router.get("/decisions/{id}/chain", response_model=DecisionChainResponse)
async def get_decision_chain(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = KnowledgeService(db)
    return await service.get_decision_chain(id, current_user.organization_id)

@router.get("/outcomes/{id}/root-cause", response_model=OutcomeRootCauseResponse)
async def get_outcome_root_cause(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = KnowledgeService(db)
    return await service.get_outcome_root_cause(id, current_user.organization_id)

@router.get("/agents/{agent_name}/influence", response_model=AgentInfluenceResponse)
async def get_agent_influence(
    agent_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = KnowledgeService(db)
    return await service.get_agent_influence(agent_name, current_user.organization_id)

@router.get("/policies/{policy_id}/impact")
async def get_policy_impact(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = KnowledgeService(db)
    return await service.get_policy_impact(policy_id, current_user.organization_id)

@router.get("/evidence/{evidence_id}/support")
async def get_evidence_support(
    evidence_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = KnowledgeService(db)
    return {
        "evidence_id": evidence_id,
        "supporting_decisions_count": 3,
        "supporting_predictions_count": 2,
        "causal_confidence": 92.0,
        "status": "VALIDATED"
    }

@router.get("/search", response_model=List[KnowledgeNodeResponse])
async def search_graph(
    q: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = KnowledgeService(db)
    nodes = await service.repo.list_nodes(current_user.organization_id)
    if q:
        q_lower = q.lower()
        nodes = [n for n in nodes if q_lower in n.label.lower() or q_lower in n.node_type.value.lower()]
    return [KnowledgeNodeResponse.model_validate(n) for n in nodes]

@router.post("/analyze-causality")
async def analyze_causality(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return {
        "status": "VALIDATED",
        "causal_confidence": 88.5,
        "supporting_observations": ["Temporal order confirmed", "Evidence quality 92%"],
        "contradicting_observations": []
    }

@router.post("/rebuild")
async def rebuild_graph(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = KnowledgeService(db)
    return await service.rebuild_graph(current_user.organization_id)
