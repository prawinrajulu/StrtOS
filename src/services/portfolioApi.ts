const API_BASE = '/api/v1/portfolio';

const getToken = () =>
  localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

const getHeaders = () => ({
  'Content-Type': 'application/json',
  ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
});

export interface PortfolioResource {
  id: string;
  resource_type: string;
  available: number;
  allocated: number;
  remaining: number;
  unit: string;
  period: string;
  utilization_pct: number;
}

export interface PortfolioMission {
  id: string;
  mission_id: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  priority_score: number;
  expected_value: number;
  success_probability: number;
  resource_requirement: number;
  selection_status: 'SELECTED' | 'DEFERRED' | 'PAUSED';
  selection_reason?: string;
  created_at: string;
}

export interface PortfolioVersion {
  id: string;
  version: string;
  parent_version?: string;
  reason?: string;
  risk_change: number;
  expected_value_change: number;
  approved_by?: string;
  created_at: string;
}

export interface Portfolio {
  id: string;
  organization_id: string;
  objective_id?: string;
  title: string;
  summary?: string;
  status: string;
  current_version: string;
  health: 'EXCELLENT' | 'HEALTHY' | 'WATCH' | 'AT_RISK' | 'CRITICAL';
  expected_value: number;
  actual_value: number;
  portfolio_risk_score: number;
  confidence_score: number;
  total_budget: number;
  allocated_budget: number;
  scenario_type: string;
  created_at: string;
  updated_at: string;
  missions: PortfolioMission[];
  resources: PortfolioResource[];
  versions: PortfolioVersion[];
}

export interface PortfolioOverview {
  organization_id: string;
  total_portfolios: number;
  active_portfolios: number;
  total_expected_value: number;
  total_allocated_budget: number;
  missions_selected: number;
  missions_deferred: number;
  missions_at_risk: number;
  portfolios_requiring_rebalance: number;
  overall_health: string;
}

export interface MissionOptimizationResult {
  mission_id: string;
  title: string;
  priority_score: number;
  expected_value: number;
  success_probability: number;
  resource_requirement: number;
  value_cost_ratio: number;
  status: 'SELECTED' | 'DEFERRED' | 'PAUSED';
  reason: string;
}

export interface OptimizationResponse {
  portfolio_id: string;
  scenario_type: string;
  selected_missions: MissionOptimizationResult[];
  deferred_missions: MissionOptimizationResult[];
  paused_missions: MissionOptimizationResult[];
  expected_portfolio_value: number;
  portfolio_risk_score: number;
  confidence: number;
  budget_utilization_pct: number;
  capacity_utilization_pct: number;
  explanation: string;
}

export interface ScenarioResult {
  scenario_type: string;
  expected_value: number;
  risk_score: number;
  budget_utilization_pct: number;
  capacity_utilization_pct: number;
  selected_mission_count: number;
  deferred_mission_count: number;
  confidence: number;
}

export interface SimulationResponse {
  portfolio_id: string;
  scenarios: ScenarioResult[];
  recommendation: string;
}

export const portfolioApi = {
  getOverview: async (): Promise<PortfolioOverview> => {
    const res = await fetch(`${API_BASE}/overview`, { headers: getHeaders() });
    return res.json();
  },

  createPortfolio: async (data: {
    title: string;
    summary?: string;
    total_budget: number;
    scenario_type?: string;
    objective_id?: string;
  }): Promise<Portfolio> => {
    const res = await fetch(`${API_BASE}/portfolios`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return res.json();
  },

  listPortfolios: async (): Promise<Portfolio[]> => {
    const res = await fetch(`${API_BASE}/portfolios`, { headers: getHeaders() });
    return res.json();
  },

  getPortfolio: async (id: string): Promise<Portfolio> => {
    const res = await fetch(`${API_BASE}/portfolios/${id}`, { headers: getHeaders() });
    return res.json();
  },

  evaluatePortfolio: async (id: string): Promise<unknown> => {
    const res = await fetch(`${API_BASE}/portfolios/${id}/evaluate`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return res.json();
  },

  optimizePortfolio: async (
    id: string,
    scenario_type = 'BALANCED',
    budget_delta_pct = 0,
    capacity_delta_pct = 0
  ): Promise<OptimizationResponse> => {
    const res = await fetch(`${API_BASE}/portfolios/${id}/optimize`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ scenario_type, budget_delta_pct, capacity_delta_pct }),
    });
    return res.json();
  },

  simulatePortfolio: async (
    id: string,
    budget_delta_pct = 0,
    capacity_delta_pct = 0
  ): Promise<SimulationResponse> => {
    const res = await fetch(`${API_BASE}/portfolios/${id}/simulate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ scenario_type: 'BALANCED', budget_delta_pct, capacity_delta_pct }),
    });
    return res.json();
  },

  rebalancePortfolio: async (id: string, reason: string, force = false): Promise<unknown> => {
    const res = await fetch(`${API_BASE}/portfolios/${id}/rebalance`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ reason, force }),
    });
    return res.json();
  },

  runCheckpoint: async (id: string): Promise<unknown> => {
    const res = await fetch(`${API_BASE}/portfolios/${id}/checkpoint`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return res.json();
  },

  getVersions: async (id: string): Promise<unknown> => {
    const res = await fetch(`${API_BASE}/portfolios/${id}/versions`, { headers: getHeaders() });
    return res.json();
  },

  getExplanation: async (id: string): Promise<unknown> => {
    const res = await fetch(`${API_BASE}/portfolios/${id}/explanation`, { headers: getHeaders() });
    return res.json();
  },
};
