const API_BASE = '/api/v1/experiments';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

export interface Experiment {
  id: string;
  organization_id: string;
  client_id?: string;
  workflow_id?: string;
  prediction_id?: string;
  baseline_policy_id?: string;
  variant_policy_id?: string;
  experiment_name: string;
  objective: string;
  hypothesis: string;
  metric_name: string;
  baseline_value: number;
  target_value: number;
  minimum_detectable_effect: number;
  confidence_threshold: number;
  control_sample_size: number;
  variant_sample_size: number;
  status: 'DRAFT' | 'DESIGNED' | 'PENDING_APPROVAL' | 'APPROVED' | 'RUNNING' | 'MEASURING' | 'COMPLETED' | 'PAUSED' | 'FAILED' | 'CANCELLED' | 'INSUFFICIENT_DATA';
  result: 'WIN' | 'LOSS' | 'NEUTRAL' | 'INCONCLUSIVE' | 'FAILED';
  winner?: 'CONTROL' | 'VARIANT_A' | 'VARIANT_B';
  confidence: number;
  created_by?: string;
  created_at: string;
  updated_at?: string;
}

export interface ExperimentCreatePayload {
  experiment_name: string;
  objective: string;
  hypothesis: string;
  metric_name: string;
  baseline_value: number;
  target_value: number;
}

export const experimentsApi = {
  listExperiments: async (): Promise<Experiment[]> => {
    const res = await fetch(API_BASE, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) return [];
    return res.json();
  },

  getExperiment: async (id: string): Promise<Experiment> => {
    const res = await fetch(`${API_BASE}/${id}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch experiment');
    return res.json();
  },

  createExperiment: async (payload: ExperimentCreatePayload): Promise<any> => {
    const res = await fetch(API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to create experiment');
    return res.json();
  },

  designExperiment: async (id: string, availableSampleSize: number = 100): Promise<any> => {
    const res = await fetch(`${API_BASE}/${id}/design`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
      body: JSON.stringify({ available_sample_size: availableSampleSize }),
    });
    if (!res.ok) throw new Error('Failed to design experiment');
    return res.json();
  },

  startExperiment: async (id: string): Promise<Experiment> => {
    const res = await fetch(`${API_BASE}/${id}/start`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to start experiment');
    return res.json();
  },

  evaluateExperiment: async (id: string): Promise<any> => {
    const res = await fetch(`${API_BASE}/${id}/evaluate`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to evaluate experiment');
    return res.json();
  },

  proposeOptimization: async (id: string): Promise<any> => {
    const res = await fetch(`${API_BASE}/${id}/optimize`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to optimize experiment');
    return res.json();
  }
};
