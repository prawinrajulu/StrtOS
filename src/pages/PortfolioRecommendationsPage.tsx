import React, { useState, useEffect } from 'react';
import {
  AlertTriangle, RefreshCw, CheckCircle2, ArrowLeft, ShieldAlert
} from 'lucide-react';
import { portfolioApi } from '../services/portfolioApi';
import type { PortfolioRecommendation, Portfolio } from '../services/portfolioApi';

const actionBadgeColors: Record<string, string> = {
  ACCELERATE: 'text-emerald-300 bg-emerald-950 border-emerald-700',
  CONTINUE: 'text-cyan-300 bg-cyan-950 border-cyan-800',
  MAINTAIN: 'text-slate-300 bg-slate-900 border-slate-700',
  DELAY: 'text-amber-300 bg-amber-950 border-amber-800',
  REDUCE: 'text-orange-300 bg-orange-950 border-orange-800',
  STOP: 'text-rose-300 bg-rose-950 border-rose-700',
  REVIEW: 'text-indigo-300 bg-indigo-950 border-indigo-800',
};

const riskBadgeColors: Record<string, string> = {
  CRITICAL: 'text-red-300 bg-red-950 border-red-800',
  HIGH: 'text-rose-300 bg-rose-950 border-rose-800',
  MEDIUM: 'text-amber-300 bg-amber-950 border-amber-800',
  LOW: 'text-emerald-300 bg-emerald-950 border-emerald-800',
};

interface Props {
  onBack?: () => void;
  portfolioId?: string;
}

export const PortfolioRecommendationsPage: React.FC<Props> = ({ onBack, portfolioId }) => {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedId, setSelectedId] = useState<string>(portfolioId || '');
  const [recommendations, setRecommendations] = useState<PortfolioRecommendation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [submittingId, setSubmittingId] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const list = await portfolioApi.listPortfolios();
      setPortfolios(list);
      const target = portfolioId || (list.length > 0 ? list[0].id : '');
      if (target) {
        setSelectedId(target);
        await fetchRecs(target);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const fetchRecs = async (id: string) => {
    try {
      const recs = await portfolioApi.listRecommendations(id);
      setRecommendations(recs);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSubmitGovernance = async (id: string) => {
    setSubmittingId(id);
    try {
      await portfolioApi.submitRecommendationGovernance(id);
      if (selectedId) await fetchRecs(selectedId);
    } catch (e) {
      console.error(e);
    }
    setSubmittingId(null);
  };

  const handlePortfolioChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = e.target.value;
    setSelectedId(id);
    setLoading(true);
    await fetchRecs(id);
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-cyan-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6 text-slate-100 p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center space-x-4">
          {onBack && (
            <button
              onClick={onBack}
              className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 transition-all"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}
          <div>
            <div className="flex items-center space-x-3">
              <AlertTriangle className="w-7 h-7 text-rose-400" />
              <h1 className="text-2xl font-bold tracking-tight">Strategic Portfolio Recommendations</h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-rose-950 text-rose-300 border border-rose-800">
                Action & Governance Layer
              </span>
            </div>
            <p className="text-slate-400 text-xs mt-1">
              Autonomous STOP, DELAY, ACCELERATE, and REDUCE recommendations routed to governance.
            </p>
          </div>
        </div>

        {/* Portfolio Selector */}
        {portfolios.length > 0 && (
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono text-slate-400">Portfolio:</span>
            <select
              value={selectedId}
              onChange={handlePortfolioChange}
              className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
            >
              {portfolios.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Recommendations Cards */}
      {recommendations.length === 0 ? (
        <div className="p-8 bg-slate-900/60 border border-slate-800 rounded-xl text-center space-y-2">
          <p className="text-slate-400 text-sm">No recommendations generated for this portfolio yet.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec) => (
            <div
              key={rec.id}
              className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3 hover:border-slate-700 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <span
                    className={`px-3 py-1 text-xs font-mono font-bold rounded-md border ${
                      actionBadgeColors[rec.recommendation_type] || 'text-slate-300 bg-slate-900 border-slate-700'
                    }`}
                  >
                    {rec.recommendation_type}
                  </span>
                  <span
                    className={`px-2 py-0.5 text-[10px] font-mono rounded border ${
                      riskBadgeColors[rec.risk_level] || 'text-slate-300 bg-slate-900 border-slate-700'
                    }`}
                  >
                    Risk: {rec.risk_level}
                  </span>
                  <span className="text-sm font-semibold text-slate-200">{rec.title}</span>
                </div>

                <div className="flex items-center space-x-2">
                  {rec.requires_governance && rec.status === 'PROPOSED' && (
                    <button
                      onClick={() => handleSubmitGovernance(rec.id)}
                      disabled={submittingId === rec.id}
                      className="px-3 py-1.5 bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-800 text-xs font-mono rounded-lg transition-all flex items-center space-x-1"
                    >
                      {submittingId === rec.id ? (
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <ShieldAlert className="w-3.5 h-3.5" />
                      )}
                      <span>Submit to Governance</span>
                    </button>
                  )}
                  {rec.status === 'SUBMITTED' && (
                    <span className="px-2.5 py-1 bg-indigo-950 text-indigo-300 border border-indigo-800 text-xs font-mono rounded-lg flex items-center space-x-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Pending Governance Review</span>
                    </span>
                  )}
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">{rec.reason}</p>

              {rec.expected_impact && (
                <div className="p-2.5 bg-slate-950 rounded border border-slate-800 text-xs font-mono text-slate-400">
                  <span className="text-slate-500 font-bold">Impact Assessment: </span>
                  {rec.expected_impact}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
