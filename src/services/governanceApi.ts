const API_BASE = '/api/v1/governance/approvals';

export interface ApprovalRequest {
  id: string;
  organization_id: string;
  workflow_id?: string;
  client_id?: string;
  report_id?: string;
  requested_by: string;
  reviewed_by?: string;
  title: string;
  description?: string;
  decision_type: 'WORKFLOW_EXECUTION' | 'CAMPAIGN_LAUNCH' | 'BUDGET_CHANGE' | 'STRATEGY_CHANGE' | 'REPORT_PUBLICATION' | 'OTHER';
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_score: number;
  status: 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'CHANGES_REQUESTED' | 'CANCELLED' | 'EXPIRED';
  requested_action?: string;
  ai_recommendation?: string;
  ai_confidence_score: number;
  evidence_count: number;
  provider?: string;
  model?: string;
  requested_at: string;
  reviewed_at?: string;
  reviewer_comment?: string;
  rejection_reason?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface ApprovalListResponse {
  approvals: ApprovalRequest[];
  total: number;
  page: number;
  page_size: number;
}

const getToken = () => localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');

export const governanceApi = {
  async getApprovals(params?: { status?: string; risk_level?: string; search?: string; page?: number }): Promise<ApprovalListResponse> {
    const token = getToken();
    const query = new URLSearchParams();
    if (params?.status) query.append('status', params.status);
    if (params?.risk_level) query.append('risk_level', params.risk_level);
    if (params?.search) query.append('search', params.search);
    if (params?.page) query.append('page', params.page.toString());

    const resp = await fetch(`${API_BASE}?${query.toString()}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) return { approvals: [], total: 0, page: 1, page_size: 20 };
    return resp.json();
  },

  async getApproval(id: string): Promise<ApprovalRequest | null> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!resp.ok) return null;
    return resp.json();
  },

  async approve(id: string, comment?: string): Promise<ApprovalRequest | null> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/${id}/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ comment })
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Failed to approve' }));
      throw new Error(err.detail || 'Approval failed');
    }
    return resp.json();
  },

  async reject(id: string, rejection_reason?: string): Promise<ApprovalRequest | null> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/${id}/reject`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ rejection_reason })
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Failed to reject' }));
      throw new Error(err.detail || 'Rejection failed');
    }
    return resp.json();
  },

  async requestChanges(id: string, comment?: string): Promise<ApprovalRequest | null> {
    const token = getToken();
    const resp = await fetch(`${API_BASE}/${id}/request-changes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ comment })
    });
    if (!resp.ok) return null;
    return resp.json();
  }
};
