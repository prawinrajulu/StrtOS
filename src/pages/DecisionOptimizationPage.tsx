import React, { useEffect, useState } from 'react';
import { decisionOptimizationApi } from '../services/decisionOptimizationApi';
import type { DecisionOverview, Recommendation } from '../services/decisionOptimizationApi';
import { Compass, Cpu, Zap, Activity, CheckCircle } from 'lucide-react';

export const DecisionOptimizationPage: React.FC = () => {
  const [overview, setOverview] = useState<DecisionOverview | null>(null);
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [overviewData, recData] = await Promise.all([
        decisionOptimizationApi.getOverview(),
        decisionOptimizationApi.getRecommendation().catch(() => null),
      ]);
      setOverview(overviewData);
      setRecommendation(recData);
    } catch (err: any) {
      setError(err.message || 'Failed to load Decision Optimization data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-cyan-400">
        <Activity className="animate-spin mr-2" /> Loading Decision Optimization Dashboard...
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-slate-950 text-slate-100 min-h-screen">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2 text-cyan-400">
            <Compass className="h-6 w-6" /> Causal Decision Optimization & Action Planning
          </h1>
          <p className="text-sm text-slate-400">
            Predictive action optimization, deterministic risk scoring, and governance-guarded planning.
          </p>
        </div>
        <button
          onClick={fetchData}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm flex items-center gap-2 transition"
        >
          <Zap className="h-4 w-4" /> Re-Optimize Now
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-900/30 border border-red-500/50 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-md">
          <div className="text-xs text-slate-400 flex items-center justify-between">
            <span>Action Candidates</span>
            <Cpu className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">{overview?.total_candidates || 0}</div>
        </div>

        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-md">
          <div className="text-xs text-slate-400 flex items-center justify-between">
            <span>Recommended Actions</span>
            <CheckCircle className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">{overview?.recommended_actions || 0}</div>
        </div>

        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-md">
          <div className="text-xs text-slate-400 flex items-center justify-between">
            <span>Expected ROI</span>
            <Activity className="h-4 w-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">
            {((overview?.expected_roi || 0) * 100).toFixed(1)}%
          </div>
        </div>

        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-md">
          <div className="text-xs text-slate-400 flex items-center justify-between">
            <span>Decision Confidence</span>
            <Compass className="h-4 w-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">
            {((overview?.decision_confidence || 0) * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Top Recommendation Section */}
      {recommendation && (
        <div className="p-6 bg-slate-900/80 border border-cyan-500/30 rounded-xl backdrop-blur-md space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-xs font-semibold px-3 py-1 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 rounded-full">
              OPTIMAL RECOMMENDATION
            </span>
            <span className={`text-xs px-2.5 py-1 rounded font-semibold ${
              recommendation.risk_level === 'LOW' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400 border border-amber-800'
            }`}>
              RISK: {recommendation.risk_level}
            </span>
          </div>

          <div>
            <h2 className="text-xl font-bold text-slate-100">{recommendation.recommended_action.action_type}</h2>
            <p className="text-slate-400 text-sm mt-1">{recommendation.explanation}</p>
          </div>

          {/* Score breakdown */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-950/60 p-4 rounded-lg border border-slate-800 text-xs">
            <div>
              <span className="text-slate-500">Total Score:</span>
              <div className="font-bold text-cyan-400 text-base">{recommendation.score_breakdown.total_score?.toFixed(3)}</div>
            </div>
            <div>
              <span className="text-slate-500">Value Score:</span>
              <div className="font-semibold text-slate-200">{recommendation.score_breakdown.value_score?.toFixed(3)}</div>
            </div>
            <div>
              <span className="text-slate-500">Confidence Score:</span>
              <div className="font-semibold text-slate-200">{recommendation.score_breakdown.confidence_score?.toFixed(3)}</div>
            </div>
            <div>
              <span className="text-slate-500">Risk Penalty:</span>
              <div className="font-semibold text-red-400">{recommendation.score_breakdown.risk_penalty?.toFixed(3)}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
