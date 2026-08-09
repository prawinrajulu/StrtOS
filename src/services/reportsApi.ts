export interface ExecutiveReport {
  id: string;
  workflow_id: string;
  organization_id: string;
  client_id?: string;
  created_by?: string;
  title: string;
  executive_summary?: string;
  report_type: string;
  status: 'DRAFT' | 'FINAL' | 'ARCHIVED';
  overall_score: number;
  confidence_score: number;
  key_findings?: any[];
  recommendations?: any[];
  agent_results?: Record<string, any>;
  metrics?: Record<string, any>;
  summary_json?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface ReportMetrics {
  total_reports: number;
  average_score: number;
  average_confidence: number;
  completed_reports: number;
}

const getHeaders = () => {
  const token = localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
};

export const reportsApi = {
  async listReports(params?: { client_id?: string; workflow_id?: string; status_filter?: string; search?: string }): Promise<ExecutiveReport[]> {
    try {
      const searchParams = new URLSearchParams();
      if (params?.client_id) searchParams.append('client_id', params.client_id);
      if (params?.workflow_id) searchParams.append('workflow_id', params.workflow_id);
      if (params?.status_filter) searchParams.append('status_filter', params.status_filter);
      if (params?.search) searchParams.append('search', params.search);

      const res = await fetch(`/api/v1/reports?${searchParams.toString()}`, { headers: getHeaders() });
      if (res.ok) {
        const json = await res.json();
        return json.data.reports || [];
      }
    } catch (e) {
      console.warn('Failed listing reports', e);
    }
    return [];
  },

  async getReport(reportId: string): Promise<ExecutiveReport | null> {
    try {
      const res = await fetch(`/api/v1/reports/${reportId}`, { headers: getHeaders() });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed getting report details', e);
    }
    return null;
  },

  async getWorkflowReport(workflowId: string): Promise<ExecutiveReport | null> {
    try {
      const res = await fetch(`/api/v1/reports/workflow/${workflowId}`, { headers: getHeaders() });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed getting workflow report', e);
    }
    return null;
  },

  async getReportMetrics(): Promise<ReportMetrics | null> {
    try {
      const res = await fetch('/api/v1/reports/metrics', { headers: getHeaders() });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed getting report metrics', e);
    }
    return null;
  },

  async archiveReport(reportId: string): Promise<ExecutiveReport | null> {
    try {
      const res = await fetch(`/api/v1/reports/${reportId}`, {
        method: 'DELETE',
        headers: getHeaders()
      });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed archiving report', e);
    }
    return null;
  },

  async exportReport(reportId: string): Promise<any> {
    try {
      const res = await fetch(`/api/v1/reports/${reportId}/export`, { headers: getHeaders() });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed exporting report', e);
    }
    return null;
  }
};
