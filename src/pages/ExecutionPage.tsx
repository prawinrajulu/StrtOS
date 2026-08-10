import React, { useEffect, useState } from 'react';
import { Play, Search, ShieldCheck, CheckCircle2, XCircle, RefreshCw, ChevronRight, Zap } from 'lucide-react';
import { executionApi } from '../services/executionApi';
import type { ActionRecord } from '../services/executionApi';
import { globalEventStream } from '../services/eventStream';

interface ExecutionPageProps {
  onSelectAction: (action: ActionRecord) => void;
}

export const ExecutionPage: React.FC<ExecutionPageProps> = ({ onSelectAction }) => {
  const [actions, setActions] = useState<ActionRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  const fetchActions = async () => {
    setLoading(true);
    const data = await executionApi.getActions({
      status: statusFilter,
      search: search
    });
    setActions(data.actions);
    setTotal(data.total);
    setLoading(false);
  };

  useEffect(() => {
    fetchActions();

    const unsubscribe = globalEventStream.subscribe((event) => {
      if (['action.created', 'action.started', 'action.completed', 'action.failed', 'action.approved'].includes(event.event_type)) {
        fetchActions();
      }
    });
    return () => unsubscribe();
  }, [statusFilter, search]);

  const handleExecuteNow = async (e: React.MouseEvent, actionId: string) => {
    e.stopPropagation();
    try {
      await executionApi.executeAction(actionId);
      fetchActions();
    } catch (err: any) {
      alert(err.message || 'Execution failed.');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <span style={{ color: '#10b981', fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}><CheckCircle2 size={13} /> COMPLETED</span>;
      case 'RUNNING':
        return <span style={{ color: '#60a5fa', fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}><RefreshCw className="animate-spin" size={13} /> RUNNING</span>;
      case 'PENDING_APPROVAL':
        return <span style={{ color: '#f59e0b', fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}><ShieldCheck size={13} /> PENDING APPROVAL</span>;
      case 'FAILED':
        return <span style={{ color: '#ef4444', fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}><XCircle size={13} /> FAILED</span>;
      default:
        return <span style={{ color: '#9ca3af', fontWeight: '600', fontSize: '11px' }}>{status}</span>;
    }
  };

  return (
    <div style={{ padding: '28px', maxWidth: '1300px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Zap style={{ color: '#10b981' }} size={28} /> Autonomous Execution Control Center
          </h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>
            Policy-enforced tool execution, governance approval loops, and closed-loop optimization ({total} Actions)
          </p>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '1px solid #1f2937', paddingBottom: '12px' }}>
        {[
          { label: 'All Actions', value: '' },
          { label: 'Pending Approval', value: 'PENDING_APPROVAL' },
          { label: 'Running', value: 'RUNNING' },
          { label: 'Completed', value: 'COMPLETED' },
          { label: 'Failed', value: 'FAILED' }
        ].map((tab) => (
          <button
            key={tab.value}
            onClick={() => setStatusFilter(tab.value)}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: statusFilter === tab.value ? '#6366f1' : '#111827',
              color: statusFilter === tab.value ? '#ffffff' : '#9ca3af',
              fontSize: '13px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Search Bar */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '16px', marginBottom: '24px', display: 'flex', gap: '14px', alignItems: 'center' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
          <input
            type="text"
            placeholder="Search execution actions, tools, or status..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px 12px 10px 38px', color: '#f9fafb', fontSize: '14px' }}
          />
        </div>
      </div>

      {/* Action Cards */}
      {loading ? (
        <div style={{ color: '#9ca3af', textAlign: 'center', padding: '40px' }}>Loading execution actions...</div>
      ) : actions.length === 0 ? (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '40px', textAlign: 'center', color: '#9ca3af' }}>
          No execution actions found matching filter criteria.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {actions.map((act) => (
            <div
              key={act.id}
              onClick={() => onSelectAction(act)}
              style={{
                backgroundColor: '#111827',
                border: '1px solid #1f2937',
                borderRadius: '14px',
                padding: '20px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '16px'
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#6366f1')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#1f2937')}
            >
              <div style={{ flex: 1, minWidth: '280px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  {getStatusBadge(act.status)}
                  <span style={{ padding: '3px 8px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#8b5cf6', borderRadius: '6px', fontSize: '11px', fontWeight: '700' }}>
                    {act.action_type}
                  </span>
                  <span style={{ fontSize: '11px', color: '#6b7280' }}>
                    {new Date(act.created_at).toLocaleDateString()}
                  </span>
                </div>
                <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0' }}>{act.name}</h3>
                <p style={{ color: '#9ca3af', fontSize: '13px', margin: 0 }}>{act.description || 'Policy-managed tool execution action'}</p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '11px', color: '#6b7280', fontWeight: '600' }}>POLICY DECISION</div>
                  <div style={{ fontSize: '14px', fontWeight: '700', color: act.policy_decision === 'ALLOW' ? '#10b981' : '#f59e0b' }}>
                    {act.policy_decision}
                  </div>
                </div>

                {['APPROVED', 'DRAFT', 'QUEUED'].includes(act.status) && (
                  <button
                    onClick={(e) => handleExecuteNow(e, act.id)}
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', backgroundColor: '#10b981', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '700', fontSize: '13px', cursor: 'pointer' }}
                  >
                    <Play size={14} /> Execute
                  </button>
                )}

                <ChevronRight size={20} style={{ color: '#6b7280' }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
