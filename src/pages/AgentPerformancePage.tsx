import React, { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { learningApi } from '../services/learningApi';
import type { AgentPerformanceRecord } from '../services/learningApi';

interface AgentPerformancePageProps {
  agent: AgentPerformanceRecord;
  onBack: () => void;
}

export const AgentPerformancePage: React.FC<AgentPerformancePageProps> = ({ agent, onBack }) => {
  const currentPerf = agent;
  const [loading, setLoading] = useState(false);
  const [proposedDelta, setProposedDelta] = useState('5.0');
  const [adaptationMessage, setAdaptationMessage] = useState<string | null>(null);

  const handleProposeAdaptation = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setAdaptationMessage(null);
    try {
      const res = await learningApi.proposeAdaptation(currentPerf.agent_name, parseFloat(proposedDelta));
      setAdaptationMessage(`Bounded Adaptation Proposed! Delta: +${res.adaptation_delta}%, Status: ${res.status}`);
    } catch (err: any) {
      alert(err.message || 'Adaptation proposal failed');
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

      {/* Header Banner */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '28px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
            <span style={{ padding: '4px 10px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981', borderRadius: '8px', fontSize: '12px', fontWeight: '700' }}>
              RELIABILITY: {currentPerf.reliability_class}
            </span>
            <span style={{ padding: '4px 10px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#8b5cf6', borderRadius: '8px', fontSize: '12px', fontWeight: '700' }}>
              VERSION {currentPerf.agent_version}
            </span>
          </div>

          <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#f9fafb', margin: '0 0 8px 0' }}>{currentPerf.agent_name} Performance Intelligence</h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>Grounded reliability scoring & bounded self-optimization limits</p>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600' }}>RELIABILITY SCORE</div>
          <div style={{ fontSize: '32px', fontWeight: '700', color: '#10b981' }}>{currentPerf.current_reliability_score}%</div>
        </div>
      </div>

      {/* Breakdown Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>PREDICTION ACCURACY (30%)</div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#6366f1' }}>{currentPerf.prediction_accuracy}%</div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>OUTCOME SUCCESS RATE (25%)</div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#10b981' }}>{currentPerf.outcome_success_rate}%</div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>EVIDENCE QUALITY (15%)</div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#8b5cf6' }}>{currentPerf.evidence_quality_score}%</div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>HUMAN APPROVAL (10%)</div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#f59e0b' }}>{currentPerf.human_approval_rate}%</div>
        </div>
      </div>

      {/* Propose Bounded Adaptation Form */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f9fafb', marginBottom: '14px' }}>Propose Bounded Policy Adaptation</h3>

        {adaptationMessage ? (
          <div style={{ backgroundColor: '#1f2937', border: '1px solid #10b981', borderRadius: '10px', padding: '16px', color: '#10b981', fontWeight: '600' }}>
            {adaptationMessage}
          </div>
        ) : (
          <form onSubmit={handleProposeAdaptation} style={{ display: 'flex', gap: '14px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: '220px' }}>
              <label style={{ display: 'block', fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '6px' }}>PROPOSED BOUNDED DELTA (MAX ±10%)</label>
              <input
                type="number"
                step="0.5"
                min="-10.0"
                max="10.0"
                value={proposedDelta}
                onChange={(e) => setProposedDelta(e.target.value)}
                required
                style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px', color: '#f9fafb', fontSize: '14px' }}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              style={{ padding: '12px 24px', backgroundColor: '#6366f1', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer' }}
            >
              Propose Policy Adaptation
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
