const API_BASE = '/api/v1/strategy';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

const getHeaders = () => {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

export interface StrategicMetric {
  id: string;
  metric_name: string;
  baseline: number;
  target: number;
  actual?: number;
  unit: string;
}

export interface StrategicConstraint {
  id: string;
  constraint_type: string;
  limit_value: number;
  current_usage: number;
  is_hard_constraint: boolean;
  description?: string;
}

export interface StrategicObjective {
  id: string;
  organization_id: string;
  title: string;
  description?: string;
  category: string;
  status: 'DRAFT' | 'ACTIVE' | 'AT_RISK' | 'ON_TRACK' | 'COMPLETED' | 'CANCELLED' | 'ARCHIVED';
  target_horizon: '30_DAYS' | '60_DAYS' | '90_DAYS' | '180_DAYS' | '365_DAYS';
  baseline_value: number;
  target_value: number;
  current_value: number;
  unit: string;
  confidence_score: number;
  risk_level: string;
  created_at: string;
  updated_at: string;
  metrics: StrategicMetric[];
  constraints: StrategicConstraint[];
}

export interface StrategicMilestone {
  id: string;
  plan_id: string;
  title: string;
  horizon_day: number;
  target_metric_value: number;
  actual_metric_value?: number;
  status: string;
  expected_outcome?: string;
  confidence_score: number;
}

export interface StrategicPlanVersion {
  id: string;
  plan_id: string;
  version: string;
  parent_version?: string;
  change_reason: string;
  performance_before: number;
  performance_after: number;
  risk_before: number;
  risk_after: number;
  created_at: string;
}

export interface StrategicPlan {
  id: string;
  organization_id: string;
  objective_id: string;
  version: string;
  scenario_type: 'CONSERVATIVE' | 'BALANCED' | 'AGGRESSIVE' | 'CUSTOM';
  title: string;
  summary?: string;
  horizon: '30_DAYS' | '60_DAYS' | '90_DAYS' | '180_DAYS' | '365_DAYS';
  expected_value: number;
  confidence_score: number;
  risk_score: number;
  risk_level: string;
  status: string;
  created_at: string;
  updated_at: string;
  milestones: StrategicMilestone[];
  versions: StrategicPlanVersion[];
}

export interface ScenarioResponse {
  scenario_type: 'CONSERVATIVE' | 'BALANCED' | 'AGGRESSIVE' | 'CUSTOM';
  expected_value: number;
  confidence_score: number;
  risk_score: number;
  risk_level: string;
  cost: number;
  time_to_impact_days: number;
  resource_requirement: string;
  dependency_count: number;
  upside_potential: string;
  downside_risk: string;
}

export interface StrategyExplanationResponse {
  plan_id: string;
  why_objective: string;
  why_target: string;
  why_horizon: string;
  why_scenario: string;
  why_risk_score: string;
  evidence_sources: Array<{ finding: string; confidence: number; source: string }>;
  memory_references: Array<{ title: string; outcome: string; relevance: number }>;
  assumptions: string[];
  invalidation_factors: string[];
}

export const strategyApi = {
  getOverview: async () => {
    const res = await fetch(`${API_BASE}/overview`, { headers: getHeaders() });
    return res.json();
  },

  createObjective: async (data: Partial<StrategicObjective>) => {
    const res = await fetch(`${API_BASE}/objectives`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return res.json() as Promise<StrategicObjective>;
  },

  listObjectives: async () => {
    const res = await fetch(`${API_BASE}/objectives`, { headers: getHeaders() });
    return res.json() as Promise<StrategicObjective[]>;
  },

  createPlan: async (data: { objective_id: string; title: string; scenario_type?: string; horizon?: string }) => {
    const res = await fetch(`${API_BASE}/plans`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return res.json() as Promise<StrategicPlan>;
  },

  listPlans: async () => {
    const res = await fetch(`${API_BASE}/plans`, { headers: getHeaders() });
    return res.json() as Promise<StrategicPlan[]>;
  },

  getPlan: async (id: string) => {
    const res = await fetch(`${API_BASE}/plans/${id}`, { headers: getHeaders() });
    return res.json() as Promise<StrategicPlan>;
  },

  simulateScenarios: async (planId: string) => {
    const res = await fetch(`${API_BASE}/plans/${planId}/simulate`, { method: 'POST', headers: getHeaders() });
    return res.json() as Promise<ScenarioResponse[]>;
  },

  activatePlan: async (planId: string) => {
    const res = await fetch(`${API_BASE}/plans/${planId}/activate`, { method: 'POST', headers: getHeaders() });
    return res.json() as Promise<StrategicPlan>;
  },

  getExplanation: async (planId: string) => {
    const res = await fetch(`${API_BASE}/plans/${planId}/explanation`, { headers: getHeaders() });
    return res.json() as Promise<StrategyExplanationResponse>;
  },

  adaptPlan: async (planId: string, actualPerformance: number, reason: string) => {
    const res = await fetch(`${API_BASE}/plans/${planId}/adapt`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        actual_performance: actualPerformance,
        adaptation_reason: reason,
      }),
    });
    return res.json();
  },
};
