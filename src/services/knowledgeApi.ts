const API_BASE = '/api/v1/knowledge';

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

export type NodeTypeEnum =
  | 'CLIENT'
  | 'INDUSTRY'
  | 'EVIDENCE'
  | 'MEMORY'
  | 'AGENT'
  | 'DECISION'
  | 'PREDICTION'
  | 'ACTION'
  | 'POLICY'
  | 'POLICY_VERSION'
  | 'OUTCOME'
  | 'METRIC'
  | 'LESSON'
  | 'APPROVAL'
  | 'WORKFLOW'
  | 'SWARM_SESSION';

export type RelationTypeEnum =
  | 'SUPPORTS'
  | 'CONTRADICTS'
  | 'INFLUENCED'
  | 'CAUSED'
  | 'CONTRIBUTED_TO'
  | 'LED_TO'
  | 'PRODUCED'
  | 'VALIDATES'
  | 'INVALIDATES'
  | 'IMPROVED'
  | 'REGRESSED'
  | 'GOVERNED'
  | 'APPROVED_BY'
  | 'REJECTED_BY'
  | 'LEARNED_FROM'
  | 'INFLUENCES';

export type CausalStatusEnum =
  | 'OBSERVED'
  | 'HYPOTHESIS'
  | 'SUPPORTED'
  | 'VALIDATED'
  | 'CONTRADICTED'
  | 'INSUFFICIENT_DATA';

export interface KnowledgeNodeRecord {
  id: string;
  organization_id: string;
  node_type: NodeTypeEnum;
  entity_id: string;
  label: string;
  confidence: number;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeRelationRecord {
  id: string;
  organization_id: string;
  source_node_id: string;
  target_node_id: string;
  relation_type: RelationTypeEnum;
  causal_status: CausalStatusEnum;
  confidence: number;
  weight: number;
  evidence_summary?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface DecisionChainRecord {
  decision_id: string;
  label: string;
  evidence_used: Array<Record<string, any>>;
  agents_involved: Array<Record<string, any>>;
  memories_used: Array<Record<string, any>>;
  prediction?: Record<string, any>;
  policy_version?: Record<string, any>;
  approval?: Record<string, any>;
  action?: Record<string, any>;
  outcome?: Record<string, any>;
  lessons: Array<Record<string, any>>;
  causal_relationships: KnowledgeRelationRecord[];
  confidence: number;
}

export interface RootCauseContributorRecord {
  contributor_name: string;
  contributor_type: string;
  contribution_score: number;
  rank: number;
  explanation: string;
}

export interface OutcomeRootCauseRecord {
  outcome_id: string;
  status: string;
  primary_root_cause: string;
  contributors: RootCauseContributorRecord[];
  supporting_observations: string[];
  contradicting_observations: string[];
  confidence: number;
}

export interface AgentInfluenceRecord {
  agent_name: string;
  total_contributions: number;
  decision_influence_score: number;
  outcome_correlation: number;
  evidence_contribution_score: number;
  historical_reliability: number;
  causal_lessons_count: number;
}

export interface KnowledgeOverviewRecord {
  total_nodes: number;
  total_relations: number;
  validated_causal_links: number;
  causal_hypotheses: number;
  contradictions_count: number;
  average_causal_confidence: number;
  nodes: KnowledgeNodeRecord[];
  relations: KnowledgeRelationRecord[];
}

export const knowledgeApi = {
  async getOverview(): Promise<KnowledgeOverviewRecord> {
    const res = await fetch(`${API_BASE}/overview`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch knowledge graph overview');
    return res.json();
  },

  async listNodes(): Promise<KnowledgeNodeRecord[]> {
    const res = await fetch(`${API_BASE}/nodes`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch knowledge nodes');
    return res.json();
  },

  async getNode(id: string): Promise<KnowledgeNodeRecord> {
    const res = await fetch(`${API_BASE}/nodes/${id}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch knowledge node');
    return res.json();
  },

  async getDecisionChain(id: string): Promise<DecisionChainRecord> {
    const res = await fetch(`${API_BASE}/decisions/${id}/chain`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch decision explanation chain');
    return res.json();
  },

  async getOutcomeRootCause(id: string): Promise<OutcomeRootCauseRecord> {
    const res = await fetch(`${API_BASE}/outcomes/${id}/root-cause`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch outcome root-cause analysis');
    return res.json();
  },

  async getAgentInfluence(agentName: string): Promise<AgentInfluenceRecord> {
    const res = await fetch(`${API_BASE}/agents/${encodeURIComponent(agentName)}/influence`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to fetch agent influence');
    return res.json();
  },

  async rebuildGraph(): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE}/rebuild`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Failed to rebuild knowledge graph');
    return res.json();
  },
};
