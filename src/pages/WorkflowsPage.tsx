import React, { useEffect, useState } from 'react';
import {
  BrainCircuit, Plus, Search, ChevronRight, X, Activity
} from 'lucide-react';
import { workflowsApi } from '../services/workflowsApi';
import type { Workflow } from '../services/workflowsApi';
import { clientsApi } from '../services/clientsApi';
import type { Client } from '../services/clientsApi';

interface WorkflowsPageProps {
  onSelectWorkflow?: (workflow: Workflow) => void;
}

export const WorkflowsPage: React.FC<WorkflowsPageProps> = ({ onSelectWorkflow }) => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [selectedClientFilter, setSelectedClientFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    client_id: '',
    title: '',
    directive: ''
  });

  const loadData = async () => {
    setLoading(true);
    const [wfList, clientList] = await Promise.all([
      workflowsApi.listWorkflows({
        search: search || undefined,
        status_filter: selectedStatus || undefined,
        client_id: selectedClientFilter || undefined
      }),
      clientsApi.listClients()
    ]);
    setWorkflows(wfList);
    setClients(clientList);
    if (clientList.length > 0 && !formData.client_id) {
      setFormData(prev => ({ ...prev, client_id: clientList[0].id }));
    }
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [search, selectedStatus, selectedClientFilter]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.client_id) return;
    setSaving(true);
    const created = await workflowsApi.createWorkflow(formData);
    setSaving(false);
    if (created) {
      setShowModal(false);
      setFormData({ client_id: clients[0]?.id || '', title: '', directive: '' });
      loadData();
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <span style={{ padding: '4px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: '700', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>COMPLETED</span>;
      case 'RUNNING':
        return <span style={{ padding: '4px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: '700', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#8b5cf6' }}>RUNNING</span>;
      case 'PAUSED':
        return <span style={{ padding: '4px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: '700', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b' }}>PAUSED</span>;
      case 'CANCELLED':
      case 'FAILED':
        return <span style={{ padding: '4px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: '700', backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#ef4444' }}>{status}</span>;
      default:
        return <span style={{ padding: '4px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: '700', backgroundColor: 'rgba(107, 114, 128, 0.15)', color: '#9ca3af' }}>DRAFT</span>;
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#f9fafb', margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <BrainCircuit style={{ color: '#8b5cf6' }} size={28} />
            Executive Workflows
          </h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', marginTop: '4px', margin: 0 }}>
            Durable workflow lifecycle management feeding the CEO Agent Orchestrator.
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
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)'
          }}
        >
          <Plus size={18} />
          Create Workflow
        </button>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '260px', position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
          <input
            type="text"
            placeholder="Search workflows by title..."
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
          value={selectedClientFilter}
          onChange={(e) => setSelectedClientFilter(e.target.value)}
          style={{
            padding: '10px 16px',
            backgroundColor: '#111827',
            border: '1px solid #374151',
            borderRadius: '8px',
            color: '#f9fafb',
            fontSize: '14px'
          }}
        >
          <option value="">All Clients</option>
          {clients.map(c => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
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
            fontSize: '14px'
          }}
        >
          <option value="">All Statuses</option>
          <option value="DRAFT">DRAFT</option>
          <option value="RUNNING">RUNNING</option>
          <option value="PAUSED">PAUSED</option>
          <option value="COMPLETED">COMPLETED</option>
          <option value="CANCELLED">CANCELLED</option>
        </select>
      </div>

      {/* Workflows List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#9ca3af' }}>Loading executive workflows...</div>
      ) : workflows.length === 0 ? (
        <div style={{ backgroundColor: '#111827', border: '1px dashed #374151', borderRadius: '12px', padding: '60px 20px', textAlign: 'center', color: '#9ca3af' }}>
          <BrainCircuit size={48} style={{ color: '#4b5563', marginBottom: '16px' }} />
          <h3 style={{ color: '#f3f4f6', fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>No Workflows Found</h3>
          <p style={{ fontSize: '14px', marginBottom: '20px' }}>Create an executive workflow to trigger multi-specialist AI Agent orchestration.</p>
          <button
            onClick={() => setShowModal(true)}
            style={{ padding: '10px 20px', backgroundColor: '#6366f1', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '600', cursor: 'pointer' }}
          >
            Create First Workflow
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px' }}>
          {workflows.map((wf) => {
            const clientObj = clients.find(c => c.id === wf.client_id);
            return (
              <div
                key={wf.id}
                onClick={() => onSelectWorkflow && onSelectWorkflow(wf)}
                style={{
                  backgroundColor: '#111827',
                  border: '1px solid #1f2937',
                  borderRadius: '12px',
                  padding: '20px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between'
                }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#6366f1'; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#1f2937'; }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <div>
                      <h3 style={{ fontSize: '17px', fontWeight: '600', color: '#f9fafb', margin: 0 }}>{wf.title}</h3>
                      <span style={{ fontSize: '12px', color: '#8b5cf6', fontWeight: '500' }}>
                        Client: {clientObj ? clientObj.name : 'Enterprise Client'}
                      </span>
                    </div>
                    {getStatusBadge(wf.status)}
                  </div>

                  {wf.directive && (
                    <p style={{ fontSize: '13px', color: '#9ca3af', marginBottom: '16px', lineHeight: '1.4' }}>
                      {wf.directive.length > 90 ? wf.directive.substring(0, 90) + '...' : wf.directive}
                    </p>
                  )}

                  {/* Progress Bar */}
                  <div style={{ marginBottom: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#9ca3af', marginBottom: '4px' }}>
                      <span>Progress ({wf.completed_stages}/{wf.total_stages} Stages)</span>
                      <span style={{ fontWeight: '600', color: '#f3f4f6' }}>{wf.progress}%</span>
                    </div>
                    <div style={{ height: '6px', width: '100%', backgroundColor: '#1f2937', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${wf.progress}%`, backgroundColor: wf.status === 'COMPLETED' ? '#10b981' : '#6366f1', transition: 'width 0.3s' }} />
                    </div>
                  </div>
                </div>

                <div style={{ paddingTop: '12px', borderTop: '1px solid #1f2937', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#10b981', fontSize: '13px', fontWeight: '600' }}>
                    <Activity size={15} /> Confidence: {wf.confidence_score}%
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#6366f1', fontSize: '13px', fontWeight: '600' }}>
                    Inspect Graph <ChevronRight size={16} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '16px', width: '100%', maxWidth: '550px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#f9fafb', margin: 0 }}>Create Executive Workflow</h2>
              <X size={20} style={{ color: '#9ca3af', cursor: 'pointer' }} onClick={() => setShowModal(false)} />
            </div>

            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <label style={{ fontSize: '13px', color: '#d1d5db', fontWeight: '500', marginBottom: '4px', display: 'block' }}>Target Client *</label>
                <select
                  required
                  value={formData.client_id}
                  onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                  style={{ width: '100%', padding: '10px', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff' }}
                >
                  {clients.map(c => (
                    <option key={c.id} value={c.id}>{c.name} ({c.industry})</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '13px', color: '#d1d5db', fontWeight: '500', marginBottom: '4px', display: 'block' }}>Workflow Title *</label>
                <input
                  required
                  type="text"
                  placeholder="e.g. Q4 Customer Acquisition & SEO Campaign"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  style={{ width: '100%', padding: '10px', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '13px', color: '#d1d5db', fontWeight: '500', marginBottom: '4px', display: 'block' }}>Executive Directive</label>
                <textarea
                  rows={3}
                  placeholder="Specific goal for CEO Agent & Specialist Orchestration..."
                  value={formData.directive}
                  onChange={(e) => setFormData({ ...formData, directive: e.target.value })}
                  style={{ width: '100%', padding: '10px', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', color: '#fff' }}
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
                  {saving ? 'Creating...' : 'Initialize Workflow'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
