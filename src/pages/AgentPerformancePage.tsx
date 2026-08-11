import React, { useEffect, useState } from 'react';
import { ArrowLeft, AlertTriangle } from 'lucide-react';
import { agentIntelligenceApi } from '../services/agentIntelligenceApi';
import type { AgentMetricRecord } from '../services/agentIntelligenceApi';

interface AgentPerformancePageProps {
  agent?: AgentMetricRecord | any;
  agentName?: string;
  onBack: () => void;
}

export const AgentPerformancePage: React.FC<AgentPerformancePageProps> = ({ agent, agentName, onBack }) => {
  const [metric, setMetric] = useState<AgentMetricRecord | null>(agent && agent.agent_name ? (agent as AgentMetricRecord) : null);
  const [history, setHistory] = useState<AgentMetricRecord[]>([]);
  const [, setLoading] = useState(!metric);
  const [error, setError] = useState<string | null>(null);

  const targetAgentName = agent?.agent_name || agentName || 'Business Analysis';

  useEffect(() => {
    loadAgentData();
  }, [targetAgentName]);

  const loadAgentData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [mRes, hRes] = await Promise.all([
        agentIntelligenceApi.getAgent(targetAgentName),
        agentIntelligenceApi.getAgentHistory(targetAgentName),
      ]);
      setMetric(mRes);
      setHistory(hRes);
    } catch (err: any) {
      console.error('Error loading agent performance:', err);
      setError(err.message || 'Failed to load performance metrics');
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
        <ArrowLeft size={16} /> Back to Agent Intelligence Overview
      </button>

      {error && (
        <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: '8px', padding: '12px 16px', marginBottom: '24px', color: '#fca5a5' }}>
          <AlertTriangle size={18} style={{ display: 'inline', marginRight: '8px' }} />
          {error}
        </div>
      )}

      {/* Header Banner */}
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '24px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
            <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#34d399', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 700 }}>
              {metric?.health_status || 'HEALTHY'}
            </span>
            <span style={{ backgroundColor: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
              Version {metric?.policy_version || '1.0.0'}
            </span>
          </div>

          <h1 style={{ fontSize: '24px', fontWeight: 700, margin: 0, color: '#f8fafc' }}>
            {targetAgentName} Performance Intelligence
          </h1>
          <p style={{ margin: '4px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>
            Empirical telemetry tracking prediction accuracy, latency, tool success, and policy metrics.
          </p>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 600 }}>OVERALL AGENT SCORE</div>
          <div style={{ fontSize: '32px', fontWeight: 700, color: '#38bdf8' }}>{metric?.overall_agent_score ?? 82.5}%</div>
        </div>
      </div>

      {/* Detailed Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Prediction Accuracy</div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: '#34d399', marginTop: '4px' }}>{metric?.prediction_accuracy ?? 85.0}%</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Evidence Quality</div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: '#38bdf8', marginTop: '4px' }}>{metric?.evidence_quality_score ?? 85.0}%</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Tool Success Rate</div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: '#a855f7', marginTop: '4px' }}>{metric?.tool_success_rate ?? 95.0}%</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Average Latency</div>
          <div style={{ fontSize: '20px', fontWeight: 700, color: '#f59e0b', marginTop: '4px' }}>{(metric?.average_latency_ms ?? 1200).toFixed(0)}ms</div>
        </div>
      </div>

      {/* Historical Telemetry Table */}
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, margin: '0 0 16px 0', color: '#f8fafc' }}>
          Historical Telemetry Log
        </h2>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8' }}>
                <th style={{ padding: '12px' }}>Recorded At</th>
                <th style={{ padding: '12px' }}>Executions</th>
                <th style={{ padding: '12px' }}>Score</th>
                <th style={{ padding: '12px' }}>Accuracy</th>
                <th style={{ padding: '12px' }}>Evidence</th>
                <th style={{ padding: '12px' }}>Latency</th>
                <th style={{ padding: '12px' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {history.map((h) => (
                <tr key={h.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', color: '#e2e8f0' }}>
                  <td style={{ padding: '12px', color: '#64748b' }}>{new Date(h.recorded_at).toLocaleString()}</td>
                  <td style={{ padding: '12px' }}>{h.execution_count}</td>
                  <td style={{ padding: '12px', fontWeight: 700, color: '#38bdf8' }}>{h.overall_agent_score}%</td>
                  <td style={{ padding: '12px' }}>{h.prediction_accuracy}%</td>
                  <td style={{ padding: '12px' }}>{h.evidence_quality_score}%</td>
                  <td style={{ padding: '12px', color: '#94a3b8' }}>{h.average_latency_ms.toFixed(0)}ms</td>
                  <td style={{ padding: '12px' }}>{h.health_status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
