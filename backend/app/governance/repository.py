from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.governance.models import ApprovalRequestModel, ApprovalStatus, RiskLevel

class GovernanceRepository:
    """Repository handling database operations for Governance Approval Requests."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, approval: ApprovalRequestModel) -> ApprovalRequestModel:
        self.session.add(approval)
        await self.session.flush()
        return approval

    async def get_by_id_and_org(self, approval_id: str, org_id: str) -> Optional[ApprovalRequestModel]:
        stmt = select(ApprovalRequestModel).where(
            ApprovalRequestModel.id == approval_id,
            ApprovalRequestModel.organization_id == org_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_workflow_and_org(self, workflow_id: str, org_id: str) -> Optional[ApprovalRequestModel]:
        stmt = select(ApprovalRequestModel).where(
            ApprovalRequestModel.workflow_id == workflow_id,
            ApprovalRequestModel.organization_id == org_id
        ).order_by(ApprovalRequestModel.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_org(
        self,
        org_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
        workflow_id: Optional[str] = None,
        client_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[ApprovalRequestModel], int]:
        stmt = select(ApprovalRequestModel).where(ApprovalRequestModel.organization_id == org_id)

        if status:
            stmt = stmt.where(ApprovalRequestModel.status == status)
        if risk_level:
            stmt = stmt.where(ApprovalRequestModel.risk_level == risk_level)
        if workflow_id:
            stmt = stmt.where(ApprovalRequestModel.workflow_id == workflow_id)
        if client_id:
            stmt = stmt.where(ApprovalRequestModel.client_id == client_id)
        if search:
            stmt = stmt.where(
                or_(
                    ApprovalRequestModel.title.ilike(f"%{search}%"),
                    ApprovalRequestModel.description.ilike(f"%{search}%")
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0

        # Paginated results
        stmt = stmt.order_by(ApprovalRequestModel.created_at.desc()).offset(skip).limit(limit)
        results = await self.session.execute(stmt)
        approvals = list(results.scalars().all())

        return approvals, total

    async def update(self, approval: ApprovalRequestModel) -> ApprovalRequestModel:
        await self.session.flush()
        return approval
