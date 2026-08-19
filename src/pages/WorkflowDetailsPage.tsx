import React, { useEffect, useState } from 'react';
import { ArrowLeft, Play, Pause, RefreshCw, XCircle, Activity, CheckCircle2, FileText } from 'lucide-react';
import { workflowsApi } from '../services/workflowsApi';
import type { Workflow, TaskItem } from '../services/workflowsApi';
import { mapInternalExecutionToBusinessLanguage } from '../services/eventTranslationLayer';

interface WorkflowDetailsPageProps {
  workflow: Workflow;
  onBack: () => void;
}

export const WorkflowDetailsPage: React.FC<WorkflowDetailsPageProps> = ({ workflow: initialWf, onBack }) => {
  const [workflow, setWorkflow] = useState<Workflow>(initialWf);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loadingAction, setLoadingAction] = useState(false);
  const [selectedTaskReport, setSelectedTaskReport] = useState<TaskItem | null>(null);

  useEffect(() => {
    loadWorkflowDetails();
  }, [initialWf.id]);

  const loadWorkflowDetails = async () => {
    try {
      const [wf, tList] = await Promise.all([
        workflowsApi.getWorkflow(initialWf.id),
        workflowsApi.getTasks(initialWf.id),
      ]);
      if (wf) setWorkflow(wf);
      setTasks(tList || []);
    } catch {
      // Ignore background errors
    }
  };

  const handleStart = async () => {
    setLoadingAction(true);
    try {
      const updated = await workflowsApi.startWorkflow(workflow.id);
      if (updated) setWorkflow(updated);
      loadWorkflowDetails();
    } catch {
      // Ignore
    } finally {
      setLoadingAction(false);
    }
  };

  const handlePause = async () => {
    setLoadingAction(true);
    try {
      const updated = await workflowsApi.pauseWorkflow(workflow.id);
      if (updated) setWorkflow(updated);
    } catch {
      // Ignore
    } finally {
      setLoadingAction(false);
    }
  };

  const handleResume = async () => {
    setLoadingAction(true);
    try {
      const updated = await workflowsApi.resumeWorkflow(workflow.id);
      if (updated) setWorkflow(updated);
    } catch {
      // Ignore
    } finally {
      setLoadingAction(false);
    }
  };

  const handleCancel = async () => {
    setLoadingAction(true);
    try {
      const updated = await workflowsApi.cancelWorkflow(workflow.id);
      if (updated) setWorkflow(updated);
    } catch {
      // Ignore
    } finally {
      setLoadingAction(false);
    }
  };

  const activeTask = tasks.find(t => t.status === 'RUNNING');
  const completedTasks = tasks.filter(t => t.status === 'COMPLETED');

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Header Bar */}
      <button
        onClick={onBack}
        className="flex items-center space-x-2 text-xs font-mono text-[#92929A] hover:text-[#F5F5F5] transition"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Workflows</span>
      </button>

      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-sky-950 text-sky-300 border border-sky-800">
              {workflow.status}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">{mapInternalExecutionToBusinessLanguage(workflow.title)}</h1>
          <p className="text-xs text-[#92929A] max-w-2xl">{workflow.directive}</p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          {workflow.status === 'DRAFT' && (
            <button
              onClick={handleStart}
              disabled={loadingAction}
              className="px-4 py-2 rounded-lg text-xs font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-950 flex items-center space-x-2 transition"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>Start Business Process</span>
            </button>
          )}

          {workflow.status === 'RUNNING' && (
            <button
              onClick={handlePause}
              disabled={loadingAction}
              className="px-4 py-2 rounded-lg text-xs font-semibold bg-amber-500 hover:bg-amber-400 text-slate-950 flex items-center space-x-2 transition"
            >
              <Pause className="w-4 h-4" />
              <span>Pause</span>
            </button>
          )}

          {workflow.status === 'PAUSED' && (
            <button
              onClick={handleResume}
              disabled={loadingAction}
              className="px-4 py-2 rounded-lg text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 flex items-center space-x-2 transition"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Resume</span>
            </button>
          )}

          {(workflow.status === 'RUNNING' || workflow.status === 'PAUSED') && (
            <button
              onClick={handleCancel}
              disabled={loadingAction}
              className="px-3 py-2 rounded-lg text-xs bg-rose-950/60 border border-rose-800 text-rose-300 hover:bg-rose-900/60 flex items-center space-x-2 transition"
            >
              <XCircle className="w-4 h-4" />
              <span>Cancel</span>
            </button>
          )}
        </div>
      </div>

      {/* Currently Working Card */}
      <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse"></span>
          <h2 className="text-xs font-mono uppercase tracking-wider text-sky-400 font-semibold">Currently Working</h2>
        </div>

        {activeTask ? (
          <div className="p-4 bg-[#151518] border border-white/5 rounded-lg space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-[#F5F5F5]">
                {mapInternalExecutionToBusinessLanguage(activeTask.agent_name || activeTask.title)}
              </h3>
              <span className="text-xs font-mono text-sky-400 flex items-center space-x-1.5">
                <Activity className="w-3.5 h-3.5 animate-spin" />
                <span>Working...</span>
              </span>
            </div>
            <p className="text-[#92929A]">StrtOS is analyzing verified business state for this request.</p>
          </div>
        ) : (
          <p className="text-xs text-[#92929A] italic">
            No intelligence task is currently active for this request.
          </p>
        )}
      </div>

      {/* Recent Results / Completed Tasks */}
      <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
        <h2 className="text-xs font-mono uppercase tracking-wider text-[#92929A] font-semibold flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Recent Results</span>
        </h2>

        {completedTasks.length === 0 ? (
          <p className="text-xs text-[#92929A] italic">No recent results.</p>
        ) : (
          <div className="space-y-3">
            {completedTasks.map((t) => (
              <div
                key={t.id}
                onClick={() => setSelectedTaskReport(t)}
                className="p-4 bg-[#151518] border border-white/5 hover:border-white/15 rounded-lg flex items-center justify-between cursor-pointer transition text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span className="font-semibold text-[#F5F5F5]">
                      {mapInternalExecutionToBusinessLanguage(t.agent_name || t.title)}
                    </span>
                  </div>
                  <p className="text-[#92929A] pl-6">
                    {mapInternalExecutionToBusinessLanguage(t.agent_name || t.title)} completed successfully.
                  </p>
                </div>
                <div className="flex items-center space-x-1 text-sky-400 font-mono text-[10px] hover:underline">
                  <span>View Result</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Result Details Modal */}
      {selectedTaskReport && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#111113] border border-white/10 rounded-xl p-6 max-w-xl w-full space-y-4 text-slate-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-sky-400" />
                <h3 className="text-base font-bold text-[#F5F5F5]">
                  {mapInternalExecutionToBusinessLanguage(selectedTaskReport.agent_name || selectedTaskReport.title)}
                </h3>
              </div>
              <button
                onClick={() => setSelectedTaskReport(null)}
                className="text-[#92929A] hover:text-[#F5F5F5] text-xs font-mono"
              >
                Close
              </button>
            </div>
            <div className="p-4 bg-[#151518] border border-white/5 rounded-lg text-xs space-y-3">
              <div>
                <span className="text-[10px] font-mono text-emerald-400 uppercase font-bold block mb-1">Status: Completed</span>
                <span className="text-[10px] font-mono text-[#92929A] uppercase block">Summary</span>
                <p className="text-[#F5F5F5] font-semibold mt-0.5">
                  {mapInternalExecutionToBusinessLanguage(selectedTaskReport.agent_name || selectedTaskReport.title)} analysis completed.
                </p>
              </div>

              <div className="pt-2 border-t border-white/5 space-y-1">
                <span className="text-[10px] font-mono text-[#92929A] uppercase block">Key Findings</span>
                <p className="text-[#92929A]">Completed successfully based on verified business telemetry.</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
