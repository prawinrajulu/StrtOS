# Decision Optimization API Routes
"""FastAPI router exposing decision optimization endpoints.
All endpoints enforce JWT authentication and organization isolation via the
auth dependencies. The router is mounted at `/api/v1/decision-optimization` in
`app/main.py`.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.auth.dependencies import get_current_user, RoleChecker
from app.auth.models import UserRole
from app.core.database import get_db
from app.decision_optimization.service import DecisionOptimizationService
from app.decision_optimization.repository import DecisionOptimizationRepository
from app.decision_optimization.schemas import (
    ActionCandidateCreate,
    ActionCandidateResponse,
    ActionCandidateListResponse,
    ActionEvaluationRequest,
    ActionEvaluationResponse,
    ActionComparisonRequest,
    ActionComparisonResponse,
    SimulationRequest,
    SimulationResponse,
    ActionPlanCreate,
    ActionPlanResponse,
    RecommendationResponse,
    GovernanceSubmissionResponse,
    ExecutionResponse,
    DecisionExplanationResponse,
    DecisionOptimizationOverviewResponse,
)

router = APIRouter()

def get_repository(db = Depends(get_db)):
    return DecisionOptimizationRepository(db)

def get_service(
    repo: DecisionOptimizationRepository = Depends(get_repository),
) -> DecisionOptimizationService:
    return DecisionOptimizationService(repo)

# ---------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------
@router.get("/overview", response_model=DecisionOptimizationOverviewResponse)
async def get_overview(
    current_user = Depends(get_current_user),
    service: DecisionOptimizationService = Depends(get_service),
):
    return await service.repo.get_overview(current_user.organization_id)

# ---------------------------------------------------------------------
# Candidates
# ---------------------------------------------------------------------
@router.post("/candidates", response_model=List[ActionCandidateResponse])
async def create_candidates(
    payload: ActionCandidateCreate,
    current_user = Depends(get_current_user),
    service: DecisionOptimizationService = Depends(get_service),
):
    candidates = await service.generate_candidates(
        organization_id=current_user.organization_id,
        client_id=payload.client_id,
        workflow_id=payload.workflow_id,
        decision_id=payload.decision_id,
    )
    return [ActionCandidateResponse.model_validate(c, from_attributes=True) for c in candidates]

@router.get("/candidates", response_model=ActionCandidateListResponse)
async def list_candidates(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    service: DecisionOptimizationService = Depends(get_service),
):
    candidates = await service.repo.list_candidates(
        organization_id=current_user.organization_id,
        offset=skip,
        limit=limit,
    )
    resps = [ActionCandidateResponse.model_validate(c, from_attributes=True) for c in candidates]
    return ActionCandidateListResponse(candidates=resps, total=len(resps))

@router.get("/candidates/{candidate_id}", response_model=ActionCandidateResponse)
async def get_candidate(
    candidate_id: str,
    current_user = Depends(get_current_user),
    service: DecisionOptimizationService = Depends(get_service),
):
    candidate = await service.repo.get_candidate(candidate_id, current_user.organization_id)
    return ActionCandidateResponse.model_validate(candidate, from_attributes=True)

# ---------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------
@router.post("/evaluate", response_model=ActionEvaluationResponse)
async def evaluate_candidate(
    req: ActionEvaluationRequest,
    current_user = Depends(get_current_user),
    service: DecisionOptimizationService = Depends(get_service),
):
    risk_level = await service.evaluate_risk(req.candidate_id, current_user.organization_id)
    cand = await service.repo.get_candidate(req.candidate_id, current_user.organization_id)
    
    from app.decision_optimization.models import ActionEvaluation
    import uuid
    eval_obj = ActionEvaluation(
        id=str(uuid.uuid4()),
        organization_id=current_user.organization_id,
        client_id=req.client_id,
        workflow_id=req.workflow_id,
        decision_id=req.decision_id,
        candidate_id=req.candidate_id,
        score_breakdown=req.overrides or {"risk_level": risk_level},
        total_score=80.0,
        risk_level=risk_level,
        status="COMPLETED",
    )
    persisted = await service.repo.create_evaluation(eval_obj)
    return ActionEvaluationResponse.model_validate(persisted, from_attributes=True)

# ---------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------
@router.post("/compare", response_model=ActionComparisonResponse)
async def compare_candidates(
    req: ActionComparisonRequest,
    current_user = Depends(get_current_user),
    service: DecisionOptimizationService = Depends(get_service),
):
    candidates = []
    for cid in req.candidate_ids:
        cand = await service.repo.get_candidate(cid, current_user.organization_id)
        candidates.append(cand)

    recommendation = await service.optimizer.optimize(candidates)
    
    evaluations = await service.repo.list_evaluations(current_user.organization_id)
    eval_resps = [ActionEvaluationResponse.model_validate(e, from_attributes=True) for e in evaluations]

    return ActionComparisonResponse(
        compared=eval_resps,
        best_candidate_id=recommendation.recommended_action.id,
        explanation=recommendation.explanation,
    )

# ---------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------
@router.post("/simulate", response_model=SimulationResponse)
async def simulate_action(
    req: SimulationRequest,
    current_user = Depends(get_current_user),
    service: DecisionOptimizationService = Depends(get_service),
):
    return await service.simulate(req.candidate_ids, current_user.organization_id, req.horizon_minutes)

# ---------------------------------------------------------------------
# Planning
# ---------------------------------------------------------------------
@router.post("/plan", response_model=ActionPlanResponse)
async def create_plan(
    req: ActionPlanCreate,
    current_user = Depends(get_current_user),
    service: DecisionOptimizationService = Depends(get_service),
):
    return await service.create_plan(
        organization_id=current_user.organization_id,
        candidate_ids=req.candidates,
        dependencies=req.dependencies,
        client_id=req.client_id,
        workflow_id=req.workflow_id,
        decision_id=req.decision_id,
    )

# ---------------------------------------------------------------------
# Recommendation
# ---------------------------------------------------------------------
@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendation(
    current_user = Depends(get_current_user),
    service: DecisionOptimizationService = Depends(get_service),
):
    return await service.optimize_decision(current_user.organization_id)

# ---------------------------------------------------------------------
# Governance Submission
# ---------------------------------------------------------------------
@router.post("/{decision_id}/submit-governance", response_model=GovernanceSubmissionResponse)
async def submit_governance(
    decision_id: str,
    current_user = Depends(get_current_user),
    service: DecisionOptimizationService = Depends(get_service),
):
    return await service.submit_governance(decision_id, current_user.organization_id, current_user.id)

# ---------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------
@router.post("/{action_id}/execute", response_model=ExecutionResponse)
async def execute_action(
    action_id: str,
    current_user = Depends(get_current_user),
    service: DecisionOptimizationService = Depends(get_service),
):
    return await service.execute_action(action_id, current_user.organization_id)

# ---------------------------------------------------------------------
# Explanation
# ---------------------------------------------------------------------
@router.get("/{decision_id}/explanation", response_model=DecisionExplanationResponse)
async def get_explanation(
    decision_id: str,
    current_user = Depends(get_current_user),
    service: DecisionOptimizationService = Depends(get_service),
):
    return await service.get_explanation(decision_id, current_user.organization_id)
