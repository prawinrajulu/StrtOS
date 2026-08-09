from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ClientKPIs(BaseModel):
    total_clients: int = 0
    active_clients: int = 0
    archived_clients: int = 0
    clients_by_industry: Dict[str, int] = {}
    average_health_score: float = 0.0

class WorkflowKPIs(BaseModel):
    total_workflows: int = 0
    running_workflows: int = 0
    completed_workflows: int = 0
    failed_workflows: int = 0
    cancelled_workflows: int = 0
    draft_workflows: int = 0
    average_confidence_score: float = 0.0
    average_completion_time_seconds: float = 0.0

class TaskKPIs(BaseModel):
    total_tasks: int = 0
    completed_tasks: int = 0
    running_tasks: int = 0
    failed_tasks: int = 0
    waiting_tasks: int = 0
    task_success_rate: float = 0.0

class ReportKPIs(BaseModel):
    total_reports: int = 0
    final_reports: int = 0
    average_overall_score: float = 0.0
    average_confidence_score: float = 0.0

class AgentPerformanceItem(BaseModel):
    agent_name: str
    total_executions: int = 0
    completed_executions: int = 0
    failed_executions: int = 0
    success_rate: float = 0.0
    average_confidence: float = 0.0

class IndustryAnalyticsItem(BaseModel):
    industry: str
    client_count: int = 0
    average_health_score: float = 0.0
    average_workflow_confidence: float = 0.0

class TrendPoint(BaseModel):
    date: str
    completed_workflows: int = 0
    reports_generated: int = 0
    tasks_completed: int = 0

class RecentActivityItem(BaseModel):
    id: str
    workflow_id: str
    event_type: str
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DashboardOverviewResponse(BaseModel):
    clients: ClientKPIs
    workflows: WorkflowKPIs
    tasks: TaskKPIs
    reports: ReportKPIs
    agent_performance: List[AgentPerformanceItem]
    industry_analytics: List[IndustryAnalyticsItem]
    trends: List[TrendPoint]
    insights: List[str]
    recent_activities: List[RecentActivityItem]
