import React, { useState, useEffect } from 'react';
import { Compass, CheckCircle2, Activity, ShieldAlert, Sparkles, Send, ArrowRight, AlertCircle, FileText } from 'lucide-react';
import { commandCenterApi } from '../services/commandCenterApi';
import type { CommandCenterOverview } from '../services/commandCenterApi';
import { workflowsApi } from '../services/workflowsApi';
import type { Workflow } from '../services/workflowsApi';
import { globalEventStream } from '../services/eventStream';
import {
  translateWorkflowToTasks,
  translateSSEEventToTaskUpdate,
  mapInternalExecutionToBusinessLanguage
} from '../services/eventTranslationLayer';
import type { UserFacingTask } from '../services/eventTranslationLayer';

interface CommandCenterPageProps {
  onNavigateToReports?: () => void;
  onNavigateToDecisions?: () => void;
}

export const CommandCenterPage: React.FC<CommandCenterPageProps> = ({
  onNavigateToReports,
  onNavigateToDecisions
}) => {
  const [overview, setOverview] = useState<CommandCenterOverview | null>(null);
  const [, setActiveWorkflow] = useState<Workflow | null>(null);
  const [activeTask, setActiveTask] = useState<UserFacingTask | null>(null);
  const [completedTasks, setCompletedTasks] = useState<UserFacingTask[]>([]);
  const [selectedCompletedTask, setSelectedCompletedTask] = useState<UserFacingTask | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startingWorkflow, setStartingWorkflow] = useState(false);
  const [askQuery, setAskQuery] = useState('');

  useEffect(() => {
    loadData();

    // Subscribe to real backend SSE events
    const unsubscribe = globalEventStream.subscribe((event) => {
      if (event.workflow_id || event.task_id) {
        const update = translateSSEEventToTaskUpdate(event);
        setActiveTask(prev => {
          if (!prev) return null;
          if (prev.id === update.id || update.title === prev.title) {
            const nextProgress = update.progress !== undefined ? update.progress : prev.progress;
            if (update.status === 'COMPLETED') {
              // Smoothly transition completed task to Recent Results
              const finishedTask: UserFacingTask = {
                ...prev,
                ...update,
                progress: 100,
                status: 'COMPLETED'
              };
              setCompletedTasks(history => [finishedTask, ...history]);

              // Refetch next real queued task from backend
              refreshTasksFromBackend();
              return null;
            }
            return { ...prev, ...update, progress: nextProgress };
          }
          return prev;
        });
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const refreshTasksFromBackend = async () => {
    try {
      const wfs = await workflowsApi.listWorkflows();
      if (wfs && wfs.length > 0) {
        const currentWf = wfs.find(w => w.status === 'RUNNING' || w.status === 'QUEUED') || wfs[0];
        setActiveWorkflow(currentWf);
        const tasks = await workflowsApi.getTasks(currentWf.id);
        const translated = translateWorkflowToTasks(currentWf, tasks);
        setActiveTask(translated.activeTask);
        setCompletedTasks(translated.completedTasks);
      }
    } catch {
      // Ignore background refresh errors
    }
  };

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [ovData, wfs] = await Promise.all([
        commandCenterApi.getOverview(),
        workflowsApi.listWorkflows()
      ]);

      setOverview(ovData);

      if (wfs && wfs.length > 0) {
        const currentWf = wfs.find(w => w.status === 'RUNNING' || w.status === 'QUEUED') || wfs[0];
        setActiveWorkflow(currentWf);
        const tasks = await workflowsApi.getTasks(currentWf.id);
        const translated = translateWorkflowToTasks(currentWf, tasks);
        setActiveTask(translated.activeTask);
        setCompletedTasks(translated.completedTasks);
      } else {
        setActiveTask(null);
        setCompletedTasks([]);
      }
    } catch {
      setError('StrtOS couldn\'t complete this request.');
    } finally {
      setLoading(false);
    }
  };

  const handleAskSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!askQuery.trim()) return;
    const queryText = askQuery;
    setAskQuery('');
    setStartingWorkflow(true);
    setError(null);
    try {
      const newWf = await workflowsApi.createWorkflow({
        client_id: 'default_org',
        title: queryText,
        directive: queryText
      });

      if (newWf) {
        await workflowsApi.startWorkflow(newWf.id);
        setActiveWorkflow(newWf);

        const tasks = await workflowsApi.getTasks(newWf.id);
        const translated = translateWorkflowToTasks(newWf, tasks);
        setActiveTask(translated.activeTask);
        setCompletedTasks(translated.completedTasks);
      }
    } catch {
      setError('StrtOS couldn\'t complete this request.');
    } finally {
      setStartingWorkflow(false);
    }
  };

  const handleQuickPrompt = (prompt: string) => {
    setAskQuery(prompt);
  };

  // Minimal Contextual Loading
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[450px] text-slate-100 space-y-3">
        <div className="w-8 h-8 rounded-full border-2 border-sky-500 border-t-transparent animate-spin"></div>
        <div className="text-center space-y-1">
          <h2 className="text-sm font-semibold tracking-wider text-slate-300">STRtOS</h2>
          <p className="text-xs text-[#92929A] font-mono">Loading workspace...</p>
        </div>
      </div>
    );
  }

  // Simplified Error State
  if (error && !activeTask && completedTasks.length === 0) {
    return (
      <div className="p-8 max-w-md mx-auto my-16 bg-[#111113] border border-white/10 rounded-xl space-y-4 text-center text-slate-100">
        <AlertCircle className="w-8 h-8 text-amber-400 mx-auto" />
        <div>
          <h2 className="text-sm font-semibold text-slate-200">{error}</h2>
          <p className="text-xs text-[#92929A] mt-1">Check network or server connection.</p>
        </div>
        <button
          onClick={loadData}
          className="px-4 py-2 rounded-lg text-xs font-medium bg-[#151518] hover:bg-slate-800 text-slate-200 border border-white/10 transition"
        >
          Retry
        </button>
      </div>
    );
  }

  const pendingDecision = overview?.active_decisions && overview.active_decisions.length > 0
    ? overview.active_decisions[0]
    : null;

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Top Header Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Compass className="w-7 h-7 text-sky-400" />
          <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">STRtOS</h1>
        </div>

        {/* Global Working / Ready Status */}
        <div>
          {activeTask ? (
            <span className="px-3 py-1.5 rounded-full text-xs font-mono bg-sky-950/60 border border-sky-800 text-sky-300 flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse"></span>
              <span>● StrtOS is working</span>
            </span>
          ) : (
            <span className="px-3 py-1.5 rounded-full text-xs font-mono bg-emerald-950/60 border border-emerald-800 text-emerald-300 flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span>StrtOS is ready</span>
            </span>
          )}
        </div>
      </div>

      {/* Governance Interrupt Banner */}
      {pendingDecision && (
        <div className="p-4 bg-amber-950/40 border border-amber-500/40 rounded-xl space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-mono text-amber-400 font-bold uppercase tracking-wider">
              <ShieldAlert className="w-4 h-4" />
              <span>ATTENTION REQUIRED</span>
            </div>
          </div>
          <div className="space-y-1 text-xs">
            <h3 className="font-bold text-[#F5F5F5] text-sm">{pendingDecision.title}</h3>
            <p className="text-slate-300">
              Risk: <span className="font-mono text-amber-300">{pendingDecision.risk_score || 'LOW'}</span> | Recommended: {pendingDecision.recommended_action || 'Review Decision'}
            </p>
          </div>
          <div className="pt-1">
            <button
              onClick={() => onNavigateToDecisions ? onNavigateToDecisions() : null}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500 text-slate-950 hover:bg-amber-400 transition flex items-center space-x-1.5"
            >
              <span>Review Required</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* Workspace Grid Layout: LEFT = Currently Working, RIGHT = Recent Results */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* LEFT COLUMN: CURRENTLY WORKING */}
        <div className="p-6 bg-[#111113] border border-white/10 rounded-xl space-y-5 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-sky-400 animate-ping"></span>
              <h2 className="text-xs font-mono uppercase tracking-wider text-sky-400 font-semibold">● CURRENTLY WORKING</h2>
            </div>
            {activeTask && (
              <span className="text-xs font-mono text-[#92929A]">{activeTask.timestamp}</span>
            )}
          </div>

          {activeTask ? (
            <div className="space-y-4">
              <div>
                <h3 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">
                  {mapInternalExecutionToBusinessLanguage(activeTask.title)}
                </h3>
                <p className="text-xs text-[#92929A] mt-1.5">
                  {activeTask.statusMessage || `Analyzing your ${mapInternalExecutionToBusinessLanguage(activeTask.title).toLowerCase()}.`}
                </p>

                {/* Real Numerical Progress % or Subtle Working State */}
                <div className="mt-4">
                  {typeof activeTask.progress === 'number' ? (
                    <div>
                      <div className="flex justify-between text-xs font-mono text-[#92929A] mb-1.5">
                        <span>Progress</span>
                        <span>{activeTask.progress}%</span>
                      </div>
                      <div className="w-full bg-[#151518] rounded-full h-1.5 overflow-hidden border border-white/10">
                        <div
                          className="bg-gradient-to-r from-sky-400 to-indigo-500 h-1.5 rounded-full transition-all duration-500"
                          style={{ width: `${activeTask.progress}%` }}
                        ></div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2 text-xs font-mono text-sky-400 pt-1">
                      <Activity className="w-3.5 h-3.5 animate-spin" />
                      <span>Analyzing...</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Real Task Steps from SSE events */}
              {activeTask.subSteps && activeTask.subSteps.length > 0 ? (
                <div className="space-y-2 pt-3 border-t border-white/5">
                  {activeTask.subSteps.map((step, idx) => (
                    <div key={idx} className="flex items-center space-x-2.5 text-xs">
                      <Activity className="w-3.5 h-3.5 text-sky-400 animate-spin shrink-0" />
                      <span className="text-sky-300 font-medium">{step}</span>
                    </div>
                  ))}
                </div>
              ) : null}
            </div>
          ) : (
            /* Calm Empty State */
            <div className="py-12 text-center space-y-3">
              <div className="w-10 h-10 rounded-full bg-[#151518] border border-white/10 flex items-center justify-center mx-auto text-sky-400">
                <Compass className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-[#F5F5F5]">STRtOS IS READY</h3>
              <p className="text-xs text-[#92929A]">No intelligence task is currently running.</p>
            </div>
          )}
        </div>

        {/* RIGHT COLUMN: RECENT RESULTS */}
        <div className="p-6 bg-[#111113] border border-white/10 rounded-xl space-y-4 shadow-lg">
          <h2 className="text-xs font-mono uppercase tracking-wider text-[#92929A] font-semibold flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>RECENT RESULTS</span>
          </h2>

          {completedTasks.length === 0 ? (
            <div className="py-12 text-center text-xs text-[#92929A] italic space-y-1">
              <p className="font-semibold text-slate-300">NO RECENT RESULTS</p>
              <p>Completed intelligence will appear here.</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-[340px] overflow-y-auto pr-1">
              {completedTasks.map((t) => (
                <div
                  key={t.id}
                  onClick={() => setSelectedCompletedTask(t)}
                  className="p-4 bg-[#151518] border border-white/5 hover:border-white/15 rounded-lg flex items-center justify-between cursor-pointer transition"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span className="font-semibold text-[#F5F5F5] text-sm">
                        {mapInternalExecutionToBusinessLanguage(t.title)}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500 pl-5 block">
                      Completed · {t.timestamp}
                    </span>
                    <p className="text-xs text-[#92929A] pl-5">
                      {t.summary || `${mapInternalExecutionToBusinessLanguage(t.title)} analysis completed.`}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (onNavigateToReports) {
                        onNavigateToReports();
                      } else {
                        setSelectedCompletedTask(t);
                      }
                    }}
                    className="flex items-center space-x-1 text-xs font-mono text-sky-400 shrink-0 hover:underline pl-2"
                  >
                    <span>View Report</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      {/* BOTTOM WORKSPACE BAR: ASK STRtOS */}
      <div className="p-5 bg-[#111113] border border-white/10 rounded-xl space-y-3 shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-mono text-sky-400 font-semibold">
            <Sparkles className="w-4 h-4" />
            <span>Ask StrtOS anything...</span>
          </div>

          {/* Quick Examples */}
          <div className="hidden sm:flex items-center space-x-2">
            <button
              onClick={() => handleQuickPrompt('Analyze my business performance')}
              className="px-2.5 py-1 rounded bg-[#151518] hover:bg-slate-800 text-[10px] font-mono text-[#92929A] hover:text-[#F5F5F5] border border-white/5 transition"
            >
              Analyze my business
            </button>
            <button
              onClick={() => handleQuickPrompt('Find growth opportunities')}
              className="px-2.5 py-1 rounded bg-[#151518] hover:bg-slate-800 text-[10px] font-mono text-[#92929A] hover:text-[#F5F5F5] border border-white/5 transition"
            >
              Find growth opportunities
            </button>
            <button
              onClick={() => handleQuickPrompt('Prepare a 90-day strategy')}
              className="px-2.5 py-1 rounded bg-[#151518] hover:bg-slate-800 text-[10px] font-mono text-[#92929A] hover:text-[#F5F5F5] border border-white/5 transition"
            >
              Prepare a 90-day strategy
            </button>
          </div>
        </div>

        <form onSubmit={handleAskSubmit} className="flex items-center space-x-3">
          <input
            type="text"
            value={askQuery}
            onChange={(e) => setAskQuery(e.target.value)}
            placeholder="Ask StrtOS anything... e.g. Analyze my business performance, Find growth opportunities"
            className="flex-1 bg-[#151518] border border-white/10 rounded-lg px-4 py-2.5 text-xs text-[#F5F5F5] outline-none placeholder:text-[#92929A]"
          />
          <button
            type="submit"
            disabled={startingWorkflow || !askQuery.trim()}
            className="px-5 py-2.5 rounded-lg text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 flex items-center space-x-2 transition disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{startingWorkflow ? 'Starting...' : 'Ask StrtOS'}</span>
          </button>
        </form>
      </div>

      {/* Result Details Report Modal (Optional view if modal pattern is triggered) */}
      {selectedCompletedTask && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#111113] border border-white/10 rounded-xl p-6 max-w-lg w-full space-y-4 text-slate-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-sky-400" />
                <h3 className="text-base font-bold text-[#F5F5F5]">
                  {mapInternalExecutionToBusinessLanguage(selectedCompletedTask.title)}
                </h3>
              </div>
              <button
                onClick={() => setSelectedCompletedTask(null)}
                className="text-slate-400 hover:text-slate-200 text-xs font-mono"
              >
                ✕ CLOSE
              </button>
            </div>

            <div className="p-4 bg-[#151518] border border-white/5 rounded-lg text-xs space-y-3">
              <div>
                <span className="text-[10px] font-mono text-emerald-400 uppercase font-bold block mb-1">Status: Completed</span>
                <span className="text-[10px] font-mono text-slate-500 uppercase block">Summary</span>
                <p className="text-slate-300 font-medium mt-0.5">
                  {selectedCompletedTask.summary || 'Summary not available yet.'}
                </p>
              </div>

              <div className="pt-2 border-t border-white/5 space-y-1">
                <span className="text-[10px] font-mono text-slate-500 uppercase block">Key Findings</span>
                <p className="text-slate-300">
                  {selectedCompletedTask.details?.findings && Array.isArray(selectedCompletedTask.details.findings) && selectedCompletedTask.details.findings.length > 0
                    ? selectedCompletedTask.details.findings.join('; ')
                    : 'Not available yet.'}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/5">
                <div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">Completed Time</span>
                  <span className="text-slate-300 font-mono">{selectedCompletedTask.timestamp || 'Not available yet.'}</span>
                </div>
                <div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">Confidence</span>
                  <span className="text-emerald-400 font-mono">
                    {typeof selectedCompletedTask.confidence === 'number' ? `${selectedCompletedTask.confidence}%` : 'Not available yet.'}
                  </span>
                </div>
              </div>

              <div className="pt-2 border-t border-white/5">
                <span className="text-[10px] font-mono text-slate-500 uppercase block">Recommended Next Step</span>
                <p className="text-sky-300">
                  {selectedCompletedTask.recommendedNextStep || 'Not available yet.'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
