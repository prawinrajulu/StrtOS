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

export type RecommendationAction =
  | 'CONTINUE'
  | 'ACCELERATE'
  | 'MAINTAIN'
  | 'DELAY'
  | 'REDUCE'
  | 'STOP'
  | 'REVIEW';

export interface PortfolioInitiative {
  id: string;
  organization_id: string;
  portfolio_id: string;
  title: string;
  description?: string;
  strategic_objective_id?: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  priority_score: number;
  expected_value: number;
  expected_roi: number;
  success_probability: number;
  risk_score: number;
  time_to_impact_days: number;
  resource_cost: number;
  capital_budget: number;
  status: string;
  selection_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface PortfolioRecommendation {
  id: string;
  organization_id: string;
  portfolio_id: string;
  initiative_id?: string;
  mission_id?: string;
  recommendation_type: RecommendationAction;
  title: string;
  reason: string;
  expected_impact?: string;
  risk_level: string;
  requires_governance: boolean;
  governance_approval_id?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CapitalAllocationBreakdown {
  id: string;
  title: string;
  allocated: number;
  expected_value: number;
  roi: number;
  pct_of_total_budget: number;
}

export interface CapitalAllocation {
  portfolio_id: string;
  total_budget?: number;
  current_spend: number;
  allocated_budget: number;
  unused_budget?: number;
  budget_shortage: number;
  expected_portfolio_roi?: number;
  allocation_breakdown: CapitalAllocationBreakdown[];
  data_quality: 'SUFFICIENT' | 'INSUFFICIENT_DATA';
  explanation: string;
}

export interface TradeoffResult {
  option_a_id: string;
  option_a_title: string;
  option_b_id: string;
  option_b_title: string;
  prioritize_a_tradeoffs: string[];
  prioritize_b_tradeoffs: string[];
  expected_value_delta: number;
  risk_delta: number;
  resource_efficiency_delta: number;
  recommendation: string;
}

export interface TradeoffResponse {
  portfolio_id: string;
  tradeoffs: TradeoffResult[];
  summary: string;
}

export interface DoNothingScenario {
  scenario_type: string;
  expected_value: number;
  expected_roi: number;
  risk_score: number;
  resource_utilization_pct: number;
  budget_utilization_pct: number;
  mission_completion_rate: number;
  strategic_progress_pct: number;
  summary: string;
}

export interface DoNothingSimulationResponse {
  portfolio_id: string;
  current: DoNothingScenario;
  optimized: DoNothingScenario;
  do_nothing: DoNothingScenario;
  recommendation: string;
  is_side_effect_free: boolean;
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

  // ─── v2.7.0 Initiatives, Allocations, Trade-offs, Recommendations, Simulation ────

  listInitiatives: async (portfolio_id?: string): Promise<PortfolioInitiative[]> => {
    const url = portfolio_id ? `${API_BASE}/initiatives?portfolio_id=${portfolio_id}` : `${API_BASE}/initiatives`;
    const res = await fetch(url, { headers: getHeaders() });
    return res.json();
  },

  createInitiative: async (
    data: {
      title: string;
      description?: string;
      priority?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
      expected_value?: number;
      expected_roi?: number;
      success_probability?: number;
      risk_score?: number;
      time_to_impact_days?: number;
      resource_cost?: number;
      capital_budget?: number;
    },
    portfolio_id?: string
  ): Promise<PortfolioInitiative> => {
    const url = portfolio_id ? `${API_BASE}/initiatives?portfolio_id=${portfolio_id}` : `${API_BASE}/initiatives`;
    const res = await fetch(url, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return res.json();
  },

  getInitiative: async (id: string): Promise<PortfolioInitiative> => {
    const res = await fetch(`${API_BASE}/initiatives/${id}`, { headers: getHeaders() });
    return res.json();
  },

  getCapitalAllocations: async (portfolio_id?: string): Promise<CapitalAllocation> => {
    const url = portfolio_id ? `${API_BASE}/allocations?portfolio_id=${portfolio_id}` : `${API_BASE}/allocations`;
    const res = await fetch(url, { headers: getHeaders() });
    return res.json();
  },

  getTradeoffs: async (portfolio_id?: string): Promise<TradeoffResponse> => {
    const url = portfolio_id ? `${API_BASE}/tradeoffs?portfolio_id=${portfolio_id}` : `${API_BASE}/tradeoffs`;
    const res = await fetch(url, { headers: getHeaders() });
    return res.json();
  },

  listRecommendations: async (portfolio_id?: string): Promise<PortfolioRecommendation[]> => {
    const url = portfolio_id ? `${API_BASE}/recommendations?portfolio_id=${portfolio_id}` : `${API_BASE}/recommendations`;
    const res = await fetch(url, { headers: getHeaders() });
    return res.json();
  },

  submitRecommendationGovernance: async (id: string): Promise<PortfolioRecommendation> => {
    const res = await fetch(`${API_BASE}/recommendations/${id}/governance`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return res.json();
  },

  simulateDoNothing: async (portfolio_id?: string): Promise<DoNothingSimulationResponse> => {
    const url = portfolio_id ? `${API_BASE}/simulate?portfolio_id=${portfolio_id}` : `${API_BASE}/simulate`;
    const res = await fetch(url, {
      method: 'POST',
      headers: getHeaders(),
    });
    return res.json();
  },
};
