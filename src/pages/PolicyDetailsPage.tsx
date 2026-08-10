import React, { useEffect, useState } from 'react';
import { ArrowLeft, RotateCcw, History } from 'lucide-react';
import { learningApi } from '../services/learningApi';
import type { AgentPolicyRecord } from '../services/learningApi';

interface PolicyDetailsPageProps {
  agentName: string;
  onBack: () => void;
}

export const PolicyDetailsPage: React.FC<PolicyDetailsPageProps> = ({ agentName, onBack }) => {
  const [policies, setPolicies] = useState<AgentPolicyRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [rollbackMsg, setRollbackMsg] = useState<string | null>(null);

  const fetchPolicies = async () => {
    setLoading(true);
    const data = await learningApi.getPolicies(agentName);
    setPolicies(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchPolicies();
  }, [agentName]);

  const handleRollback = async () => {
    setLoading(true);
    setRollbackMsg(null);
    try {
      const res = await learningApi.rollbackPolicy(agentName);
      setRollbackMsg(res.message);
      fetchPolicies();
    } catch (err: any) {
      alert(err.message || 'Rollback failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '28px', maxWidth: '1100px', margin: '0 auto' }}>
      <button
        onClick={onBack}
        style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'none', border: 'none', color: '#9ca3af', fontSize: '14px', cursor: 'pointer', marginBottom: '20px' }}
      >
        <ArrowLeft size={16} /> Back to Learning Overview
      </button>

      {/* Header */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '28px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#f9fafb', margin: '0 0 8px 0' }}>{agentName} Versioned Policies</h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>Auditable, reversible, and version-controlled agent configurations</p>
        </div>

        <button
          onClick={handleRollback}
          disabled={loading || policies.length < 2}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 20px', backgroundColor: '#ef4444', color: '#fff', border: 'none', borderRadius: '10px', fontWeight: '700', cursor: 'pointer' }}
        >
          <RotateCcw size={16} /> Rollback Policy
        </button>
      </div>

      {rollbackMsg && (
        <div style={{ backgroundColor: '#1f2937', border: '1px solid #ef4444', borderRadius: '12px', padding: '16px', color: '#f87171', fontWeight: '600', marginBottom: '24px' }}>
          {rollbackMsg}
        </div>
      )}

      {/* Policy History List */}
      <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f9fafb', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <History style={{ color: '#6366f1' }} size={20} /> Policy Version History ({policies.length})
      </h3>

      {loading ? (
        <div style={{ color: '#9ca3af', textAlign: 'center', padding: '40px' }}>Loading versioned policies...</div>
      ) : policies.length === 0 ? (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '40px', textAlign: 'center', color: '#9ca3af' }}>
          No versioned policy records found for {agentName}. Default base policy active.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {policies.map((p) => (
            <div key={p.id} style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                  <span style={{ padding: '3px 8px', backgroundColor: p.status === 'ACTIVE' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(156, 163, 175, 0.15)', color: p.status === 'ACTIVE' ? '#10b981' : '#9ca3af', borderRadius: '6px', fontSize: '11px', fontWeight: '700' }}>
                    {p.status}
                  </span>
                  <span style={{ fontSize: '12px', color: '#6b7280' }}>VERSION {p.policy_version}</span>
                </div>
                <div style={{ fontSize: '14px', color: '#d1d5db', fontWeight: '600' }}>{p.reason}</div>
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>
                {new Date(p.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
