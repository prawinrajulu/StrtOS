import React, { useEffect, useState } from 'react';
import { Compass, Target, TrendingUp, ShieldAlert, Clock, Layers } from 'lucide-react';
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
    } catch {
      setObjectives([]);
      setPlans([]);
    } finally {
      setLoading(false);
    }
  };

  const activePlan = Array.isArray(plans) && plans.length > 0 ? (plans.find(p => p.status === 'ACTIVE') || plans[0]) : null;

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Compass className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Strategy</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            Track where your business is heading.
          </p>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#92929A] font-mono uppercase">Strategic Objectives</span>
            <Target className="w-4 h-4 text-sky-400" />
          </div>
          <p className="text-2xl font-bold text-[#F5F5F5] mt-1">{objectives.length}</p>
          <p className="text-[10px] text-[#92929A]">Tracked business objectives</p>
        </div>

        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#92929A] font-mono uppercase">Strategy Confidence</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-emerald-400 mt-1">
            {activePlan && typeof activePlan.confidence_score === 'number' ? `${activePlan.confidence_score}%` : 'No current data'}
          </p>
          <p className="text-[10px] text-[#92929A]">Baseline confidence score</p>
        </div>

        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#92929A] font-mono uppercase">Strategy Risk</span>
            <ShieldAlert className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold text-amber-400 mt-1">
            {activePlan ? activePlan.risk_level : 'No current data'}
          </p>
          <p className="text-[10px] text-[#92929A]">{activePlan ? `Score: ${activePlan.risk_score}` : 'Risk evaluation'}</p>
        </div>

        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#92929A] font-mono uppercase">Time Horizon</span>
            <Clock className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-indigo-400 mt-1">
            {activePlan && activePlan.horizon ? activePlan.horizon.replace('_', ' ') : '90 DAYS'}
          </p>
          <p className="text-[10px] text-[#92929A]">Target timeframe</p>
        </div>
      </div>

      {/* Multi-Horizon Timeline */}
      <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
        <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
          <Layers className="w-4 h-4 text-sky-400" />
          <span>Strategic Multi-Horizon Timeline</span>
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 pt-1">
          {['30 DAYS', '60 DAYS', '90 DAYS', '180 DAYS', '365 DAYS'].map((hz, idx) => (
            <div key={hz} className="p-3 bg-[#151518] border border-white/5 rounded-lg text-center space-y-1 text-xs">
              <span className="text-[10px] font-mono text-sky-400">{hz}</span>
              <p className="font-semibold text-[#F5F5F5]">
                {idx === 0 ? 'Foundation' : idx === 1 ? 'Optimization' : idx === 2 ? 'Target Milestone' : idx === 3 ? 'Scale' : 'Dominance'}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Objectives List */}
      <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
        <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
          <Target className="w-4 h-4 text-indigo-400" />
          <span>Strategic Objectives ({objectives.length})</span>
        </h2>

        {loading ? (
          <p className="text-xs text-[#92929A]">Loading strategic information...</p>
        ) : objectives.length === 0 ? (
          <p className="text-xs text-[#92929A] italic">No current data.</p>
        ) : (
          <div className="space-y-3">
            {objectives.map((o) => (
              <div key={o.id} className="p-4 bg-[#151518] border border-white/5 rounded-lg flex items-center justify-between text-xs">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-sky-950 text-sky-300 border border-sky-800">{o.category}</span>
                    <span className="text-[10px] font-mono text-[#92929A]">{o.target_horizon ? o.target_horizon.replace('_', ' ') : ''}</span>
                  </div>
                  <h3 className="font-semibold text-[#F5F5F5] text-sm mt-1">{o.title}</h3>
                  <p className="text-[#92929A]">
                    Target: <span className="font-mono text-[#F5F5F5]">{o.baseline_value} $\rightarrow$ {o.target_value} {o.unit}</span>
                  </p>
                </div>
                <div className="text-right space-y-1">
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-950 border border-emerald-800 text-emerald-300">
                    {o.status}
                  </span>
                  <p className="text-emerald-400 font-mono font-semibold">{o.confidence_score}% Confidence</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
