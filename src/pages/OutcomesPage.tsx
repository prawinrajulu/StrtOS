import React, { useEffect, useState } from 'react';
import { Target, PlusCircle, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { memoryApi } from '../services/memoryApi';
import type { MemoryRecord, OutcomeResponse } from '../services/memoryApi';

export const OutcomesPage: React.FC = () => {
  const [outcomes, setOutcomes] = useState<MemoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  // Form State
  const [metricName, setMetricName] = useState('ROAS');
  const [predictedValue, setPredictedValue] = useState('4.2');
  const [actualValue, setActualValue] = useState('2.8');
  const [unit, setUnit] = useState('x');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<OutcomeResponse | null>(null);

  const fetchOutcomes = async () => {
    setLoading(true);
    const data = await memoryApi.getMemories({ memory_type: 'OUTCOME' });
    setOutcomes(data.memories);
    setLoading(false);
  };

  useEffect(() => {
    fetchOutcomes();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await memoryApi.submitOutcome({
        metric_name: metricName,
        predicted_value: parseFloat(predictedValue),
        actual_value: parseFloat(actualValue),
        unit: unit,
        notes: notes
      });
      setResult(res);
      fetchOutcomes();
      setShowForm(false);
    } catch (err: any) {
      alert(err.message || 'Outcome submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  const getOutcomeBadge = (status: string, pctVar: number) => {
    switch (status) {
      case 'SUCCESS':
        return <span style={{ color: '#10b981', fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px' }}><CheckCircle2 size={14} /> SUCCESS ({pctVar}% var)</span>;
      case 'PARTIAL':
        return <span style={{ color: '#f59e0b', fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px' }}><AlertTriangle size={14} /> PARTIAL ({pctVar}% var)</span>;
      case 'FAILED':
        return <span style={{ color: '#ef4444', fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px' }}><XCircle size={14} /> FAILED ({pctVar}% var)</span>;
      default:
        return null;
    }
  };

  return (
    <div style={{ padding: '28px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Target style={{ color: '#10b981' }} size={28} /> Measured Outcome Tracking & Variance Engine
          </h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>
            Compare AI predictions against actual business KPI performance to extract deterministic learned signals
          </p>
        </div>

        <button
          onClick={() => setShowForm(!showForm)}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 20px', backgroundColor: '#6366f1', color: '#fff', border: 'none', borderRadius: '10px', fontWeight: '700', cursor: 'pointer' }}
        >
          <PlusCircle size={18} /> Submit Actual Outcome
        </button>
      </div>

      {/* Result Alert */}
      {result && (
        <div style={{ backgroundColor: '#111827', border: '1px solid #10b981', borderRadius: '14px', padding: '20px', marginBottom: '24px' }}>
          <h3 style={{ color: '#10b981', fontSize: '16px', fontWeight: '700', margin: '0 0 8px 0' }}>Outcome Successfully Recorded!</h3>
          <p style={{ color: '#d1d5db', fontSize: '14px', margin: '0 0 8px 0' }}>{result.lesson_summary}</p>
          <div style={{ fontSize: '12px', color: '#9ca3af' }}>
            Absolute Variance: {result.absolute_variance}{result.unit} | Percentage Variance: {result.percentage_variance}% | Status: {result.outcome_status}
          </div>
        </div>
      )}

      {/* Submission Form Modal / Panel */}
      {showForm && (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '24px', marginBottom: '28px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f9fafb', marginBottom: '16px' }}>Submit Actual Business KPI Outcome</h3>

          <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '6px' }}>METRIC NAME</label>
              <input
                type="text"
                value={metricName}
                onChange={(e) => setMetricName(e.target.value)}
                required
                style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px', color: '#f9fafb', fontSize: '14px' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '6px' }}>PREDICTED VALUE</label>
              <input
                type="number"
                step="0.01"
                value={predictedValue}
                onChange={(e) => setPredictedValue(e.target.value)}
                required
                style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px', color: '#f9fafb', fontSize: '14px' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '6px' }}>ACTUAL VALUE</label>
              <input
                type="number"
                step="0.01"
                value={actualValue}
                onChange={(e) => setActualValue(e.target.value)}
                required
                style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px', color: '#f9fafb', fontSize: '14px' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '6px' }}>UNIT</label>
              <input
                type="text"
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px', color: '#f9fafb', fontSize: '14px' }}
              />
            </div>

            <div style={{ gridColumn: '1 / -1' }}>
              <label style={{ display: 'block', fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '6px' }}>NOTES / CONTEXT</label>
              <input
                type="text"
                placeholder="Optional operational context or channel details..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px', color: '#f9fafb', fontSize: '14px' }}
              />
            </div>

            <div style={{ gridColumn: '1 / -1', display: 'flex', gap: '12px' }}>
              <button
                type="submit"
                disabled={submitting}
                style={{ padding: '12px 24px', backgroundColor: '#10b981', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer' }}
              >
                Evaluate & Record Outcome
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                style={{ padding: '12px 20px', backgroundColor: '#374151', color: '#9ca3af', border: 'none', borderRadius: '8px', cursor: 'pointer' }}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Outcomes List */}
      {loading ? (
        <div style={{ color: '#9ca3af', textAlign: 'center', padding: '40px' }}>Loading outcome tracking records...</div>
      ) : outcomes.length === 0 ? (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '40px', textAlign: 'center', color: '#9ca3af' }}>
          No actual outcomes submitted yet. Submit your first KPI result above!
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {outcomes.map((mem) => {
            const data = mem.structured_data || {};
            return (
              <div
                key={mem.id}
                style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}
              >
                <div style={{ flex: 1, minWidth: '280px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                    {getOutcomeBadge(mem.outcome_status, data.percentage_variance || 0)}
                    <span style={{ fontSize: '12px', color: '#6b7280' }}>{new Date(mem.created_at).toLocaleDateString()}</span>
                  </div>
                  <h3 style={{ fontSize: '17px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0' }}>{mem.title}</h3>
                  <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>{mem.content}</p>
                </div>

                <div style={{ display: 'flex', gap: '20px' }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '11px', color: '#6b7280', fontWeight: '600' }}>PREDICTED</div>
                    <div style={{ fontSize: '18px', fontWeight: '700', color: '#60a5fa' }}>{data.predicted_value || '0'}{data.unit || ''}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '11px', color: '#6b7280', fontWeight: '600' }}>ACTUAL</div>
                    <div style={{ fontSize: '18px', fontWeight: '700', color: '#10b981' }}>{data.actual_value || '0'}{data.unit || ''}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
