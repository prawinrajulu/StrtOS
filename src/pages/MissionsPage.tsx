import React, { useState, useEffect } from 'react';
import { Target, RefreshCw, Play, BarChart2, AlertTriangle, CheckCircle, Clock, Layers } from 'lucide-react';
import { missionsApi } from '../services/missionsApi';
import type { Mission, MissionEvaluation } from '../services/missionsApi';

const statusColors: Record<string, string> = {
  READY: 'text-cyan-400 bg-cyan-950 border-cyan-800',
  ACTIVE: 'text-emerald-400 bg-emerald-950 border-emerald-800',
  PAUSED: 'text-amber-400 bg-amber-950 border-amber-800',
  BLOCKED: 'text-rose-400 bg-rose-950 border-rose-800',
  COMPLETED: 'text-emerald-300 bg-emerald-950 border-emerald-700',
  FAILED: 'text-rose-300 bg-rose-950 border-rose-700',
  AWAITING_APPROVAL: 'text-indigo-400 bg-indigo-950 border-indigo-800',
  ADAPTING: 'text-violet-400 bg-violet-950 border-violet-800',
  DRAFT: 'text-slate-400 bg-slate-900 border-slate-700',
};

const stepStatusIcons: Record<string, React.ReactNode> = {
  COMPLETED: <CheckCircle className="w-4 h-4 text-emerald-400" />,
  RUNNING: <RefreshCw className="w-4 h-4 text-cyan-400 animate-spin" />,
  FAILED: <AlertTriangle className="w-4 h-4 text-rose-400" />,
  BLOCKED: <AlertTriangle className="w-4 h-4 text-amber-400" />,
  READY: <Play className="w-4 h-4 text-cyan-300" />,
  PENDING: <Clock className="w-4 h-4 text-slate-400" />,
};

export const MissionsPage: React.FC = () => {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [selected, setSelected] = useState<Mission | null>(null);
  const [evaluation, setEvaluation] = useState<MissionEvaluation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await missionsApi.listMissions();
      setMissions(data);
      if (data.length > 0) await selectMission(data[0]);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const selectMission = async (m: Mission) => {
    setSelected(m);
    try {
      const ev = await missionsApi.evaluateMission(m.id);
      setEvaluation(ev);
    } catch {}
  };

  const handleStart = async (id: string) => {
    try {
      const updated = await missionsApi.startMission(id);
      setMissions(prev => prev.map(m => m.id === id ? updated : m));
      if (selected?.id === id) await selectMission(updated);
    } catch (e) { console.error(e); }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64 text-cyan-400">
      <RefreshCw className="animate-spin mr-2" /> Loading Mission Control Center...
    </div>
  );

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Target className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl font-bold tracking-tight">Mission Control Center</h1>
          </div>
          <p className="text-slate-400 mt-1">Autonomous strategic mission execution, checkpoint evaluation & bounded adaptive replanning.</p>
        </div>
        <div className="flex space-x-3">
          <button onClick={loadData} className="px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 flex items-center space-x-2 transition">
            <RefreshCw className="w-3.5 h-3.5" /><span>SYNC</span>
          </button>
          <span className="px-3 py-1.5 rounded-full text-xs font-mono bg-cyan-950/80 border border-cyan-800 text-cyan-300 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
            <span>STRTOS v2.4.0 MISSION ENGINE</span>
          </span>
        </div>
      </div>

      {/* Mission List */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {missions.map(m => (
          <div
            key={m.id}
            onClick={() => selectMission(m)}
            className={`p-5 rounded-xl border cursor-pointer transition backdrop-blur-sm ${selected?.id === m.id ? 'bg-cyan-950/40 border-cyan-500' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'}`}
          >
            <div className="flex justify-between items-start">
              <span className={`px-2 py-0.5 rounded text-xs font-mono border ${statusColors[m.status] || 'text-slate-400 bg-slate-900 border-slate-700'}`}>{m.status}</span>
              <span className="text-xs font-mono text-slate-400">{m.current_version}</span>
            </div>
            <h3 className="font-bold text-slate-100 mt-2 text-sm">{m.title}</h3>
            <div className="mt-3 space-y-1">
              <div className="flex justify-between text-xs text-slate-400">
                <span>Progress</span><span>{m.progress_percentage}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5">
                <div className="bg-cyan-500 h-1.5 rounded-full transition-all" style={{ width: `${m.progress_percentage}%` }} />
              </div>
            </div>
            {m.status === 'READY' && (
              <button
                onClick={e => { e.stopPropagation(); handleStart(m.id); }}
                className="mt-3 w-full py-1.5 rounded-lg text-xs font-mono bg-cyan-900 border border-cyan-700 hover:bg-cyan-800 text-cyan-200 flex items-center justify-center space-x-1 transition"
              >
                <Play className="w-3.5 h-3.5" /><span>ACTIVATE MISSION</span>
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Selected Mission Detail */}
      {selected && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Mission Execution Tasks */}
          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
            <h2 className="text-lg font-semibold flex items-center space-x-2">
              <Layers className="w-5 h-5 text-cyan-400" /><span>Mission Execution Tasks</span>
            </h2>
            <div className="space-y-2">
              {selected.steps.map((step, idx) => (
                <div key={step.id} className="flex items-center space-x-3 p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
                  <span className="text-xs font-mono text-slate-500 w-4">{idx + 1}</span>
                  {stepStatusIcons[step.status] || <Clock className="w-4 h-4 text-slate-500" />}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-200 truncate">{step.title}</p>
                    <p className="text-xs text-slate-500 font-mono">{step.action_type} Â· {step.autonomy_level} Â· {step.risk_level} risk</p>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs font-mono border ${statusColors[step.status] || 'text-slate-400 bg-slate-900 border-slate-700'}`}>{step.status}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Evaluation & Success Criteria */}
          <div className="space-y-4">
            {evaluation && (
              <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3">
                <h2 className="text-lg font-semibold flex items-center space-x-2">
                  <BarChart2 className="w-5 h-5 text-indigo-400" /><span>Mission Evaluation</span>
                </h2>
                <div className="flex justify-between items-center">
                  <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold border ${
                    evaluation.status === 'ON_TRACK' ? 'text-emerald-400 bg-emerald-950 border-emerald-800' :
                    evaluation.status === 'AT_RISK' ? 'text-amber-400 bg-amber-950 border-amber-800' :
                    'text-rose-400 bg-rose-950 border-rose-800'
                  }`}>{evaluation.status}</span>
                  <span className="text-2xl font-bold font-mono text-cyan-400">{evaluation.progress_percentage}%</span>
                </div>
                <p className="text-xs text-slate-400">{evaluation.summary}</p>
                <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                  <div className="p-2 bg-slate-950 rounded border border-slate-800">
                    <span className="text-slate-400">Risk Score</span>
                    <p className="text-slate-200 font-bold mt-1">{evaluation.risk_score}</p>
                  </div>
                  <div className="p-2 bg-slate-950 rounded border border-slate-800">
                    <span className="text-slate-400">Confidence</span>
                    <p className="text-slate-200 font-bold mt-1">{evaluation.confidence_score}%</p>
                  </div>
                </div>
              </div>
            )}

            <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3">
              <h2 className="text-lg font-semibold flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-emerald-400" /><span>Success Criteria</span>
              </h2>
              {selected.criteria.length === 0 ? (
                <p className="text-slate-400 text-sm">No success criteria defined.</p>
              ) : (
                selected.criteria.map(c => (
                  <div key={c.id} className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
                    <div className="flex justify-between text-xs font-mono text-slate-300">
                      <span>{c.metric_name}</span>
                      <span className="text-cyan-300">{c.current_value} / {c.target_value} {c.unit}</span>
                    </div>
                    <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5">
                      <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${Math.min(100, (c.current_value / c.target_value) * 100)}%` }} />
                    </div>
                    <span className="text-xs font-mono text-slate-500 mt-1">{c.status}</span>
                  </div>
                ))
              )}
            </div>

            <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3">
              <h2 className="text-lg font-semibold">Plan Versions</h2>
              {selected.plans.map(p => (
                <div key={p.id} className="flex justify-between text-xs font-mono p-2 bg-slate-950 rounded border border-slate-800">
                  <span className="text-cyan-300">{p.version}</span>
                  <span className="text-slate-400">{p.adaptation_reason}</span>
                  <span className="text-slate-500">Î”{p.delta_percentage}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
