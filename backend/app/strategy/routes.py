from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.strategy.schemas import (
    StrategicObjectiveCreate, StrategicObjectiveResponse,
    StrategicPlanCreate, StrategicPlanResponse, ScenarioResponse,
    StrategyEvaluationResponse, StrategyAdaptationRequest, StrategyAdaptationResponse,
    StrategyExplanationResponse
)
from app.strategy.service import StrategyService

router = APIRouter(prefix="/strategy", tags=["Strategy & Strategic Intelligence"])

@router.get("/overview")
async def get_strategy_overview(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = StrategyService(db)
    objectives = await service.list_objectives(org_id)
    plans = await service.list_plans(org_id)
    active_plan = next((p for p in plans if p.status == "ACTIVE"), None)

    return {
        "organization_id": org_id,
        "total_objectives": len(objectives),
        "total_plans": len(plans),
        "active_plan": active_plan,
        "objectives_summary": [
            {"id": o.id, "title": o.title, "status": o.status, "target_horizon": o.target_horizon} for o in objectives
        ]
    }

@router.post("/objectives", response_model=StrategicObjectiveResponse, status_code=status.HTTP_201_CREATED)
async def create_objective(
    payload: StrategicObjectiveCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = StrategyService(db)
    return await service.create_objective(payload, org_id)

@router.get("/objectives", response_model=List[StrategicObjectiveResponse])
async def list_objectives(
    status: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = StrategyService(db)
    return await service.list_objectives(org_id, status=status)

@router.get("/objectives/{id}", response_model=StrategicObjectiveResponse)
async def get_objective(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = StrategyService(db)
    try:
        return await service.get_objective(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/plans", response_model=StrategicPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    payload: StrategicPlanCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = StrategyService(db)
    try:
        return await service.create_plan(payload, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/plans", response_model=List[StrategicPlanResponse])
async def list_plans(
    objective_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = StrategyService(db)
    return await service.list_plans(org_id, objective_id=objective_id)

@router.get("/plans/{id}", response_model=StrategicPlanResponse)
async def get_plan(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = StrategyService(db)
    try:
        return await service.get_plan(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/plans/{id}/evaluate", response_model=StrategyEvaluationResponse)
async def evaluate_plan(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = StrategyService(db)
    try:
        return await service.evaluate_plan(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/plans/{id}/simulate", response_model=List[ScenarioResponse])
async def simulate_scenarios(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = StrategyService(db)
    try:
        plan = await service.get_plan(id, org_id)
        return await service.generate_scenarios(plan.objective_id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/plans/{id}/activate", response_model=StrategicPlanResponse)
async def activate_plan(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = StrategyService(db)
    try:
        return await service.activate_plan(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/plans/{id}/explanation", response_model=StrategyExplanationResponse)
async def get_explanation(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = StrategyService(db)
    try:
        return await service.get_explanation(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/plans/{id}/adapt", response_model=StrategyAdaptationResponse)
async def adapt_plan(
    id: str,
    payload: StrategyAdaptationRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = StrategyService(db)
    try:
        return await service.adapt_plan(id, payload, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
