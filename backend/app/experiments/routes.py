from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import UserModel
from app.experiments.schemas import (
    ExperimentCreate, ExperimentSchema, ExperimentDesignRequest,
    ExperimentMeasurementCreate, ExperimentMeasurementSchema
)
from app.experiments.service import ExperimentService

router = APIRouter(prefix="/experiments", tags=["Experiments"])

@router.post("", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_experiment(
    payload: ExperimentCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ExperimentService(db)
    try:
        return await service.create_experiment(current_user.organization_id, payload, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[ExperimentSchema])
async def list_experiments(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ExperimentService(db)
    return await service.repo.list_experiments(current_user.organization_id)

@router.get("/{exp_id}", response_model=ExperimentSchema)
async def get_experiment(
    exp_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ExperimentService(db)
    exp = await service.repo.get_experiment(exp_id, current_user.organization_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp

@router.post("/{exp_id}/design", response_model=Dict[str, Any])
async def design_experiment(
    exp_id: str,
    payload: ExperimentDesignRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ExperimentService(db)
    try:
        return await service.design_experiment(exp_id, current_user.organization_id, payload.available_sample_size)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{exp_id}/start", response_model=ExperimentSchema)
async def start_experiment(
    exp_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ExperimentService(db)
    try:
        return await service.start_experiment(exp_id, current_user.organization_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{exp_id}/measurements", response_model=Dict[str, Any])
async def record_measurement(
    exp_id: str,
    payload: ExperimentMeasurementCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ExperimentService(db)
    try:
        return await service.record_execution_measurement(exp_id, current_user.organization_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{exp_id}/evaluate", response_model=Dict[str, Any])
async def evaluate_experiment(
    exp_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ExperimentService(db)
    try:
        return await service.evaluate_experiment(exp_id, current_user.organization_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{exp_id}/optimize", response_model=Dict[str, Any])
async def propose_optimization(
    exp_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = ExperimentService(db)
    try:
        return await service.propose_optimization(exp_id, current_user.organization_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
