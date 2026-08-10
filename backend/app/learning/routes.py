from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user, get_current_organization_id
from app.auth.models import UserModel
from app.learning.schemas import (
    AgentPerformanceResponse, ToolReliabilityResponse, LLMProviderPerformanceResponse,
    AgentPolicyResponse, AgentAdaptationResponse, LearningOverviewResponse,
    PolicyActivateResponse, PolicyRollbackResponse
)
from app.learning.service import LearningService

router = APIRouter(prefix="/api/v1/learning", tags=["Adaptive Agent Learning & Self-Optimization"])

@router.get("/overview", response_model=LearningOverviewResponse)
async def get_learning_overview(
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = LearningService(db)
    return await service.get_overview(org_id=org_id)

@router.get("/agents", response_model=List[AgentPerformanceResponse])
async def list_agent_performances(
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = LearningService(db)
    return await service.list_agent_performances(org_id=org_id)

@router.get("/agents/{agent_name}", response_model=AgentPerformanceResponse)
async def get_agent_performance(
    agent_name: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = LearningService(db)
    return await service.get_agent_performance(agent_name=agent_name, org_id=org_id)

@router.post("/agents/{agent_name}/adapt", response_model=AgentAdaptationResponse)
async def propose_agent_adaptation(
    agent_name: str,
    proposed_delta: float = Query(..., ge=-10.0, le=10.0),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = LearningService(db)
    return await service.propose_agent_adaptation(
        agent_name=agent_name,
        proposed_delta=proposed_delta,
        org_id=org_id,
        creator_user=current_user
    )

@router.get("/policies", response_model=List[AgentPolicyResponse])
async def list_agent_policies(
    agent_name: str = Query(...),
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = LearningService(db)
    return await service.list_policies(agent_name=agent_name, org_id=org_id)

@router.post("/policies/{id}/activate", response_model=PolicyActivateResponse)
async def activate_agent_policy(
    id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = LearningService(db)
    return await service.activate_policy(policy_id=id, org_id=org_id)

@router.post("/policies/{agent_name}/rollback", response_model=PolicyRollbackResponse)
async def rollback_agent_policy(
    agent_name: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = LearningService(db)
    return await service.rollback_policy(agent_name=agent_name, org_id=org_id)
