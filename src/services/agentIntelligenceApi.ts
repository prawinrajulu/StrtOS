const API_BASE = '/api/v1/agent-intelligence';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

export type AgentHealthStatus = 'EXCELLENT' | 'HEALTHY' | 'DEGRADED' | 'AT_RISK' | 'CRITICAL';
export type AgentTrendStatus = 'IMPROVING' | 'STABLE' | 'DECLINING' | 'INSUFFICIENT_DATA';
export type WeaknessSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type RecommendationStatus = 'DRAFT' | 'EVALUATING' | 'PENDING_GOVERNANCE' | 'APPROVED' | 'REJECTED' | 'APPLIED' | 'ROLLED_BACK';

export interface AgentMetricRecord {
  id: string;
  organization_id: string;
  agent_name: string;
  policy_version: string;
  execution_count: number;
  successful_execution_count: number;
  failed_execution_count: number;
  degraded_execution_count: number;
  success_rate: number;
  failure_rate: number;
  average_latency_ms: number;
  p95_latency_ms: number;
  average_confidence: number;
  evidence_quality_score: number;
  tool_success_rate: number;
  llm_success_rate: number;
  prediction_accuracy: number;
  outcome_success_rate: number;
  policy_score: number;
  average_token_usage: number;
  estimated_cost: number;
  regression_score: number;
  overall_agent_score: number;
  health_status: AgentHealthStatus;
  trend: AgentTrendStatus;
  recorded_at: string;
}

export interface AgentBenchmarkRecord {
  id: string;
  organization_id: string;
  agent_name: string;
  rank: number;
  overall_score: number;
  reliability_score: number;
  accuracy_score: number;
  evidence_quality: number;
  execution_speed_ms: number;
  outcome_success: number;
  confidence: number;
  sample_count: number;
  trend: AgentTrendStatus;
  evaluated_at: string;
}

export interface AgentAnomalyRecord {
  id: string;
  organization_id: string;
  agent_name: string;
  anomaly_type: string;
  severity: WeaknessSeverity;
  baseline_value: number;
  observed_value: number;
  deviation_percent: number;
  explanation?: string;
  detected_at: string;
}

export interface AgentWeaknessRecord {
  id: string;
  organization_id: string;
  agent_name: string;
  weakness_type: string;
  severity: WeaknessSeverity;
  metric_name: string;
  current_value: number;
  baseline_value: number;
  deviation: number;
  sample_count: number;
  explanation: string;
  detected_at: string;
}

export interface AgentOptimizationRecommendationRecord {
  id: string;
  organization_id: string;
  agent_name: string;
  target_metric: string;
  current_value: number;
  target_value: number;
  expected_improvement: number;
  risk_score: number;
  risk_level: string;
  recommended_policy_change: Record<string, any>;
  reason: string;
  evidence_summary?: Record<string, any>;
  status: RecommendationStatus;
  governance_approval_id?: string;
  candidate_policy_id?: string;
  created_at: string;
}

export interface AgentIntelligenceOverview {
  total_agents: number;
  healthy_agents: number;
  at_risk_agents: number;
  critical_agents: number;
  average_agent_score: number;
  average_accuracy: number;
  average_reliability: number;
  optimization_recommendations_count: number;
  agents: AgentMetricRecord[];
  benchmarks: AgentBenchmarkRecord[];
  recent_anomalies: AgentAnomalyRecord[];
  recent_weaknesses: AgentWeaknessRecord[];
}

export const agentIntelligenceApi = {
  async getOverview(): Promise<AgentIntelligenceOverview> {
    const res = await fetch(`${API_BASE}/overview`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch agent intelligence overview');
    return res.json();
  },

  async listAgents(): Promise<AgentMetricRecord[]> {
    const res = await fetch(`${API_BASE}/agents`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch agents');
    return res.json();
  },

  async getAgent(agentName: string): Promise<AgentMetricRecord> {
    const res = await fetch(`${API_BASE}/agents/${encodeURIComponent(agentName)}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch agent metrics');
    return res.json();
  },

  async getAgentHistory(agentName: string): Promise<AgentMetricRecord[]> {
    const res = await fetch(`${API_BASE}/agents/${encodeURIComponent(agentName)}/history`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch agent history');
    return res.json();
  },

  async getBenchmarks(): Promise<AgentBenchmarkRecord[]> {
    const res = await fetch(`${API_BASE}/benchmarks`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch agent benchmarks');
    return res.json();
  },

  async getAnomalies(): Promise<AgentAnomalyRecord[]> {
    const res = await fetch(`${API_BASE}/anomalies`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch anomalies');
    return res.json();
  },

  async getWeaknesses(): Promise<AgentWeaknessRecord[]> {
    const res = await fetch(`${API_BASE}/weaknesses`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch weaknesses');
    return res.json();
  },

  async getRecommendations(): Promise<AgentOptimizationRecommendationRecord[]> {
    const res = await fetch(`${API_BASE}/recommendations`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch recommendations');
    return res.json();
  },

  async analyzeAgent(agentName?: string): Promise<AgentMetricRecord> {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify({ agent_name: agentName }),
    });
    if (!res.ok) throw new Error('Failed to run agent analysis');
    return res.json();
  },

  async evaluateRecommendation(recId: string): Promise<AgentOptimizationRecommendationRecord> {
    const res = await fetch(`${API_BASE}/recommendations/${recId}/evaluate`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to evaluate recommendation');
    return res.json();
  },

  async submitGovernanceRecommendation(recId: string): Promise<AgentOptimizationRecommendationRecord> {
    const res = await fetch(`${API_BASE}/recommendations/${recId}/submit-governance`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to submit recommendation to governance');
    return res.json();
  },
};
