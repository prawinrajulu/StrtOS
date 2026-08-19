import React, { useEffect, useState } from 'react';
import { decisionOptimizationApi } from '../services/decisionOptimizationApi';
import type { DecisionOverview, Recommendation } from '../services/decisionOptimizationApi';
import { GitFork, Activity, CheckCircle2, RefreshCw } from 'lucide-react';

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
      setError(null);
      const [overviewData, recData] = await Promise.all([
        decisionOptimizationApi.getOverview(),
        decisionOptimizationApi.getRecommendation().catch(() => null),
      ]);
      setOverview(overviewData);
      setRecommendation(recData);
    } catch {
      setError('StrtOS decision engine is temporarily unavailable.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-slate-100 space-y-3">
        <Activity className="w-6 h-6 text-sky-400 animate-spin" />
        <p className="text-xs text-[#92929A] font-mono">Loading business decisions...</p>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <GitFork className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Decisions</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            StrtOS analyzes your business situation and recommends strategic decisions.
          </p>
        </div>
        <button
          onClick={fetchData}
          className="px-3 py-1.5 rounded-lg text-xs bg-[#151518] border border-white/10 hover:border-white/20 text-[#92929A] hover:text-[#F5F5F5] flex items-center space-x-2 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-950/60 border border-rose-800 rounded-xl text-xs text-rose-200">
          {error}
        </div>
      )}

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl">
          <span className="text-xs text-[#92929A] font-mono uppercase">Evaluated Options</span>
          <p className="text-2xl font-bold mt-1 text-sky-400">
            {typeof overview?.total_candidates === 'number' ? overview.total_candidates : 'No current data'}
          </p>
        </div>

        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl">
          <span className="text-xs text-[#92929A] font-mono uppercase">Recommended Decisions</span>
          <p className="text-2xl font-bold mt-1 text-emerald-400">
            {typeof overview?.recommended_actions === 'number' ? overview.recommended_actions : 'No current data'}
          </p>
        </div>

        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl">
          <span className="text-xs text-[#92929A] font-mono uppercase">Expected Outcome Value</span>
          <p className="text-2xl font-bold mt-1 text-indigo-400">
            {typeof overview?.expected_roi === 'number' ? `${(overview.expected_roi * 100).toFixed(0)}%` : 'No current data'}
          </p>
        </div>

        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl">
          <span className="text-xs text-[#92929A] font-mono uppercase">Confidence</span>
          <p className="text-2xl font-bold mt-1 text-amber-400">
            {typeof overview?.decision_confidence === 'number' ? `${(overview.decision_confidence * 100).toFixed(0)}%` : 'No current data'}
          </p>
        </div>
      </div>

      {/* Recommended Decision Section */}
      {recommendation ? (
        <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-xs font-mono uppercase tracking-wider text-sky-400 font-semibold flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Recommended Decision</span>
            </span>
            <span className="text-xs px-2.5 py-0.5 rounded font-mono bg-emerald-950/80 border border-emerald-800 text-emerald-300">
              Risk: {recommendation.risk_level}
            </span>
          </div>

          <div>
            <h2 className="text-xl font-bold text-[#F5F5F5]">{recommendation.recommended_action.action_type}</h2>
            <p className="text-[#92929A] text-xs mt-1 leading-relaxed">{recommendation.explanation}</p>
          </div>

          {/* Breakdown */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-[#151518] p-4 rounded-lg border border-white/5 text-xs">
            <div>
              <span className="text-[#92929A] block font-mono text-[10px]">TOTAL SCORE</span>
              <div className="font-bold text-sky-400 text-sm mt-0.5">{recommendation.score_breakdown.total_score?.toFixed(2)}</div>
            </div>
            <div>
              <span className="text-[#92929A] block font-mono text-[10px]">VALUE IMPACT</span>
              <div className="font-semibold text-[#F5F5F5] text-sm mt-0.5">{recommendation.score_breakdown.value_score?.toFixed(2)}</div>
            </div>
            <div>
              <span className="text-[#92929A] block font-mono text-[10px]">CONFIDENCE</span>
              <div className="font-semibold text-emerald-400 text-sm mt-0.5">{recommendation.score_breakdown.confidence_score?.toFixed(2)}</div>
            </div>
            <div>
              <span className="text-[#92929A] block font-mono text-[10px]">RISK FACTOR</span>
              <div className="font-semibold text-rose-400 text-sm mt-0.5">{recommendation.score_breakdown.risk_penalty?.toFixed(2)}</div>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-8 bg-[#111113] border border-white/[0.06] rounded-xl text-center space-y-2">
          <p className="text-xs text-[#92929A]">No active decision recommendation required at this time.</p>
        </div>
      )}
    </div>
  );
};
