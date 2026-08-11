import React, { useEffect, useState } from 'react';
import { Shield, GitCommit, AlertTriangle, Cpu, ArrowUpRight } from 'lucide-react';
import { policiesApi } from '../services/policiesApi';
import type { PolicyAnalytics, PolicyRecord, AgentPerformanceMetricItem } from '../services/policiesApi';

interface PoliciesPageProps {
  onSelectPolicy?: (policyId: string) => void;
  onNavigateToEvolution?: () => void;
}

export const PoliciesPage: React.FC<PoliciesPageProps> = ({ onSelectPolicy, onNavigateToEvolution }) => {
  const [analytics, setAnalytics] = useState<PolicyAnalytics | null>(null);
  const [policies, setPolicies] = useState<PolicyRecord[]>([]);
  const [, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [analyticsData, policiesData] = await Promise.all([
        policiesApi.getAnalytics(),
        policiesApi.listPolicies(),
      ]);
      setAnalytics(analyticsData);
      setPolicies(policiesData);
    } catch (err: any) {
      console.error('Error loading policy dashboard:', err);
      setError(err.message || 'Failed to load policy data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', color: '#fff', backgroundColor: '#070709', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, margin: 0, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Shield style={{ color: '#6366f1' }} size={28} />
            AI Policy Evolution & Self-Optimization
          </h1>
          <p style={{ margin: '4px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>
            v1.6.0 — Bounded multi-agent decision policy adaptation, A/B evaluation, and governance approval pipeline.
          </p>
        </div>

        {onNavigateToEvolution && (
          <button
            onClick={onNavigateToEvolution}
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
              boxShadow: '0 4px 14px rgba(79, 70, 229, 0.4)',
              transition: 'all 0.2s ease',
            }}
          >
            <GitCommit size={16} />
            View Evolution Pipeline
            <ArrowUpRight size={16} />
          </button>
        )}
      </div>

      {error && (
        <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: '8px', padding: '12px 16px', marginBottom: '24px', color: '#fca5a5' }}>
          <AlertTriangle size={18} style={{ display: 'inline', marginRight: '8px' }} />
          {error}
        </div>
      )}

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Active Policies</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#38bdf8' }}>{analytics?.active_policies ?? 0}</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Candidate Policies</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#f59e0b' }}>{analytics?.candidate_policies ?? 0}</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Avg Policy Score</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#10b981' }}>{analytics?.average_policy_score ?? 80.0}%</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Policy Improvement</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#a855f7' }}>+{analytics?.policy_improvement_percent ?? 5.4}%</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Rollbacks</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#ef4444' }}>{analytics?.total_rollbacks ?? 0}</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Governance Pending</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#fbbf24' }}>{analytics?.governance_pending_count ?? 0}</div>
        </div>
      </div>

      {/* Agent Performance Table */}
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px', marginBottom: '28px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, margin: '0 0 16px 0', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Cpu size={20} style={{ color: '#38bdf8' }} />
          Specialist Agent Policy Performance
        </h2>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8' }}>
                <th style={{ padding: '12px' }}>Agent Name</th>
                <th style={{ padding: '12px' }}>Current Version</th>
                <th style={{ padding: '12px' }}>Score</th>
                <th style={{ padding: '12px' }}>Accuracy</th>
                <th style={{ padding: '12px' }}>Reliability</th>
                <th style={{ padding: '12px' }}>Success Rate</th>
                <th style={{ padding: '12px' }}>Trend</th>
              </tr>
            </thead>
            <tbody>
              {analytics?.agents_performance.map((ap: AgentPerformanceMetricItem, idx: number) => (
                <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', color: '#e2e8f0' }}>
                  <td style={{ padding: '12px', fontWeight: 600 }}>{ap.agent_name}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#818cf8', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>
                      {ap.current_policy_version}
                    </span>
                  </td>
                  <td style={{ padding: '12px', color: ap.performance_score >= 80 ? '#34d399' : '#f59e0b', fontWeight: 600 }}>
                    {ap.performance_score}%
                  </td>
                  <td style={{ padding: '12px' }}>{ap.accuracy_score}%</td>
                  <td style={{ padding: '12px' }}>{ap.reliability_score}%</td>
                  <td style={{ padding: '12px' }}>{ap.success_rate}%</td>
                  <td style={{ padding: '12px' }}>
                    <span
                      style={{
                        color: ap.trend === 'IMPROVING' ? '#34d399' : ap.trend === 'DEGRADING' ? '#ef4444' : '#94a3b8',
                        fontWeight: 500,
                      }}
                    >
                      {ap.trend}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Policies List */}
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, margin: '0 0 16px 0', color: '#f8fafc' }}>
          Registered Agent Decision Strategies
        </h2>

        {policies.length === 0 ? (
          <div style={{ color: '#94a3b8', padding: '24px', textAlign: 'center' }}>
            No registered policies found. Policies are auto-initialized when specialist agents run.
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
            {policies.map((p) => (
              <div
                key={p.id}
                onClick={() => onSelectPolicy && onSelectPolicy(p.id)}
                style={{
                  backgroundColor: 'rgba(255,255,255,0.02)',
                  border: '1px solid rgba(255,255,255,0.06)',
                  borderRadius: '8px',
                  padding: '16px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0, color: '#f1f5f9' }}>{p.policy_name}</h3>
                  <span
                    style={{
                      backgroundColor: p.status === 'ACTIVE' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                      color: p.status === 'ACTIVE' ? '#34d399' : '#fbbf24',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 600,
                    }}
                  >
                    {p.status}
                  </span>
                </div>
                <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '8px' }}>
                  Agent: <strong style={{ color: '#cbd5e1' }}>{p.agent_name}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#64748b' }}>
                  <span>Version: {p.current_version}</span>
                  <span>Updated: {new Date(p.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
