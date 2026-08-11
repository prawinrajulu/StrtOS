from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.command_center.schemas import (
    CommandCenterOverviewResponse, ExecutiveHealthResponse, StrategicPriorityResponse,
    StrategicDecisionResponse, DecisionAlternativeResponse, DecisionExplanationResponse,
    MultiAgentConsensusResponse
)
from app.command_center.service import CommandCenterService

router = APIRouter(prefix="/command-center", tags=["Autonomous Strategic Command Center"])

@router.get("/overview", response_model=CommandCenterOverviewResponse)
async def get_overview(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = CommandCenterService(db)
    return await service.get_overview(org_id)

@router.get("/health", response_model=ExecutiveHealthResponse)
async def get_health(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = CommandCenterService(db)
    return await service.get_health(org_id)

@router.get("/priorities", response_model=List[StrategicPriorityResponse])
async def get_priorities(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = CommandCenterService(db)
    return await service.get_priorities(org_id)

@router.get("/decisions", response_model=List[StrategicDecisionResponse])
async def list_decisions(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = CommandCenterService(db)
    return await service.list_decisions(org_id)

@router.get("/decisions/{id}", response_model=StrategicDecisionResponse)
async def get_decision(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = CommandCenterService(db)
    try:
        return await service.get_decision(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/decisions/{id}/alternatives", response_model=List[DecisionAlternativeResponse])
async def get_decision_alternatives(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = CommandCenterService(db)
    try:
        return await service.get_decision_alternatives(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/decisions/{id}/explanation", response_model=DecisionExplanationResponse)
async def get_decision_explanation(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = CommandCenterService(db)
    try:
        return await service.get_decision_explanation(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/decisions/{id}/consensus", response_model=MultiAgentConsensusResponse)
async def get_multi_agent_consensus(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = CommandCenterService(db)
    return await service.get_multi_agent_consensus(id, org_id)
