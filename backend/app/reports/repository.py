from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from app.models.database import Report as ReportModel

class ReportRepository:
    """Async SQLAlchemy Repository for Executive Reports enforcing strict tenant isolation."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id_and_org(self, report_id: str, org_id: str) -> Optional[ReportModel]:
        stmt = select(ReportModel).where(
            ReportModel.id == report_id,
            ReportModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_workflow_and_org(self, workflow_id: str, org_id: str) -> Optional[ReportModel]:
        stmt = select(ReportModel).where(
            ReportModel.workflow_id == workflow_id,
            ReportModel.organization_id == org_id
        ).order_by(ReportModel.created_at.desc())
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_by_org(
        self,
        org_id: str,
        skip: int = 0,
        limit: int = 50,
        client_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[ReportModel], int]:
        stmt = select(ReportModel).where(ReportModel.organization_id == org_id)
        count_stmt = select(func.count(ReportModel.id)).where(ReportModel.organization_id == org_id)

        if client_id:
            stmt = stmt.where(ReportModel.client_id == client_id)
            count_stmt = count_stmt.where(ReportModel.client_id == client_id)

        if workflow_id:
            stmt = stmt.where(ReportModel.workflow_id == workflow_id)
            count_stmt = count_stmt.where(ReportModel.workflow_id == workflow_id)

        if status:
            stmt = stmt.where(ReportModel.status == status)
            count_stmt = count_stmt.where(ReportModel.status == status)

        if search:
            search_filter = ReportModel.title.ilike(f"%{search}%")
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        stmt = stmt.order_by(ReportModel.created_at.desc()).offset(skip).limit(limit)

        res = await self.session.execute(stmt)
        reports = res.scalars().all()

        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar() or 0

        return list(reports), total

    async def create(self, report: ReportModel) -> ReportModel:
        self.session.add(report)
        await self.session.flush()
        return report

    async def update(self, report: ReportModel) -> ReportModel:
        await self.session.flush()
        return report

    async def archive(self, report_id: str, org_id: str) -> Optional[ReportModel]:
        report = await self.get_by_id_and_org(report_id, org_id)
        if report:
            report.status = "ARCHIVED"
            await self.session.flush()
        return report

    async def get_stats(self, org_id: str) -> Tuple[int, float, float, int]:
        stmt = select(
            func.count(ReportModel.id),
            func.coalesce(func.avg(ReportModel.overall_score), 0.0),
            func.coalesce(func.avg(ReportModel.confidence_score), 0.0),
            func.count(ReportModel.id).filter(ReportModel.status == "FINAL")
        ).where(ReportModel.organization_id == org_id)

        res = await self.session.execute(stmt)
        row = res.fetchone()
        if not row:
            return 0, 0.0, 0.0, 0
        return row[0], float(row[1]), float(row[2]), row[3]
