import React, { useEffect, useState } from 'react';
import { decisionOptimizationApi } from '../services/decisionOptimizationApi';
import type { Recommendation } from '../services/decisionOptimizationApi';
import { Compass, ShieldCheck, Activity } from 'lucide-react';

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
      if (rec.decision_id) {
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
    return <div className="p-8 text-center text-cyan-400">Loading Decision Explanation Details...</div>;
  }

  return (
    <div className="p-6 space-y-6 bg-slate-950 text-slate-100 min-h-screen">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold text-cyan-400 flex items-center gap-2">
          <Compass className="h-6 w-6" /> Decision Audit & Causal Explanation
        </h1>
        <p className="text-sm text-slate-400">
          Traceable proof linking verified evidence, historical outcomes, prediction models, and governance policies.
        </p>
      </div>

      {recommendation && (
        <div className="space-y-6">
          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4 backdrop-blur-md">
            <h2 className="text-lg font-bold text-slate-100">Decision Context: {recommendation.decision_id}</h2>
            <p className="text-sm text-slate-300">{recommendation.explanation}</p>
          </div>

          {explanation && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3 backdrop-blur-md">
                <h3 className="text-sm font-semibold text-cyan-400 flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4" /> Current Verified Evidence
                </h3>
                <pre className="text-xs bg-slate-950 p-4 rounded-lg border border-slate-800 text-slate-300 overflow-x-auto">
                  {JSON.stringify(explanation.evidence, null, 2)}
                </pre>
              </div>

              <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3 backdrop-blur-md">
                <h3 className="text-sm font-semibold text-emerald-400 flex items-center gap-2">
                  <Activity className="h-4 w-4" /> Historical Memory Links
                </h3>
                <pre className="text-xs bg-slate-950 p-4 rounded-lg border border-slate-800 text-slate-300 overflow-x-auto">
                  {JSON.stringify(explanation.memory_links, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
