import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, Zap, ShieldAlert, CheckCircle, RefreshCw } from 'lucide-react';
import { businessStateApi } from '../services/businessStateApi';
import type {
  StateSnapshot,
  BusinessAlert,
  Opportunity,
  Threat
} from '../services/businessStateApi';

export const BusinessStatePage: React.FC = () => {
  const [snapshot, setSnapshot] = useState<StateSnapshot | null>(null);
  const [activeAlerts, setActiveAlerts] = useState<BusinessAlert[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [threats, setThreats] = useState<Threat[]>([]);
  const [, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [snaps, alerts, opps, thr] = await Promise.all([
        businessStateApi.listSnapshots(),
        businessStateApi.listAlerts(),
        businessStateApi.listOpportunities(),
        businessStateApi.listThreats()
      ]);

      setSnapshot(snaps && snaps.length > 0 ? snaps[0] : null);
      setActiveAlerts(alerts || []);
      setOpportunities(opps || []);
      setThreats(thr || []);
    } catch {
      setError('Business state engine is temporarily unavailable.');
    } finally {
      setLoading(false);
    }
  };

  const handleResolveAlert = async (id: string) => {
    try {
      await businessStateApi.resolveAlert(id);
      setActiveAlerts((prev) => prev.filter((a) => a.id !== id));
    } catch {
      setError('Failed to resolve alert.');
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Activity className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Business State</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            Understand what is changing across your business.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button 
            onClick={loadData}
            className="px-3 py-1.5 rounded-lg text-xs font-mono bg-[#151518] border border-white/10 hover:border-white/20 text-[#92929A] hover:text-[#F5F5F5] flex items-center space-x-2 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Sync State</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-950/60 border border-rose-800 rounded-xl flex items-center space-x-3 text-rose-200 text-xs">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* KPI Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#92929A] font-mono uppercase">Business Health Score</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-emerald-400 mt-1">
            {snapshot && typeof snapshot.health_score === 'number' ? `${snapshot.health_score}%` : 'No current data'}
          </p>
          <p className="text-[10px] text-[#92929A]">Status: {snapshot?.health_status || 'No current data'}</p>
        </div>

        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#92929A] font-mono uppercase">Early Warnings</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold text-amber-400 mt-1">{activeAlerts.length}</p>
          <p className="text-[10px] text-[#92929A]">Active strategic warnings</p>
        </div>

        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#92929A] font-mono uppercase">Opportunities</span>
            <Zap className="w-4 h-4 text-sky-400" />
          </div>
          <p className="text-2xl font-bold text-sky-400 mt-1">{opportunities.length}</p>
          <p className="text-[10px] text-[#92929A]">Evidence-backed growth opportunities</p>
        </div>

        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#92929A] font-mono uppercase">Strategic Threats</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-2xl font-bold text-rose-400 mt-1">{threats.length}</p>
          <p className="text-[10px] text-[#92929A]">Monitored risk factors</p>
        </div>
      </div>

      {/* Active Alerts List */}
      <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
        <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          <span>Active Early-Warning Alerts ({activeAlerts.length})</span>
        </h2>
        {activeAlerts.length === 0 ? (
          <p className="text-xs text-[#92929A] italic">No current data.</p>
        ) : (
          <div className="space-y-3">
            {activeAlerts.map((a) => (
              <div key={a.id} className="p-4 bg-[#151518] border border-white/5 rounded-lg flex items-center justify-between text-xs">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-950 text-amber-300 border border-amber-800">{a.severity}</span>
                    <span className="text-[10px] font-mono text-[#92929A]">{a.alert_type}</span>
                  </div>
                  <h3 className="font-semibold text-[#F5F5F5] mt-1">{a.title}</h3>
                  <p className="text-[#92929A]">{a.message}</p>
                  {a.recommended_action && (
                    <p className="text-sky-300 pt-1 font-mono text-[11px]">Recommended Action: {a.recommended_action}</p>
                  )}
                </div>
                <button
                  onClick={() => handleResolveAlert(a.id)}
                  className="px-3 py-1.5 rounded text-xs font-mono bg-emerald-950/60 hover:bg-emerald-900 border border-emerald-800 text-emerald-300 flex items-center space-x-1.5 transition"
                >
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>Resolve</span>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Opportunities & Threats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Opportunities */}
        <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
          <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
            <Zap className="w-4 h-4 text-sky-400" />
            <span>Opportunities ({opportunities.length})</span>
          </h2>
          {opportunities.length === 0 ? (
            <p className="text-xs text-[#92929A] italic">No current data.</p>
          ) : (
            <div className="space-y-3">
              {opportunities.map((opp, idx) => (
                <div key={idx} className="p-4 bg-[#151518] border border-white/5 rounded-lg space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-sky-400 uppercase">{opp.category}</span>
                    <span className="text-[10px] font-mono text-[#92929A]">Value: ${opp.expected_value?.toLocaleString()}</span>
                  </div>
                  <h3 className="font-semibold text-[#F5F5F5]">{opp.title}</h3>
                  <p className="text-[#92929A]">{opp.evidence}</p>
                  <p className="text-sky-300 pt-1 font-mono text-[11px]">Action: {opp.recommended_action}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Threats */}
        <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
          <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-rose-400" />
            <span>Threats ({threats.length})</span>
          </h2>
          {threats.length === 0 ? (
            <p className="text-xs text-[#92929A] italic">No current data.</p>
          ) : (
            <div className="space-y-3">
              {threats.map((thr, idx) => (
                <div key={idx} className="p-4 bg-[#151518] border border-white/5 rounded-lg space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-rose-950 text-rose-300 border border-rose-800">{thr.severity}</span>
                    <span className="text-[10px] font-mono text-[#92929A]">Confidence: {thr.confidence_score}%</span>
                  </div>
                  <h3 className="font-semibold text-[#F5F5F5]">{thr.title}</h3>
                  <p className="text-[#92929A]">{thr.evidence}</p>
                  <p className="text-rose-300 pt-1 font-mono text-[11px]">Mitigation: {thr.recommended_action}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
