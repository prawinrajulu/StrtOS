import React, { useState, useEffect } from 'react';
import { Activity, ShieldAlert, Zap, AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react';
import { businessStateApi } from '../services/businessStateApi';
import type { BusinessAlert, Opportunity, Threat, StateSnapshot } from '../services/businessStateApi';

export const BusinessStatePage: React.FC = () => {
  const [snapshot, setSnapshot] = useState<StateSnapshot | null>(null);
  const [alerts, setAlerts] = useState<BusinessAlert[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [threats, setThreats] = useState<Threat[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [overview, alts, opps, thrts] = await Promise.all([
        businessStateApi.getOverview(),
        businessStateApi.listAlerts(),
        businessStateApi.listOpportunities(),
        businessStateApi.listThreats()
      ]);
      setSnapshot(overview?.latest_snapshot || null);
      setAlerts(Array.isArray(alts) ? alts : []);
      setOpportunities(Array.isArray(opps) ? opps : []);
      setThreats(Array.isArray(thrts) ? thrts : []);
    } catch (e) {
      console.error('Failed to load business state intelligence data:', e);
    }
  };

  const handleResolveAlert = async (id: string) => {
    try {
      await businessStateApi.resolveAlert(id);
      loadData();
    } catch (e) {
      console.error('Failed to resolve alert:', e);
    }
  };

  const activeAlerts = Array.isArray(alerts) ? alerts.filter(a => a.status !== 'RESOLVED') : [];

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Activity className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl font-bold text-slate-100 tracking-tight">Continuous Business State Intelligence</h1>
          </div>
          <p className="text-slate-400 mt-1">Real-time baseline comparison, change detection & strategic early-warning telemetry.</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={loadData}
            className="px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 flex items-center space-x-2 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>SYNC STATE</span>
          </button>
          <span className="px-3 py-1.5 rounded-full text-xs font-mono bg-emerald-950/80 border border-emerald-800 text-emerald-300 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>STRTOS v2.1.0 CONTINUOUS OBSERVER</span>
          </span>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono uppercase">Business Health Score</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-3xl font-extrabold mt-2 text-emerald-400">
            {snapshot ? `${snapshot.health_score}` : '88.5'}
          </p>
          <p className="text-xs text-slate-400 mt-1">Status: {snapshot ? snapshot.health_status : 'HEALTHY'}</p>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono uppercase">Active Early Warnings</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-3xl font-extrabold mt-2 text-amber-400">
            {activeAlerts.length}
          </p>
          <p className="text-xs text-slate-400 mt-1">Actionable strategic warnings</p>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono uppercase">Discovered Opportunities</span>
            <Zap className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-3xl font-extrabold mt-2 text-cyan-400">{opportunities.length}</p>
          <p className="text-xs text-slate-400 mt-1">Evidence-backed tailwinds</p>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono uppercase">Active Strategic Threats</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-3xl font-extrabold mt-2 text-rose-400">{threats.length}</p>
          <p className="text-xs text-slate-400 mt-1">Monitored risk vectors</p>
        </div>
      </div>

      {/* Active Alerts List */}
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
        <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <span>Active Early-Warning Alerts ({activeAlerts.length})</span>
        </h2>
        {activeAlerts.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No active early warning alerts detected.</p>
        ) : (
          <div className="space-y-3">
            {activeAlerts.map((a) => (
              <div key={a.id} className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded text-xs font-mono bg-amber-950 text-amber-300 border border-amber-800">{a.severity}</span>
                    <span className="text-xs font-mono text-slate-400">{a.alert_type}</span>
                  </div>
                  <h3 className="font-semibold text-slate-200 mt-1">{a.title}</h3>
                  <p className="text-xs text-slate-400">{a.message}</p>
                  {a.recommended_action && (
                    <p className="text-xs text-cyan-300 pt-1">Recommended Action: {a.recommended_action}</p>
                  )}
                </div>
                <button
                  onClick={() => handleResolveAlert(a.id)}
                  className="px-3 py-1.5 rounded text-xs font-mono bg-emerald-950 hover:bg-emerald-900 border border-emerald-800 text-emerald-300 flex items-center space-x-1.5 transition"
                >
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>RESOLVE</span>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Opportunities & Threats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Opportunities */}
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
            <Zap className="w-5 h-5 text-cyan-400" />
            <span>Market Opportunities ({opportunities.length})</span>
          </h2>
          {opportunities.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No market opportunities detected.</p>
          ) : (
            <div className="space-y-3">
              {opportunities.map((opp, idx) => (
                <div key={idx} className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono text-cyan-400 uppercase">{opp.category}</span>
                    <span className="text-xs font-mono text-slate-400">Value: ${opp.expected_value?.toLocaleString()}</span>
                  </div>
                  <h3 className="font-semibold text-slate-200">{opp.title}</h3>
                  <p className="text-xs text-slate-400">{opp.evidence}</p>
                  <p className="text-xs text-cyan-300 pt-1">Action: {opp.recommended_action}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Threats */}
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            <span>Strategic Threats ({threats.length})</span>
          </h2>
          {threats.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No strategic threats detected.</p>
          ) : (
            <div className="space-y-3">
              {threats.map((thr, idx) => (
                <div key={idx} className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded text-xs font-mono bg-rose-950 text-rose-300 border border-rose-800">{thr.severity}</span>
                    <span className="text-xs font-mono text-slate-400">Confidence: {thr.confidence_score}%</span>
                  </div>
                  <h3 className="font-semibold text-slate-200">{thr.title}</h3>
                  <p className="text-xs text-slate-400">{thr.evidence}</p>
                  <p className="text-xs text-rose-300 pt-1">Mitigation: {thr.recommended_action}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
