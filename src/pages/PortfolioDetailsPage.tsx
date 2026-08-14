import React, { useState, useEffect } from 'react';
import { RefreshCw, ArrowLeft } from 'lucide-react';
import { portfolioApi } from '../services/portfolioApi';
import type { Portfolio } from '../services/portfolioApi';

interface Props {
  onBack?: () => void;
  portfolioId?: string;
}

export const PortfolioDetailsPage: React.FC<Props> = ({ onBack, portfolioId }) => {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [explanation, setExplanation] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadDetails();
  }, [portfolioId]);

  const loadDetails = async () => {
    setLoading(true);
    try {
      const list = await portfolioApi.listPortfolios();
      const id = portfolioId || (list.length > 0 ? list[0].id : null);
      if (id) {
        const [p, exp] = await Promise.all([
          portfolioApi.getPortfolio(id),
          portfolioApi.getExplanation(id),
        ]);
        setPortfolio(p);
        setExplanation(exp);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-cyan-400" />
      </div>
    );
  }

  if (!portfolio) {
    return (
      <div className="p-8 text-center text-slate-400">
        Portfolio not found.
      </div>
    );
  }

  return (
    <div className="space-y-6 text-slate-100 p-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-5">
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
            <h1 className="text-2xl font-bold tracking-tight">{portfolio.title}</h1>
            <p className="text-slate-400 text-xs mt-1">
              Portfolio Version {portfolio.current_version} • Status: {portfolio.status}
            </p>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1">
          <span className="text-slate-400 text-xs font-mono">Health Status</span>
          <p className="text-xl font-bold text-emerald-400 font-mono">{portfolio.health}</p>
        </div>
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1">
          <span className="text-slate-400 text-xs font-mono">Expected Value</span>
          <p className="text-xl font-bold text-cyan-400 font-mono">${(portfolio.expected_value / 1000).toFixed(0)}K</p>
        </div>
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1">
          <span className="text-slate-400 text-xs font-mono">Risk Score</span>
          <p className="text-xl font-bold text-amber-400 font-mono">{portfolio.portfolio_risk_score.toFixed(1)}</p>
        </div>
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1">
          <span className="text-slate-400 text-xs font-mono">Confidence</span>
          <p className="text-xl font-bold text-violet-400 font-mono">{portfolio.confidence_score.toFixed(0)}%</p>
        </div>
      </div>

      {/* Causal Explanation Chain */}
      {explanation && explanation.mission_explanations && (
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-base font-semibold text-slate-200">Knowledge Graph Causal Explanation</h2>
          <div className="space-y-3">
            {explanation.mission_explanations.map((item: any, idx: number) => (
              <div key={idx} className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-2">
                <div className="flex justify-between text-xs font-mono text-cyan-300">
                  <span>Mission: {item.mission_id}</span>
                  <span>Status: {item.selection_status}</span>
                </div>
                <div className="space-y-1">
                  {item.causal_chain.map((c: string, ci: number) => (
                    <p key={ci} className="text-xs text-slate-400 font-mono">
                      ↳ {c}
                    </p>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
