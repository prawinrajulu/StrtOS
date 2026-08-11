const API_BASE = '/api/v1/policies';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

export type PolicyStatus =
  | 'DRAFT'
  | 'CANDIDATE'
  | 'TESTING'
  | 'ACTIVE'
  | 'SUPERSEDED'
  | 'ROLLED_BACK'
  | 'REJECTED'
  | 'ARCHIVED';

export interface PolicyVersionRecord {
  id: string;
  policy_id: string;
  organization_id: string;
  agent_name: string;
  version: string;
  status: PolicyStatus;
  parameters: Record<string, any>;
  performance_score: number;
  confidence_score: number;
  risk_score: number;
  adaptation_delta: number;
  parent_version?: string;
  change_reason?: string;
  performance_metrics?: Record<string, any>;
  created_by?: string;
  created_at: string;
  activated_at?: string;
  retired_at?: string;
}

export interface PolicyRecord {
  id: string;
  organization_id: string;
  agent_name: string;
  policy_name: string;
  current_version: string;
  status: PolicyStatus;
  created_by?: string;
  created_at: string;
  updated_at: string;
  active_version?: PolicyVersionRecord;
}

export interface PolicyEvaluationRecord {
  id: string;
  policy_id: string;
  version: string;
  agent_name: string;
  accuracy_score: number;
  reliability_score: number;
  outcome_score: number;
  confidence_score: number;
  evidence_score: number;
  overall_policy_score: number;
  sample_count: number;
  evaluated_at: string;
}

export interface AgentPerformanceMetricItem {
  agent_name: string;
  current_policy_version: string;
  performance_score: number;
  accuracy_score: number;
  reliability_score: number;
  success_rate: number;
  sample_count: number;
  trend: 'IMPROVING' | 'STABLE' | 'DEGRADING';
  last_evaluated_at: string;
}

export interface PolicyAnalytics {
  total_policies: number;
  active_policies: number;
  candidate_policies: number;
  average_policy_score: number;
  policy_improvement_percent: number;
  total_rollbacks: number;
  governance_pending_count: number;
  agents_performance: AgentPerformanceMetricItem[];
}

export interface PolicyOptimizeResponse {
  status: string;
  reason?: string;
  candidate_version?: PolicyVersionRecord;
  expected_improvement?: number;
  risk_level?: string;
  governance_approval_id?: string;
}

export interface PolicyRollbackResponse {
  status: string;
  policy_id: string;
  active_version: string;
  previous_version: string;
  reason: string;
  rolled_back_at: string;
}

export const policiesApi = {
  async listPolicies(): Promise<PolicyRecord[]> {
    const res = await fetch(API_BASE, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch policies');
    return res.json();
  },

  async getPolicy(id: string): Promise<PolicyRecord> {
    const res = await fetch(`${API_BASE}/${id}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch policy');
    return res.json();
  },

  async listVersions(policyId: string): Promise<PolicyVersionRecord[]> {
    const res = await fetch(`${API_BASE}/${policyId}/versions`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch policy versions');
    return res.json();
  },

  async getPerformance(policyId: string): Promise<PolicyEvaluationRecord[]> {
    const res = await fetch(`${API_BASE}/${policyId}/performance`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch policy performance');
    return res.json();
  },

  async evaluatePolicy(policyId: string, payload: {
    predicted_kpi: number;
    actual_kpi: number;
    prediction_accuracy?: number;
    confidence?: number;
    outcome_status?: string;
    agent_execution_success?: boolean;
    evidence_quality?: number;
  }): Promise<PolicyEvaluationRecord> {
    const res = await fetch(`${API_BASE}/${policyId}/evaluate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to evaluate policy');
    return res.json();
  },

  async optimizePolicy(policyId: string, payload?: {
    target_performance_score?: number;
    proposed_parameters?: Record<string, any>;
    reason?: string;
  }): Promise<PolicyOptimizeResponse> {
    const res = await fetch(`${API_BASE}/${policyId}/optimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify(payload || {}),
    });
    if (!res.ok) throw new Error('Failed to optimize policy');
    return res.json();
  },

  async activateVersion(policyId: string, version: string): Promise<PolicyRecord> {
    const res = await fetch(`${API_BASE}/${policyId}/activate?version=${encodeURIComponent(version)}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to activate policy version');
    return res.json();
  },

  async rollbackPolicy(policyId: string, payload: {
    target_version?: string;
    reason: string;
  }): Promise<PolicyRollbackResponse> {
    const res = await fetch(`${API_BASE}/${policyId}/rollback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to rollback policy');
    return res.json();
  },

  async getAgentsPerformance(): Promise<AgentPerformanceMetricItem[]> {
    const res = await fetch(`${API_BASE}/agents/performance`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch agent performances');
    return res.json();
  },

  async getAnalytics(): Promise<PolicyAnalytics> {
    const res = await fetch(`${API_BASE}/analytics`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch policy analytics');
    return res.json();
  },
};
