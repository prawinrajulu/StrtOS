import React, { useEffect, useState } from 'react';
import { decisionOptimizationApi } from '../services/decisionOptimizationApi';
import type { Recommendation } from '../services/decisionOptimizationApi';
import { Compass, Activity } from 'lucide-react';

export const DecisionOptimizationDetailsPage: React.FC = () => {
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [explanation, setExplanation] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadDetails();
  }, []);

  const loadDetails = async () => {
    try {
      setLoading(true);
      const rec = await decisionOptimizationApi.getRecommendation();
      setRecommendation(rec);
      if (rec && rec.decision_id) {
        const exp = await decisionOptimizationApi.getExplanation(rec.decision_id);
        setExplanation(exp);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-cyan-400">
        <Activity className="animate-spin mr-2" /> Loading Decision Details...
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100 space-y-8">
      <div className="flex items-center space-x-3">
        <Compass className="w-8 h-8 text-cyan-400" />
        <h1 className="text-3xl font-bold text-slate-100">Decision Optimization & Causal Trace</h1>
      </div>

      {recommendation ? (
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-100">{recommendation.recommended_action?.action_type || 'Recommended Strategy'}</h2>
            <span className="px-3 py-1 rounded bg-emerald-950 text-emerald-300 text-xs font-mono border border-emerald-800">
              Risk: {recommendation.risk_level}
            </span>
          </div>
          <p className="text-sm text-slate-300">{recommendation.explanation}</p>

          {explanation && (
            <div className="mt-4 p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-2">
              <span className="text-xs font-mono text-cyan-400 uppercase">Causal Evidence</span>
              <p className="text-xs text-slate-400">{JSON.stringify(explanation)}</p>
            </div>
          )}
        </div>
      ) : (
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl text-slate-400">
          No recommendation details available.
        </div>
      )}
    </div>
  );
};
