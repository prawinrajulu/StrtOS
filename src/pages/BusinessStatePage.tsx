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
      setSnapshot(overview.latest_snapshot);
      setAlerts(alts);
      setOpportunities(opps);
      setThreats(thrts);
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
            {alerts.filter(a => a.status !== 'RESOLVED').length}
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
            <span className="text-xs text-slate-400 font-mono uppercase">Active Threat Vectors</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-3xl font-extrabold mt-2 text-rose-400">{threats.length}</p>
          <p className="text-xs text-slate-400 mt-1">Proactive threat mitigation</p>
        </div>
      </div>

      {/* Early-Warning Alerts */}
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
        <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <span>Strategic Early-Warning Alerts</span>
        </h2>

        {alerts.length === 0 ? (
          <div className="p-6 text-center text-slate-400 border border-dashed border-slate-800 rounded-lg">
            No active early-warning alerts detected. Business metrics operating within normal baseline limits.
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map(a => (
              <div key={a.id} className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg flex items-center justify-between hover:border-slate-700 transition">
                <div>
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-mono font-semibold ${
                      a.severity === 'CRITICAL' || a.severity === 'HIGH' ? 'bg-rose-950 text-rose-300 border border-rose-800' : 'bg-amber-950 text-amber-300 border border-amber-800'
                    }`}>
                      {a.severity}
                    </span>
                    <h3 className="font-semibold text-slate-200">{a.title}</h3>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{a.message}</p>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-xs font-mono text-slate-400">{a.status}</span>
                  {a.status !== 'RESOLVED' && (
                    <button
                      onClick={() => handleResolveAlert(a.id)}
                      className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-xs font-mono text-slate-200 rounded transition flex items-center space-x-1"
                    >
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                      <span>RESOLVE</span>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Opportunities & Threats Split Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Opportunities */}
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
            <Zap className="w-5 h-5 text-cyan-400" />
            <span>Growth Opportunities</span>
          </h2>
          {opportunities.map((op, idx) => (
            <div key={idx} className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-cyan-300">{op.category}</span>
                <span className="text-xs font-mono text-emerald-400">+{op.expected_value}% Expected Value</span>
              </div>
              <h3 className="font-semibold text-slate-200">{op.title}</h3>
              <p className="text-xs text-slate-400">{op.evidence}</p>
              <div className="pt-2 border-t border-slate-900 flex items-center justify-between text-xs text-slate-300">
                <span>Action: {op.recommended_action}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Threats */}
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            <span>Threat Vectors</span>
          </h2>
          {threats.map((th, idx) => (
            <div key={idx} className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-rose-300">{th.severity} SEVERITY</span>
                <span className="text-xs font-mono text-slate-400">Confidence: {th.confidence_score}%</span>
              </div>
              <h3 className="font-semibold text-slate-200">{th.title}</h3>
              <p className="text-xs text-slate-400">{th.evidence}</p>
              <div className="pt-2 border-t border-slate-900 text-xs text-rose-300">
                <span>Recommended Mitigation: {th.recommended_action}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
