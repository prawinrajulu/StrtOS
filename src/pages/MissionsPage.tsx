import React, { useEffect, useState } from 'react';
import { Target, Play, Clock, CheckCircle, AlertTriangle, XCircle, RefreshCw, Layers, BarChart2 } from 'lucide-react';
import { missionsApi } from '../services/missionsApi';
import type { Mission, MissionEvaluation } from '../services/missionsApi';

const statusColors: Record<string, string> = {
  READY: 'text-sky-300 bg-sky-950/80 border-sky-800',
  IN_PROGRESS: 'text-amber-300 bg-amber-950/80 border-amber-800',
  COMPLETED: 'text-emerald-300 bg-emerald-950/80 border-emerald-800',
  FAILED: 'text-rose-300 bg-rose-950/80 border-rose-800',
  PAUSED: 'text-slate-400 bg-slate-900 border-slate-700',
};

const stepStatusIcons: Record<string, React.ReactNode> = {
  COMPLETED: <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0" />,
  IN_PROGRESS: <Clock className="w-4 h-4 text-amber-400 animate-spin shrink-0" />,
  FAILED: <XCircle className="w-4 h-4 text-rose-400 shrink-0" />,
  BLOCKED: <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />,
  PENDING: <Clock className="w-4 h-4 text-slate-500 shrink-0" />,
};

export const MissionsPage: React.FC = () => {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [selected, setSelected] = useState<Mission | null>(null);
  const [evaluation, setEvaluation] = useState<MissionEvaluation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await missionsApi.listMissions();
      const list = Array.isArray(data) ? data : [];
      setMissions(list);
      if (list.length > 0) {
        selectMission(list[0]);
      }
    } catch {
      setMissions([]);
    } finally {
      setLoading(false);
    }
  };

  const selectMission = async (m: Mission) => {
    setSelected(m);
    try {
      const ev = await missionsApi.evaluateMission(m.id);
      setEvaluation(ev);
    } catch {
      setEvaluation(null);
    }
  };

  const handleStart = async (id: string) => {
    try {
      const updated = await missionsApi.startMission(id);
      setMissions(prev => prev.map(item => item.id === id ? updated : item));
      if (selected?.id === id) setSelected(updated);
    } catch {
      // Ignore background errors
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Target className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Missions</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            Track important business goals from start to finish.
          </p>
        </div>
        <button
          onClick={loadData}
          className="px-3 py-1.5 rounded-lg text-xs font-mono bg-[#151518] border border-white/10 hover:border-white/20 text-[#92929A] hover:text-[#F5F5F5] flex items-center space-x-2 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Mission List */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {loading ? (
          <div className="md:col-span-3 p-6 bg-[#111113] border border-white/[0.06] rounded-xl text-xs text-[#92929A] italic">
            Loading business missions...
          </div>
        ) : missions.length === 0 ? (
          <div className="md:col-span-3 p-6 bg-[#111113] border border-white/[0.06] rounded-xl text-xs text-[#92929A] italic">
            No active mission.
          </div>
        ) : (
          missions.map(m => (
            <div
              key={m.id}
              onClick={() => selectMission(m)}
              className={`p-4 rounded-xl border cursor-pointer transition ${
                selected?.id === m.id
                  ? 'bg-sky-950/40 border-sky-500/80 text-sky-200'
                  : 'bg-[#111113] border-white/[0.06] hover:border-white/15 text-[#F5F5F5]'
              }`}
            >
              <div className="flex justify-between items-start">
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${statusColors[m.status] || 'text-[#92929A] bg-[#151518] border-white/10'}`}>
                  {m.status}
                </span>
                <span className="text-[10px] font-mono text-[#92929A]">{m.current_version}</span>
              </div>
              <h3 className="font-bold text-sm mt-2">{m.title}</h3>
              <div className="mt-3 space-y-1">
                <div className="flex justify-between text-[10px] text-[#92929A] font-mono">
                  <span>Progress</span>
                  <span>{m.progress_percentage}%</span>
                </div>
                <div className="w-full bg-[#151518] rounded-full h-1.5 border border-white/10">
                  <div className="bg-sky-500 h-1.5 rounded-full transition-all" style={{ width: `${m.progress_percentage}%` }} />
                </div>
              </div>
              {m.status === 'READY' && (
                <button
                  onClick={e => { e.stopPropagation(); handleStart(m.id); }}
                  className="mt-3 w-full py-1.5 rounded-lg text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 flex items-center justify-center space-x-1.5 transition"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Activate Mission</span>
                </button>
              )}
            </div>
          ))
        )}
      </div>

      {/* Selected Mission Detail */}
      {selected && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Mission Execution Steps */}
          <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
            <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
              <Layers className="w-4 h-4 text-sky-400" />
              <span>Mission Steps</span>
            </h2>
            <div className="space-y-2">
              {selected.steps && selected.steps.length > 0 ? (
                selected.steps.map((step, idx) => (
                  <div key={step.id} className="flex items-center space-x-3 p-3 bg-[#151518] border border-white/5 rounded-lg text-xs">
                    <span className="font-mono text-[#92929A] w-4">{idx + 1}</span>
                    {stepStatusIcons[step.status] || <Clock className="w-4 h-4 text-slate-500" />}
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-[#F5F5F5] truncate">{step.title}</p>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${statusColors[step.status] || 'text-[#92929A] bg-[#151518] border-white/10'}`}>
                      {step.status}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-xs text-[#92929A] italic">No step breakdown available.</p>
              )}
            </div>
          </div>

          {/* Evaluation & Success Criteria */}
          <div className="space-y-4">
            {evaluation && (
              <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-3 text-xs">
                <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
                  <BarChart2 className="w-4 h-4 text-indigo-400" />
                  <span>Mission Status</span>
                </h2>
                <div className="flex justify-between items-center">
                  <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold border ${
                    evaluation.status === 'ON_TRACK' ? 'text-emerald-300 bg-emerald-950 border-emerald-800' :
                    evaluation.status === 'AT_RISK' ? 'text-amber-300 bg-amber-950 border-amber-800' :
                    'text-rose-300 bg-rose-950 border-rose-800'
                  }`}>
                    {evaluation.status}
                  </span>
                  <span className="text-xl font-bold font-mono text-sky-400">{evaluation.progress_percentage}%</span>
                </div>
                <p className="text-[#92929A]">{evaluation.summary}</p>
              </div>
            )}

            <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-3 text-xs">
              <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                <span>Success Criteria</span>
              </h2>
              {selected.criteria && selected.criteria.length > 0 ? (
                selected.criteria.map(c => (
                  <div key={c.id} className="p-3 bg-[#151518] border border-white/5 rounded-lg space-y-1">
                    <div className="flex justify-between font-mono text-[#92929A]">
                      <span className="text-[#F5F5F5]">{c.metric_name}</span>
                      <span className="text-sky-300">{c.current_value} / {c.target_value} {c.unit}</span>
                    </div>
                    <div className="w-full bg-[#151518] rounded-full h-1.5 border border-white/10">
                      <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${Math.min(100, (c.current_value / c.target_value) * 100)}%` }} />
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-[#92929A] italic">No success criteria defined.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
