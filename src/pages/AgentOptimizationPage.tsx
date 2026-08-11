import React, { useEffect, useState } from 'react';
import { ArrowLeft, Zap, ShieldCheck, AlertTriangle, CheckCircle2, ArrowRight } from 'lucide-react';
import { agentIntelligenceApi } from '../services/agentIntelligenceApi';
import type {
  AgentOptimizationRecommendationRecord,
  AgentWeaknessRecord,
  AgentAnomalyRecord
} from '../services/agentIntelligenceApi';

interface AgentOptimizationPageProps {
  onBack: () => void;
}

export const AgentOptimizationPage: React.FC<AgentOptimizationPageProps> = ({ onBack }) => {
  const [recommendations, setRecommendations] = useState<AgentOptimizationRecommendationRecord[]>([]);
  const [weaknesses, setWeaknesses] = useState<AgentWeaknessRecord[]>([]);
  const [anomalies, setAnomalies] = useState<AgentAnomalyRecord[]>([]);
  const [, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [rData, wData, aData] = await Promise.all([
        agentIntelligenceApi.getRecommendations(),
        agentIntelligenceApi.getWeaknesses(),
        agentIntelligenceApi.getAnomalies(),
      ]);
      setRecommendations(rData);
      setWeaknesses(wData);
      setAnomalies(aData);
    } catch (err: any) {
      console.error('Error loading optimization recommendations:', err);
      setError(err.message || 'Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitGovernance = async (recId: string) => {
    try {
      setLoading(true);
      setActionMsg(null);
      const res = await agentIntelligenceApi.submitGovernanceRecommendation(recId);
      setActionMsg(`Recommendation submitted to Governance! Governance Request ID: ${res.governance_approval_id || 'Submitted'}`);
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to submit recommendation to governance');
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

      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, margin: 0, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Zap style={{ color: '#f59e0b' }} size={28} />
          Optimization Control Center
        </h1>
        <p style={{ margin: '4px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>
          Bridging detected weakness & anomaly feeds into bounded policy evolution proposals and governance approvals.
        </p>
      </div>

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

      {/* Visual Optimization Pipeline */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))', gap: '8px', alignItems: 'center', marginBottom: '32px' }}>
        <div style={{ backgroundColor: '#0f172a', border: '1px solid #38bdf8', borderRadius: '10px', padding: '12px', textAlign: 'center' }}>
          <div style={{ fontSize: '10px', color: '#38bdf8', fontWeight: 700 }}>STEP 1</div>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#fff', marginTop: '4px' }}>Performance</div>
        </div>
        <ArrowRight size={16} style={{ color: '#475569', margin: '0 auto' }} />

        <div style={{ backgroundColor: '#0f172a', border: '1px solid #ef4444', borderRadius: '10px', padding: '12px', textAlign: 'center' }}>
          <div style={{ fontSize: '10px', color: '#ef4444', fontWeight: 700 }}>STEP 2</div>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#fff', marginTop: '4px' }}>Weakness</div>
        </div>
        <ArrowRight size={16} style={{ color: '#475569', margin: '0 auto' }} />

        <div style={{ backgroundColor: '#0f172a', border: '1px solid #f59e0b', borderRadius: '10px', padding: '12px', textAlign: 'center' }}>
          <div style={{ fontSize: '10px', color: '#f59e0b', fontWeight: 700 }}>STEP 3</div>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#fff', marginTop: '4px' }}>Recommendation</div>
        </div>
        <ArrowRight size={16} style={{ color: '#475569', margin: '0 auto' }} />

        <div style={{ backgroundColor: '#0f172a', border: '1px solid #818cf8', borderRadius: '10px', padding: '12px', textAlign: 'center' }}>
          <div style={{ fontSize: '10px', color: '#818cf8', fontWeight: 700 }}>STEP 4</div>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#fff', marginTop: '4px' }}>Policy Candidate</div>
        </div>
        <ArrowRight size={16} style={{ color: '#475569', margin: '0 auto' }} />

        <div style={{ backgroundColor: '#0f172a', border: '1px solid #a855f7', borderRadius: '10px', padding: '12px', textAlign: 'center' }}>
          <div style={{ fontSize: '10px', color: '#a855f7', fontWeight: 700 }}>STEP 5</div>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#fff', marginTop: '4px' }}>A/B Test</div>
        </div>
        <ArrowRight size={16} style={{ color: '#475569', margin: '0 auto' }} />

        <div style={{ backgroundColor: '#0f172a', border: '1px solid #ec4899', borderRadius: '10px', padding: '12px', textAlign: 'center' }}>
          <div style={{ fontSize: '10px', color: '#ec4899', fontWeight: 700 }}>STEP 6</div>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#fff', marginTop: '4px' }}>Risk Engine</div>
        </div>
        <ArrowRight size={16} style={{ color: '#475569', margin: '0 auto' }} />

        <div style={{ backgroundColor: '#0f172a', border: '1px solid #fbbf24', borderRadius: '10px', padding: '12px', textAlign: 'center' }}>
          <div style={{ fontSize: '10px', color: '#fbbf24', fontWeight: 700 }}>STEP 7</div>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#fff', marginTop: '4px' }}>Governance</div>
        </div>
        <ArrowRight size={16} style={{ color: '#475569', margin: '0 auto' }} />

        <div style={{ backgroundColor: '#0f172a', border: '1px solid #10b981', borderRadius: '10px', padding: '12px', textAlign: 'center' }}>
          <div style={{ fontSize: '10px', color: '#10b981', fontWeight: 700 }}>STEP 8</div>
          <div style={{ fontSize: '12px', fontWeight: 700, color: '#fff', marginTop: '4px' }}>Apply</div>
        </div>
      </div>

      {/* Recommendations Feed */}
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px', marginBottom: '28px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, margin: '0 0 16px 0', color: '#f8fafc' }}>
          Active Autonomous Optimization Recommendations
        </h2>

        {recommendations.length === 0 ? (
          <div style={{ color: '#94a3b8', padding: '20px', textAlign: 'center' }}>
            No recommendations generated. Trigger agent analysis to run weakness detection.
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
            {recommendations.map((rec) => (
              <div key={rec.id} style={{ backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '8px', padding: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0, color: '#f1f5f9' }}>{rec.agent_name}</h3>
                  <span style={{ backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    {rec.status}
                  </span>
                </div>

                <p style={{ fontSize: '13px', color: '#cbd5e1', margin: '0 0 12px 0' }}>{rec.reason}</p>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#94a3b8', marginBottom: '16px' }}>
                  <span>Metric: <strong>{rec.target_metric}</strong></span>
                  <span>Target: <strong style={{ color: '#34d399' }}>{rec.target_value}</strong></span>
                  <span>Risk: <strong style={{ color: '#38bdf8' }}>{rec.risk_level}</strong></span>
                </div>

                {rec.status === 'DRAFT' && (
                  <button
                    onClick={() => handleSubmitGovernance(rec.id)}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px',
                      backgroundColor: '#4f46e5',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '6px',
                      padding: '8px 12px',
                      fontSize: '13px',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                  >
                    <ShieldCheck size={14} /> Submit to Governance
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Weaknesses & Anomalies Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 14px 0', color: '#f8fafc' }}>
            Detected Weaknesses Feed
          </h2>
          {weaknesses.length === 0 ? (
            <div style={{ color: '#94a3b8', fontSize: '13px' }}>No weaknesses detected.</div>
          ) : (
            weaknesses.map((w) => (
              <div key={w.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', padding: '10px 0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: 600 }}>
                  <span style={{ color: '#f8fafc' }}>{w.agent_name} ({w.weakness_type})</span>
                  <span style={{ color: '#ef4444' }}>{w.severity}</span>
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>{w.explanation}</div>
              </div>
            ))
          )}
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 14px 0', color: '#f8fafc' }}>
            Detected Anomalies Feed
          </h2>
          {anomalies.length === 0 ? (
            <div style={{ color: '#94a3b8', fontSize: '13px' }}>No empirical anomalies detected.</div>
          ) : (
            anomalies.map((a) => (
              <div key={a.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', padding: '10px 0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: 600 }}>
                  <span style={{ color: '#f8fafc' }}>{a.agent_name} ({a.anomaly_type})</span>
                  <span style={{ color: '#f59e0b' }}>+{a.deviation_percent}% dev</span>
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>{a.explanation}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
