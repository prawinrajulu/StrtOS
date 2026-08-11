# Decision Optimization Repository
"""Async SQLAlchemy repository for decision optimization components.
All queries enforce tenant isolation by filtering on `organization_id` taken from the
provided `organization_id` argument. Functions raise `HTTPException(status_code=404)` when a record
is not found or belongs to another organization.
"""

from typing import List, Optional

from sqlalchemy import select, update
from fastapi import HTTPException, status

from app.core.database import AsyncSessionLocal
from app.decision_optimization.models import ActionCandidate, ActionEvaluation, ActionPlan, ActionPlanStep

class DecisionOptimizationRepository:
    """Repository providing CRUD operations for decision optimization entities."""

    def __init__(self, db_session: AsyncSessionLocal):
        self.db = db_session

    # ---------- ActionCandidate ----------
    async def create_candidate(self, candidate: ActionCandidate) -> ActionCandidate:
        self.db.add(candidate)
        await self.db.flush()
        await self.db.refresh(candidate)
        return candidate

    async def get_candidate(self, candidate_id: str, organization_id: str) -> ActionCandidate:
        stmt = select(ActionCandidate).where(ActionCandidate.id == candidate_id, ActionCandidate.organization_id == organization_id)
        result = await self.db.execute(stmt)
        candidate = result.scalar_one_or_none()
        if candidate is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
        return candidate

    async def list_candidates(self, organization_id: str, limit: int = 100, offset: int = 0) -> List[ActionCandidate]:
        stmt = (
            select(ActionCandidate)
            .where(ActionCandidate.organization_id == organization_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_candidate(self, candidate_id: str, organization_id: str, **kwargs) -> ActionCandidate:
        stmt = (
            update(ActionCandidate)
            .where(ActionCandidate.id == candidate_id, ActionCandidate.organization_id == organization_id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get_candidate(candidate_id, organization_id)

    # ---------- ActionEvaluation ----------
    async def create_evaluation(self, evaluation: ActionEvaluation) -> ActionEvaluation:
        self.db.add(evaluation)
        await self.db.flush()
        await self.db.refresh(evaluation)
        return evaluation

    async def get_evaluation(self, evaluation_id: str, organization_id: str) -> ActionEvaluation:
        stmt = select(ActionEvaluation).where(ActionEvaluation.id == evaluation_id, ActionEvaluation.organization_id == organization_id)
        result = await self.db.execute(stmt)
        eval_obj = result.scalar_one_or_none()
        if eval_obj is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found")
        return eval_obj

    async def list_evaluations(self, organization_id: str, limit: int = 100, offset: int = 0) -> List[ActionEvaluation]:
        stmt = (
            select(ActionEvaluation)
            .where(ActionEvaluation.organization_id == organization_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    # ---------- ActionPlan & ActionPlanStep ----------
    async def create_plan(self, plan: ActionPlan) -> ActionPlan:
        self.db.add(plan)
        await self.db.flush()
        await self.db.refresh(plan)
        return plan

    async def get_plan_by_id(self, plan_id: str, organization_id: str) -> ActionPlan:
        stmt = select(ActionPlan).where(ActionPlan.id == plan_id, ActionPlan.organization_id == organization_id)
        result = await self.db.execute(stmt)
        plan = result.scalar_one_or_none()
        if plan is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
        return plan

    async def create_plan_step(self, step: ActionPlanStep) -> ActionPlanStep:
        self.db.add(step)
        await self.db.flush()
        await self.db.refresh(step)
        return step

    async def get_plan_steps(self, plan_id: str, organization_id: str) -> List[ActionPlanStep]:
        stmt = select(ActionPlanStep).where(ActionPlanStep.plan_id == plan_id, ActionPlanStep.organization_id == organization_id).order_by(ActionPlanStep.step_order.asc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_plan_step(self, step_id: str, organization_id: str, **kwargs) -> ActionPlanStep:
        stmt = (
            update(ActionPlanStep)
            .where(ActionPlanStep.id == step_id, ActionPlanStep.organization_id == organization_id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(stmt)
        await self.db.commit()
        stmt = select(ActionPlanStep).where(ActionPlanStep.id == step_id, ActionPlanStep.organization_id == organization_id)
        result = await self.db.execute(stmt)
        step = result.scalar_one_or_none()
        if step is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan step not found")
        return step

    async def get_overview(self, organization_id: str) -> dict:
        """Return a high‑level overview for the organization."""
        cand_stmt = select(ActionCandidate.status, ActionCandidate.expected_roi).where(ActionCandidate.organization_id == organization_id)
        result = await self.db.execute(cand_stmt)
        rows = result.all()
        total = len(rows)
        recommended = sum(1 for r in rows if r[0] == "EVALUATED")
        pending = sum(1 for r in rows if r[0] == "PENDING")
        
        exec_stmt = select(ActionPlanStep).where(ActionPlanStep.organization_id == organization_id, ActionPlanStep.status == "COMPLETED")
        exec_res = await self.db.execute(exec_stmt)
        executed_count = len(exec_res.scalars().all())

        success_rate = (recommended / total) if total else 0.0
        expected_roi = sum(r[1] for r in rows if r[1] is not None) / total if total else 0.0
        return {
            "total_candidates": total,
            "recommended_actions": recommended,
            "pending_approvals": pending,
            "executed_actions": executed_count,
            "success_rate": success_rate,
            "expected_roi": expected_roi,
            "decision_confidence": 0.85,
            "recent_decisions": [],
        }
