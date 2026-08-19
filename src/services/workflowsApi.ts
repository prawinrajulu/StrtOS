export interface Workflow {
  id: string;
  organization_id: string;
  client_id: string;
  created_by?: string;
  title: string;
  directive?: string;
  status: 'DRAFT' | 'QUEUED' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  active_stage: string;
  progress: number;
  confidence_score: number;
  total_stages: number;
  completed_stages: number;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface TaskItem {
  id: string;
  workflow_id: string;
  title: string;
  agent_name: string;
  priority: string;
  status: 'WAITING' | 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'SKIPPED';
  retry_count: number;
  max_retries: number;
  started_at?: string;
  completed_at?: string;
  output?: Record<string, any>;
  error_message?: string;
}

export interface WorkflowEvent {
  id: string;
  workflow_id: string;
  event_type: string;
  payload?: any;
  created_at: string;
}

const getHeaders = () => {
  const token = localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
};

export const workflowsApi = {
  async listWorkflows(params?: { client_id?: string; status_filter?: string; search?: string }): Promise<Workflow[]> {
    try {
      const searchParams = new URLSearchParams();
      if (params?.client_id) searchParams.append('client_id', params.client_id);
      if (params?.status_filter) searchParams.append('status_filter', params.status_filter);
      if (params?.search) searchParams.append('search', params.search);

      const res = await fetch(`/api/v1/workflows?${searchParams.toString()}`, { headers: getHeaders() });
      if (res.ok) {
        const json = await res.json();
        return json.data.workflows || [];
      }
    } catch (e) {
      console.warn('Failed listing workflows', e);
    }
    return [];
  },

  async getWorkflow(workflowId: string): Promise<Workflow | null> {
    try {
      const res = await fetch(`/api/v1/workflows/${workflowId}`, { headers: getHeaders() });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed getting workflow details', e);
    }
    return null;
  },

  async createWorkflow(payload: { client_id: string; title: string; directive?: string }): Promise<Workflow | null> {
    try {
      const res = await fetch('/api/v1/workflows', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed creating workflow', e);
    }
    return null;
  },

  async startWorkflow(workflowId: string): Promise<Workflow | null> {
    try {
      const res = await fetch(`/api/v1/workflows/${workflowId}/start`, {
        method: 'POST',
        headers: getHeaders()
      });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed starting workflow', e);
    }
    return null;
  },

  async pauseWorkflow(workflowId: string): Promise<Workflow | null> {
    try {
      const res = await fetch(`/api/v1/workflows/${workflowId}/pause`, {
        method: 'POST',
        headers: getHeaders()
      });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed pausing workflow', e);
    }
    return null;
  },

  async resumeWorkflow(workflowId: string): Promise<Workflow | null> {
    try {
      const res = await fetch(`/api/v1/workflows/${workflowId}/resume`, {
        method: 'POST',
        headers: getHeaders()
      });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed resuming workflow', e);
    }
    return null;
  },

  async cancelWorkflow(workflowId: string): Promise<Workflow | null> {
    try {
      const res = await fetch(`/api/v1/workflows/${workflowId}/cancel`, {
        method: 'POST',
        headers: getHeaders()
      });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed cancelling workflow', e);
    }
    return null;
  },

  async getTasks(workflowId: string): Promise<TaskItem[]> {
    try {
      const res = await fetch(`/api/v1/workflows/${workflowId}/tasks`, { headers: getHeaders() });
      if (res.ok) {
        const json = await res.json();
        return json.data || [];
      }
    } catch (e) {
      console.warn('Failed getting workflow tasks', e);
    }
    return [];
  },

  async getEvents(workflowId: string): Promise<WorkflowEvent[]> {
    try {
      const res = await fetch(`/api/v1/workflows/${workflowId}/events`, { headers: getHeaders() });
      if (res.ok) {
        const json = await res.json();
        return json.data || [];
      }
    } catch (e) {
      console.warn('Failed getting workflow events', e);
    }
    return [];
  }
};
