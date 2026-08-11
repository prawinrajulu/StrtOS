const API_BASE = '/api/v1/decision-optimization';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

const getHeaders = () => {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

export interface DecisionOverview {
  total_candidates: number;
  recommended_actions: number;
  pending_approvals: number;
  executed_actions: number;
  success_rate: number;
  expected_roi: number;
  decision_confidence: number;
  recent_decisions: any[];
}

export interface ActionCandidate {
  id: string;
  organization_id: string;
  client_id?: string;
  workflow_id?: string;
  decision_id?: string;
  action_type: string;
  expected_value?: number;
  expected_cost?: number;
  expected_roi?: number;
  expected_confidence?: number;
  expected_risk?: string;
  causal_support?: number;
  historical_success?: number;
  agent_reliability?: number;
  reversibility?: string;
  time_to_impact?: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ActionPlanStep {
  id: string;
  action_id: string;
  step_order: number;
  dependency?: string;
  estimated_cost?: number;
  estimated_time?: number;
  risk_level: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ActionPlan {
  plan_id: string;
  steps: ActionPlanStep[];
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Recommendation {
  decision_id: string;
  recommended_action: ActionCandidate;
  alternatives: ActionCandidate[];
  score_breakdown: Record<string, number>;
  explanation: string;
  risk_level: string;
  governance_required: boolean;
}

export const decisionOptimizationApi = {
  getOverview: async (): Promise<DecisionOverview> => {
    const res = await fetch(`${API_BASE}/overview`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch overview');
    return res.json();
  },

  getCandidates: async (): Promise<{ candidates: ActionCandidate[]; total: number }> => {
    const res = await fetch(`${API_BASE}/candidates`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch candidates');
    return res.json();
  },

  generateCandidates: async (data: { client_id?: string; workflow_id?: string; decision_id?: string }): Promise<ActionCandidate[]> => {
    const res = await fetch(`${API_BASE}/candidates`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to generate candidates');
    return res.json();
  },

  getRecommendation: async (): Promise<Recommendation> => {
    const res = await fetch(`${API_BASE}/recommend`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch recommendation');
    return res.json();
  },

  createPlan: async (data: { candidates: string[]; dependencies?: Record<string, string[]> }): Promise<ActionPlan> => {
    const res = await fetch(`${API_BASE}/plan`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create plan');
    return res.json();
  },

  executeAction: async (actionId: string): Promise<any> => {
    const res = await fetch(`${API_BASE}/${actionId}/execute`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to execute action');
    return res.json();
  },

  getExplanation: async (decisionId: string): Promise<any> => {
    const res = await fetch(`${API_BASE}/${decisionId}/explanation`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch explanation');
    return res.json();
  },

  submitGovernance: async (decisionId: string): Promise<any> => {
    const res = await fetch(`${API_BASE}/${decisionId}/submit-governance`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to submit governance');
    return res.json();
  },
};
