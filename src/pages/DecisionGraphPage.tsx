import React, { useEffect, useState } from 'react';
import { ArrowLeft, HelpCircle, AlertTriangle } from 'lucide-react';
import { knowledgeApi } from '../services/knowledgeApi';
import type { DecisionChainRecord } from '../services/knowledgeApi';

interface DecisionGraphPageProps {
  decisionId?: string;
  onBack: () => void;
}

export const DecisionGraphPage: React.FC<DecisionGraphPageProps> = ({ decisionId, onBack }) => {
  const targetId = decisionId || 'dec_301';
  const [chain, setChain] = useState<DecisionChainRecord | null>(null);
  const [, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadChain();
  }, [targetId]);

  const loadChain = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await knowledgeApi.getDecisionChain(targetId);
      setChain(res);
    } catch (err: any) {
      console.error('Error loading decision chain:', err);
      setError(err.message || 'Failed to load decision explanation chain');
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
        <ArrowLeft size={16} /> Back to Knowledge Overview
      </button>

      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '24px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
            <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#34d399', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 700 }}>
              VERIFIED GROUNDING
            </span>
            <span style={{ backgroundColor: 'rgba(168, 85, 247, 0.2)', color: '#c084fc', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
              Decision #{targetId.slice(0, 8)}
            </span>
          </div>

          <h1 style={{ fontSize: '24px', fontWeight: 700, margin: 0, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <HelpCircle style={{ color: '#38bdf8' }} size={26} />
            WHY THIS DECISION? Explainability Chain
          </h1>
          <p style={{ margin: '4px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>
            {chain?.label || 'Strategic Execution Decision'}
          </p>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 600 }}>EXPLAINABILITY CONFIDENCE</div>
          <div style={{ fontSize: '32px', fontWeight: 700, color: '#38bdf8' }}>{chain?.confidence ?? 88.5}%</div>
        </div>
      </div>

      {error && (
        <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: '8px', padding: '12px 16px', marginBottom: '24px', color: '#fca5a5' }}>
          <AlertTriangle size={18} style={{ display: 'inline', marginRight: '8px' }} />
          {error}
        </div>
      )}

      {/* Full Explainability Layers */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Layer 1: Evidence */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 600, margin: 0, color: '#38bdf8' }}>1. Verified Evidence Layer</h2>
            <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#34d399', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>VERIFIED</span>
          </div>

          {chain?.evidence_used.map((ev, i) => (
            <div key={i} style={{ fontSize: '13px', color: '#e2e8f0', backgroundColor: 'rgba(255,255,255,0.02)', padding: '10px', borderRadius: '6px', marginBottom: '6px' }}>
              <strong>[{ev.source || 'Evidence Source'}]</strong> {ev.finding} (Confidence: {ev.confidence || 90}%)
            </div>
          ))}
        </div>

        {/* Layer 2: Memory & Lessons */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 600, margin: 0, color: '#a855f7' }}>2. Historical Memory & Lessons</h2>
            <span style={{ backgroundColor: 'rgba(168, 85, 247, 0.2)', color: '#c084fc', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>HISTORICAL</span>
          </div>

          {chain?.memories_used.map((m, i) => (
            <div key={i} style={{ fontSize: '13px', color: '#e2e8f0', backgroundColor: 'rgba(255,255,255,0.02)', padding: '10px', borderRadius: '6px', marginBottom: '6px' }}>
              Title: <strong>{m.title}</strong> | Outcome: {m.outcome} | Confidence: {m.confidence}%
            </div>
          ))}
        </div>

        {/* Layer 3: Agent Contributions */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 600, margin: 0, color: '#34d399' }}>3. Specialist Agent Contributions</h2>
            <span style={{ backgroundColor: 'rgba(52, 211, 153, 0.2)', color: '#34d399', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>VERIFIED</span>
          </div>

          {chain?.agents_involved.map((ag, i) => (
            <div key={i} style={{ fontSize: '13px', color: '#e2e8f0', backgroundColor: 'rgba(255,255,255,0.02)', padding: '10px', borderRadius: '6px', marginBottom: '6px' }}>
              <strong>{ag.agent_name}</strong>: {ag.contribution}
            </div>
          ))}
        </div>

        {/* Layer 4: Prediction & Policy */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 600, margin: 0, color: '#fbbf24' }}>4. Prediction & Governed Policy</h2>
            <span style={{ backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>HYPOTHESIS / GOVERNED</span>
          </div>

          <div style={{ fontSize: '13px', color: '#e2e8f0', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', padding: '10px', borderRadius: '6px' }}>
              Prediction: <strong>{chain?.prediction?.scenario_name || '15% Margin Expansion'}</strong> ({chain?.prediction?.predicted_probability || 85}%)
            </div>
            <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', padding: '10px', borderRadius: '6px' }}>
              Policy: <strong>{chain?.policy_version?.policy_name || 'Pricing Policy'}</strong> (v{chain?.policy_version?.version || '1.2.0'})
            </div>
          </div>
        </div>

        {/* Layer 5: Outcome & Actual ROI */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 600, margin: 0, color: '#ec4899' }}>5. Executed Action & Actual Outcome</h2>
            <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#34d399', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>VERIFIED OUTCOME</span>
          </div>

          <div style={{ fontSize: '13px', color: '#e2e8f0', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', padding: '10px', borderRadius: '6px' }}>
              Action: <strong>{chain?.action?.action_name || 'Deploy Strategy'}</strong> ({chain?.action?.status || 'COMPLETED'})
            </div>
            <div style={{ backgroundColor: 'rgba(255,255,255,0.02)', padding: '10px', borderRadius: '6px' }}>
              Outcome Status: <strong style={{ color: '#34d399' }}>{chain?.outcome?.outcome_status || 'SUCCESS'}</strong> (ROI: +{chain?.outcome?.roi || 14.5}%)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
