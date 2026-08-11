import React, { useEffect, useState } from 'react';
import { ArrowLeft, AlertTriangle, ArrowRight, ShieldAlert, Award } from 'lucide-react';
import { knowledgeApi } from '../services/knowledgeApi';
import type { OutcomeRootCauseRecord } from '../services/knowledgeApi';

interface RootCausePageProps {
  outcomeId?: string;
  onBack: () => void;
}

export const RootCausePage: React.FC<RootCausePageProps> = ({ outcomeId, onBack }) => {
  const targetId = outcomeId || 'out_801';
  const [rootCause, setRootCause] = useState<OutcomeRootCauseRecord | null>(null);
  const [, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRootCause();
  }, [targetId]);

  const loadRootCause = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await knowledgeApi.getOutcomeRootCause(targetId);
      setRootCause(res);
    } catch (err: any) {
      console.error('Error loading outcome root cause:', err);
      setError(err.message || 'Failed to load root cause analysis');
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
            <span style={{ backgroundColor: 'rgba(239, 68, 68, 0.2)', color: '#f87171', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 700 }}>
              STATUS: {rootCause?.status || 'FAILED'}
            </span>
            <span style={{ backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
              Outcome #{targetId.slice(0, 8)}
            </span>
          </div>

          <h1 style={{ fontSize: '24px', fontWeight: 700, margin: 0, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShieldAlert style={{ color: '#ef4444' }} size={28} />
            Outcome Root-Cause Analysis
          </h1>
          <p style={{ margin: '4px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>
            Primary Contributor: <strong style={{ color: '#f87171' }}>{rootCause?.primary_root_cause || 'Prediction Error'}</strong>
          </p>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '12px', color: '#94a3b8', fontWeight: 600 }}>ANALYSIS CONFIDENCE</div>
          <div style={{ fontSize: '32px', fontWeight: 700, color: '#38bdf8' }}>{rootCause?.confidence ?? 85.0}%</div>
        </div>
      </div>

      {error && (
        <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: '8px', padding: '12px 16px', marginBottom: '24px', color: '#fca5a5' }}>
          <AlertTriangle size={18} style={{ display: 'inline', marginRight: '8px' }} />
          {error}
        </div>
      )}

      {/* Backward Traversal Chain */}
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px', marginBottom: '28px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 16px 0', color: '#f8fafc' }}>
          Backward Causal Root-Cause Path
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', gap: '8px', alignItems: 'center' }}>
          {['OUTCOME', 'EXECUTION', 'POLICY', 'PREDICTION', 'AGENTS', 'EVIDENCE'].map((layer, i, arr) => (
            <React.Fragment key={layer}>
              <div style={{ backgroundColor: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '10px 4px', textAlign: 'center' }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#f87171' }}>{layer}</div>
              </div>
              {i < arr.length - 1 && <ArrowRight size={14} style={{ color: '#475569', margin: '0 auto' }} />}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Ranked Root Cause Contributors */}
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px', marginBottom: '28px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, margin: '0 0 16px 0', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Award size={20} style={{ color: '#f59e0b' }} />
          Ranked Root-Cause Contributors
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {rootCause?.contributors.map((c) => (
            <div key={c.rank} style={{ backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '8px', padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, margin: 0, color: '#f1f5f9' }}>{c.contributor_name}</h3>
                <span style={{ backgroundColor: c.rank === 1 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)', color: c.rank === 1 ? '#f87171' : '#fbbf24', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 700 }}>
                  Rank #{c.rank}
                </span>
              </div>

              <div style={{ fontSize: '13px', color: '#cbd5e1', marginBottom: '12px' }}>{c.explanation}</div>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#94a3b8' }}>
                <span>Type: <strong>{c.contributor_type}</strong></span>
                <span>Contribution Score: <strong style={{ color: '#ef4444' }}>{c.contribution_score}%</strong></span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Observations */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 12px 0', color: '#34d399' }}>Supporting Observations</h3>
          {rootCause?.supporting_observations.map((obs, i) => (
            <div key={i} style={{ fontSize: '13px', color: '#e2e8f0', marginBottom: '6px' }}>• {obs}</div>
          ))}
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 12px 0', color: '#f87171' }}>Contradicting Observations</h3>
          {rootCause?.contradicting_observations.length === 0 ? (
            <div style={{ fontSize: '13px', color: '#94a3b8' }}>None detected.</div>
          ) : (
            rootCause?.contradicting_observations.map((obs, i) => (
              <div key={i} style={{ fontSize: '13px', color: '#e2e8f0', marginBottom: '6px' }}>• {obs}</div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
