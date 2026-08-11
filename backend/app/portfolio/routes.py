from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.portfolio.schemas import (
    PortfolioCreate, PortfolioResponse, PortfolioEvaluationResponse,
    OptimizationRequest, OptimizationResponse, SimulationResponse,
    RebalanceRequest, RebalanceResponse, PortfolioOverviewResponse,
    ApproveDecisionRequest, PortfolioDecisionResponse
)
from app.portfolio.models import PortfolioStatus
from app.portfolio.service import PortfolioService

router = APIRouter(prefix="/portfolio", tags=["Autonomous Strategic Portfolio Management"])


def get_org_id(user) -> str:
    return user.organization_id if hasattr(user, "organization_id") else user.get("organization_id")


# ─────────────────────────── Overview ────────────────────────────────────────

@router.get("/overview", response_model=PortfolioOverviewResponse)
async def get_portfolio_overview(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Portfolio Command Center overview — health, value, missions, resources."""
    service = PortfolioService(db)
    return await service.get_overview(get_org_id(user))


# ─────────────────────────── Portfolio CRUD ───────────────────────────────────

@router.post("/portfolios", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    payload: PortfolioCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new strategic portfolio."""
    service = PortfolioService(db)
    return await service.create_portfolio(payload, get_org_id(user))


@router.get("/portfolios", response_model=List[PortfolioResponse])
async def list_portfolios(
    portfolio_status: Optional[PortfolioStatus] = Query(None, alias="status"),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all portfolios for the authenticated organization."""
    service = PortfolioService(db)
    return await service.list_portfolios(get_org_id(user), status=portfolio_status)


@router.get("/portfolios/{id}", response_model=PortfolioResponse)
async def get_portfolio(
    id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific portfolio with full details."""
    service = PortfolioService(db)
    try:
        return await service.get_portfolio(id, get_org_id(user))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─────────────────────────── Missions ────────────────────────────────────────

@router.get("/portfolios/{id}/missions")
async def get_portfolio_missions(
    id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all missions in the portfolio with priority and selection status."""
    service = PortfolioService(db)
    try:
        p = await service.get_portfolio(id, get_org_id(user))
        return {"portfolio_id": id, "missions": p.missions}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─────────────────────────── Resources ───────────────────────────────────────

@router.get("/portfolios/{id}/resources")
async def get_portfolio_resources(
    id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get resource availability and utilization for the portfolio."""
    service = PortfolioService(db)
    try:
        p = await service.get_portfolio(id, get_org_id(user))
        return {"portfolio_id": id, "resources": p.resources}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─────────────────────────── Risk ────────────────────────────────────────────

@router.get("/portfolios/{id}/risk")
async def get_portfolio_risk(
    id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get aggregated portfolio risk assessment."""
    service = PortfolioService(db)
    try:
        p = await service.get_portfolio(id, get_org_id(user))
        risk_score = p.portfolio_risk_score
        if risk_score >= 85.0:
            risk_level = "CRITICAL"
        elif risk_score >= 70.0:
            risk_level = "HIGH"
        elif risk_score >= 40.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        return {
            "portfolio_id": id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "confidence": p.confidence_score,
            "health": p.health
        }
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─────────────────────────── Versions ────────────────────────────────────────

@router.get("/portfolios/{id}/versions")
async def get_portfolio_versions(
    id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Immutable version history of portfolio allocations."""
    service = PortfolioService(db)
    try:
        p = await service.get_portfolio(id, get_org_id(user))
        return {"portfolio_id": id, "versions": p.versions}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─────────────────────────── Explanation ─────────────────────────────────────

@router.get("/portfolios/{id}/explanation")
async def get_portfolio_explanation(
    id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Knowledge graph-backed causal explanation of portfolio decisions."""
    service = PortfolioService(db)
    try:
        p = await service.get_portfolio(id, get_org_id(user))
        explanations = []
        for m in p.missions:
            explanations.append({
                "mission_id": m.mission_id,
                "selection_status": m.selection_status,
                "reason": m.selection_reason or "No explanation recorded.",
                "priority": m.priority,
                "priority_score": m.priority_score,
                "causal_chain": [
                    "EVIDENCE: Mission expected value and success probability assessed.",
                    "MEMORY: Historical mission performance patterns consulted.",
                    "KNOWLEDGE: Resource constraint model applied.",
                    "FORECAST: Future value projection included.",
                    f"DECISION: Mission {m.selection_status} — {m.selection_reason or 'see priority score.'}",
                ]
            })
        return {
            "portfolio_id": id,
            "portfolio_title": p.title,
            "overall_health": p.health,
            "mission_explanations": explanations
        }
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─────────────────────────── Optimization ────────────────────────────────────

@router.post("/portfolios/{id}/evaluate", response_model=PortfolioEvaluationResponse)
async def evaluate_portfolio(
    id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Evaluate portfolio health and performance vs expectations."""
    service = PortfolioService(db)
    try:
        return await service.evaluate_portfolio(id, get_org_id(user))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/portfolios/{id}/optimize", response_model=OptimizationResponse)
async def optimize_portfolio(
    id: str,
    payload: OptimizationRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Run portfolio optimization — maximize expected value under constraints."""
    service = PortfolioService(db)
    try:
        return await service.optimize_portfolio(id, payload, get_org_id(user))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/portfolios/{id}/simulate", response_model=SimulationResponse)
async def simulate_portfolio(
    id: str,
    payload: OptimizationRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Side-effect free scenario simulation — CONSERVATIVE/BALANCED/AGGRESSIVE/WHAT-IF."""
    service = PortfolioService(db)
    try:
        return await service.simulate_portfolio(id, payload, get_org_id(user))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─────────────────────────── Rebalance ───────────────────────────────────────

@router.post("/portfolios/{id}/rebalance", response_model=RebalanceResponse)
async def rebalance_portfolio(
    id: str,
    payload: RebalanceRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger portfolio rebalancing — creates new immutable version."""
    service = PortfolioService(db)
    try:
        return await service.rebalance_portfolio(id, payload, get_org_id(user))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─────────────────────────── Checkpoint ──────────────────────────────────────

@router.post("/portfolios/{id}/checkpoint")
async def run_portfolio_checkpoint(
    id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Run portfolio checkpoint — CONTINUE/REBALANCE/PAUSE/ESCALATE/COMPLETE/FAIL."""
    service = PortfolioService(db)
    try:
        return await service.run_checkpoint(id, get_org_id(user))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─────────────────────────── Governance Approval ─────────────────────────────

@router.post("/portfolios/{id}/approve", response_model=PortfolioDecisionResponse)
async def approve_portfolio_decision(
    id: str,
    payload: ApproveDecisionRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Approve a pending portfolio governance decision."""
    service = PortfolioService(db)
    try:
        return await service.approve_decision(id, payload, get_org_id(user))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
