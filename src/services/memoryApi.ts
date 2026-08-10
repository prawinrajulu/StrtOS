const API_BASE = '/api/v1/memory';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

export interface MemoryRecord {
  id: string;
  organization_id: string;
  client_id?: string;
  workflow_id?: string;
  report_id?: string;
  approval_id?: string;
  memory_type: 'CLIENT_CONTEXT' | 'DECISION' | 'STRATEGY' | 'APPROVAL' | 'WORKFLOW' | 'OUTCOME' | 'FEEDBACK' | 'LESSON';
  title: string;
  content?: string;
  structured_data?: Record<string, any>;
  source?: string;
  source_type?: string;
  confidence_score: number;
  importance_score: number;
  outcome_status: 'UNKNOWN' | 'PENDING' | 'SUCCESS' | 'PARTIAL' | 'FAILED';
  created_by?: string;
  created_at: string;
  updated_at?: string;
  occurred_at: string;
  expires_at?: string;
  extra_metadata?: Record<string, any>;
  relevance_score?: number;
}

export interface MemoryListResponse {
  memories: MemoryRecord[];
  total: number;
  page: number;
  page_size: number;
}

export interface OutcomeSubmissionPayload {
  client_id?: string;
  workflow_id?: string;
  metric_name: string;
  predicted_value: number;
  actual_value: number;
  unit?: string;
  measurement_period?: string;
  notes?: string;
}

export interface OutcomeResponse {
  outcome_memory_id: string;
  lesson_memory_id?: string;
  metric_name: string;
  predicted_value: number;
  actual_value: number;
  unit: string;
  absolute_variance: number;
  percentage_variance: number;
  outcome_status: 'UNKNOWN' | 'PENDING' | 'SUCCESS' | 'PARTIAL' | 'FAILED';
  lesson_summary?: string;
}

export const memoryApi = {
  async getMemories(params?: { client_id?: string; memory_type?: string; search?: string; page?: number }): Promise<MemoryListResponse> {
    const token = getToken();
    const query = new URLSearchParams();
    if (params?.client_id) query.append('client_id', params.client_id);
    if (params?.memory_type) query.append('memory_type', params.memory_type);
    if (params?.search) query.append('search', params.search);
    if (params?.page) query.append('page', params.page.toString());

    const resp = await fetch(`${API_BASE}?${query.toString()}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) return { memories: [], total: 0, page: 1, page_size: 20 };
    return resp.json();
  },

  async retrieveContext(clientId?: string, queryText?: string, limit: number = 5): Promise<MemoryRecord[]> {
    const token = getToken();
    const query = new URLSearchParams();
    if (clientId) query.append('client_id', clientId);
    if (queryText) query.append('query', queryText);
    query.append('limit', limit.toString());

    const resp = await fetch(`${API_BASE}/retrieve?${query.toString()}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) return [];
    return resp.json();
  },

  async getMemory(id: string): Promise<MemoryRecord | null> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) return null;
    return resp.json();
  },

  async submitOutcome(payload: OutcomeSubmissionPayload): Promise<OutcomeResponse> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/outcomes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Outcome submission failed' }));
      throw new Error(err.detail || 'Outcome submission failed');
    }
    return resp.json();
  }
};
