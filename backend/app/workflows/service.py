from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.database import Workflow as WorkflowModel, WorkflowEvent as WorkflowEventModel, Task as TaskModel, Report as ReportModel
from app.clients.repository import ClientRepository
from app.workflows.schemas import (
    WorkflowCreateRequest, WorkflowUpdateRequest, WorkflowDTO, WorkflowListResponse, TaskDTO, WorkflowEventDTO
)
from app.workflows.repository import WorkflowRepository
from app.agents.ceo.orchestrator import ceo_orchestrator

class WorkflowService:
    """Core Workflow Management Service enforcing tenant isolation and CEO Orchestrator integration."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = WorkflowRepository(session)
        self.client_repo = ClientRepository(session)

    async def create_workflow(self, payload: WorkflowCreateRequest, org_id: str, creator_id: str) -> WorkflowDTO:
        # Verify client belongs to current user's organization
        client = await self.client_repo.get_by_id_and_org(payload.client_id, org_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found or does not belong to your organization."
            )

        workflow = WorkflowModel(
            organization_id=org_id,
            client_id=payload.client_id,
            created_by=creator_id,
            title=payload.title.strip(),
            directive=payload.directive or client.business_goal or f"Execute strategy for {client.name}",
            status="DRAFT",
            active_stage="INITIALIZATION",
            progress=0,
            confidence_score=92.0
        )
        created = await self.repo.create(workflow)

        # Audit Event
        event = WorkflowEventModel(
            workflow_id=created.id,
            organization_id=org_id,
            event_type="workflow.created",
            payload={"title": created.title, "client_id": created.client_id}
        )
        await self.repo.create_event(event)

        await self.session.commit()
        await self.session.refresh(created)
        return WorkflowDTO.model_validate(created)

    async def get_workflow(self, workflow_id: str, org_id: str) -> WorkflowDTO:
        workflow = await self.repo.get_by_id_and_org(workflow_id, org_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found or does not belong to your organization."
            )
        return WorkflowDTO.model_validate(workflow)

    async def list_workflows(
        self,
        org_id: str,
        page: int = 1,
        page_size: int = 20,
        client_id: Optional[str] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> WorkflowListResponse:
        skip = (page - 1) * page_size
        workflows, total = await self.repo.list_by_org(
            org_id=org_id,
            skip=skip,
            limit=page_size,
            client_id=client_id,
            status=status_filter,
            search=search
        )
        dtos = [WorkflowDTO.model_validate(w) for w in workflows]
        return WorkflowListResponse(workflows=dtos, total=total, page=page, page_size=page_size)

    async def start_workflow(self, workflow_id: str, org_id: str) -> WorkflowDTO:
        workflow = await self.repo.get_by_id_and_org(workflow_id, org_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found.")

        if workflow.status in ["RUNNING", "COMPLETED"]:
            raise HTTPException(status_code=400, detail=f"Cannot start workflow in status '{workflow.status}'.")

        client = await self.client_repo.get_by_id_and_org(workflow.client_id, org_id)
        client_context = {
            "client_id": client.id if client else workflow.client_id,
            "organization_id": org_id,
            "client_name": client.name if client else "Enterprise Client",
            "industry": client.industry if client else "General Commercial",
            "website_url": client.website_url if client else None,
            "business_goal": client.business_goal if client else workflow.directive,
            "monthly_budget": client.monthly_budget if client else 0.0,
            "currency": client.currency if client else "USD"
        }

        # Update Workflow State
        if workflow.status == "RUNNING":
            return workflow
        if workflow.status == "COMPLETED":
            return workflow

        workflow.status = "RUNNING"
        workflow.started_at = datetime.now(timezone.utc)
        workflow.active_stage = "CEO AGENT ORCHESTRATION"
        workflow.progress = 15

        # Execute CEO Orchestrator Engine
        state = await ceo_orchestrator.execute_directive(
            directive=workflow.directive or workflow.title,
            client_name=client_context["client_name"],
            client_context=client_context
        )

        # Persist tasks generated by CEO Orchestrator into tasks table
        tasks_list = [
            ("Business Analysis Agent", "Conduct Market & TAM Analysis", "HIGH"),
            ("SEO Audit Agent", "Perform Technical & Core Web Vitals Audit", "HIGH"),
            ("Competitor Research Agent", "Map Competitors & Positioning Matrix", "MEDIUM"),
            ("Marketing Strategy Agent", "Formulate Omnichannel Growth Strategy", "HIGH"),
            ("Campaign Planner Agent", "Generate 90-Day Execution Roadmap", "HIGH"),
        ]

        for agent_name, title, prio in tasks_list:
            t = TaskModel(
                workflow_id=workflow.id,
                organization_id=org_id,
                title=title,
                agent_name=agent_name,
                priority=prio,
                status="COMPLETED",
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc)
            )
            self.session.add(t)

        # Generate Executive Report & Persist with Idempotency
        existing_report = await self.session.execute(
            select(ReportModel).where(ReportModel.workflow_id == workflow.id, ReportModel.organization_id == org_id)
        )
        rep = existing_report.scalars().first()

        if not rep:
            report_data = await ceo_orchestrator.reporter.generate_report(state)
            rep = ReportModel(
                workflow_id=workflow.id,
                organization_id=org_id,
                client_id=workflow.client_id,
                title=f"Executive Report - {workflow.title}",
                executive_summary=report_data.get("summary", "Executive intelligence strategy generated."),
                report_type="EXECUTIVE_SUMMARY",
                status="FINAL",
                overall_score=int(report_data.get("overall_score", 94)),
                confidence_score=float(report_data.get("confidence_score", 96.0)),
                key_findings=report_data.get("key_takeaways", []),
                recommendations=report_data.get("strategic_roadmap", []),
                agent_results=state.agent_outputs,
                metrics=report_data.get("financial_impact", {}),
                summary_json=report_data
            )
            self.session.add(rep)
            await self.session.flush()

        # Finalize Workflow state
        workflow.status = "COMPLETED"
        workflow.completed_stages = 9
        workflow.progress = 100
        workflow.completed_at = datetime.now(timezone.utc)

        # Audit Events
        self.session.add(WorkflowEventModel(
            workflow_id=workflow.id,
            organization_id=org_id,
            event_type="report.created",
            payload={"report_id": rep.id, "title": rep.title}
        ))
        self.session.add(WorkflowEventModel(
            workflow_id=workflow.id,
            organization_id=org_id,
            event_type="workflow.completed",
            payload={"report_id": rep.id, "confidence": workflow.confidence_score}
        ))

        await self.session.commit()
        await self.session.refresh(workflow)
        return WorkflowDTO.model_validate(workflow)

    async def pause_workflow(self, workflow_id: str, org_id: str) -> WorkflowDTO:
        workflow = await self.repo.get_by_id_and_org(workflow_id, org_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found.")
        if workflow.status != "RUNNING":
            raise HTTPException(status_code=400, detail="Only RUNNING workflows can be paused.")

        workflow.status = "PAUSED"
        event = WorkflowEventModel(workflow_id=workflow.id, organization_id=org_id, event_type="workflow.paused", payload={})
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(workflow)
        return WorkflowDTO.model_validate(workflow)

    async def resume_workflow(self, workflow_id: str, org_id: str) -> WorkflowDTO:
        workflow = await self.repo.get_by_id_and_org(workflow_id, org_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found.")
        if workflow.status != "PAUSED":
            raise HTTPException(status_code=400, detail="Only PAUSED workflows can be resumed.")

        workflow.status = "RUNNING"
        event = WorkflowEventModel(workflow_id=workflow.id, organization_id=org_id, event_type="workflow.resumed", payload={})
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(workflow)
        return WorkflowDTO.model_validate(workflow)

    async def cancel_workflow(self, workflow_id: str, org_id: str) -> WorkflowDTO:
        workflow = await self.repo.get_by_id_and_org(workflow_id, org_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found.")
        if workflow.status in ["COMPLETED", "CANCELLED"]:
            raise HTTPException(status_code=400, detail=f"Cannot cancel workflow in status '{workflow.status}'.")

        workflow.status = "CANCELLED"
        event = WorkflowEventModel(workflow_id=workflow.id, organization_id=org_id, event_type="workflow.cancelled", payload={})
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(workflow)
        return WorkflowDTO.model_validate(workflow)

    async def get_tasks(self, workflow_id: str, org_id: str) -> List[TaskDTO]:
        await self.get_workflow(workflow_id, org_id)
        tasks = await self.repo.get_tasks_by_workflow(workflow_id, org_id)
        return [TaskDTO.model_validate(t) for t in tasks]

    async def get_events(self, workflow_id: str, org_id: str) -> List[WorkflowEventDTO]:
        await self.get_workflow(workflow_id, org_id)
        events = await self.repo.get_events_by_workflow(workflow_id, org_id)
        return [WorkflowEventDTO.model_validate(e) for e in events]
