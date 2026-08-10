const API_BASE = '/api/v1/swarm';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

export interface SwarmSessionRecord {
  id: string;
  organization_id: string;
  client_id?: string;
  workflow_id?: string;
  prediction_id?: string;
  status: 'DRAFT' | 'PLANNING' | 'RUNNING' | 'DEBATING' | 'CRITIQUING' | 'CONSENSUS' | 'COMPLETED' | 'DEGRADED' | 'FAILED' | 'CANCELLED';
  objective: string;
  strategy?: string;
  participating_agents: string[];
  active_agents: string[];
  completed_agents: string[];
  failed_agents: string[];
  consensus_score: number;
  confidence_score: number;
  conflict_count: number;
  debate_rounds: number;
  synthesis_output?: Record<string, any>;
  created_by?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at?: string;
  extra_metadata?: Record<string, any>;
}

export interface SwarmSessionListResponse {
  sessions: SwarmSessionRecord[];
  total: number;
  page: number;
  page_size: number;
}

export interface SwarmConflictRecord {
  id: string;
  swarm_id: string;
  organization_id: string;
  subject: string;
  agent_a: string;
  agent_b: string;
  claim_a: string;
  claim_b: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  resolution?: string;
  created_at: string;
}

export interface SwarmDebateRecord {
  id: string;
  swarm_id: string;
  organization_id: string;
  round_number: number;
  claim: string;
  challenge: string;
  resolution?: string;
  created_at: string;
}

export const swarmApi = {
  async getSessions(params?: { status?: string; search?: string; page?: number }): Promise<SwarmSessionListResponse> {
    const token = getToken();
    const query = new URLSearchParams();
    if (params?.status) query.append('status', params.status);
    if (params?.search) query.append('search', params.search);
    if (params?.page) query.append('page', params.page.toString());

    const resp = await fetch(`${API_BASE}/sessions?${query.toString()}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) return { sessions: [], total: 0, page: 1, page_size: 20 };
    return resp.json();
  },

  async createSession(objective: string): Promise<SwarmSessionRecord> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ objective })
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Failed to create swarm session' }));
      throw new Error(err.detail || 'Failed to create swarm session');
    }
    return resp.json();
  },

  async startSession(id: string): Promise<SwarmSessionRecord> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/sessions/${id}/start`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Swarm execution failed' }));
      throw new Error(err.detail || 'Swarm execution failed');
    }
    return resp.json();
  },

  async getConflicts(swarmId: string): Promise<SwarmConflictRecord[]> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/sessions/${swarmId}/conflicts`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) return [];
    return resp.json();
  },

  async getDebates(swarmId: string): Promise<SwarmDebateRecord[]> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/sessions/${swarmId}/debates`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) return [];
    return resp.json();
  }
};
