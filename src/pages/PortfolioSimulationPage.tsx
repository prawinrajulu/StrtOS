import React, { useState, useEffect } from 'react';
import {
  Zap, RefreshCw, BarChart2, TrendingUp, ShieldCheck, ArrowLeft
} from 'lucide-react';
import { portfolioApi } from '../services/portfolioApi';
import type {
  Portfolio, DoNothingSimulationResponse, TradeoffResponse
} from '../services/portfolioApi';

interface Props {
  onBack?: () => void;
  portfolioId?: string;
}

export const PortfolioSimulationPage: React.FC<Props> = ({ onBack, portfolioId }) => {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedId, setSelectedId] = useState<string>(portfolioId || '');
  const [doNothingSim, setDoNothingSim] = useState<DoNothingSimulationResponse | null>(null);
  const [tradeoffs, setTradeoffs] = useState<TradeoffResponse | null>(null);

  // Sliders for custom scenario simulation
  const [budgetDelta, setBudgetDelta] = useState<number>(0);
  const [capacityDelta, setCapacityDelta] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [simulating, setSimulating] = useState<boolean>(false);

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
        await runSimulation(target);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const runSimulation = async (id: string) => {
    setSimulating(true);
    try {
      const [dn, tr] = await Promise.all([
        portfolioApi.simulateDoNothing(id),
        portfolioApi.getTradeoffs(id),
      ]);
      setDoNothingSim(dn);
      setTradeoffs(tr);
    } catch (e) {
      console.error(e);
    }
    setSimulating(false);
  };

  const handlePortfolioChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const id = e.target.value;
    setSelectedId(id);
    await runSimulation(id);
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
              <Zap className="w-7 h-7 text-amber-400" />
              <h1 className="text-2xl font-bold tracking-tight">Portfolio Scenario & What-If Simulator</h1>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-amber-950 text-amber-300 border border-amber-800 flex items-center space-x-1">
                <ShieldCheck className="w-3 h-3" />
                <span>Side-Effect Free</span>
              </span>
            </div>
            <p className="text-slate-400 text-xs mt-1">
              Simulate strategic trade-offs, resource constraints, and do-nothing baseline trajectories.
            </p>
          </div>
        </div>

        {/* Portfolio selector */}
        {portfolios.length > 0 && (
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono text-slate-400">Target Portfolio:</span>
            <select
              value={selectedId}
              onChange={handlePortfolioChange}
              className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
            >
              {portfolios.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title} (${(p.expected_value / 1000).toFixed(0)}K EV)
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Do-Nothing vs Optimized vs Current Scenario Comparison Grid */}
      {doNothingSim && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center space-x-2">
              <BarChart2 className="w-5 h-5 text-cyan-400" />
              <span>Comparative Trajectory Simulation</span>
            </h2>
            <span className="text-xs text-cyan-300 italic">{doNothingSim.recommendation}</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Current */}
            <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs font-mono font-bold text-slate-400">CURRENT PORTFOLIO</span>
                <span className="px-2 py-0.5 text-[10px] font-mono bg-slate-800 text-slate-300 rounded border border-slate-700">
                  Baseline
                </span>
              </div>
              <p className="text-2xl font-extrabold text-cyan-300 font-mono">
                ${(doNothingSim.current.expected_value / 1000).toFixed(0)}K EV
              </p>
              <div className="space-y-1 text-xs font-mono">
                <div className="flex justify-between text-slate-400">
                  <span>Expected ROI</span>
                  <span className="text-emerald-400">{doNothingSim.current.expected_roi.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Risk Score</span>
                  <span className="text-amber-400">{doNothingSim.current.risk_score.toFixed(1)}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Strategic Progress</span>
                  <span className="text-slate-300">{doNothingSim.current.strategic_progress_pct.toFixed(0)}%</span>
                </div>
              </div>
              <p className="text-[11px] text-slate-500 pt-2 border-t border-slate-800">
                {doNothingSim.current.summary}
              </p>
            </div>

            {/* Optimized */}
            <div className="p-5 bg-cyan-950/20 border border-cyan-800/80 rounded-xl space-y-3 shadow-lg shadow-cyan-950/40">
              <div className="flex justify-between items-center">
                <span className="text-xs font-mono font-bold text-cyan-300">OPTIMIZED PORTFOLIO</span>
                <span className="px-2 py-0.5 text-[10px] font-mono bg-cyan-900 text-cyan-200 rounded border border-cyan-700">
                  Recommended
                </span>
              </div>
              <p className="text-2xl font-extrabold text-emerald-300 font-mono">
                ${(doNothingSim.optimized.expected_value / 1000).toFixed(0)}K EV
              </p>
              <div className="space-y-1 text-xs font-mono">
                <div className="flex justify-between text-slate-400">
                  <span>Expected ROI</span>
                  <span className="text-emerald-300 font-bold">{doNothingSim.optimized.expected_roi.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Risk Score</span>
                  <span className="text-emerald-400">{doNothingSim.optimized.risk_score.toFixed(1)}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Strategic Progress</span>
                  <span className="text-cyan-300 font-bold">{doNothingSim.optimized.strategic_progress_pct.toFixed(0)}%</span>
                </div>
              </div>
              <p className="text-[11px] text-cyan-200/80 pt-2 border-t border-cyan-900">
                {doNothingSim.optimized.summary}
              </p>
            </div>

            {/* Do-Nothing */}
            <div className="p-5 bg-rose-950/20 border border-rose-900/60 rounded-xl space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs font-mono font-bold text-rose-400">DO NOTHING TRAJECTORY</span>
                <span className="px-2 py-0.5 text-[10px] font-mono bg-rose-950 text-rose-300 rounded border border-rose-800">
                  Degraded
                </span>
              </div>
              <p className="text-2xl font-extrabold text-rose-300 font-mono">
                ${(doNothingSim.do_nothing.expected_value / 1000).toFixed(0)}K EV
              </p>
              <div className="space-y-1 text-xs font-mono">
                <div className="flex justify-between text-slate-400">
                  <span>Expected ROI</span>
                  <span className="text-rose-400">{doNothingSim.do_nothing.expected_roi.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Risk Score</span>
                  <span className="text-red-400 font-bold">{doNothingSim.do_nothing.risk_score.toFixed(1)}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Strategic Progress</span>
                  <span className="text-rose-400">{doNothingSim.do_nothing.strategic_progress_pct.toFixed(0)}%</span>
                </div>
              </div>
              <p className="text-[11px] text-rose-300/80 pt-2 border-t border-rose-950">
                {doNothingSim.do_nothing.summary}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Interactive Controls & Trade-off pair analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: What-if sliders */}
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-base font-semibold flex items-center space-x-2">
            <Zap className="w-5 h-5 text-amber-400" />
            <span>Interactive Parameter Sliders</span>
          </h2>

          <div className="space-y-4 text-xs font-mono">
            <div>
              <div className="flex justify-between text-slate-400 mb-1">
                <span>Budget Adjustment Delta</span>
                <span className={budgetDelta > 0 ? 'text-emerald-400' : budgetDelta < 0 ? 'text-rose-400' : 'text-slate-300'}>
                  {budgetDelta > 0 ? `+${budgetDelta}%` : `${budgetDelta}%`}
                </span>
              </div>
              <input
                type="range"
                min="-50"
                max="50"
                value={budgetDelta}
                onChange={(e) => setBudgetDelta(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
            </div>

            <div>
              <div className="flex justify-between text-slate-400 mb-1">
                <span>Capacity Limit Delta</span>
                <span className={capacityDelta > 0 ? 'text-emerald-400' : capacityDelta < 0 ? 'text-rose-400' : 'text-slate-300'}>
                  {capacityDelta > 0 ? `+${capacityDelta}%` : `${capacityDelta}%`}
                </span>
              </div>
              <input
                type="range"
                min="-50"
                max="50"
                value={capacityDelta}
                onChange={(e) => setCapacityDelta(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
            </div>

            <button
              onClick={() => selectedId && runSimulation(selectedId)}
              disabled={simulating}
              className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold rounded transition-all flex items-center justify-center space-x-2"
            >
              {simulating ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Zap className="w-4 h-4" />
              )}
              <span>Run Parameterized Simulation</span>
            </button>
          </div>
        </div>

        {/* Right (2-span): Trade-off Pair Evaluation */}
        <div className="lg:col-span-2 p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-base font-semibold flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            <span>Strategic Trade-Off Pair Evaluation</span>
          </h2>

          {tradeoffs && tradeoffs.tradeoffs.length > 0 ? (
            <div className="space-y-4">
              {tradeoffs.tradeoffs.map((tr, idx) => (
                <div key={idx} className="p-4 bg-slate-950 border border-slate-800 rounded-lg space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-900 pb-2">
                    <span className="text-xs font-bold text-slate-200">
                      '{tr.option_a_title}' vs '{tr.option_b_title}'
                    </span>
                    <span className="text-xs font-mono text-cyan-300">
                      EV Delta: ${tr.expected_value_delta >= 0 ? '+' : ''}{(tr.expected_value_delta / 1000).toFixed(0)}K
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                    <div className="p-2.5 bg-slate-900/80 rounded border border-slate-800 space-y-1">
                      <p className="text-slate-400 font-bold">Option A: {tr.option_a_title}</p>
                      {tr.prioritize_a_tradeoffs.map((t, i) => (
                        <p key={i} className="text-[11px] text-slate-300">{t}</p>
                      ))}
                    </div>
                    <div className="p-2.5 bg-slate-900/80 rounded border border-slate-800 space-y-1">
                      <p className="text-slate-400 font-bold">Option B: {tr.option_b_title}</p>
                      {tr.prioritize_b_tradeoffs.map((t, i) => (
                        <p key={i} className="text-[11px] text-slate-300">{t}</p>
                      ))}
                    </div>
                  </div>

                  <p className="text-xs text-amber-300 bg-amber-950/30 p-2 rounded border border-amber-900/50">
                    💡 {tr.recommendation}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500">No trade-off pairs found for current portfolio.</p>
          )}
        </div>
      </div>
    </div>
  );
};
