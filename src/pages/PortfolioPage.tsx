import React, { useState, useEffect } from 'react';
import {
  Briefcase, RefreshCw, BarChart2, TrendingUp,
  CheckCircle, Target, Layers, DollarSign, Zap
} from 'lucide-react';
import { portfolioApi } from '../services/portfolioApi';
import type {
  Portfolio, PortfolioOverview, OptimizationResponse, SimulationResponse
} from '../services/portfolioApi';

const healthColors: Record<string, string> = {
  EXCELLENT: 'text-emerald-300 bg-emerald-950 border-emerald-700',
  HEALTHY: 'text-emerald-400 bg-emerald-950 border-emerald-800',
  WATCH: 'text-amber-400 bg-amber-950 border-amber-800',
  AT_RISK: 'text-rose-400 bg-rose-950 border-rose-800',
  CRITICAL: 'text-red-300 bg-red-950 border-red-700',
};

const statusColors: Record<string, string> = {
  ACTIVE: 'text-emerald-400 bg-emerald-950 border-emerald-800',
  DRAFT: 'text-slate-400 bg-slate-900 border-slate-700',
  REBALANCING: 'text-violet-400 bg-violet-950 border-violet-800',
  AWAITING_APPROVAL: 'text-indigo-400 bg-indigo-950 border-indigo-800',
  AT_RISK: 'text-rose-400 bg-rose-950 border-rose-800',
  COMPLETED: 'text-emerald-300 bg-emerald-950 border-emerald-700',
};

const missionStatusColors: Record<string, string> = {
  SELECTED: 'text-emerald-400 bg-emerald-950 border-emerald-800',
  DEFERRED: 'text-amber-400 bg-amber-950 border-amber-800',
  PAUSED: 'text-slate-400 bg-slate-900 border-slate-700',
};

const priorityColors: Record<string, string> = {
  CRITICAL: 'text-red-300 bg-red-950 border-red-700',
  HIGH: 'text-rose-400 bg-rose-950 border-rose-800',
  MEDIUM: 'text-amber-400 bg-amber-950 border-amber-800',
  LOW: 'text-slate-400 bg-slate-900 border-slate-700',
};

const ResourceBar: React.FC<{ label: string; pct: number; unit?: string }> = ({ label, pct, unit }) => {
  const color = pct >= 90 ? 'bg-rose-500' : pct >= 80 ? 'bg-amber-500' : 'bg-cyan-500';
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs font-mono text-slate-400">
        <span>{label}</span>
        <span className={pct >= 90 ? 'text-rose-400' : pct >= 80 ? 'text-amber-400' : 'text-slate-300'}>
          {pct.toFixed(1)}% {unit}
        </span>
      </div>
      <div className="w-full bg-slate-800 rounded-full h-1.5">
        <div className={`${color} h-1.5 rounded-full transition-all`} style={{ width: `${Math.min(100, pct)}%` }} />
      </div>
    </div>
  );
};

export const PortfolioPage: React.FC = () => {
  const [overview, setOverview] = useState<PortfolioOverview | null>(null);
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selected, setSelected] = useState<Portfolio | null>(null);
  const [optimization, setOptimization] = useState<OptimizationResponse | null>(null);
  const [simulation, setSimulation] = useState<SimulationResponse | null>(null);
  const [activeScenario, setActiveScenario] = useState<'CONSERVATIVE' | 'BALANCED' | 'AGGRESSIVE'>('BALANCED');
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [ov, list] = await Promise.all([portfolioApi.getOverview(), portfolioApi.listPortfolios()]);
      setOverview(ov);
      setPortfolios(list);
      if (list.length > 0) await selectPortfolio(list[0]);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const selectPortfolio = async (p: Portfolio) => {
    setSelected(p);
    try {
      const sim = await portfolioApi.simulatePortfolio(p.id);
      setSimulation(sim);
    } catch {}
  };

  const handleOptimize = async (scenario: 'CONSERVATIVE' | 'BALANCED' | 'AGGRESSIVE') => {
    if (!selected) return;
    setOptimizing(true);
    setActiveScenario(scenario);
    try {
      const result = await portfolioApi.optimizePortfolio(selected.id, scenario);
      setOptimization(result);
      await loadData();
    } catch (e) { console.error(e); }
    setOptimizing(false);
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64 text-cyan-400">
      <RefreshCw className="animate-spin mr-2" /> Loading Portfolio Command Center...
    </div>
  );

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Briefcase className="w-8 h-8 text-violet-400" />
            <h1 className="text-3xl font-bold tracking-tight">Portfolio Command Center</h1>
          </div>
          <p className="text-slate-400 mt-1">
            Autonomous Strategic Portfolio Orchestration — maximize value across constrained resources.
          </p>
        </div>
        <div className="flex space-x-3">
          <button onClick={loadData} className="px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 flex items-center space-x-2 transition">
            <RefreshCw className="w-3.5 h-3.5" /><span>SYNC</span>
          </button>
          <span className="px-3 py-1.5 rounded-full text-xs font-mono bg-violet-950/80 border border-violet-800 text-violet-300 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
            <span>STRTOS v2.5.0 PORTFOLIO ENGINE</span>
          </span>
        </div>
      </div>

      {/* Overview Cards */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Total Portfolios', value: overview.total_portfolios, icon: <Briefcase className="w-5 h-5 text-violet-400" /> },
            { label: 'Expected Value', value: `$${(overview.total_expected_value / 1000).toFixed(0)}K`, icon: <TrendingUp className="w-5 h-5 text-emerald-400" /> },
            { label: 'Missions Selected', value: overview.missions_selected, icon: <CheckCircle className="w-5 h-5 text-cyan-400" /> },
            { label: 'Missions Deferred', value: overview.missions_deferred, icon: <Layers className="w-5 h-5 text-amber-400" /> },
          ].map((card, i) => (
            <div key={i} className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl">
              <div className="flex justify-between items-start">
                {card.icon}
                <span className="text-2xl font-bold font-mono text-slate-100">{card.value}</span>
              </div>
              <p className="text-xs text-slate-400 mt-2">{card.label}</p>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Portfolio List */}
        <div className="space-y-3">
          <h2 className="text-sm font-mono font-semibold text-slate-400 uppercase tracking-wider">Active Portfolios</h2>
          {portfolios.map(p => (
            <div
              key={p.id}
              onClick={() => selectPortfolio(p)}
              className={`p-4 rounded-xl border cursor-pointer transition ${
                selected?.id === p.id ? 'bg-violet-950/40 border-violet-500' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className={`px-2 py-0.5 rounded text-xs font-mono border ${statusColors[p.status] || 'text-slate-400 bg-slate-900 border-slate-700'}`}>
                  {p.status}
                </span>
                <span className={`px-2 py-0.5 rounded text-xs font-mono border ${healthColors[p.health]}`}>
                  {p.health}
                </span>
              </div>
              <h3 className="text-sm font-bold text-slate-100 truncate">{p.title}</h3>
              <div className="mt-2 text-xs font-mono text-slate-400 space-y-1">
                <div className="flex justify-between">
                  <span>Expected Value</span>
                  <span className="text-emerald-300">${(p.expected_value / 1000).toFixed(0)}K</span>
                </div>
                <div className="flex justify-between">
                  <span>Risk</span>
                  <span className={p.portfolio_risk_score >= 70 ? 'text-rose-400' : 'text-slate-300'}>
                    {p.portfolio_risk_score.toFixed(0)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Version</span>
                  <span className="text-violet-300">{p.current_version}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Selected Portfolio Detail */}
        {selected && (
          <div className="md:col-span-2 space-y-5">
            {/* Resource Utilization */}
            <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
              <h2 className="text-base font-semibold flex items-center space-x-2">
                <DollarSign className="w-5 h-5 text-emerald-400" /><span>Resource Utilization</span>
              </h2>
              {selected.resources.length === 0 ? (
                <p className="text-slate-500 text-xs">No resources configured.</p>
              ) : (
                selected.resources.map(r => (
                  <ResourceBar
                    key={r.id}
                    label={`${r.resource_type} (${r.period})`}
                    pct={r.utilization_pct}
                    unit={r.unit}
                  />
                ))
              )}
              <div className="grid grid-cols-3 gap-2 mt-2 text-xs font-mono">
                <div className="p-2 bg-slate-950 rounded border border-slate-800 text-center">
                  <span className="text-slate-400 block">Budget</span>
                  <span className="text-slate-200 font-bold">${(selected.total_budget / 1000).toFixed(0)}K</span>
                </div>
                <div className="p-2 bg-slate-950 rounded border border-slate-800 text-center">
                  <span className="text-slate-400 block">Allocated</span>
                  <span className="text-cyan-300 font-bold">${(selected.allocated_budget / 1000).toFixed(0)}K</span>
                </div>
                <div className="p-2 bg-slate-950 rounded border border-slate-800 text-center">
                  <span className="text-slate-400 block">Missions</span>
                  <span className="text-violet-300 font-bold">{selected.missions.length}</span>
                </div>
              </div>
            </div>

            {/* Scenario Optimizer */}
            <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
              <h2 className="text-base font-semibold flex items-center space-x-2">
                <Zap className="w-5 h-5 text-violet-400" /><span>Portfolio Optimizer</span>
              </h2>
              <div className="flex space-x-2">
                {(['CONSERVATIVE', 'BALANCED', 'AGGRESSIVE'] as const).map(s => (
                  <button
                    key={s}
                    onClick={() => handleOptimize(s)}
                    disabled={optimizing}
                    className={`flex-1 py-1.5 rounded-lg text-xs font-mono border transition ${
                      activeScenario === s && optimization
                        ? s === 'AGGRESSIVE' ? 'bg-rose-900 border-rose-600 text-rose-200'
                          : s === 'CONSERVATIVE' ? 'bg-slate-800 border-slate-600 text-slate-200'
                          : 'bg-violet-900 border-violet-600 text-violet-200'
                        : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-600'
                    }`}
                  >
                    {optimizing && activeScenario === s ? <RefreshCw className="w-3 h-3 animate-spin inline mr-1" /> : null}
                    {s}
                  </button>
                ))}
              </div>

              {/* Simulation results */}
              {simulation && (
                <div className="grid grid-cols-3 gap-2 text-xs font-mono">
                  {simulation.scenarios.map(sc => (
                    <div
                      key={sc.scenario_type}
                      className={`p-3 rounded-lg border ${
                        sc.scenario_type === 'CONSERVATIVE' ? 'border-slate-700 bg-slate-950' :
                        sc.scenario_type === 'BALANCED' ? 'border-violet-800 bg-violet-950/30' :
                        'border-rose-800 bg-rose-950/20'
                      }`}
                    >
                      <p className="text-slate-400 font-bold mb-2">{sc.scenario_type}</p>
                      <p className="text-emerald-300">${(sc.expected_value / 1000).toFixed(0)}K EV</p>
                      <p className="text-slate-300">{sc.selected_mission_count}M selected</p>
                      <p className="text-amber-400">Risk {sc.risk_score.toFixed(0)}</p>
                      <p className="text-slate-400">{sc.confidence.toFixed(0)}% confidence</p>
                    </div>
                  ))}
                </div>
              )}
              {simulation && (
                <p className="text-xs text-cyan-300 italic">{simulation.recommendation}</p>
              )}

              {/* Optimization result */}
              {optimization && (
                <div className="space-y-2">
                  <p className="text-xs font-mono text-slate-400">{optimization.explanation}</p>
                  <div className="space-y-1">
                    {[...optimization.selected_missions, ...optimization.deferred_missions].map(m => (
                      <div key={m.mission_id} className="flex items-center space-x-2 text-xs p-2 bg-slate-950 rounded border border-slate-800">
                        <span className={`px-1.5 py-0.5 rounded font-mono border ${missionStatusColors[m.status]}`}>{m.status}</span>
                        <span className="text-slate-300 flex-1 truncate">{m.title || m.mission_id.slice(0, 8)}</span>
                        <span className="text-emerald-300 font-mono">${(m.expected_value / 1000).toFixed(0)}K</span>
                        <span className="text-slate-400 font-mono">VCR {m.value_cost_ratio.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Mission Priority Panel */}
            <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3">
              <h2 className="text-base font-semibold flex items-center space-x-2">
                <Target className="w-5 h-5 text-cyan-400" /><span>Mission Portfolio</span>
              </h2>
              {selected.missions.length === 0 ? (
                <p className="text-slate-500 text-xs">No missions in portfolio.</p>
              ) : (
                selected.missions.map(m => (
                  <div key={m.id} className="flex items-center space-x-3 p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
                    <span className={`px-2 py-0.5 rounded text-xs font-mono border ${priorityColors[m.priority]}`}>{m.priority}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-slate-400 font-mono truncate">{m.mission_id.slice(0, 16)}...</p>
                      <p className="text-xs text-slate-500 truncate">{m.selection_reason}</p>
                    </div>
                    <div className="text-right text-xs font-mono space-y-0.5">
                      <p className="text-emerald-300">${(m.expected_value / 1000).toFixed(0)}K</p>
                      <p className="text-slate-400">{m.success_probability.toFixed(0)}% prob</p>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-xs font-mono border ${missionStatusColors[m.selection_status]}`}>
                      {m.selection_status}
                    </span>
                  </div>
                ))
              )}
            </div>

            {/* Version History */}
            <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-2">
              <h2 className="text-base font-semibold flex items-center space-x-2">
                <BarChart2 className="w-5 h-5 text-indigo-400" /><span>Version History</span>
              </h2>
              {selected.versions.map(v => (
                <div key={v.id} className="flex items-center justify-between text-xs font-mono p-2 bg-slate-950 rounded border border-slate-800">
                  <span className="text-violet-300">{v.version}</span>
                  {v.parent_version && <span className="text-slate-500">← {v.parent_version}</span>}
                  <span className="text-slate-400 truncate max-w-48">{v.reason || 'Initial'}</span>
                  <span className={v.risk_change > 0 ? 'text-rose-400' : 'text-emerald-400'}>
                    {v.risk_change > 0 ? '+' : ''}{v.risk_change.toFixed(1)} risk
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
