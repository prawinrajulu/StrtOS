export interface ClientKPIs {
  total_clients: number;
  active_clients: number;
  archived_clients: number;
  clients_by_industry: Record<string, number>;
  average_health_score: number;
}

export interface WorkflowKPIs {
  total_workflows: number;
  running_workflows: number;
  completed_workflows: number;
  failed_workflows: number;
  cancelled_workflows: number;
  draft_workflows: number;
  average_confidence_score: number;
  average_completion_time_seconds: number;
}

export interface TaskKPIs {
  total_tasks: number;
  completed_tasks: number;
  running_tasks: number;
  failed_tasks: number;
  waiting_tasks: number;
  task_success_rate: number;
}

export interface ReportKPIs {
  total_reports: number;
  final_reports: number;
  average_overall_score: number;
  average_confidence_score: number;
}

export interface AgentPerformanceItem {
  agent_name: string;
  total_executions: number;
  completed_executions: number;
  failed_executions: number;
  success_rate: number;
  average_confidence: number;
}

export interface IndustryAnalyticsItem {
  industry: string;
  client_count: number;
  average_health_score: number;
  average_workflow_confidence: number;
}

export interface TrendPoint {
  date: string;
  completed_workflows: number;
  reports_generated: number;
  tasks_completed: number;
}

export interface RecentActivityItem {
  id: string;
  workflow_id: string;
  event_type: string;
  payload?: any;
  created_at: string;
}

export interface DashboardOverview {
  clients: ClientKPIs;
  workflows: WorkflowKPIs;
  tasks: TaskKPIs;
  reports: ReportKPIs;
  agent_performance: AgentPerformanceItem[];
  industry_analytics: IndustryAnalyticsItem[];
  trends: TrendPoint[];
  insights: string[];
  recent_activities: RecentActivityItem[];
}

const getHeaders = () => {
  const token = localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
};

export const dashboardApi = {
  async getOverview(days: number = 30): Promise<DashboardOverview | null> {
    try {
      const res = await fetch(`/api/v1/dashboard/overview?days=${days}`, { headers: getHeaders() });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed getting dashboard overview', e);
    }
    return null;
  }
};
