import React, { useState } from 'react';
import { ArrowLeft, ShieldCheck, Database, FileText, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { predictionsApi } from '../services/predictionsApi';
import type { PredictionRecord } from '../services/predictionsApi';

interface PredictionDetailsPageProps {
  prediction: PredictionRecord;
  onBack: () => void;
}

export const PredictionDetailsPage: React.FC<PredictionDetailsPageProps> = ({ prediction, onBack }) => {
  const [submitting, setSubmitting] = useState(false);
  const [approvalSent, setApprovalSent] = useState(false);

  const handleApproveSubmit = async () => {
    setSubmitting(true);
    try {
      await predictionsApi.approvePrediction(prediction.id);
      setApprovalSent(true);
    } catch (err: any) {
      alert(err.message || 'Failed to submit prediction for approval.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ padding: '28px', maxWidth: '1100px', margin: '0 auto' }}>
      <button
        onClick={onBack}
        style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'none', border: 'none', color: '#9ca3af', fontSize: '14px', cursor: 'pointer', marginBottom: '20px' }}
      >
        <ArrowLeft size={16} /> Back to Predictions List
      </button>

      {/* Header Banner */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '28px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
            <span style={{ padding: '4px 10px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#8b5cf6', borderRadius: '8px', fontSize: '12px', fontWeight: '700' }}>
              SCENARIO: {prediction.scenario_type}
            </span>
            <span style={{ padding: '4px 10px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b', borderRadius: '8px', fontSize: '12px', fontWeight: '700' }}>
              RISK: {prediction.risk_level} ({prediction.risk_score}/100)
            </span>
          </div>

          <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#f9fafb', margin: '0 0 8px 0' }}>{prediction.scenario_name}</h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>{prediction.objective || 'Predictive Decision Intelligence'}</p>
        </div>

        {approvalSent ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10b981', fontWeight: '700', backgroundColor: 'rgba(16, 185, 129, 0.15)', padding: '12px 20px', borderRadius: '10px' }}>
            <CheckCircle2 size={18} /> Governance Approval Requested
          </div>
        ) : (
          <button
            onClick={handleApproveSubmit}
            disabled={submitting}
            style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 20px', backgroundColor: '#6366f1', color: '#fff', border: 'none', borderRadius: '10px', fontWeight: '700', cursor: 'pointer' }}
          >
            <ShieldCheck size={18} /> Submit for Human Approval
          </button>
        )}
      </div>

      {/* Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>PREDICTED {prediction.metric_name}</div>
          <div style={{ fontSize: '26px', fontWeight: '700', color: '#8b5cf6' }}>{prediction.predicted_value}{prediction.unit}</div>
          <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>Expected Range: {prediction.lower_bound}–{prediction.upper_bound}{prediction.unit}</div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>PREDICTION CONFIDENCE</div>
          <div style={{ fontSize: '26px', fontWeight: '700', color: '#60a5fa' }}>{prediction.confidence_score}%</div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>VERIFIED EVIDENCE / MEMORIES</div>
          <div style={{ fontSize: '26px', fontWeight: '700', color: '#10b981' }}>{prediction.evidence_count} / {prediction.memory_count}</div>
        </div>
      </div>

      {/* Mandatory Transparency Sections */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* 1. Verified Evidence */}
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f9fafb', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText style={{ color: '#10b981' }} size={20} /> CURRENT VERIFIED EVIDENCE
          </h3>
          {prediction.evidence_references && prediction.evidence_references.length > 0 ? (
            <ul style={{ color: '#d1d5db', paddingLeft: '20px', margin: 0, lineHeight: '1.6' }}>
              {prediction.evidence_references.map((ev, i) => (
                <li key={i}>{ev.finding || JSON.stringify(ev)}</li>
              ))}
            </ul>
          ) : (
            <div style={{ color: '#9ca3af', fontSize: '14px' }}>{prediction.evidence_count} verified sources indexed during graph execution.</div>
          )}
        </div>

        {/* 2. Historical Memory */}
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f9fafb', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database style={{ color: '#8b5cf6' }} size={20} /> HISTORICAL MEMORY
          </h3>
          {prediction.memory_references && prediction.memory_references.length > 0 ? (
            <ul style={{ color: '#d1d5db', paddingLeft: '20px', margin: 0, lineHeight: '1.6' }}>
              {prediction.memory_references.map((mem, i) => (
                <li key={i}>{mem.title || JSON.stringify(mem)}</li>
              ))}
            </ul>
          ) : (
            <div style={{ color: '#9ca3af', fontSize: '14px' }}>{prediction.memory_count} historical memory records retrieved for client context.</div>
          )}
        </div>

        {/* 3. AI Assumptions */}
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f9fafb', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle style={{ color: '#f59e0b' }} size={20} /> AI ASSUMPTIONS & CONSTRAINTS
          </h3>
          {prediction.assumptions && prediction.assumptions.length > 0 ? (
            <ul style={{ color: '#d1d5db', paddingLeft: '20px', margin: 0, lineHeight: '1.6' }}>
              {prediction.assumptions.map((asm, i) => (
                <li key={i}>{asm}</li>
              ))}
            </ul>
          ) : (
            <div style={{ color: '#9ca3af', fontSize: '14px' }}>Standard channel budget allocation & attribution assumptions.</div>
          )}
        </div>
      </div>
    </div>
  );
};
