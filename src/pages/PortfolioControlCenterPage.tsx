import React, { useState, useEffect } from 'react';
import {
  Briefcase, RefreshCw, Target, DollarSign, Zap, AlertTriangle, ArrowUpRight, Plus
} from 'lucide-react';
import { portfolioApi } from '../services/portfolioApi';
import type {
  Portfolio, CapitalAllocation, PortfolioInitiative, PortfolioRecommendation
} from '../services/portfolioApi';

const healthColors: Record<string, string> = {
  EXCELLENT: 'text-emerald-300 bg-emerald-950 border-emerald-700',
  HEALTHY: 'text-emerald-400 bg-emerald-950 border-emerald-800',
  WATCH: 'text-amber-400 bg-amber-950 border-amber-800',
  AT_RISK: 'text-rose-400 bg-rose-950 border-rose-800',
  CRITICAL: 'text-red-300 bg-red-950 border-red-700',
};

const actionColors: Record<string, string> = {
  ACCELERATE: 'text-emerald-300 bg-emerald-950 border-emerald-700',
  CONTINUE: 'text-cyan-300 bg-cyan-950 border-cyan-800',
  MAINTAIN: 'text-slate-300 bg-slate-900 border-slate-700',
  DELAY: 'text-amber-300 bg-amber-950 border-amber-800',
  REDUCE: 'text-orange-300 bg-orange-950 border-orange-800',
  STOP: 'text-rose-300 bg-rose-950 border-rose-700',
  REVIEW: 'text-indigo-300 bg-indigo-950 border-indigo-800',
};

interface Props {
  onNavigateToSimulation?: () => void;
  onNavigateToRecommendations?: () => void;
  onSelectPortfolio?: (p: Portfolio) => void;
}

export const PortfolioControlCenterPage: React.FC<Props> = ({
  onNavigateToSimulation,
  onNavigateToRecommendations,
  onSelectPortfolio,
}) => {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selected, setSelected] = useState<Portfolio | null>(null);
  const [initiatives, setInitiatives] = useState<PortfolioInitiative[]>([]);
  const [recommendations, setRecommendations] = useState<PortfolioRecommendation[]>([]);
  const [capitalAlloc, setCapitalAlloc] = useState<CapitalAllocation | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // New initiative form state
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newEV, setNewEV] = useState('150000');
  const [newCost, setNewCost] = useState('45000');
  const [newPriority, setNewPriority] = useState<'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'>('HIGH');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const list = await portfolioApi.listPortfolios();
      setPortfolios(list);
      if (list.length > 0) {
        await selectPortfolioItem(list[0]);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const selectPortfolioItem = async (p: Portfolio) => {
    setSelected(p);
    if (onSelectPortfolio) onSelectPortfolio(p);
    try {
      const [inits, recs, alloc] = await Promise.all([
        portfolioApi.listInitiatives(p.id),
        portfolioApi.listRecommendations(p.id),
        portfolioApi.getCapitalAllocations(p.id),
      ]);
      setInitiatives(inits);
      setRecommendations(recs);
      setCapitalAlloc(alloc);
    } catch (e) {
      console.error(e);
    }
  };

  const handleCreateInitiative = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selected || !newTitle.trim()) return;
    try {
      await portfolioApi.createInitiative(
        {
          title: newTitle,
          description: newDesc,
          priority: newPriority,
          expected_value: parseFloat(newEV) || 0,
          resource_cost: parseFloat(newCost) || 0,
          capital_budget: parseFloat(newCost) || 0,
        },
        selected.id
      );
      setShowAddModal(false);
      setNewTitle('');
      setNewDesc('');
      await selectPortfolioItem(selected);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-cyan-400" />
      </div>
    );
  }

  const score = selected ? Math.round(100 - selected.portfolio_risk_score * 0.4 + selected.confidence_score * 0.3) : 85;

  return (
    <div className="space-y-6 text-slate-100 p-6">
      {/* Header & Overview Stats */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center space-x-3">
            <Briefcase className="w-7 h-7 text-cyan-400" />
            <h1 className="text-2xl font-bold tracking-tight">Portfolio Control Center</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-cyan-950 text-cyan-300 border border-cyan-800">
              STRtOS v2.7.0
            </span>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Autonomous multi-initiative prioritization & resource allocation engine.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          {portfolios.length > 0 && (
            <select
              value={selected?.id || ''}
              onChange={(e) => {
                const found = portfolios.find(p => p.id === e.target.value);
                if (found) selectPortfolioItem(found);
              }}
              className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
            >
              {portfolios.map(p => (
                <option key={p.id} value={p.id}>{p.title}</option>
              ))}
            </select>
          )}
          <button
            onClick={() => onNavigateToSimulation?.()}
            className="flex items-center space-x-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono rounded-lg border border-slate-700 transition-all"
          >
            <Zap className="w-4 h-4 text-amber-400" />
            <span>Scenario Simulator</span>
          </button>
          <button
            onClick={() => onNavigateToRecommendations?.()}
            className="flex items-center space-x-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono rounded-lg border border-slate-700 transition-all"
          >
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            <span>Recommendations ({recommendations.length})</span>
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-semibold text-xs rounded-lg transition-all shadow-lg shadow-cyan-950"
          >
            <Plus className="w-4 h-4" />
            <span>New Initiative</span>
          </button>
        </div>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1">
          <p className="text-slate-400 text-xs font-mono">Strategic Portfolio Score</p>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-cyan-300 font-mono">{score}/100</span>
            {selected && (
              <span className={`px-2 py-0.5 text-xs font-mono rounded border ${healthColors[selected.health]}`}>
                {selected.health}
              </span>
            )}
          </div>
          <p className="text-slate-500 text-[11px]">Aggregated strategic health & risk score</p>
        </div>

        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1">
          <p className="text-slate-400 text-xs font-mono">Expected Portfolio Value</p>
          <div className="text-3xl font-extrabold text-emerald-400 font-mono">
            ${selected ? (selected.expected_value / 1000).toFixed(0) : '0'}K
          </div>
          <p className="text-slate-500 text-[11px]">Weighted return projection</p>
        </div>

        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1">
          <p className="text-slate-400 text-xs font-mono">Capital & Budget Spend</p>
          <div className="text-3xl font-extrabold text-violet-400 font-mono">
            ${selected ? (selected.allocated_budget / 1000).toFixed(0) : '0'}K
            <span className="text-xs text-slate-400 font-normal ml-1">
              / ${selected ? (selected.total_budget / 1000).toFixed(0) : '0'}K
            </span>
          </div>
          <p className="text-slate-500 text-[11px]">Allocated vs Total Available</p>
        </div>

        <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-1">
          <p className="text-slate-400 text-xs font-mono">Active Initiatives</p>
          <div className="text-3xl font-extrabold text-amber-300 font-mono">
            {initiatives.length || selected?.missions.length || 0}
          </div>
          <p className="text-slate-500 text-[11px] truncate">
            {recommendations.filter(r => r.requires_governance).length} require governance review
          </p>
        </div>
      </div>

      {/* Main Grid: Initiatives + Capital Allocation */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Col (2-span): Strategic Initiatives List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold flex items-center space-x-2">
                <Target className="w-5 h-5 text-cyan-400" />
                <span>Strategic Initiatives & Prioritization</span>
              </h2>
              <span className="text-xs font-mono text-slate-400">
                Sorted by Score (0–100)
              </span>
            </div>

            {initiatives.length === 0 ? (
              <div className="p-6 bg-slate-950/60 rounded-lg text-center space-y-2 border border-slate-800">
                <p className="text-slate-400 text-xs">No explicit initiatives created yet.</p>
                <button
                  onClick={() => setShowAddModal(true)}
                  className="px-3 py-1.5 bg-cyan-950 text-cyan-300 border border-cyan-800 hover:bg-cyan-900 text-xs font-mono rounded"
                >
                  + Add First Initiative
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {initiatives.map((init) => (
                  <div
                    key={init.id}
                    className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg hover:border-slate-700 transition-all space-y-2"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-bold text-slate-200">{init.title}</span>
                          <span
                            className={`px-2 py-0.5 text-[10px] font-mono rounded border ${
                              init.priority === 'CRITICAL' ? 'text-red-300 bg-red-950 border-red-800' :
                              init.priority === 'HIGH' ? 'text-rose-300 bg-rose-950 border-rose-800' :
                              'text-amber-300 bg-amber-950 border-amber-800'
                            }`}
                          >
                            {init.priority}
                          </span>
                        </div>
                        {init.description && (
                          <p className="text-xs text-slate-400 mt-1">{init.description}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-mono font-bold text-cyan-400">
                          Score {init.priority_score.toFixed(1)}
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-4 gap-2 pt-2 border-t border-slate-900 text-xs font-mono">
                      <div>
                        <span className="text-slate-500 block text-[10px]">Expected Value</span>
                        <span className="text-emerald-400">${(init.expected_value / 1000).toFixed(0)}K</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[10px]">Success Prob</span>
                        <span className="text-slate-300">{init.success_probability.toFixed(0)}%</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[10px]">Resource Cost</span>
                        <span className="text-violet-300">${(init.resource_cost / 1000).toFixed(0)}K</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[10px]">Status</span>
                        <span className="text-amber-400">{init.status}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Capital Allocation Breakdown */}
          <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3">
            <h2 className="text-base font-semibold flex items-center space-x-2">
              <DollarSign className="w-5 h-5 text-violet-400" />
              <span>Capital & Budget Allocation</span>
            </h2>

            {capitalAlloc && capitalAlloc.data_quality === 'INSUFFICIENT_DATA' ? (
              <div className="p-3 bg-amber-950/30 border border-amber-800/50 rounded-lg text-xs text-amber-300 flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{capitalAlloc.explanation}</span>
              </div>
            ) : capitalAlloc ? (
              <div className="space-y-3">
                <p className="text-xs text-slate-400 font-mono">{capitalAlloc.explanation}</p>
                <div className="space-y-2">
                  {capitalAlloc.allocation_breakdown.map((item) => (
                    <div key={item.id} className="flex items-center justify-between text-xs font-mono p-2.5 bg-slate-950 rounded border border-slate-800">
                      <span className="text-slate-300 truncate max-w-[200px]">{item.title}</span>
                      <span className="text-violet-300">${(item.allocated / 1000).toFixed(0)}K</span>
                      <span className="text-emerald-400">${(item.expected_value / 1000).toFixed(0)}K EV</span>
                      <span className="text-slate-400">{item.pct_of_total_budget.toFixed(1)}% budget</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500">Loading capital allocation details...</p>
            )}
          </div>
        </div>

        {/* Right Col: Top Recommendations & Actions */}
        <div className="space-y-4">
          <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-semibold flex items-center space-x-2">
                <Zap className="w-5 h-5 text-amber-400" />
                <span>System Recommendations</span>
              </h2>
              <button
                onClick={() => onNavigateToRecommendations?.()}
                className="text-xs text-cyan-400 hover:underline flex items-center"
              >
                View All <ArrowUpRight className="w-3 h-3 ml-0.5" />
              </button>
            </div>

            {recommendations.length === 0 ? (
              <p className="text-xs text-slate-500">No active recommendations generated.</p>
            ) : (
              <div className="space-y-3">
                {recommendations.slice(0, 4).map((rec) => (
                  <div key={rec.id} className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-0.5 text-[10px] font-mono rounded border ${actionColors[rec.recommendation_type] || 'text-slate-300 bg-slate-900 border-slate-700'}`}>
                        {rec.recommendation_type}
                      </span>
                      {rec.requires_governance && (
                        <span className="text-[10px] font-mono text-rose-400 bg-rose-950/60 border border-rose-800 px-1.5 py-0.5 rounded">
                          Gov Approval
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-300 font-medium">{rec.title}</p>
                    <p className="text-[11px] text-slate-400 line-clamp-2">{rec.reason}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add Initiative Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-md w-full space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-100">Add Strategic Initiative</h3>
            <form onSubmit={handleCreateInitiative} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Initiative Title</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Market Expansion Phase 2"
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Description</label>
                <textarea
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Initiative objective and scope..."
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1">Expected Value ($)</label>
                  <input
                    type="number"
                    value={newEV}
                    onChange={(e) => setNewEV(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Resource Cost ($)</label>
                  <input
                    type="number"
                    value={newCost}
                    onChange={(e) => setNewCost(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Priority Level</label>
                <select
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value as any)}
                  className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="CRITICAL">CRITICAL</option>
                  <option value="HIGH">HIGH</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="LOW">LOW</option>
                </select>
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-cyan-600 text-slate-950 font-bold rounded hover:bg-cyan-500"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
