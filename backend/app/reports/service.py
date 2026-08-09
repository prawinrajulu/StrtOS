from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.database import Report as ReportModel, Workflow as WorkflowModel, WorkflowEvent as WorkflowEventModel
from app.reports.schemas import (
    ReportCreateRequest, ReportUpdateRequest, ReportResponse, ReportListResponse, ReportMetricsResponse
)
from app.reports.repository import ReportRepository

class ReportService:
    """Core Service managing Executive Report persistence, retrieval, and stats."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ReportRepository(session)

    async def create_report(self, payload: ReportCreateRequest, org_id: str, creator_id: str) -> ReportResponse:
        # Idempotency check: check if report already exists for this workflow
        existing = await self.repo.get_by_workflow_and_org(payload.workflow_id, org_id)
        if existing:
            return ReportResponse.model_validate(existing)

        report = ReportModel(
            organization_id=org_id,
            workflow_id=payload.workflow_id,
            client_id=payload.client_id,
            created_by=creator_id,
            title=payload.title,
            executive_summary=payload.executive_summary,
            report_type=payload.report_type,
            status="FINAL",
            overall_score=payload.overall_score,
            confidence_score=payload.confidence_score,
            key_findings=payload.key_findings or [],
            recommendations=payload.recommendations or [],
            agent_results=payload.agent_results or {},
            metrics=payload.metrics or {}
        )

        created = await self.repo.create(report)

        # Audit Event
        event = WorkflowEventModel(
            workflow_id=created.workflow_id,
            organization_id=org_id,
            event_type="report.created",
            payload={"report_id": created.id, "title": created.title}
        )
        self.session.add(event)

        await self.session.commit()
        await self.session.refresh(created)
        return ReportResponse.model_validate(created)

    async def get_report(self, report_id: str, org_id: str) -> ReportResponse:
        report = await self.repo.get_by_id_and_org(report_id, org_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Executive report not found.")
        return ReportResponse.model_validate(report)

    async def get_by_workflow(self, workflow_id: str, org_id: str) -> ReportResponse:
        report = await self.repo.get_by_workflow_and_org(workflow_id, org_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found for this workflow.")
        return ReportResponse.model_validate(report)

    async def list_reports(
        self,
        org_id: str,
        page: int = 1,
        page_size: int = 20,
        client_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> ReportListResponse:
        skip = (page - 1) * page_size
        reports, total = await self.repo.list_by_org(
            org_id=org_id,
            skip=skip,
            limit=page_size,
            client_id=client_id,
            workflow_id=workflow_id,
            status=status_filter,
            search=search
        )
        dtos = [ReportResponse.model_validate(r) for r in reports]
        return ReportListResponse(reports=dtos, total=total, page=page, page_size=page_size)

    async def update_report(self, report_id: str, payload: ReportUpdateRequest, org_id: str) -> ReportResponse:
        report = await self.repo.get_by_id_and_org(report_id, org_id)
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Executive report not found.")

        if payload.title is not None:
            report.title = payload.title
        if payload.executive_summary is not None:
            report.executive_summary = payload.executive_summary
        if payload.status is not None:
            report.status = payload.status.value
        if payload.overall_score is not None:
            report.overall_score = payload.overall_score

        updated = await self.repo.update(report)
        await self.session.commit()
        await self.session.refresh(updated)
        return ReportResponse.model_validate(updated)

    async def archive_report(self, report_id: str, org_id: str) -> ReportResponse:
        archived = await self.repo.archive(report_id, org_id)
        if not archived:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Executive report not found.")
        await self.session.commit()
        await self.session.refresh(archived)
        return ReportResponse.model_validate(archived)

    async def get_metrics(self, org_id: str) -> ReportMetricsResponse:
        total, avg_score, avg_conf, completed = await self.repo.get_stats(org_id)
        return ReportMetricsResponse(
            total_reports=total,
            average_score=round(avg_score, 1),
            average_confidence=round(avg_conf, 1),
            completed_reports=completed
        )

    async def export_report(self, report_id: str, org_id: str) -> Dict[str, Any]:
        report = await self.get_report(report_id, org_id)
        return {
            "format": "STRTOS_EXECUTIVE_PDF_JSON_EXPORT",
            "report_id": report.id,
            "title": report.title,
            "organization_id": report.organization_id,
            "client_id": report.client_id,
            "workflow_id": report.workflow_id,
            "overall_score": report.overall_score,
            "confidence_score": report.confidence_score,
            "executive_summary": report.executive_summary,
            "key_findings": report.key_findings,
            "recommendations": report.recommendations,
            "agent_results": report.agent_results,
            "metrics": report.metrics,
            "exported_at": datetime.now(timezone.utc).isoformat()
        }
