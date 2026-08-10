import React, { useEffect, useState } from 'react';
import {
  ShieldAlert, CheckCircle2, XCircle, Clock, Search,
  ShieldCheck, AlertTriangle, AlertOctagon, Activity, ChevronRight
} from 'lucide-react';
import { governanceApi } from '../services/governanceApi';
import type { ApprovalRequest } from '../services/governanceApi';
import { globalEventStream } from '../services/eventStream';

interface ApprovalsPageProps {
  onSelectApproval: (approval: ApprovalRequest) => void;
}

export const ApprovalsPage: React.FC<ApprovalsPageProps> = ({ onSelectApproval }) => {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('PENDING_APPROVAL');
  const [riskFilter, setRiskFilter] = useState<string>('');

  const fetchApprovals = async () => {
    setLoading(true);
    const data = await governanceApi.getApprovals({
      status: statusFilter,
      risk_level: riskFilter,
      search: search
    });
    setApprovals(data.approvals);
    setTotal(data.total);
    setLoading(false);
  };

  useEffect(() => {
    fetchApprovals();

    // Subscribe to SSE real-time event stream for auto-refresh
    const unsubscribe = globalEventStream.subscribe((event) => {
      if (['approval.created', 'approval.pending', 'approval.approved', 'approval.rejected', 'approval.changes_requested', 'approval.cancelled'].includes(event.event_type)) {
        fetchApprovals();
      }
    });
    return () => unsubscribe();
  }, [statusFilter, riskFilter, search]);

  const getRiskBadge = (level: string, score: number) => {
    switch (level) {
      case 'CRITICAL':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 10px', backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', border: '1px solid #ef4444', borderRadius: '8px', fontSize: '11px', fontWeight: '700' }}>
            <AlertOctagon size={14} /> CRITICAL ({score}/100)
          </span>
        );
      case 'HIGH':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 10px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b', border: '1px solid #f59e0b', borderRadius: '8px', fontSize: '11px', fontWeight: '700' }}>
            <AlertTriangle size={14} /> HIGH RISK ({score}/100)
          </span>
        );
      case 'MEDIUM':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 10px', backgroundColor: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', border: '1px solid #3b82f6', borderRadius: '8px', fontSize: '11px', fontWeight: '600' }}>
            <ShieldAlert size={14} /> MEDIUM RISK ({score}/100)
          </span>
        );
      default:
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '4px 10px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981', border: '1px solid #10b981', borderRadius: '8px', fontSize: '11px', fontWeight: '600' }}>
            <ShieldCheck size={14} /> LOW RISK ({score}/100)
          </span>
        );
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return <span style={{ color: '#10b981', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px' }}><CheckCircle2 size={14} /> APPROVED</span>;
      case 'REJECTED':
        return <span style={{ color: '#ef4444', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px' }}><XCircle size={14} /> REJECTED</span>;
      case 'CHANGES_REQUESTED':
        return <span style={{ color: '#f59e0b', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px' }}><Clock size={14} /> CHANGES REQUESTED</span>;
      default:
        return <span style={{ color: '#8b5cf6', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px' }}><Activity size={14} /> PENDING REVIEW</span>;
    }
  };

  return (
    <div style={{ padding: '28px', maxWidth: '1300px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShieldCheck style={{ color: '#8b5cf6' }} size={28} /> Decision Governance & Human Approvals
          </h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>
            Enterprise AI Decision Control Layer & Deterministic Risk Governance ({total} Total Requests)
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '16px', marginBottom: '24px', display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'center' }}>
        {/* Search */}
        <div style={{ flex: 1, minWidth: '240px', position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
          <input
            type="text"
            placeholder="Search approval title or directive..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px 12px 10px 38px', color: '#f9fafb', fontSize: '14px' }}
          />
        </div>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px 14px', color: '#f9fafb', fontSize: '14px' }}
        >
          <option value="">All Statuses</option>
          <option value="PENDING_APPROVAL">Pending Review</option>
          <option value="APPROVED">Approved</option>
          <option value="REJECTED">Rejected</option>
          <option value="CHANGES_REQUESTED">Changes Requested</option>
        </select>

        {/* Risk Filter */}
        <select
          value={riskFilter}
          onChange={(e) => setRiskFilter(e.target.value)}
          style={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px 14px', color: '#f9fafb', fontSize: '14px' }}
        >
          <option value="">All Risk Levels</option>
          <option value="CRITICAL">Critical Risk</option>
          <option value="HIGH">High Risk</option>
          <option value="MEDIUM">Medium Risk</option>
          <option value="LOW">Low Risk</option>
        </select>
      </div>

      {/* Approvals List */}
      {loading ? (
        <div style={{ color: '#9ca3af', textAlign: 'center', padding: '40px' }}>Loading governance requests...</div>
      ) : approvals.length === 0 ? (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '40px', textAlign: 'center', color: '#9ca3af' }}>
          No governance approval requests matching filter criteria.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {approvals.map((req) => (
            <div
              key={req.id}
              onClick={() => onSelectApproval(req)}
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
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                  {getRiskBadge(req.risk_level, req.risk_score)}
                  <span style={{ fontSize: '12px', color: '#9ca3af', fontWeight: '600' }}>{req.decision_type}</span>
                </div>
                <h3 style={{ fontSize: '17px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0' }}>{req.title}</h3>
                {req.requested_action && (
                  <p style={{ color: '#9ca3af', fontSize: '13px', margin: 0, lineHeight: '1.4' }}>{req.requested_action}</p>
                )}
              </div>

              {/* AI Metrics & Telemetry */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '11px', color: '#9ca3af', fontWeight: '600' }}>AI CONFIDENCE</div>
                  <div style={{ fontSize: '16px', fontWeight: '700', color: '#8b5cf6' }}>{req.ai_confidence_score}%</div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '11px', color: '#9ca3af', fontWeight: '600' }}>EVIDENCE</div>
                  <div style={{ fontSize: '16px', fontWeight: '700', color: '#60a5fa' }}>{req.evidence_count} Items</div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '11px', color: '#9ca3af', fontWeight: '600' }}>STATUS</div>
                  <div>{getStatusBadge(req.status)}</div>
                </div>

                <ChevronRight size={20} style={{ color: '#6b7280' }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
