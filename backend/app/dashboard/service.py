from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.dashboard.schemas import (
    DashboardOverviewResponse, ClientKPIs, WorkflowKPIs, TaskKPIs, ReportKPIs,
    AgentPerformanceItem, IndustryAnalyticsItem, TrendPoint, RecentActivityItem
)
from app.dashboard.repository import DashboardRepository

class DashboardService:
    """Core Service calculating tenant-isolated executive metrics & insights."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = DashboardRepository(session)

    async def get_overview(self, org_id: str, days: int = 30) -> DashboardOverviewResponse:
        client_kpis = await self.repo.get_client_kpis(org_id)
        workflow_kpis = await self.repo.get_workflow_kpis(org_id)
        task_kpis = await self.repo.get_task_kpis(org_id)
        report_kpis = await self.repo.get_report_kpis(org_id)
        agent_perf = await self.repo.get_agent_performance(org_id)
        ind_analytics = await self.repo.get_industry_analytics(org_id)
        trends_raw = await self.repo.get_daily_trends(org_id, days=days)
        events_raw = await self.repo.get_recent_activities(org_id, limit=10)

        # Generate Deterministic Insights
        insights = []
        if workflow_kpis["total"] > 0:
            comp_pct = round((workflow_kpis["completed"] / workflow_kpis["total"]) * 100, 1)
            insights.append(f"Workflow completion rate stands at {comp_pct}% across active campaigns.")
        else:
            insights.append("Initialize executive workflows to start tracking agent execution metrics.")

        if client_kpis["total"] > 0:
            insights.append(f"Active accounts maintain an average strategic health score of {round(client_kpis['avg_health'], 1)}/100.")

        if len(agent_perf) > 0:
            top_agent = max(agent_perf, key=lambda x: x["success_rate"])
            insights.append(f"{top_agent['agent_name']} maintains peak execution reliability ({top_agent['success_rate']}% success rate).")

        c_dto = ClientKPIs(
            total_clients=client_kpis["total"],
            active_clients=client_kpis["active"],
            archived_clients=client_kpis["archived"],
            clients_by_industry=client_kpis["by_industry"],
            average_health_score=round(client_kpis["avg_health"], 1)
        )

        w_dto = WorkflowKPIs(
            total_workflows=workflow_kpis["total"],
            running_workflows=workflow_kpis["running"],
            completed_workflows=workflow_kpis["completed"],
            failed_workflows=workflow_kpis["failed"],
            cancelled_workflows=workflow_kpis["cancelled"],
            draft_workflows=workflow_kpis["draft"],
            average_confidence_score=round(workflow_kpis["avg_conf"], 1)
        )

        t_dto = TaskKPIs(
            total_tasks=task_kpis["total"],
            completed_tasks=task_kpis["completed"],
            running_tasks=task_kpis["running"],
            failed_tasks=task_kpis["failed"],
            waiting_tasks=task_kpis["waiting"],
            task_success_rate=task_kpis["success_rate"]
        )

        r_dto = ReportKPIs(
            total_reports=report_kpis["total"],
            final_reports=report_kpis["final_count"],
            average_overall_score=round(report_kpis["avg_score"], 1),
            average_confidence_score=round(report_kpis["avg_conf"], 1)
        )

        agent_dtos = [AgentPerformanceItem(**a) for a in agent_perf]
        ind_dtos = [IndustryAnalyticsItem(**i) for i in ind_analytics]
        trend_dtos = [TrendPoint(**t) for t in trends_raw]
        act_dtos = [RecentActivityItem.model_validate(e) for e in events_raw]

        return DashboardOverviewResponse(
            clients=c_dto,
            workflows=w_dto,
            tasks=t_dto,
            reports=r_dto,
            agent_performance=agent_dtos,
            industry_analytics=ind_dtos,
            trends=trend_dtos,
            insights=insights,
            recent_activities=act_dtos
        )
