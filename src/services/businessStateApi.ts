const API_BASE = '/api/v1/business-state';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

const getHeaders = () => {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

export interface MetricSnapshot {
  id: string;
  metric_name: string;
  category: string;
  value: number;
  unit: string;
  confidence_score: number;
  source: string;
}

export interface StateSnapshot {
  id: string;
  organization_id: string;
  snapshot_type: 'CURRENT' | 'BASELINE' | 'HISTORICAL';
  health_score: number;
  health_status: 'EXCELLENT' | 'HEALTHY' | 'WATCH' | 'AT_RISK' | 'CRITICAL';
  summary?: string;
  created_at: string;
  metrics: MetricSnapshot[];
}

export interface Signal {
  id: string;
  metric_name: string;
  previous_value: number;
  current_value: number;
  delta: number;
  percentage_change: number;
  direction: 'INCREASE' | 'DECREASE' | 'STABLE' | 'UNKNOWN';
  confidence: number;
  created_at: string;
}

export interface BusinessAlert {
  id: string;
  alert_type: string;
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'DETECTED' | 'ACKNOWLEDGED' | 'INVESTIGATING' | 'ACTION_RECOMMENDED' | 'GOVERNANCE_PENDING' | 'RESOLVED' | 'DISMISSED';
  title: string;
  message: string;
  confidence_score: number;
  recommended_action?: string;
  governance_required: boolean;
  created_at: string;
}

export interface Opportunity {
  title: string;
  category: string;
  expected_value: number;
  confidence_score: number;
  evidence: string;
  recommended_action: string;
}

export interface Threat {
  title: string;
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence_score: number;
  evidence: string;
  potential_impact: string;
  recommended_action: string;
}

export interface BusinessExplanation {
  alert_id: string;
  why_detected: string;
  what_changed: string;
  evidence_summary: string;
  causation_vs_correlation: string;
  affected_objective: string;
  expected_impact: string;
  governance_required: boolean;
}

export const businessStateApi = {
  getOverview: async () => {
    const res = await fetch(`${API_BASE}/overview`, { headers: getHeaders() });
    return res.json();
  },

  listSnapshots: async () => {
    const res = await fetch(`${API_BASE}/snapshots`, { headers: getHeaders() });
    return res.json() as Promise<StateSnapshot[]>;
  },

  listSignals: async () => {
    const res = await fetch(`${API_BASE}/signals`, { headers: getHeaders() });
    return res.json() as Promise<Signal[]>;
  },

  listOpportunities: async () => {
    const res = await fetch(`${API_BASE}/opportunities`, { headers: getHeaders() });
    return res.json() as Promise<Opportunity[]>;
  },

  listThreats: async () => {
    const res = await fetch(`${API_BASE}/threats`, { headers: getHeaders() });
    return res.json() as Promise<Threat[]>;
  },

  listAlerts: async () => {
    const res = await fetch(`${API_BASE}/alerts`, { headers: getHeaders() });
    return res.json() as Promise<BusinessAlert[]>;
  },

  acknowledgeAlert: async (id: string) => {
    const res = await fetch(`${API_BASE}/alerts/${id}/acknowledge`, { method: 'POST', headers: getHeaders() });
    return res.json() as Promise<BusinessAlert>;
  },

  resolveAlert: async (id: string) => {
    const res = await fetch(`${API_BASE}/alerts/${id}/resolve`, { method: 'POST', headers: getHeaders() });
    return res.json() as Promise<BusinessAlert>;
  },

  getAlertExplanation: async (id: string) => {
    const res = await fetch(`${API_BASE}/alerts/${id}/explanation`, { headers: getHeaders() });
    return res.json() as Promise<BusinessExplanation>;
  }
};
