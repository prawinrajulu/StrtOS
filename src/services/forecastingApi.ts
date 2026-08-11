const API_BASE = '/api/v1/forecasting';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

const getHeaders = () => {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

export interface ForecastMetric {
  id: string;
  metric_name: string;
  current_value: number;
  forecast_value?: number;
  lower_bound?: number;
  upper_bound?: number;
  unit: string;
  confidence_score: number;
}

export interface ForecastScenario {
  id: string;
  scenario_type: string;
  expected_outcome: number;
  lower_bound: number;
  upper_bound: number;
  confidence_score: number;
  risk_score: number;
  required_budget: number;
  time_to_impact_days: number;
}

export interface Forecast {
  id: string;
  organization_id: string;
  forecast_type: 'BUSINESS_HEALTH' | 'REVENUE' | 'CUSTOMER_GROWTH' | 'LEAD_GENERATION' | 'CONVERSION' | 'TRAFFIC' | 'SEO' | 'CAMPAIGN' | 'EXECUTION' | 'PREDICTION_ACCURACY' | 'AGENT_RELIABILITY' | 'STRATEGIC_OBJECTIVE';
  horizon: '7_DAYS' | '14_DAYS' | '30_DAYS' | '60_DAYS' | '90_DAYS' | '180_DAYS' | '365_DAYS';
  status: string;
  title: string;
  summary?: string;
  confidence_score: number;
  trend_direction: string;
  created_at: string;
  metrics: ForecastMetric[];
  scenarios: ForecastScenario[];
}

export interface SimulationResponse {
  forecast_id: string;
  baseline_outcome: number;
  simulated_outcome: number;
  delta_outcome: number;
  risk_score: number;
  confidence_score: number;
  assumptions: string[];
}

export interface FutureRisk {
  risk_type: string;
  probability: number;
  impact: string;
  risk_score: number;
  confidence: number;
  evidence: string;
  mitigation: string;
}

export interface FutureOpportunity {
  opportunity_type: string;
  expected_value: number;
  probability: number;
  confidence: number;
  evidence: string;
  time_to_impact: string;
  recommended_preparation: string;
}

export const forecastingApi = {
  getOverview: async () => {
    const res = await fetch(`${API_BASE}/overview`, { headers: getHeaders() });
    return res.json();
  },

  createForecast: async (data: Partial<Forecast>) => {
    const res = await fetch(`${API_BASE}/forecasts`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return res.json() as Promise<Forecast>;
  },

  listForecasts: async () => {
    const res = await fetch(`${API_BASE}/forecasts`, { headers: getHeaders() });
    return res.json() as Promise<Forecast[]>;
  },

  getForecast: async (id: string) => {
    const res = await fetch(`${API_BASE}/forecasts/${id}`, { headers: getHeaders() });
    return res.json() as Promise<Forecast>;
  },

  simulateForecast: async (id: string, budgetDelta: number, intensityMultiplier: number) => {
    const res = await fetch(`${API_BASE}/forecasts/${id}/simulate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        budget_delta: budgetDelta,
        intensity_multiplier: intensityMultiplier,
      }),
    });
    return res.json() as Promise<SimulationResponse>;
  },

  getFutureRisks: async (id: string) => {
    const res = await fetch(`${API_BASE}/forecasts/${id}/risks`, { headers: getHeaders() });
    return res.json() as Promise<FutureRisk[]>;
  },

  getFutureOpportunities: async (id: string) => {
    const res = await fetch(`${API_BASE}/forecasts/${id}/opportunities`, { headers: getHeaders() });
    return res.json() as Promise<FutureOpportunity[]>;
  }
};
