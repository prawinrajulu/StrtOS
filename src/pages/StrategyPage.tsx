import React, { useState, useEffect } from 'react';
import { Compass, Target, ShieldAlert, Layers, Clock, TrendingUp } from 'lucide-react';
import { strategyApi } from '../services/strategyApi';
import type { StrategicObjective, StrategicPlan } from '../services/strategyApi';

export const StrategyPage: React.FC = () => {
  const [objectives, setObjectives] = useState<StrategicObjective[]>([]);
  const [plans, setPlans] = useState<StrategicPlan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [objs, pls] = await Promise.all([
        strategyApi.listObjectives(),
        strategyApi.listPlans()
      ]);
      setObjectives(Array.isArray(objs) ? objs : []);
      setPlans(Array.isArray(pls) ? pls : []);
    } catch (e) {
      console.error('Failed to load strategy data:', e);
    } finally {
      setLoading(false);
    }
  };

  const activePlan = Array.isArray(plans) && plans.length > 0 ? (plans.find(p => p.status === 'ACTIVE') || plans[0]) : null;

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Compass className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl font-bold text-slate-100 tracking-tight">Strategic Intelligence Control Center</h1>
          </div>
          <p className="text-slate-400 mt-1">Autonomous multi-horizon objective planning, risk-bounded scenarios & adaptive strategy execution.</p>
        </div>
        <div className="flex space-x-3">
          <span className="px-3 py-1.5 rounded-full text-xs font-mono bg-cyan-950/80 border border-cyan-800 text-cyan-300 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
            <span>STRTOS v2.0.0 ACTIVE</span>
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono uppercase">Strategic Objectives</span>
            <Target className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-3xl font-extrabold mt-2 text-slate-100">{objectives.length}</p>
          <p className="text-xs text-slate-400 mt-1">Multi-horizon goals tracked</p>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono uppercase">Active Strategy Score</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-3xl font-extrabold mt-2 text-emerald-400">
            {activePlan ? `${activePlan.confidence_score}%` : 'N/A'}
          </p>
          <p className="text-xs text-slate-400 mt-1">Confidence baseline score</p>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono uppercase">Strategy Risk</span>
            <ShieldAlert className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-3xl font-extrabold mt-2 text-amber-400">
            {activePlan ? activePlan.risk_level : 'LOW'}
          </p>
          <p className="text-xs text-slate-400 mt-1">{activePlan ? `Score: ${activePlan.risk_score}` : 'Governance cleared'}</p>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono uppercase">Horizon Timeframe</span>
            <Clock className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-3xl font-extrabold mt-2 text-indigo-400">
            {activePlan && activePlan.horizon ? activePlan.horizon.replace('_', ' ') : '90 DAYS'}
          </p>
          <p className="text-xs text-slate-400 mt-1">Multi-horizon checkpoint</p>
        </div>
      </div>

      {/* Multi-Horizon Visual Timeline */}
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
        <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
          <Layers className="w-5 h-5 text-cyan-400" />
          <span>Strategic Multi-Horizon Timeline</span>
        </h2>
        <div className="grid grid-cols-5 gap-3 pt-2">
          {['30 DAYS', '60 DAYS', '90 DAYS', '180 DAYS', '365 DAYS'].map((hz, idx) => (
            <div key={hz} className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg text-center relative hover:border-cyan-500/50 transition">
              <span className="text-xs font-mono text-cyan-400">{hz}</span>
              <p className="text-sm font-semibold text-slate-200 mt-2">
                {idx === 0 ? 'Foundation' : idx === 1 ? 'Optimization' : idx === 2 ? 'Target Milestone' : idx === 3 ? 'Scale' : 'Dominance'}
              </p>
              <div className="mt-3 flex justify-center">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Objectives Table */}
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
            <Target className="w-5 h-5 text-indigo-400" />
            <span>Active Strategic Objectives</span>
          </h2>
        </div>

        {loading ? (
          <p className="text-slate-400 text-sm">Loading strategic objectives...</p>
        ) : objectives.length === 0 ? (
          <div className="p-8 text-center text-slate-400 border border-dashed border-slate-800 rounded-lg">
            No strategic objectives initialized yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950/80 text-xs font-mono uppercase text-slate-400">
                <tr>
                  <th className="p-3">Title</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">Horizon</th>
                  <th className="p-3">Baseline / Target</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {objectives.map(o => (
                  <tr key={o.id} className="hover:bg-slate-800/40 transition">
                    <td className="p-3 font-semibold text-slate-100">{o.title}</td>
                    <td className="p-3"><span className="px-2 py-1 rounded bg-slate-800 text-xs font-mono text-cyan-300">{o.category}</span></td>
                    <td className="p-3 font-mono text-xs">{o.target_horizon ? o.target_horizon.replace('_', ' ') : ''}</td>
                    <td className="p-3 font-mono">{o.baseline_value} / {o.target_value} {o.unit}</td>
                    <td className="p-3">
                      <span className="px-2 py-1 rounded-full text-xs font-mono bg-emerald-950 border border-emerald-800 text-emerald-300">
                        {o.status}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-emerald-400">{o.confidence_score}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
