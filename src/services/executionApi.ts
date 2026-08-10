const API_BASE = '/api/v1/execution';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

export interface ActionRecord {
  id: string;
  organization_id: string;
  client_id?: string;
  workflow_id?: string;
  prediction_id?: string;
  approval_id?: string;
  created_by?: string;
  action_type: string;
  name: string;
  description?: string;
  status: 'DRAFT' | 'PENDING_POLICY' | 'PENDING_APPROVAL' | 'APPROVED' | 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'ROLLED_BACK' | 'EXPIRED' | 'DEGRADED';
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  autonomy_mode: 'MANUAL' | 'ASSISTED' | 'APPROVAL_REQUIRED' | 'AUTONOMOUS';
  policy_decision: 'ALLOW' | 'DENY' | 'REQUIRE_APPROVAL' | 'EXPIRED';
  input_payload?: Record<string, any>;
  validated_payload?: Record<string, any>;
  output_payload?: Record<string, any>;
  error_message?: string;
  retry_count: number;
  max_retries: number;
  idempotency_key?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at?: string;
  extra_metadata?: Record<string, any>;
}

export interface ActionListResponse {
  actions: ActionRecord[];
  total: number;
  page: number;
  page_size: number;
}

export interface ActionCreatePayload {
  client_id?: string;
  workflow_id?: string;
  prediction_id?: string;
  approval_id?: string;
  action_type: string;
  name: string;
  description?: string;
  risk_level?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  autonomy_mode?: 'MANUAL' | 'ASSISTED' | 'APPROVAL_REQUIRED' | 'AUTONOMOUS';
  input_payload?: Record<string, any>;
  idempotency_key?: string;
}

export interface ClosedLoopOptimizationResponse {
  action_id: string;
  prediction_id?: string;
  metric_name: string;
  predicted_value: number;
  actual_value: number;
  accuracy_score: number;
  percentage_error: number;
  outcome_status: string;
  lesson_memory_id: string;
  lesson_summary: string;
}

export const executionApi = {
  async getActions(params?: { client_id?: string; status?: string; search?: string; page?: number }): Promise<ActionListResponse> {
    const token = getToken();
    const query = new URLSearchParams();
    if (params?.client_id) query.append('client_id', params.client_id);
    if (params?.status) query.append('status', params.status);
    if (params?.search) query.append('search', params.search);
    if (params?.page) query.append('page', params.page.toString());

    const resp = await fetch(`${API_BASE}/actions?${query.toString()}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) return { actions: [], total: 0, page: 1, page_size: 20 };
    return resp.json();
  },

  async createAction(payload: ActionCreatePayload): Promise<ActionRecord> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/actions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Failed to create action' }));
      throw new Error(err.detail || 'Failed to create action');
    }
    return resp.json();
  },

  async executeAction(id: string): Promise<ActionRecord> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/actions/${id}/execute`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Execution failed' }));
      throw new Error(err.detail || 'Execution failed');
    }
    return resp.json();
  },

  async approveAction(id: string): Promise<ActionRecord> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/actions/${id}/approve`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Approval request failed' }));
      throw new Error(err.detail || 'Approval request failed');
    }
    return resp.json();
  },

  async retryAction(id: string): Promise<ActionRecord> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/actions/${id}/retry`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Retry failed' }));
      throw new Error(err.detail || 'Retry failed');
    }
    return resp.json();
  },

  async measureOutcome(id: string, actualMetricValue: number): Promise<ClosedLoopOptimizationResponse> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/actions/${id}/measure`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ actual_metric_value: actualMetricValue })
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Outcome measurement failed' }));
      throw new Error(err.detail || 'Outcome measurement failed');
    }
    return resp.json();
  }
};
