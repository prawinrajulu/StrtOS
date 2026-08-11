const API_BASE = '/api/v1/missions';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');
const getHeaders = () => {
  const token = getToken();
  return { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) };
};

export interface MissionSuccessCriterion {
  id: string;
  metric_name: string;
  baseline_value: number;
  target_value: number;
  current_value: number;
  unit: string;
  status: string;
}

export interface MissionStep {
  id: string;
  step_order: number;
  title: string;
  action_type: string;
  status: 'PENDING' | 'READY' | 'BLOCKED' | 'AWAITING_APPROVAL' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'SKIPPED';
  risk_level: string;
  autonomy_level: string;
  result_summary?: string;
}

export interface MissionPlanVersion {
  id: string;
  version: string;
  parent_version?: string;
  adaptation_reason?: string;
  delta_percentage: number;
  created_at: string;
}

export interface Mission {
  id: string;
  organization_id: string;
  objective_id?: string;
  title: string;
  summary?: string;
  status: 'DRAFT' | 'READY' | 'AWAITING_APPROVAL' | 'ACTIVE' | 'PAUSED' | 'BLOCKED' | 'ADAPTING' | 'COMPLETED' | 'FAILED' | 'CANCELLED' | 'EXPIRED';
  current_version: string;
  progress_percentage: number;
  risk_score: number;
  confidence_score: number;
  created_at: string;
  updated_at: string;
  criteria: MissionSuccessCriterion[];
  plans: MissionPlanVersion[];
  steps: MissionStep[];
}

export interface MissionEvaluation {
  mission_id: string;
  status: 'ON_TRACK' | 'AT_RISK' | 'OFF_TRACK' | 'LIKELY_TO_FAIL' | 'COMPLETED' | 'FAILED' | 'INSUFFICIENT_DATA';
  progress_percentage: number;
  risk_score: number;
  confidence_score: number;
  summary: string;
}

export const missionsApi = {
  getOverview: async () => {
    const res = await fetch(`${API_BASE}/overview`, { headers: getHeaders() });
    return res.json();
  },
  createMission: async (data: Partial<Mission>) => {
    const res = await fetch(`${API_BASE}`, { method: 'POST', headers: getHeaders(), body: JSON.stringify(data) });
    return res.json() as Promise<Mission>;
  },
  listMissions: async () => {
    const res = await fetch(`${API_BASE}`, { headers: getHeaders() });
    return res.json() as Promise<Mission[]>;
  },
  getMission: async (id: string) => {
    const res = await fetch(`${API_BASE}/${id}`, { headers: getHeaders() });
    return res.json() as Promise<Mission>;
  },
  startMission: async (id: string) => {
    const res = await fetch(`${API_BASE}/${id}/start`, { method: 'POST', headers: getHeaders() });
    return res.json() as Promise<Mission>;
  },
  evaluateMission: async (id: string) => {
    const res = await fetch(`${API_BASE}/${id}/evaluation`, { headers: getHeaders() });
    return res.json() as Promise<MissionEvaluation>;
  },
  replanMission: async (id: string, reason: string, delta: number) => {
    const res = await fetch(`${API_BASE}/${id}/replan`, {
      method: 'POST', headers: getHeaders(),
      body: JSON.stringify({ reason, adaptation_delta_percentage: delta })
    });
    return res.json() as Promise<Mission>;
  }
};
