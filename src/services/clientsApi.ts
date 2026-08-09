export interface Client {
  id: string;
  organization_id: string;
  name: string;
  industry: string;
  website_url?: string;
  description?: string;
  business_goal?: string;
  monthly_budget?: number;
  currency: string;
  status: 'ACTIVE' | 'PAUSED' | 'ARCHIVED';
  contact_name?: string;
  contact_email?: string;
  contact_phone?: string;
  created_by?: string;
  health_score: number;
  created_at: string;
  updated_at: string;
}

export interface ClientCreatePayload {
  name: string;
  industry: string;
  website_url?: string;
  description?: string;
  business_goal?: string;
  monthly_budget?: number;
  currency?: string;
  status?: 'ACTIVE' | 'PAUSED' | 'ARCHIVED';
  contact_name?: string;
  contact_email?: string;
  contact_phone?: string;
}

const getHeaders = () => {
  const token = localStorage.getItem('strtos_auth_token') || sessionStorage.getItem('strtos_auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
};

export const clientsApi = {
  async listClients(params?: { search?: string; industry?: string; status_filter?: string }): Promise<Client[]> {
    try {
      const searchParams = new URLSearchParams();
      if (params?.search) searchParams.append('search', params.search);
      if (params?.industry) searchParams.append('industry', params.industry);
      if (params?.status_filter) searchParams.append('status_filter', params.status_filter);

      const res = await fetch(`/api/v1/clients?${searchParams.toString()}`, {
        headers: getHeaders()
      });
      if (res.ok) {
        const json = await res.json();
        return json.data.clients || [];
      }
    } catch (e) {
      console.warn('Failed listing clients', e);
    }
    return [];
  },

  async getClient(clientId: string): Promise<Client | null> {
    try {
      const res = await fetch(`/api/v1/clients/${clientId}`, {
        headers: getHeaders()
      });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed getting client details', e);
    }
    return null;
  },

  async createClient(payload: ClientCreatePayload): Promise<Client | null> {
    try {
      const res = await fetch('/api/v1/clients', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed creating client', e);
    }
    return null;
  },

  async updateClient(clientId: string, payload: Partial<ClientCreatePayload>): Promise<Client | null> {
    try {
      const res = await fetch(`/api/v1/clients/${clientId}`, {
        method: 'PATCH',
        headers: getHeaders(),
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed updating client', e);
    }
    return null;
  },

  async archiveClient(clientId: string): Promise<Client | null> {
    try {
      const res = await fetch(`/api/v1/clients/${clientId}`, {
        method: 'DELETE',
        headers: getHeaders()
      });
      if (res.ok) {
        const json = await res.json();
        return json.data;
      }
    } catch (e) {
      console.warn('Failed archiving client', e);
    }
    return null;
  }
};
