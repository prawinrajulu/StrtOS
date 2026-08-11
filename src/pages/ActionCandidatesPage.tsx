import React, { useEffect, useState } from 'react';
import { decisionOptimizationApi } from '../services/decisionOptimizationApi';
import type { ActionCandidate } from '../services/decisionOptimizationApi';
import { Cpu, RefreshCw } from 'lucide-react';

export const ActionCandidatesPage: React.FC = () => {
  const [candidates, setCandidates] = useState<ActionCandidate[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      setLoading(true);
      const res = await decisionOptimizationApi.getCandidates();
      setCandidates(res.candidates || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load candidates');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setLoading(true);
      await decisionOptimizationApi.generateCandidates({});
      await fetchCandidates();
    } catch (err: any) {
      setError(err.message || 'Failed to generate candidates');
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 bg-slate-950 text-slate-100 min-h-screen">
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2 text-cyan-400">
            <Cpu className="h-6 w-6" /> Action Candidates Registry
          </h1>
          <p className="text-sm text-slate-400">
            Allow-listed candidate actions generated from ActionRegistry and enriched via StrtOS intelligence services.
          </p>
        </div>
        <button
          onClick={handleGenerate}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm flex items-center gap-2 transition"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} /> Generate & Enrich Candidates
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-900/30 border border-red-500/50 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden backdrop-blur-md">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-950/80 text-xs uppercase text-slate-400 border-b border-slate-800">
            <tr>
              <th className="p-4">Action Type</th>
              <th className="p-4">Expected Value</th>
              <th className="p-4">ROI</th>
              <th className="p-4">Confidence</th>
              <th className="p-4">Risk Level</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {candidates.map((c) => (
              <tr key={c.id} className="hover:bg-slate-800/40 transition">
                <td className="p-4 font-semibold text-slate-100">{c.action_type}</td>
                <td className="p-4 text-cyan-400 font-mono">${c.expected_value?.toFixed(2) || 'N/A'}</td>
                <td className="p-4 text-emerald-400 font-mono">{c.expected_roi ? `${(c.expected_roi * 100).toFixed(1)}%` : 'N/A'}</td>
                <td className="p-4 font-mono">{c.expected_confidence ? `${(c.expected_confidence * 100).toFixed(0)}%` : 'N/A'}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    c.expected_risk === 'LOW' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
                    c.expected_risk === 'MEDIUM' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                    'bg-red-950 text-red-400 border border-red-800'
                  }`}>
                    {c.expected_risk || 'LOW'}
                  </span>
                </td>
                <td className="p-4">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-950 text-cyan-300 border border-cyan-800">
                    {c.status}
                  </span>
                </td>
              </tr>
            ))}
            {candidates.length === 0 && !loading && (
              <tr>
                <td colSpan={6} className="p-8 text-center text-slate-500">
                  No action candidates found. Click "Generate & Enrich Candidates" to evaluate allow-listed actions.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
