const API_BASE = '/api/v1/command-center';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

const getHeaders = () => {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

export interface ExecutiveHealth {
  overall_score: number;
  status: 'EXCELLENT' | 'HEALTHY' | 'WATCH' | 'AT_RISK' | 'CRITICAL';
  business_health: number;
  strategy_health: number;
  execution_health: number;
  ai_health: number;
  prediction_health: number;
  governance_health: number;
  learning_health: number;
  breakdown: Record<string, number>;
}

export interface StrategicPriority {
  id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  why_it_matters: string;
  evidence: string;
  affected_objective: string;
  expected_impact: string;
  risk: string;
  recommended_next_step: string;
}

export interface DecisionAlternative {
  option_type: 'DO_NOTHING' | 'RECOMMENDED_ACTION' | 'CONSERVATIVE' | 'BALANCED' | 'AGGRESSIVE';
  title: string;
  expected_value: number;
  confidence: number;
  risk_score: number;
  cost: number;
  time_to_impact: string;
  probability_of_success: number;
}

export interface MultiAgentConsensus {
  consensus_score: number;
  status: 'CONSENSUS_ACHIEVED' | 'DEBATE_REQUIRED' | 'HUMAN_REVIEW_REQUIRED';
  supporting_agents: string[];
  dissenting_agents: string[];
  agent_contributions: Array<{ agent: string; recommendation: string; confidence: number }>;
}

export interface StrategicDecision {
  id: string;
  organization_id: string;
  title: string;
  problem_statement: string;
  do_nothing_outcome: string;
  recommended_action: string;
  expected_value: number;
  risk_score: number;
  confidence_score: number;
  consensus_score: number;
  autonomy_level: 'MANUAL' | 'ASSISTED' | 'APPROVAL_REQUIRED' | 'AUTONOMOUS';
  governance_status: string;
  created_at: string;
}

export interface DecisionExplanation {
  decision_id: string;
  why_this_decision: string;
  verified_evidence: string[];
  historical_memory: string[];
  causal_support: string;
  forecast_summary: string;
  agent_consensus_summary: string;
  risk_breakdown: string;
  assumptions: string[];
  uncertainties: string[];
}

export interface CommandCenterOverview {
  organization_id: string;
  executive_health: ExecutiveHealth;
  top_priorities: StrategicPriority[];
  active_decisions: StrategicDecision[];
  active_alerts_count: number;
  active_executions_count: number;
  summary: string;
}

export const commandCenterApi = {
  getOverview: async (): Promise<CommandCenterOverview | null> => {
    try {
      const res = await fetch(`${API_BASE}/overview`, { headers: getHeaders() });
      if (!res.ok) return null;
      return (await res.json()) as CommandCenterOverview;
    } catch {
      return null;
    }
  },

  getHealth: async (): Promise<ExecutiveHealth | null> => {
    try {
      const res = await fetch(`${API_BASE}/health`, { headers: getHeaders() });
      if (!res.ok) return null;
      return (await res.json()) as ExecutiveHealth;
    } catch {
      return null;
    }
  },

  getPriorities: async (): Promise<StrategicPriority[]> => {
    try {
      const res = await fetch(`${API_BASE}/priorities`, { headers: getHeaders() });
      if (!res.ok) return [];
      return (await res.json()) as StrategicPriority[];
    } catch {
      return [];
    }
  },

  listDecisions: async (): Promise<StrategicDecision[]> => {
    try {
      const res = await fetch(`${API_BASE}/decisions`, { headers: getHeaders() });
      if (!res.ok) return [];
      return (await res.json()) as StrategicDecision[];
    } catch {
      return [];
    }
  },

  getDecision: async (id: string): Promise<StrategicDecision | null> => {
    try {
      const res = await fetch(`${API_BASE}/decisions/${id}`, { headers: getHeaders() });
      if (!res.ok) return null;
      return (await res.json()) as StrategicDecision;
    } catch {
      return null;
    }
  },

  getDecisionAlternatives: async (id: string): Promise<DecisionAlternative[]> => {
    try {
      const res = await fetch(`${API_BASE}/decisions/${id}/alternatives`, { headers: getHeaders() });
      if (!res.ok) return [];
      return (await res.json()) as DecisionAlternative[];
    } catch {
      return [];
    }
  },

  getDecisionExplanation: async (id: string): Promise<DecisionExplanation | null> => {
    try {
      const res = await fetch(`${API_BASE}/decisions/${id}/explanation`, { headers: getHeaders() });
      if (!res.ok) return null;
      return (await res.json()) as DecisionExplanation;
    } catch {
      return null;
    }
  },

  getMultiAgentConsensus: async (id: string): Promise<MultiAgentConsensus | null> => {
    try {
      const res = await fetch(`${API_BASE}/decisions/${id}/consensus`, { headers: getHeaders() });
      if (!res.ok) return null;
      return (await res.json()) as MultiAgentConsensus;
    } catch {
      return null;
    }
  }
};
