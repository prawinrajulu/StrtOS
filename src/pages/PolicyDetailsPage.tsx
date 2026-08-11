import React, { useEffect, useState } from 'react';
import { ArrowLeft, RotateCcw, CheckCircle2, AlertTriangle, Zap } from 'lucide-react';
import { policiesApi } from '../services/policiesApi';
import type { PolicyRecord, PolicyVersionRecord, PolicyEvaluationRecord } from '../services/policiesApi';

interface PolicyDetailsPageProps {
  policyId?: string;
  agentName?: string;
  onBack: () => void;
}

export const PolicyDetailsPage: React.FC<PolicyDetailsPageProps> = ({ policyId, agentName, onBack }) => {
  const [policy, setPolicy] = useState<PolicyRecord | null>(null);
  const [versions, setVersions] = useState<PolicyVersionRecord[]>([]);
  const [, setEvaluations] = useState<PolicyEvaluationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  useEffect(() => {
    loadPolicyDetails();
  }, [policyId, agentName]);

  const loadPolicyDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      let targetId = policyId;
      if (!targetId && agentName) {
        const allPolicies = await policiesApi.listPolicies();
        const found = allPolicies.find((p) => p.agent_name.toLowerCase() === agentName.toLowerCase());
        if (found) targetId = found.id;
      }

      if (targetId) {
        const [pData, vData, eData] = await Promise.all([
          policiesApi.getPolicy(targetId),
          policiesApi.listVersions(targetId),
          policiesApi.getPerformance(targetId),
        ]);
        setPolicy(pData);
        setVersions(vData);
        setEvaluations(eData);
      }
    } catch (err: any) {
      console.error('Error loading policy details:', err);
      setError(err.message || 'Failed to load policy details');
    } finally {
      setLoading(false);
    }
  };

  const handleOptimize = async () => {
    if (!policy) return;
    try {
      setLoading(true);
      setActionMsg(null);
      const res = await policiesApi.optimizePolicy(policy.id, {
        reason: 'Manual optimization request from Policy Details dashboard',
      });
      setActionMsg(`Optimization proposal submitted: ${res.status}. Governance ID: ${res.governance_approval_id || 'N/A'}`);
      await loadPolicyDetails();
    } catch (err: any) {
      setError(err.message || 'Optimization failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRollback = async () => {
    if (!policy) return;
    const reason = prompt('Enter mandatory reason for policy rollback:');
    if (!reason) return;

    try {
      setLoading(true);
      setActionMsg(null);
      const res = await policiesApi.rollbackPolicy(policy.id, { reason });
      setActionMsg(`Rollback successful! Active version reverted from ${res.previous_version} to ${res.active_version}.`);
      await loadPolicyDetails();
    } catch (err: any) {
      setError(err.message || 'Rollback failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', color: '#fff', backgroundColor: '#070709', minHeight: '100vh' }}>
      <button
        onClick={onBack}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          backgroundColor: 'transparent',
          border: 'none',
          color: '#94a3b8',
          fontSize: '14px',
          cursor: 'pointer',
          marginBottom: '20px',
        }}
      >
        <ArrowLeft size={16} /> Back to Policies Dashboard
      </button>

      {error && (
        <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: '8px', padding: '12px 16px', marginBottom: '20px', color: '#fca5a5' }}>
          <AlertTriangle size={18} style={{ display: 'inline', marginRight: '8px' }} />
          {error}
        </div>
      )}

      {actionMsg && (
        <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10b981', borderRadius: '8px', padding: '12px 16px', marginBottom: '20px', color: '#6ee7b7' }}>
          <CheckCircle2 size={18} style={{ display: 'inline', marginRight: '8px' }} />
          {actionMsg}
        </div>
      )}

      {/* Header */}
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '24px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '13px', color: '#6366f1', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600, marginBottom: '4px' }}>
            Agent: {policy?.agent_name || agentName || 'Specialist Agent'}
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, margin: 0, color: '#f8fafc' }}>
            {policy?.policy_name || 'Versioned Strategy Strategy'}
          </h1>
          <div style={{ marginTop: '8px', display: 'flex', gap: '12px', alignItems: 'center' }}>
            <span style={{ backgroundColor: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', padding: '4px 10px', borderRadius: '6px', fontSize: '13px', fontWeight: 600 }}>
              Active Version: v{policy?.current_version || '1.0.0'}
            </span>
            <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#34d399', padding: '4px 10px', borderRadius: '6px', fontSize: '13px', fontWeight: 600 }}>
              Status: {policy?.status || 'ACTIVE'}
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={handleOptimize}
            disabled={loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: '#4f46e5',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 16px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <Zap size={16} />
            Trigger Optimization
          </button>

          <button
            onClick={handleRollback}
            disabled={loading || versions.length < 2}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: '#dc2626',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 16px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <RotateCcw size={16} />
            Rollback Policy
          </button>
        </div>
      </div>

      {/* Version History Table */}
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, margin: '0 0 16px 0', color: '#f8fafc' }}>
          Immutable Version History
        </h2>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8' }}>
                <th style={{ padding: '12px' }}>Version</th>
                <th style={{ padding: '12px' }}>Status</th>
                <th style={{ padding: '12px' }}>Score</th>
                <th style={{ padding: '12px' }}>Confidence</th>
                <th style={{ padding: '12px' }}>Adaptation Delta</th>
                <th style={{ padding: '12px' }}>Parent Version</th>
                <th style={{ padding: '12px' }}>Change Reason</th>
                <th style={{ padding: '12px' }}>Created At</th>
              </tr>
            </thead>
            <tbody>
              {versions.map((v) => (
                <tr key={v.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', color: '#e2e8f0' }}>
                  <td style={{ padding: '12px', fontWeight: 600, color: '#38bdf8' }}>v{v.version}</td>
                  <td style={{ padding: '12px' }}>
                    <span
                      style={{
                        backgroundColor:
                          v.status === 'ACTIVE'
                            ? 'rgba(16, 185, 129, 0.2)'
                            : v.status === 'ROLLED_BACK'
                            ? 'rgba(239, 68, 68, 0.2)'
                            : 'rgba(245, 158, 11, 0.2)',
                        color:
                          v.status === 'ACTIVE'
                            ? '#34d399'
                            : v.status === 'ROLLED_BACK'
                            ? '#f87171'
                            : '#fbbf24',
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 600,
                      }}
                    >
                      {v.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>{v.performance_score}%</td>
                  <td style={{ padding: '12px' }}>{v.confidence_score}%</td>
                  <td style={{ padding: '12px' }}>+{v.adaptation_delta}%</td>
                  <td style={{ padding: '12px', color: '#94a3b8' }}>{v.parent_version || 'N/A'}</td>
                  <td style={{ padding: '12px', color: '#cbd5e1' }}>{v.change_reason || 'N/A'}</td>
                  <td style={{ padding: '12px', color: '#64748b' }}>{new Date(v.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
