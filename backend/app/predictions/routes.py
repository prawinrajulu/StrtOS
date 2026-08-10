from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user, get_current_organization_id
from app.auth.models import UserModel
from app.predictions.models import ScenarioType, PredictionStatus
from app.predictions.schemas import (
    PredictionCreate, PredictionResponse, PredictionListResponse,
    ScenarioGenerateRequest, ScenarioListResponse,
    WhatIfSimulationRequest, WhatIfSimulationResponse
)
from app.predictions.service import PredictionService

router = APIRouter(prefix="/api/v1/predictions", tags=["Predictive Decision Intelligence"])

@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    payload: PredictionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = PredictionService(db)
    return await service.create_prediction(payload, org_id=org_id, creator_id=current_user.id)

@router.get("", response_model=PredictionListResponse)
async def list_predictions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    client_id: Optional[str] = Query(None),
    workflow_id: Optional[str] = Query(None),
    scenario_type: Optional[ScenarioType] = Query(None),
    prediction_status: Optional[PredictionStatus] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = PredictionService(db)
    return await service.list_predictions(
        org_id=org_id,
        page=page,
        page_size=page_size,
        client_id=client_id,
        workflow_id=workflow_id,
        scenario_type=scenario_type,
        prediction_status=prediction_status,
        search=search
    )

@router.post("/scenarios", response_model=ScenarioListResponse, status_code=status.HTTP_201_CREATED)
async def generate_scenarios(
    payload: ScenarioGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = PredictionService(db)
    return await service.generate_scenarios(payload, org_id=org_id, creator_id=current_user.id)

@router.post("/simulate", response_model=WhatIfSimulationResponse)
async def simulate_what_if(
    payload: WhatIfSimulationRequest,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = PredictionService(db)
    return await service.simulate_what_if(payload, org_id=org_id)

@router.get("/client/{client_id}", response_model=PredictionListResponse)
async def list_client_predictions(
    client_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = PredictionService(db)
    return await service.list_predictions(org_id=org_id, client_id=client_id, page=page, page_size=page_size)

@router.get("/workflow/{workflow_id}", response_model=PredictionListResponse)
async def list_workflow_predictions(
    workflow_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = PredictionService(db)
    return await service.list_predictions(org_id=org_id, workflow_id=workflow_id, page=page, page_size=page_size)

@router.get("/{id}", response_model=PredictionResponse)
async def get_prediction(
    id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_current_organization_id)
):
    service = PredictionService(db)
    return await service.get_prediction(id, org_id=org_id)

@router.post("/{id}/approve", response_model=PredictionResponse)
async def approve_prediction_scenario(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
    org_id: str = Depends(get_current_organization_id)
):
    service = PredictionService(db)
    return await service.submit_prediction_for_approval(id, org_id=org_id, current_user=current_user)
