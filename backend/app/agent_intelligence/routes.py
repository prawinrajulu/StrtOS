from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user, get_current_organization_id
from app.auth.models import UserModel
from app.agent_intelligence.schemas import (
    AgentMetricResponse, AgentBenchmarkResponse, AgentAnomalyResponse,
    AgentWeaknessResponse, AgentOptimizationRecommendationResponse,
    AgentIntelligenceOverviewResponse, AgentAnalyzeRequest
)
from app.agent_intelligence.service import AgentIntelligenceService

router = APIRouter(prefix="/api/v1/agent-intelligence", tags=["Agent Performance Intelligence & Autonomous Optimization"])

@router.get("/overview", response_model=AgentIntelligenceOverviewResponse)
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = AgentIntelligenceService(db)
    return await service.get_overview(current_user.organization_id)

@router.get("/agents", response_model=List[AgentMetricResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = AgentIntelligenceService(db)
    return await service.list_agents(current_user.organization_id)

@router.get("/agents/{agent_name}", response_model=AgentMetricResponse)
async def get_agent(
    agent_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = AgentIntelligenceService(db)
    return await service.get_agent(agent_name, current_user.organization_id)

@router.get("/agents/{agent_name}/metrics", response_model=AgentMetricResponse)
async def get_agent_metrics(
    agent_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = AgentIntelligenceService(db)
    return await service.get_agent(agent_name, current_user.organization_id)

@router.get("/agents/{agent_name}/history", response_model=List[AgentMetricResponse])
async def get_agent_history(
    agent_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = AgentIntelligenceService(db)
    return await service.list_agent_history(agent_name, current_user.organization_id)

@router.get("/benchmarks", response_model=List[AgentBenchmarkResponse])
async def get_benchmarks(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = AgentIntelligenceService(db)
    return await service.list_benchmarks(current_user.organization_id)

@router.get("/anomalies", response_model=List[AgentAnomalyResponse])
async def get_anomalies(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = AgentIntelligenceService(db)
    return await service.list_anomalies(current_user.organization_id)

@router.get("/weaknesses", response_model=List[AgentWeaknessResponse])
async def get_weaknesses(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = AgentIntelligenceService(db)
    return await service.list_weaknesses(current_user.organization_id)

@router.get("/recommendations", response_model=List[AgentOptimizationRecommendationResponse])
async def get_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = AgentIntelligenceService(db)
    return await service.list_recommendations(current_user.organization_id)

@router.post("/analyze", response_model=AgentMetricResponse)
async def analyze_performance(
    data: AgentAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = AgentIntelligenceService(db)
    agent_name = data.agent_name or "Business Analysis"
    return await service.analyze_agent(agent_name, current_user.organization_id)

@router.post("/recommendations/{id}/evaluate", response_model=AgentOptimizationRecommendationResponse)
async def evaluate_recommendation(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = AgentIntelligenceService(db)
    rec = await service.repo.get_recommendation(id, current_user.organization_id)
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found.")
    rec.status = RecommendationStatus.EVALUATING
    await service.session.commit()
    return AgentOptimizationRecommendationResponse.model_validate(rec)

@router.post("/recommendations/{id}/submit-governance", response_model=AgentOptimizationRecommendationResponse)
async def submit_governance_recommendation(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = AgentIntelligenceService(db)
    return await service.submit_governance_recommendation(id, current_user.organization_id, current_user.id)

@router.get("/analytics", response_model=AgentIntelligenceOverviewResponse)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = AgentIntelligenceService(db)
    return await service.get_overview(current_user.organization_id)
