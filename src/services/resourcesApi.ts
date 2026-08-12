const API_BASE = '/api/v1/resources';

const getHeaders = () => {
  const token =
    localStorage.getItem('strtos_auth_token') ||
    sessionStorage.getItem('strtos_auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

// ─── Type Definitions ─────────────────────────────────────────────────────────

export type ResourceType =
  | 'HUMAN'
  | 'AI_AGENT'
  | 'BUDGET'
  | 'TIME'
  | 'COMPUTE'
  | 'TOOL'
  | 'EXECUTION_CAPACITY'
  | 'MARKETING_CAPACITY'
  | 'OPERATIONAL_CAPACITY';

export type ResourceStatus =
  | 'AVAILABLE'
  | 'LIMITED'
  | 'EXHAUSTED'
  | 'BLOCKED'
  | 'DEGRADED'
  | 'UNKNOWN';

export type AllocationPlanStatus =
  | 'DRAFT'
  | 'SIMULATED'
  | 'PENDING_GOVERNANCE'
  | 'APPROVED'
  | 'ACTIVE'
  | 'COMPLETED'
  | 'REJECTED'
  | 'ROLLED_BACK'
  | 'DEGRADED';

export type BottleneckSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type ConflictSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface Resource {
  id: string;
  organization_id: string;
  client_id?: string;
  name: string;
  resource_type: ResourceType;
  description?: string;
  total_capacity?: number;
  available_capacity?: number;
  allocated_capacity: number;
  utilization_percentage: number;
  unit: string;
  cost_per_unit?: number;
  status: ResourceStatus;
  is_shared: boolean;
  created_at: string;
  updated_at: string;
}

export interface CapacityInfo {
  resource_id: string;
  resource_name: string;
  resource_type: ResourceType;
  total_capacity?: number;
  available_capacity?: number;
  allocated_capacity: number;
  remaining_capacity: number;
  utilization_percentage: number;
  status: ResourceStatus;
  is_measured: boolean;
  shortage_detected: boolean;
  shortage_amount: number;
}

export interface UtilizationOverview {
  organization_id: string;
  total_resources: number;
  available_count: number;
  limited_count: number;
  exhausted_count: number;
  unknown_count: number;
  blocked_count: number;
  degraded_count: number;
  overall_utilization_pct: number;
  highest_utilization_resource?: string;
  highest_utilization_pct: number;
}

export interface BottleneckResult {
  resource_id: string;
  resource_name: string;
  resource_type: ResourceType;
  current_capacity?: number;
  required_capacity: number;
  shortage: number;
  shortage_pct: number;
  affected_mission_ids: string[];
  severity: BottleneckSeverity;
  recommended_action: string;
}

export interface BottleneckResponse {
  organization_id: string;
  bottlenecks: BottleneckResult[];
  critical_count: number;
  high_count: number;
  total_count: number;
  summary: string;
}

export interface ConflictResult {
  conflict_id: string;
  resource_id: string;
  resource_name: string;
  resource_type: ResourceType;
  mission_ids: string[];
  required_capacity: number;
  available_capacity: number;
  shortage: number;
  severity: ConflictSeverity;
  resolution_options: string[];
}

export interface ConflictResponse {
  organization_id: string;
  conflicts: ConflictResult[];
  critical_count: number;
  total_count: number;
  summary: string;
}

export interface SimulationScenarioResult {
  scenario_type: string;
  feasible_mission_ids: string[];
  blocked_mission_ids: string[];
  bottleneck_count: number;
  budget_utilization_pct: number;
  capacity_utilization_pct: number;
  expected_value: number;
  opportunity_cost_score: number;
  strategic_impact_summary: string;
}

export interface SimulationResponse {
  portfolio_id?: string;
  organization_id: string;
  scenario: SimulationScenarioResult;
  recommendation: string;
  is_side_effect_free: boolean;
}

export interface AllocationPlanVersion {
  id: string;
  version: string;
  parent_version?: string;
  change_reason?: string;
  risk_change: number;
  value_change: number;
  created_at: string;
}

export interface AllocationPlan {
  id: string;
  organization_id: string;
  portfolio_id?: string;
  version: string;
  status: AllocationPlanStatus;
  title: string;
  summary?: string;
  resource_allocations_json?: Record<string, unknown>;
  bottlenecks_json?: Record<string, unknown>;
  conflicts_json?: Record<string, unknown>;
  expected_value: number;
  risk_score: number;
  confidence_score: number;
  explanation?: string;
  governance_approval_id?: string;
  approved_by?: string;
  created_at: string;
  updated_at: string;
}

export interface ResourceOverview {
  organization_id: string;
  total_resources: number;
  resources_available: number;
  resources_limited: number;
  resources_exhausted: number;
  resources_unknown: number;
  active_allocation_plans: number;
  open_bottlenecks: number;
  open_conflicts: number;
  overall_capacity_health: string;
  top_bottleneck_type?: string;
  governance_pending_count: number;
}

// ─── API Client ───────────────────────────────────────────────────────────────

export const resourcesApi = {
  // Overview
  getOverview: (): Promise<ResourceOverview> =>
    fetch(`${API_BASE}/overview`, { headers: getHeaders() }).then(r => r.json()),

  // Resources
  listResources: (type?: ResourceType): Promise<Resource[]> => {
    const url = type ? `${API_BASE}/resources?resource_type=${type}` : `${API_BASE}/resources`;
    return fetch(url, { headers: getHeaders() }).then(r => r.json());
  },

  createResource: (data: {
    name: string;
    resource_type: ResourceType;
    total_capacity?: number;
    available_capacity?: number;
    unit?: string;
    cost_per_unit?: number;
    description?: string;
  }): Promise<Resource> =>
    fetch(`${API_BASE}/resources`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    }).then(r => r.json()),

  getResource: (id: string): Promise<Resource> =>
    fetch(`${API_BASE}/resources/${id}`, { headers: getHeaders() }).then(r => r.json()),

  // Capacity & Utilization
  getCapacity: (): Promise<CapacityInfo[]> =>
    fetch(`${API_BASE}/capacity`, { headers: getHeaders() }).then(r => r.json()),

  getUtilization: (): Promise<UtilizationOverview> =>
    fetch(`${API_BASE}/utilization`, { headers: getHeaders() }).then(r => r.json()),

  // Bottlenecks & Conflicts
  getBottlenecks: (): Promise<BottleneckResponse> =>
    fetch(`${API_BASE}/bottlenecks`, { headers: getHeaders() }).then(r => r.json()),

  getConflicts: (): Promise<ConflictResponse> =>
    fetch(`${API_BASE}/conflicts`, { headers: getHeaders() }).then(r => r.json()),

  // Allocation Plans
  listAllocationPlans: (): Promise<AllocationPlan[]> =>
    fetch(`${API_BASE}/allocations`, { headers: getHeaders() }).then(r => r.json()),

  simulateAllocation: (
    scenario_type: string,
    capacity_delta_pct = 0,
    budget_delta_pct = 0
  ): Promise<SimulationResponse> =>
    fetch(`${API_BASE}/allocations/simulate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ scenario_type, capacity_delta_pct, budget_delta_pct }),
    }).then(r => r.json()),

  recommendAllocation: (
    missions: unknown[] = [],
    requirements: unknown[] = []
  ): Promise<unknown> =>
    fetch(`${API_BASE}/allocations/recommend`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ missions, requirements }),
    }).then(r => r.json()),

  createAllocationPlan: (data: {
    title: string;
    portfolio_id?: string;
  }): Promise<AllocationPlan> =>
    fetch(`${API_BASE}/allocations/plan`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ payload: data, missions: [], requirements: [] }),
    }).then(r => r.json()),

  getAllocationPlan: (id: string): Promise<AllocationPlan> =>
    fetch(`${API_BASE}/allocations/${id}`, { headers: getHeaders() }).then(r => r.json()),

  getPlanExplanation: (id: string): Promise<unknown> =>
    fetch(`${API_BASE}/allocations/${id}/explanation`, { headers: getHeaders() }).then(r => r.json()),

  submitGovernance: (id: string): Promise<unknown> =>
    fetch(`${API_BASE}/allocations/${id}/submit-governance`, {
      method: 'POST',
      headers: getHeaders(),
    }).then(r => r.json()),

  approvePlan: (id: string): Promise<unknown> =>
    fetch(`${API_BASE}/allocations/${id}/approve`, {
      method: 'POST',
      headers: getHeaders(),
    }).then(r => r.json()),

  activatePlan: (id: string): Promise<unknown> =>
    fetch(`${API_BASE}/allocations/${id}/activate`, {
      method: 'POST',
      headers: getHeaders(),
    }).then(r => r.json()),

  getMissionResources: (mission_id: string): Promise<unknown> =>
    fetch(`${API_BASE}/missions/${mission_id}/resources`, { headers: getHeaders() }).then(r => r.json()),
};
