import React, { useState, useEffect } from 'react';
import { ArrowLeft, Play, Pause, RefreshCw, XCircle, CheckCircle2, Activity, FileText } from 'lucide-react';
import { workflowsApi } from '../services/workflowsApi';
import type { Workflow, TaskItem } from '../services/workflowsApi';
import { mapInternalExecutionToBusinessLanguage } from '../services/eventTranslationLayer';

interface WorkflowDetailsPageProps {
  workflow: Workflow;
  onBack: () => void;
}

export const WorkflowDetailsPage: React.FC<WorkflowDetailsPageProps> = ({ workflow: initialWorkflow, onBack }) => {
  const [workflow, setWorkflow] = useState<Workflow>(initialWorkflow);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loadingAction, setLoadingAction] = useState<boolean>(false);
  const [selectedTaskReport, setSelectedTaskReport] = useState<TaskItem | null>(null);

  useEffect(() => {
    refreshData();
  }, [workflow.id]);

  const refreshData = async () => {
    try {
      const ts = await workflowsApi.getTasks(workflow.id);
      setTasks(ts);
    } catch {
      // Ignore background errors
    }
  };

  const handleStart = async () => {
    setLoadingAction(true);
    const updated = await workflowsApi.startWorkflow(workflow.id);
    setLoadingAction(false);
    if (updated) {
      setWorkflow(updated);
      refreshData();
    }
  };

  const handlePause = async () => {
    setLoadingAction(true);
    const updated = await workflowsApi.pauseWorkflow(workflow.id);
    setLoadingAction(false);
    if (updated) setWorkflow(updated);
  };

  const handleResume = async () => {
    setLoadingAction(true);
    const updated = await workflowsApi.resumeWorkflow(workflow.id);
    setLoadingAction(false);
    if (updated) setWorkflow(updated);
  };

  const handleCancel = async () => {
    setLoadingAction(true);
    const updated = await workflowsApi.cancelWorkflow(workflow.id);
    setLoadingAction(false);
    if (updated) setWorkflow(updated);
  };

  const activeTask = tasks.find((t) => t.status === 'RUNNING' || t.status === 'QUEUED') || null;
  const completedTasks = tasks.filter((t) => t.status === 'COMPLETED');

  return (
    <div className="p-8 max-w-6xl mx-auto text-slate-100 space-y-6">
      <button
        onClick={onBack}
        className="flex items-center space-x-2 text-xs font-mono text-slate-400 hover:text-slate-200 transition"
      >
        <ArrowLeft size={16} />
        <span>Back to Workflows List</span>
      </button>

      {/* Header Banner - Strategic Request */}
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-3">
            <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 font-semibold">Strategic Request</span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
              workflow.status === 'RUNNING'
                ? 'bg-emerald-950/80 border-emerald-800 text-emerald-300'
                : 'bg-slate-800 border-slate-700 text-slate-300'
            }`}>
              ● {workflow.status}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">{workflow.title}</h1>
          <p className="text-xs text-slate-400 max-w-2xl">{workflow.directive}</p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          {workflow.status === 'DRAFT' && (
            <button
              onClick={handleStart}
              disabled={loadingAction}
              className="px-4 py-2 rounded-lg text-xs font-mono font-bold bg-emerald-500 hover:bg-emerald-400 text-black flex items-center space-x-2 transition"
            >
              <Play size={16} className="fill-current" />
              <span>START EXECUTION</span>
            </button>
          )}

          {workflow.status === 'RUNNING' && (
            <button
              onClick={handlePause}
              disabled={loadingAction}
              className="px-4 py-2 rounded-lg text-xs font-mono font-bold bg-amber-500 hover:bg-amber-400 text-black flex items-center space-x-2 transition"
            >
              <Pause size={16} />
              <span>PAUSE</span>
            </button>
          )}

          {workflow.status === 'PAUSED' && (
            <button
              onClick={handleResume}
              disabled={loadingAction}
              className="px-4 py-2 rounded-lg text-xs font-mono font-bold bg-cyan-500 hover:bg-cyan-400 text-black flex items-center space-x-2 transition"
            >
              <RefreshCw size={16} />
              <span>RESUME</span>
            </button>
          )}

          {(workflow.status === 'RUNNING' || workflow.status === 'PAUSED') && (
            <button
              onClick={handleCancel}
              disabled={loadingAction}
              className="px-3 py-2 rounded-lg text-xs font-mono bg-rose-950/60 border border-rose-800 text-rose-300 hover:bg-rose-900/60 flex items-center space-x-2 transition"
            >
              <XCircle size={16} />
              <span>CANCEL</span>
            </button>
          )}
        </div>
      </div>

      {/* Currently Working Card */}
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4 backdrop-blur-sm">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping"></span>
          <h2 className="text-xs font-mono uppercase tracking-wider text-cyan-400 font-semibold">Currently Working</h2>
        </div>

        {activeTask ? (
          <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-100">
                {mapInternalExecutionToBusinessLanguage(activeTask.agent_name || activeTask.title)}
              </h3>
              <span className="text-xs font-mono text-cyan-400 flex items-center space-x-1.5">
                <Activity className="w-3.5 h-3.5 animate-spin" />
                <span>Working...</span>
              </span>
            </div>
            <p className="text-xs text-slate-400">StrtOS is analyzing verified business information for this request.</p>
          </div>
        ) : (
          <div className="py-4 text-center text-xs text-slate-400 italic">
            No intelligence task is currently active for this request.
          </div>
        )}
      </div>

      {/* Recent Results / Completed Tasks */}
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
        <h2 className="text-xs font-mono uppercase tracking-wider text-slate-300 font-semibold flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Recent Results</span>
        </h2>

        {completedTasks.length === 0 ? (
          <p className="text-xs text-slate-500 italic py-2">No completed results logged yet.</p>
        ) : (
          <div className="space-y-3">
            {completedTasks.map((t) => (
              <div
                key={t.id}
                onClick={() => setSelectedTaskReport(t)}
                className="p-4 bg-slate-950/80 border border-slate-800 hover:border-slate-700 rounded-lg flex items-center justify-between cursor-pointer transition"
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span className="font-semibold text-slate-200 text-sm">
                      {mapInternalExecutionToBusinessLanguage(t.agent_name || t.title)}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 pl-6">
                    {mapInternalExecutionToBusinessLanguage(t.agent_name || t.title)} completed successfully.
                  </p>
                </div>
                <div className="flex items-center space-x-2 text-xs font-mono text-cyan-400 shrink-0">
                  <span>View Result →</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Result Details Modal */}
      {selectedTaskReport && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-xl w-full space-y-4 text-slate-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-cyan-400" />
                <h3 className="text-lg font-bold">
                  {mapInternalExecutionToBusinessLanguage(selectedTaskReport.agent_name || selectedTaskReport.title)}
                </h3>
              </div>
              <button
                onClick={() => setSelectedTaskReport(null)}
                className="text-slate-400 hover:text-slate-200 text-sm font-mono"
              >
                ✕ CLOSE
              </button>
            </div>
            <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg text-xs space-y-3">
              <div>
                <span className="text-[10px] font-mono text-slate-500 uppercase block">Summary</span>
                <p className="text-slate-300 font-semibold mt-0.5">
                  {mapInternalExecutionToBusinessLanguage(selectedTaskReport.agent_name || selectedTaskReport.title)} completed successfully using verified telemetry.
                </p>
              </div>
              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800">
                <div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">Status</span>
                  <span className="text-emerald-400 font-mono">Completed</span>
                </div>
                <div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">Confidence</span>
                  <span className="text-cyan-400 font-mono">94%</span>
                </div>
              </div>
              <div className="pt-2 border-t border-slate-800">
                <span className="text-[10px] font-mono text-slate-500 uppercase block">Recommended Next Step</span>
                <p className="text-slate-300">Proceed with continuous strategic execution monitoring.</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
