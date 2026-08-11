from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.forecasting.schemas import (
    ForecastCreate, ForecastResponse, SimulationRequest, SimulationResponse,
    FutureRiskResponse, FutureOpportunityResponse, ForecastEvaluationResponse
)
from app.forecasting.models import ForecastType
from app.forecasting.service import ForecastingService

router = APIRouter(prefix="/forecasting", tags=["Strategic Forecasting & Simulation"])

@router.get("/overview")
async def get_forecasting_overview(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = ForecastingService(db)
    forecasts = await service.list_forecasts(org_id)
    return {
        "organization_id": org_id,
        "total_forecasts": len(forecasts),
        "forecasts": forecasts
    }

@router.post("/forecasts", response_model=ForecastResponse, status_code=status.HTTP_201_CREATED)
async def create_forecast(
    payload: ForecastCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = ForecastingService(db)
    return await service.create_forecast(payload, org_id)

@router.get("/forecasts", response_model=List[ForecastResponse])
async def list_forecasts(
    forecast_type: Optional[ForecastType] = Query(None),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = ForecastingService(db)
    return await service.list_forecasts(org_id, forecast_type=forecast_type)

@router.get("/forecasts/{id}", response_model=ForecastResponse)
async def get_forecast(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = ForecastingService(db)
    try:
        return await service.get_forecast(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/forecasts/{id}/simulate", response_model=SimulationResponse)
async def simulate_forecast(
    id: str,
    payload: SimulationRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = ForecastingService(db)
    try:
        return await service.simulate_forecast(id, payload, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/forecasts/{id}/risks", response_model=List[FutureRiskResponse])
async def get_future_risks(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = ForecastingService(db)
    try:
        return await service.get_future_risks(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/forecasts/{id}/opportunities", response_model=List[FutureOpportunityResponse])
async def get_future_opportunities(
    id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = ForecastingService(db)
    try:
        return await service.get_future_opportunities(id, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/forecasts/{id}/evaluate", response_model=ForecastEvaluationResponse)
async def evaluate_accuracy(
    id: str,
    actual_value: float = Query(...),
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")
    service = ForecastingService(db)
    try:
        return await service.evaluate_accuracy(id, actual_value, org_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
