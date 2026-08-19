import React, { useState, useEffect } from 'react';
import { Target, PlusCircle, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';
import { memoryApi } from '../services/memoryApi';
import type { MemoryRecord, OutcomeResponse } from '../services/memoryApi';

export const OutcomesPage: React.FC = () => {
  const [outcomes, setOutcomes] = useState<MemoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [metricName, setMetricName] = useState('Monthly Revenue Growth');
  const [predictedValue, setPredictedValue] = useState('15.0');
  const [actualValue, setActualValue] = useState('18.2');
  const [unit, setUnit] = useState('%');
  const [notes, setNotes] = useState('');
  const [result, setResult] = useState<OutcomeResponse | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await memoryApi.getMemories({ memory_type: 'OUTCOME' });
      setOutcomes(res && Array.isArray(res.memories) ? res.memories : []);
    } catch {
      setOutcomes([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const evalRes = await memoryApi.submitOutcome({
        metric_name: metricName,
        predicted_value: parseFloat(predictedValue),
        actual_value: parseFloat(actualValue),
        unit,
        notes: notes || undefined,
      });
      setResult(evalRes);
      setShowForm(false);
      loadData();
    } catch {
      alert('Failed to record outcome.');
    } finally {
      setSubmitting(false);
    }
  };

  const getOutcomeBadge = (status?: string, variance?: number) => {
    switch (status) {
      case 'SUCCESS':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800 flex items-center space-x-1">
            <CheckCircle2 className="w-3 h-3" />
            <span>Success (+{variance || 0}%)</span>
          </span>
        );
      case 'PARTIAL':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-sky-950 text-sky-300 border border-sky-800 flex items-center space-x-1">
            <ShieldCheck className="w-3 h-3" />
            <span>Partial Match</span>
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-950 text-amber-300 border border-amber-800 flex items-center space-x-1">
            <AlertTriangle className="w-3 h-3" />
            <span>Variance Recorded</span>
          </span>
        );
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Target className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Outcomes</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            See what happened after decisions were made.
          </p>
        </div>

        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 rounded-lg text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 flex items-center space-x-2 transition"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Record KPI Outcome</span>
        </button>
      </div>

      {/* Result Alert */}
      {result && (
        <div className="p-4 bg-emerald-950/60 border border-emerald-800 rounded-xl space-y-1 text-xs">
          <h3 className="font-bold text-emerald-400">Outcome Successfully Recorded</h3>
          <p className="text-slate-200">{result.lesson_summary || 'Outcome evaluation complete.'}</p>
        </div>
      )}

      {/* Form Panel */}
      {showForm && (
        <div className="p-6 bg-[#111113] border border-white/10 rounded-xl space-y-4 text-xs">
          <h3 className="font-bold text-[#F5F5F5] text-sm">Submit Actual Business KPI Outcome</h3>

          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div>
              <label className="text-[#92929A] block mb-1">METRIC NAME</label>
              <input
                type="text"
                value={metricName}
                onChange={(e) => setMetricName(e.target.value)}
                required
                className="w-full bg-[#151518] border border-white/10 rounded-lg p-2 text-[#F5F5F5] outline-none"
              />
            </div>

            <div>
              <label className="text-[#92929A] block mb-1">PREDICTED VALUE</label>
              <input
                type="number"
                step="0.01"
                value={predictedValue}
                onChange={(e) => setPredictedValue(e.target.value)}
                required
                className="w-full bg-[#151518] border border-white/10 rounded-lg p-2 text-[#F5F5F5] outline-none"
              />
            </div>

            <div>
              <label className="text-[#92929A] block mb-1">ACTUAL VALUE</label>
              <input
                type="number"
                step="0.01"
                value={actualValue}
                onChange={(e) => setActualValue(e.target.value)}
                required
                className="w-full bg-[#151518] border border-white/10 rounded-lg p-2 text-[#F5F5F5] outline-none"
              />
            </div>

            <div>
              <label className="text-[#92929A] block mb-1">UNIT</label>
              <input
                type="text"
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                className="w-full bg-[#151518] border border-white/10 rounded-lg p-2 text-[#F5F5F5] outline-none"
              />
            </div>

            <div className="md:col-span-4">
              <label className="text-[#92929A] block mb-1">OPERATIONAL CONTEXT / NOTES</label>
              <input
                type="text"
                placeholder="Optional notes or details..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full bg-[#151518] border border-white/10 rounded-lg p-2 text-[#F5F5F5] outline-none"
              />
            </div>

            <div className="md:col-span-4 flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-3 py-2 rounded-lg bg-[#151518] text-[#92929A] border border-white/10 hover:text-[#F5F5F5] transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold transition"
              >
                {submitting ? 'Submitting...' : 'Record Outcome'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Outcomes List */}
      {loading ? (
        <p className="text-xs text-[#92929A]">Loading outcome records...</p>
      ) : outcomes.length === 0 ? (
        <div className="p-8 bg-[#111113] border border-white/[0.06] rounded-xl text-center text-xs text-[#92929A] italic space-y-1">
          <p className="font-semibold text-slate-300">No current data.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {outcomes.map((mem) => {
            const data = mem.structured_data || {};
            return (
              <div
                key={mem.id}
                className="p-4 bg-[#111113] border border-white/[0.06] rounded-xl flex items-center justify-between text-xs space-x-4"
              >
                <div className="space-y-1 flex-1">
                  <div className="flex items-center space-x-2">
                    {getOutcomeBadge(mem.outcome_status, data.percentage_variance || 0)}
                    <span className="text-[10px] font-mono text-[#92929A]">{new Date(mem.created_at).toLocaleDateString()}</span>
                  </div>
                  <h3 className="font-semibold text-[#F5F5F5] text-sm mt-1">{mem.title}</h3>
                  <p className="text-[#92929A]">{mem.content}</p>
                </div>

                <div className="flex items-center space-x-4 shrink-0 font-mono text-right">
                  <div>
                    <span className="text-[10px] text-[#92929A] block">PREDICTED</span>
                    <span className="text-sky-300 font-bold text-sm">{data.predicted_value || '0'}{data.unit || ''}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-[#92929A] block">ACTUAL</span>
                    <span className="text-emerald-400 font-bold text-sm">{data.actual_value || '0'}{data.unit || ''}</span>
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
