import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, ArrowUpRight, RefreshCw, Cpu, Award, Zap } from 'lucide-react';
import { agentIntelligenceApi } from '../services/agentIntelligenceApi';
import type {
  AgentIntelligenceOverview,
  AgentMetricRecord,
  AgentBenchmarkRecord
} from '../services/agentIntelligenceApi';

interface AgentIntelligencePageProps {
  onSelectAgent?: (agentName: string) => void;
  onNavigateToOptimization?: () => void;
}

export const AgentIntelligencePage: React.FC<AgentIntelligencePageProps> = ({
  onSelectAgent,
  onNavigateToOptimization,
}) => {
  const [overview, setOverview] = useState<AgentIntelligenceOverview | null>(null);
  const [, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await agentIntelligenceApi.getOverview();
      setOverview(data);
    } catch (err: any) {
      console.error('Error loading agent intelligence overview:', err);
      setError(err.message || 'Failed to load agent performance intelligence');
    } finally {
      setLoading(false);
    }
  };

  const getHealthBadge = (status: string) => {
    switch (status) {
      case 'EXCELLENT':
      case 'HEALTHY':
        return { bg: 'rgba(16, 185, 129, 0.2)', color: '#34d399' };
      case 'DEGRADED':
      case 'AT_RISK':
        return { bg: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24' };
      case 'CRITICAL':
      default:
        return { bg: 'rgba(239, 68, 68, 0.2)', color: '#f87171' };
    }
  };

  return (
    <div style={{ padding: '24px', color: '#fff', backgroundColor: '#070709', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, margin: 0, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Cpu style={{ color: '#38bdf8' }} size={28} />
            Agent Performance Intelligence
          </h1>
          <p style={{ margin: '4px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>
            v1.7.0 — Continuous specialist agent performance measurement, weakness detection, and autonomous optimization recommendations.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={loadData}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: '#1e293b',
              color: '#94a3b8',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              padding: '10px 14px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={16} /> Refresh
          </button>

          {onNavigateToOptimization && (
            <button
              onClick={onNavigateToOptimization}
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
              }}
            >
              <Zap size={16} /> Optimization Control Center
              <ArrowUpRight size={16} />
            </button>
          )}
        </div>
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
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Total Agents</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#f8fafc' }}>{overview?.total_agents ?? 5}</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Healthy Agents</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#34d399' }}>{overview?.healthy_agents ?? 0}</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>At-Risk Agents</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#fbbf24' }}>{overview?.at_risk_agents ?? 0}</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Critical Agents</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#ef4444' }}>{overview?.critical_agents ?? 0}</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Avg Agent Score</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#38bdf8' }}>{overview?.average_agent_score ?? 82.5}%</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Avg Accuracy</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#a855f7' }}>{overview?.average_accuracy ?? 85.0}%</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Recommendations</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#f59e0b' }}>{overview?.optimization_recommendations_count ?? 0}</div>
        </div>
      </div>

      {/* Specialist Agent Telemetry Table */}
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px', marginBottom: '28px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, margin: '0 0 16px 0', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={20} style={{ color: '#38bdf8' }} />
          Specialist Agent Health & Telemetry
        </h2>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8' }}>
                <th style={{ padding: '12px' }}>Agent Name</th>
                <th style={{ padding: '12px' }}>Health Status</th>
                <th style={{ padding: '12px' }}>Overall Score</th>
                <th style={{ padding: '12px' }}>Accuracy</th>
                <th style={{ padding: '12px' }}>Reliability</th>
                <th style={{ padding: '12px' }}>Evidence Quality</th>
                <th style={{ padding: '12px' }}>Success Rate</th>
                <th style={{ padding: '12px' }}>Avg Latency</th>
                <th style={{ padding: '12px' }}>Trend</th>
              </tr>
            </thead>
            <tbody>
              {overview?.agents.map((ag: AgentMetricRecord, idx: number) => {
                const badge = getHealthBadge(ag.health_status);
                return (
                  <tr
                    key={idx}
                    onClick={() => onSelectAgent && onSelectAgent(ag.agent_name)}
                    style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', color: '#e2e8f0', cursor: 'pointer' }}
                  >
                    <td style={{ padding: '12px', fontWeight: 600 }}>{ag.agent_name}</td>
                    <td style={{ padding: '12px' }}>
                      <span style={{ backgroundColor: badge.bg, color: badge.color, padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                        {ag.health_status}
                      </span>
                    </td>
                    <td style={{ padding: '12px', fontWeight: 700, color: '#38bdf8' }}>{ag.overall_agent_score}%</td>
                    <td style={{ padding: '12px' }}>{ag.prediction_accuracy}%</td>
                    <td style={{ padding: '12px' }}>{ag.policy_score}%</td>
                    <td style={{ padding: '12px' }}>{ag.evidence_quality_score}%</td>
                    <td style={{ padding: '12px' }}>{ag.success_rate}%</td>
                    <td style={{ padding: '12px', color: '#94a3b8' }}>{ag.average_latency_ms.toFixed(0)}ms</td>
                    <td style={{ padding: '12px' }}>
                      <span style={{ color: ag.trend === 'IMPROVING' ? '#34d399' : ag.trend === 'DECLINING' ? '#ef4444' : '#94a3b8', fontWeight: 500 }}>
                        {ag.trend}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Specialist Benchmarks Matrix */}
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, margin: '0 0 16px 0', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Award size={20} style={{ color: '#f59e0b' }} />
          Normalized Specialist Agent Benchmarks
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {overview?.benchmarks.map((bm: AgentBenchmarkRecord) => (
            <div key={bm.id} style={{ backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '8px', padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0, color: '#f1f5f9' }}>{bm.agent_name}</h3>
                <span style={{ backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 700 }}>
                  Rank #{bm.rank}
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '13px', color: '#94a3b8', marginTop: '12px' }}>
                <div>Overall: <strong style={{ color: '#38bdf8' }}>{bm.overall_score}%</strong></div>
                <div>Accuracy: <strong style={{ color: '#e2e8f0' }}>{bm.accuracy_score}%</strong></div>
                <div>Reliability: <strong style={{ color: '#e2e8f0' }}>{bm.reliability_score}%</strong></div>
                <div>Evidence: <strong style={{ color: '#e2e8f0' }}>{bm.evidence_quality}%</strong></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
