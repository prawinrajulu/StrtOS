const API_BASE = '/api/v1/predictions';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

export interface PredictionRecord {
  id: string;
  organization_id: string;
  client_id?: string;
  workflow_id?: string;
  report_id?: string;
  approval_id?: string;
  scenario_id?: string;
  scenario_type: 'CONSERVATIVE' | 'BALANCED' | 'AGGRESSIVE' | 'CUSTOM';
  scenario_name: string;
  objective?: string;
  metric_name: string;
  predicted_value: number;
  lower_bound?: number;
  upper_bound?: number;
  unit: string;
  currency: string;
  confidence_score: number;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  evidence_count: number;
  memory_count: number;
  provider?: string;
  model?: string;
  assumptions?: string[];
  evidence_references?: Record<string, any>[];
  memory_references?: Record<string, any>[];
  prediction_status: 'DRAFT' | 'GENERATED' | 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'EXECUTED' | 'MEASURED' | 'EXPIRED' | 'DEGRADED' | 'UNAVAILABLE';
  created_by?: string;
  created_at: string;
  updated_at?: string;
  valid_from: string;
  valid_until?: string;
  extra_metadata?: Record<string, any>;
}

export interface PredictionListResponse {
  predictions: PredictionRecord[];
  total: number;
  page: number;
  page_size: number;
}

export interface ScenarioGeneratePayload {
  client_id?: string;
  workflow_id?: string;
  metric_name?: string;
  monthly_budget?: number;
  timeline_days?: number;
  objective?: string;
}

export interface ScenarioListResponse {
  scenarios: PredictionRecord[];
  recommended_scenario_type: 'CONSERVATIVE' | 'BALANCED' | 'AGGRESSIVE' | 'CUSTOM';
  summary: string;
}

export interface WhatIfSimulationPayload {
  client_id?: string;
  metric_name?: string;
  current_budget: number;
  simulated_budget: number;
  timeline_days?: number;
}

export interface WhatIfSimulationResponse {
  baseline: Record<string, any>;
  simulated_scenario: Record<string, any>;
  delta: Record<string, any>;
  confidence_score: number;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  assumptions: string[];
}

export const predictionsApi = {
  async getPredictions(params?: { client_id?: string; scenario_type?: string; search?: string; page?: number }): Promise<PredictionListResponse> {
    const token = getToken();
    const query = new URLSearchParams();
    if (params?.client_id) query.append('client_id', params.client_id);
    if (params?.scenario_type) query.append('scenario_type', params.scenario_type);
    if (params?.search) query.append('search', params.search);
    if (params?.page) query.append('page', params.page.toString());

    const resp = await fetch(`${API_BASE}?${query.toString()}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) return { predictions: [], total: 0, page: 1, page_size: 20 };
    return resp.json();
  },

  async generateScenarios(payload: ScenarioGeneratePayload): Promise<ScenarioListResponse> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/scenarios`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Failed to generate scenarios' }));
      throw new Error(err.detail || 'Failed to generate scenarios');
    }
    return resp.json();
  },

  async simulateWhatIf(payload: WhatIfSimulationPayload): Promise<WhatIfSimulationResponse> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/simulate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Simulation failed' }));
      throw new Error(err.detail || 'Simulation failed');
    }
    return resp.json();
  },

  async getPrediction(id: string): Promise<PredictionRecord | null> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) return null;
    return resp.json();
  },

  async approvePrediction(id: string): Promise<PredictionRecord> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/${id}/approve`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Approval submission failed' }));
      throw new Error(err.detail || 'Approval submission failed');
    }
    return resp.json();
  }
};
