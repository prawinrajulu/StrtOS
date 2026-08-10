const API_BASE = '/api/v1/learning';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

export interface AgentPerformanceRecord {
  id: string;
  organization_id: string;
  client_id?: string;
  agent_name: string;
  agent_version: string;
  total_executions: number;
  successful_executions: number;
  degraded_executions: number;
  failed_executions: number;
  average_confidence: number;
  average_latency_ms: number;
  average_token_usage: number;
  prediction_accuracy: number;
  outcome_success_rate: number;
  human_approval_rate: number;
  human_rejection_rate: number;
  swarm_consensus_rate: number;
  tool_success_rate: number;
  evidence_quality_score: number;
  current_reliability_score: number;
  reliability_class: 'EXCELLENT' | 'GOOD' | 'MODERATE' | 'LOW' | 'CRITICAL' | 'INSUFFICIENT_DATA';
  created_at: string;
}

export interface ToolReliabilityRecord {
  id: string;
  organization_id: string;
  tool_name: string;
  success_count: number;
  failure_count: number;
  timeout_count: number;
  average_latency_ms: number;
  availability_rate: number;
  evidence_quality: number;
  reliability_score: number;
  last_successful_execution?: string;
}

export interface LLMProviderPerformanceRecord {
  id: string;
  organization_id: string;
  provider: string;
  model: string;
  agent_name?: string;
  average_latency_ms: number;
  average_token_usage: number;
  estimated_cost: number;
  success_count: number;
  failure_count: number;
  retry_count: number;
  fallback_count: number;
  structured_output_success_rate: number;
  confidence_score: number;
}

export interface AgentPolicyRecord {
  id: string;
  organization_id: string;
  agent_name: string;
  policy_version: string;
  configuration: Record<string, any>;
  reason: string;
  evidence_count: number;
  confidence: number;
  status: 'DRAFT' | 'TESTING' | 'ACTIVE' | 'ROLLED_BACK' | 'DEPRECATED';
  created_by?: string;
  created_at: string;
}

export interface AgentAdaptationRecord {
  id: string;
  organization_id: string;
  agent_name: string;
  title: string;
  description: string;
  previous_performance?: Record<string, any>;
  expected_improvement?: Record<string, any>;
  adaptation_delta: number;
  status: 'PROPOSED' | 'PENDING_GOVERNANCE' | 'APPROVED' | 'ACTIVATED' | 'REJECTED' | 'ROLLED_BACK';
  approval_id?: string;
  policy_id?: string;
  created_at: string;
}

export interface LearningOverviewRecord {
  overall_system_reliability: number;
  prediction_accuracy_avg: number;
  total_adaptations_applied: number;
  active_policies_count: number;
  agent_performance: AgentPerformanceRecord[];
  tool_reliability: ToolReliabilityRecord[];
  provider_performance: LLMProviderPerformanceRecord[];
}

export const learningApi = {
  async getOverview(): Promise<LearningOverviewRecord> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/overview`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) {
      return {
        overall_system_reliability: 80,
        prediction_accuracy_avg: 80,
        total_adaptations_applied: 0,
        active_policies_count: 5,
        agent_performance: [],
        tool_reliability: [],
        provider_performance: []
      };
    }
    return resp.json();
  },

  async getAgentPerformances(): Promise<AgentPerformanceRecord[]> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/agents`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) return [];
    return resp.json();
  },

  async proposeAdaptation(agentName: string, delta: number): Promise<AgentAdaptationRecord> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/agents/${encodeURIComponent(agentName)}/adapt?proposed_delta=${delta}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Failed to propose adaptation' }));
      throw new Error(err.detail || 'Failed to propose adaptation');
    }
    return resp.json();
  },

  async getPolicies(agentName: string): Promise<AgentPolicyRecord[]> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/policies?agent_name=${encodeURIComponent(agentName)}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) return [];
    return resp.json();
  },

  async rollbackPolicy(agentName: string): Promise<{ message: string }> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/policies/${encodeURIComponent(agentName)}/rollback`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Policy rollback failed' }));
      throw new Error(err.detail || 'Policy rollback failed');
    }
    return resp.json();
  }
};
