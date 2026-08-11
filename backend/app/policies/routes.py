from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user, get_current_organization_id
from app.auth.models import UserModel
from app.policies.schemas import (
    PolicyCreate, PolicyResponse, PolicyVersionResponse, PolicyEvaluationInput,
    PolicyEvaluationResponse, PolicyOptimizeRequest, PolicyOptimizeResponse,
    PolicyRollbackRequest, PolicyRollbackResponse, AgentPerformanceMetricItem, PolicyAnalyticsResponse
)
from app.policies.service import PolicyService

router = APIRouter(prefix="/api/v1/policies", tags=["Policies"])

@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    data: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = PolicyService(db)
    return await service.create_policy(data, current_user.organization_id, current_user.id)

@router.get("", response_model=List[PolicyResponse])
async def list_policies(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = PolicyService(db)
    return await service.list_policies(current_user.organization_id)

@router.get("/agents/performance", response_model=List[AgentPerformanceMetricItem])
async def get_agents_performance(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = PolicyService(db)
    return await service.get_agents_performance(current_user.organization_id)

@router.get("/analytics", response_model=PolicyAnalyticsResponse)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = PolicyService(db)
    return await service.get_analytics(current_user.organization_id)

@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = PolicyService(db)
    return await service.get_policy(policy_id, current_user.organization_id)

@router.get("/{policy_id}/versions", response_model=List[PolicyVersionResponse])
async def get_policy_versions(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = PolicyService(db)
    return await service.list_versions(policy_id, current_user.organization_id)

@router.get("/{policy_id}/performance", response_model=List[PolicyEvaluationResponse])
async def get_policy_performance(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = PolicyService(db)
    policy = await service.repo.get_policy(policy_id, current_user.organization_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found.")
    evals = await service.repo.list_evaluations(policy_id, current_user.organization_id)
    return [PolicyEvaluationResponse.model_validate(e) for e in evals]

@router.post("/{policy_id}/evaluate", response_model=PolicyEvaluationResponse)
async def evaluate_policy(
    policy_id: str,
    data: PolicyEvaluationInput,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = PolicyService(db)
    return await service.evaluate_policy(policy_id, data, current_user.organization_id)

@router.post("/{policy_id}/optimize", response_model=PolicyOptimizeResponse)
async def optimize_policy(
    policy_id: str,
    data: PolicyOptimizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = PolicyService(db)
    return await service.optimize_policy(policy_id, data, current_user.organization_id, current_user.id)

@router.post("/{policy_id}/activate", response_model=PolicyResponse)
async def activate_policy(
    policy_id: str,
    version: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = PolicyService(db)
    return await service.activate_policy_version(policy_id, version, current_user.organization_id, current_user.id)

@router.post("/{policy_id}/rollback", response_model=PolicyRollbackResponse)
async def rollback_policy(
    policy_id: str,
    data: PolicyRollbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = PolicyService(db)
    return await service.rollback_policy(policy_id, data, current_user.organization_id, current_user.id)
