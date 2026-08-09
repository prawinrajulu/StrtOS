import React, { useEffect, useState } from 'react';
import {
  Users, Plus, Search, DollarSign, Building2, ChevronRight, X
} from 'lucide-react';
import { clientsApi } from '../services/clientsApi';
import type { Client, ClientCreatePayload } from '../services/clientsApi';

interface ClientsPageProps {
  onSelectClient?: (client: Client) => void;
}

export const ClientsPage: React.FC<ClientsPageProps> = ({ onSelectClient }) => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState<ClientCreatePayload>({
    name: '',
    industry: 'FinTech',
    website_url: '',
    business_goal: '',
    description: '',
    monthly_budget: 15000,
    currency: 'USD',
    contact_name: '',
    contact_email: '',
    contact_phone: ''
  });

  const loadClients = async () => {
    setLoading(true);
    const data = await clientsApi.listClients({
      search: search || undefined,
      industry: selectedIndustry || undefined,
      status_filter: selectedStatus || undefined
    });
    setClients(data);
    setLoading(false);
  };

  useEffect(() => {
    loadClients();
  }, [search, selectedIndustry, selectedStatus]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const created = await clientsApi.createClient(formData);
    setSaving(false);
    if (created) {
      setShowModal(false);
      setFormData({
        name: '',
        industry: 'FinTech',
        website_url: '',
        business_goal: '',
        description: '',
        monthly_budget: 15000,
        currency: 'USD',
        contact_name: '',
        contact_email: '',
        contact_phone: ''
      });
      loadClients();
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#f9fafb', margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Users style={{ color: '#8b5cf6' }} size={28} />
            Client Portfolio
          </h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', marginTop: '4px', margin: 0 }}>
            Enterprise multi-tenant business contexts feeding the CEO Agent Orchestrator.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 18px',
            background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontWeight: '600',
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)',
            transition: 'all 0.2s'
          }}
        >
          <Plus size={18} />
          Create Client
        </button>
      </div>

      {/* Search & Filters */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '260px', position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
          <input
            type="text"
            placeholder="Search clients by name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 12px 10px 40px',
              backgroundColor: '#111827',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#f9fafb',
              fontSize: '14px',
              outline: 'none'
            }}
          />
        </div>

        <select
          value={selectedIndustry}
          onChange={(e) => setSelectedIndustry(e.target.value)}
          style={{
            padding: '10px 16px',
            backgroundColor: '#111827',
            border: '1px solid #374151',
            borderRadius: '8px',
            color: '#f9fafb',
            fontSize: '14px',
            outline: 'none'
          }}
        >
          <option value="">All Industries</option>
          <option value="FinTech">FinTech</option>
          <option value="HealthTech">HealthTech</option>
          <option value="Food & Beverage">Food & Beverage</option>
          <option value="E-Commerce">E-Commerce</option>
          <option value="SaaS & Cloud">SaaS & Cloud</option>
        </select>

        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          style={{
            padding: '10px 16px',
            backgroundColor: '#111827',
            border: '1px solid #374151',
            borderRadius: '8px',
            color: '#f9fafb',
            fontSize: '14px',
            outline: 'none'
          }}
        >
          <option value="">All Statuses</option>
          <option value="ACTIVE">ACTIVE</option>
          <option value="PAUSED">PAUSED</option>
          <option value="ARCHIVED">ARCHIVED</option>
        </select>
      </div>

      {/* Client Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#9ca3af' }}>
          Loading enterprise client portfolio...
        </div>
      ) : clients.length === 0 ? (
        <div
          style={{
            backgroundColor: '#111827',
            border: '1px dashed #374151',
            borderRadius: '12px',
            padding: '60px 20px',
            textAlign: 'center',
            color: '#9ca3af'
          }}
        >
          <Building2 size={48} style={{ color: '#4b5563', marginBottom: '16px' }} />
          <h3 style={{ color: '#f3f4f6', fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>No Clients Found</h3>
          <p style={{ fontSize: '14px', marginBottom: '20px' }}>Create your organization's first client profile to enable tenant-aware AI Agent execution.</p>
          <button
            onClick={() => setShowModal(true)}
            style={{
              padding: '10px 20px',
              backgroundColor: '#6366f1',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Create First Client
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
          {clients.map((client) => (
            <div
              key={client.id}
              onClick={() => onSelectClient && onSelectClient(client)}
              style={{
                backgroundColor: '#111827',
                border: '1px solid #1f2937',
                borderRadius: '12px',
                padding: '20px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                position: 'relative'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#6366f1';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#1f2937';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <div>
                    <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f9fafb', margin: 0 }}>{client.name}</h3>
                    <span style={{ fontSize: '12px', color: '#8b5cf6', fontWeight: '500' }}>{client.industry}</span>
                  </div>
                  <span
                    style={{
                      fontSize: '11px',
                      fontWeight: '700',
                      padding: '4px 8px',
                      borderRadius: '12px',
                      backgroundColor: client.status === 'ACTIVE' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                      color: client.status === 'ACTIVE' ? '#10b981' : '#ef4444'
                    }}
                  >
                    {client.status}
                  </span>
                </div>

                {client.business_goal && (
                  <p style={{ fontSize: '13px', color: '#9ca3af', marginBottom: '16px', lineHeight: '1.4' }}>
                    {client.business_goal.length > 90 ? client.business_goal.substring(0, 90) + '...' : client.business_goal}
                  </p>
                )}
              </div>

              <div style={{ paddingTop: '12px', borderTop: '1px solid #1f2937', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#10b981', fontSize: '14px', fontWeight: '600' }}>
                  <DollarSign size={16} />
                  {client.monthly_budget ? client.monthly_budget.toLocaleString() : '0'} /mo
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#6366f1', fontSize: '13px', fontWeight: '600' }}>
                  View Brief <ChevronRight size={16} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '16px', width: '100%', maxWidth: '600px', padding: '24px', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.5)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#f9fafb', margin: 0 }}>Add New Enterprise Client</h2>
              <X size={20} style={{ color: '#9ca3af', cursor: 'pointer' }} onClick={() => setShowModal(false)} />
            </div>

            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '13px', color: '#d1d5db', fontWeight: '500', marginBottom: '4px', display: 'block' }}>Client Name *</label>
                <input
                  required
                  type="text"
                  placeholder="e.g. Acme Health Corp"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  style={{ width: '100%', padding: '10px', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ fontSize: '13px', color: '#d1d5db', fontWeight: '500', marginBottom: '4px', display: 'block' }}>Industry *</label>
                  <input
                    required
                    type="text"
                    placeholder="e.g. FinTech"
                    value={formData.industry}
                    onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                    style={{ width: '100%', padding: '10px', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff' }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '13px', color: '#d1d5db', fontWeight: '500', marginBottom: '4px', display: 'block' }}>Monthly Budget (USD)</label>
                  <input
                    type="number"
                    value={formData.monthly_budget}
                    onChange={(e) => setFormData({ ...formData, monthly_budget: parseFloat(e.target.value) || 0 })}
                    style={{ width: '100%', padding: '10px', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff' }}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '13px', color: '#d1d5db', fontWeight: '500', marginBottom: '4px', display: 'block' }}>Website URL</label>
                <input
                  type="url"
                  placeholder="https://example.com"
                  value={formData.website_url}
                  onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
                  style={{ width: '100%', padding: '10px', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '13px', color: '#d1d5db', fontWeight: '500', marginBottom: '4px', display: 'block' }}>Business Objective / Directive Goal</label>
                <textarea
                  rows={3}
                  placeholder="Describe primary growth objective feeding CEO Agent Orchestrator..."
                  value={formData.business_goal}
                  onChange={(e) => setFormData({ ...formData, business_goal: e.target.value })}
                  style={{ width: '100%', padding: '10px', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff', resize: 'vertical' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '10px' }}>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  style={{ padding: '10px 18px', backgroundColor: 'transparent', color: '#9ca3af', border: '1px solid #374151', borderRadius: '8px', cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  style={{ padding: '10px 20px', backgroundColor: '#6366f1', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '600', cursor: 'pointer' }}
                >
                  {saving ? 'Saving...' : 'Create Client Profile'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
