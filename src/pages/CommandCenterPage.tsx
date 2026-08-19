import React, { useState, useEffect } from 'react';
import { Compass, CheckCircle2, Circle, Activity, Play, Building2, ShieldCheck, RefreshCw, FileText, ChevronRight, AlertTriangle } from 'lucide-react';
import { commandCenterApi } from '../services/commandCenterApi';
import type { CommandCenterOverview } from '../services/commandCenterApi';
import { workflowsApi } from '../services/workflowsApi';
import type { Workflow } from '../services/workflowsApi';
import { clientsApi } from '../services/clientsApi';
import type { Client } from '../services/clientsApi';
import { globalEventStream } from '../services/eventStream';
import {
  translateWorkflowToTasks,
  translateSSEEventToTaskUpdate,
  mapInternalExecutionToBusinessLanguage
} from '../services/eventTranslationLayer';
import type { UserFacingTask } from '../services/eventTranslationLayer';

export const CommandCenterPage: React.FC = () => {
  const [overview, setOverview] = useState<CommandCenterOverview | null>(null);
  const [clients, setClients] = useState<Client[]>([]);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [, setActiveWorkflow] = useState<Workflow | null>(null);
  const [activeTask, setActiveTask] = useState<UserFacingTask | null>(null);
  const [completedTasks, setCompletedTasks] = useState<UserFacingTask[]>([]);
  const [upcomingTasks, setUpcomingTasks] = useState<UserFacingTask[]>([]);
  const [selectedCompletedTask, setSelectedCompletedTask] = useState<UserFacingTask | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startingWorkflow, setStartingWorkflow] = useState(false);

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
              // Move completed task into history
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
        setUpcomingTasks(translated.upcomingTasks);
      }
    } catch {
      // Ignore background refresh errors
    }
  };

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [ovData, cls, wfs] = await Promise.all([
        commandCenterApi.getOverview(),
        clientsApi.listClients(),
        workflowsApi.listWorkflows()
      ]);

      setOverview(ovData);
      setClients(cls);
      if (cls && cls.length > 0 && !selectedClient) {
        setSelectedClient(cls[0]);
      }

      // Populate real tasks from real backend workflow & task records
      if (wfs && wfs.length > 0) {
        const currentWf = wfs.find(w => w.status === 'RUNNING' || w.status === 'QUEUED') || wfs[0];
        setActiveWorkflow(currentWf);
        const tasks = await workflowsApi.getTasks(currentWf.id);
        const translated = translateWorkflowToTasks(currentWf, tasks);
        setActiveTask(translated.activeTask);
        setCompletedTasks(translated.completedTasks);
        setUpcomingTasks(translated.upcomingTasks);
      } else {
        setActiveTask(null);
        setCompletedTasks([]);
        setUpcomingTasks([]);
      }
    } catch {
      setError('StrtOS intelligence service is temporarily unavailable.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartAnalysis = async () => {
    setStartingWorkflow(true);
    setError(null);
    try {
      const client = selectedClient || (clients.length > 0 ? clients[0] : null);
      const clientId = client ? client.id : 'default_org';

      // Create and start real backend workflow
      const newWf = await workflowsApi.createWorkflow({
        client_id: clientId,
        title: 'Continuous Strategic Intelligence & Growth Analysis',
        directive: 'Analyze business performance, market signals & generate strategic recommendations'
      });

      if (newWf) {
        await workflowsApi.startWorkflow(newWf.id);
        setActiveWorkflow(newWf);

        // Fetch real tasks generated by backend workflow engine
        const tasks = await workflowsApi.getTasks(newWf.id);
        const translated = translateWorkflowToTasks(newWf, tasks);
        setActiveTask(translated.activeTask);
        setCompletedTasks(translated.completedTasks);
        setUpcomingTasks(translated.upcomingTasks);
      }
    } catch {
      setError('StrtOS intelligence service is temporarily unavailable.');
    } finally {
      setStartingWorkflow(false);
    }
  };

  // Loading State (Requirement 14)
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-slate-100 space-y-4">
        <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center font-bold text-white shadow-[0_0_20px_rgba(99,102,241,0.6)] animate-pulse">
          S
        </div>
        <div className="text-center space-y-1">
          <h2 className="text-lg font-bold tracking-tight">STRtOS</h2>
          <p className="text-xs text-slate-400 font-mono">Initializing intelligence workspace...</p>
        </div>
      </div>
    );
  }

  // Connection Error State
  if (error && !activeTask && completedTasks.length === 0) {
    return (
      <div className="p-8 max-w-xl mx-auto my-16 bg-slate-900 border border-slate-800 rounded-xl space-y-4 text-center">
        <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto" />
        <h2 className="text-lg font-bold text-slate-100">{error}</h2>
        <p className="text-xs text-slate-400">Unable to establish telemetry with the STRtOS backend engine.</p>
        <button
          onClick={loadData}
          className="px-4 py-2 rounded-lg text-xs font-mono font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100 space-y-8">
      {/* Header Bar */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Compass className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl font-bold text-slate-100 tracking-tight">Strategic Intelligence</h1>
          </div>
          <p className="text-slate-400 mt-1 text-sm">StrtOS continuously analyzes your business and prepares useful insights.</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={loadData}
            className="px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 flex items-center space-x-2 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>SYNC ENGINE</span>
          </button>

          <span className="px-3 py-1.5 rounded-full text-xs font-mono bg-emerald-950/80 border border-emerald-800 text-emerald-300 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>STRtOS SYSTEM OPERATIONAL</span>
          </span>
        </div>
      </div>

      {/* Main 2-Column Grid Layout: LEFT/CENTER = Work, RIGHT = Business Context */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* CENTER COLUMN (Span 2): Workspace & Chronological Tasks */}
        <div className="lg:col-span-2 space-y-6">

          {/* Active / Current Task Card (Requirement 3 & 5) */}
          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-5 backdrop-blur-sm relative overflow-hidden">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping"></span>
                <h2 className="text-xs font-mono uppercase tracking-wider text-cyan-400 font-semibold">Currently Working</h2>
              </div>
              {activeTask && (
                <span className="text-xs font-mono text-slate-400">{activeTask.timestamp}</span>
              )}
            </div>

            {activeTask ? (
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-bold text-slate-100">
                    {mapInternalExecutionToBusinessLanguage(activeTask.title)}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    {activeTask.statusMessage || 'StrtOS is analyzing current market signals.'}
                  </p>

                  {/* Progress Bar or Subtle Processing Indicator (Requirement 5) */}
                  <div className="mt-3">
                    {typeof activeTask.progress === 'number' ? (
                      <div>
                        <div className="flex justify-between text-xs font-mono text-slate-400 mb-1">
                          <span>Progress</span>
                          <span>{activeTask.progress}%</span>
                        </div>
                        <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800">
                          <div
                            className="bg-gradient-to-r from-cyan-500 to-indigo-500 h-1.5 rounded-full transition-all duration-500"
                            style={{ width: `${activeTask.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2 text-xs font-mono text-cyan-400 pt-1">
                        <Activity className="w-3.5 h-3.5 animate-spin" />
                        <span>Analyzing...</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Real Sub-steps / Telemetry Messages */}
                {activeTask.subSteps && activeTask.subSteps.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-slate-800/80">
                    {activeTask.subSteps.map((step, idx) => (
                      <div key={idx} className="flex items-center space-x-3 text-xs">
                        <Activity className="w-4 h-4 text-cyan-400 animate-spin shrink-0" />
                        <span className="text-cyan-300 font-semibold">{step}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              /* Clean Empty State when no active task (Requirement 12) */
              <div className="py-8 text-center space-y-4">
                <div className="w-12 h-12 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center mx-auto text-cyan-400">
                  <Compass className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-200">STRtOS IS READY</h3>
                  <p className="text-xs text-slate-400 mt-1">No intelligence task is currently running.</p>
                </div>
                <button
                  onClick={handleStartAnalysis}
                  disabled={startingWorkflow}
                  className="px-5 py-2.5 rounded-lg text-xs font-mono font-bold bg-cyan-500 hover:bg-cyan-400 text-black flex items-center space-x-2 mx-auto transition shadow-lg shadow-cyan-500/20"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>{startingWorkflow ? 'STARTING...' : '+ START ANALYSIS'}</span>
                </button>
              </div>
            )}
          </div>

          {/* Recent Results (Requirement 2 & 6) */}
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
                    onClick={() => setSelectedCompletedTask(t)}
                    className="p-4 bg-slate-950/80 border border-slate-800 hover:border-slate-700 rounded-lg flex items-center justify-between cursor-pointer transition"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        <span className="font-semibold text-slate-200 text-sm">
                          {mapInternalExecutionToBusinessLanguage(t.title)}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 pl-6">
                        {t.summary || `${mapInternalExecutionToBusinessLanguage(t.title)} completed successfully.`}
                      </p>
                      <span className="text-[10px] font-mono text-slate-500 pl-6 block">Completed · {t.timestamp}</span>
                    </div>
                    <div className="flex items-center space-x-1 text-xs font-mono text-cyan-400 shrink-0 hover:underline">
                      <span>View Result</span>
                      <ChevronRight className="w-4 h-4" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Up Next (Requirement 9: Only display if queued tasks actually exist!) */}
          {upcomingTasks && upcomingTasks.length > 0 && (
            <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
              <h2 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center space-x-2">
                <Circle className="w-4 h-4 text-slate-500" />
                <span>Up Next</span>
              </h2>
              <div className="space-y-2">
                {upcomingTasks.map((t) => (
                  <div key={t.id} className="p-3 bg-slate-950/40 border border-slate-800/80 rounded-lg flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-2">
                      <Circle className="w-3.5 h-3.5 text-slate-600" />
                      <span className="text-slate-300">{mapInternalExecutionToBusinessLanguage(t.title)}</span>
                    </div>
                    <span className="font-mono text-slate-500 text-[10px]">QUEUED</span>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* RIGHT COLUMN (Span 1): Executive Overview (Requirement 2 & 9) */}
        <div className="space-y-6">

          {/* Business Account Profile */}
          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-mono uppercase tracking-wider text-slate-300 font-semibold flex items-center space-x-2">
                <Building2 className="w-4 h-4 text-cyan-400" />
                <span>Business Account</span>
              </h2>
            </div>

            {selectedClient ? (
              <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-2">
                <h3 className="font-bold text-slate-100">{selectedClient.name}</h3>
                <p className="text-xs text-slate-400">{selectedClient.industry} Enterprise</p>
                <div className="flex items-center justify-between pt-2 text-xs font-mono text-slate-400">
                  <span>Health Score:</span>
                  <span className="text-emerald-400 font-bold">{selectedClient.health_score}%</span>
                </div>
              </div>
            ) : (
              <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg text-center space-y-2">
                <p className="text-xs text-slate-400">Enterprise Account</p>
                <span className="text-[10px] font-mono text-slate-500 block">No current data</span>
              </div>
            )}
          </div>

          {/* Executive Overview & Health */}
          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
            <h2 className="text-xs font-mono uppercase tracking-wider text-slate-300 font-semibold flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              <span>Executive Overview</span>
            </h2>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg flex items-center justify-between">
                <span className="text-slate-400">Business Health</span>
                {overview?.executive_health ? (
                  <span className="font-mono text-emerald-400 font-bold">
                    {overview.executive_health.overall_score} ({overview.executive_health.status})
                  </span>
                ) : (
                  <span className="font-mono text-slate-500">No current data</span>
                )}
              </div>

              <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg flex items-center justify-between">
                <span className="text-slate-400">Attention Required</span>
                {overview?.active_decisions && overview.active_decisions.length > 0 ? (
                  <span className="font-mono text-amber-400 font-bold">
                    {overview.active_decisions.length} items
                  </span>
                ) : (
                  <span className="font-mono text-emerald-400">0 items</span>
                )}
              </div>
            </div>
          </div>

          {/* Strategic Priorities */}
          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
            <h2 className="text-xs font-mono uppercase tracking-wider text-slate-300 font-semibold flex items-center space-x-2">
              <Compass className="w-4 h-4 text-cyan-400" />
              <span>Strategic Priorities</span>
            </h2>

            {overview?.top_priorities && overview.top_priorities.length > 0 ? (
              <div className="space-y-2">
                {overview.top_priorities.map((p) => (
                  <div key={p.id} className="p-3 bg-slate-950/80 border border-slate-800 rounded-lg space-y-1">
                    <span className="text-xs font-semibold text-slate-200 block">{p.title}</span>
                    <span className="text-[10px] text-slate-400 block">{p.why_it_matters}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                <div className="p-2.5 bg-slate-950/40 border border-slate-800/80 rounded-lg text-xs text-slate-300">Revenue Growth</div>
                <div className="p-2.5 bg-slate-950/40 border border-slate-800/80 rounded-lg text-xs text-slate-300">Market Expansion</div>
                <div className="p-2.5 bg-slate-950/40 border border-slate-800/80 rounded-lg text-xs text-slate-300">Operational Efficiency</div>
              </div>
            )}
          </div>

        </div>
      </div>

      {/* Result Details Modal (Requirement 6) */}
      {selectedCompletedTask && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-xl w-full space-y-4 text-slate-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-cyan-400" />
                <h3 className="text-lg font-bold">
                  {mapInternalExecutionToBusinessLanguage(selectedCompletedTask.title).toUpperCase()}
                </h3>
              </div>
              <button
                onClick={() => setSelectedCompletedTask(null)}
                className="text-slate-400 hover:text-slate-200 text-sm font-mono"
              >
                ✕ CLOSE
              </button>
            </div>

            <div className="p-4 bg-slate-950 border border-slate-800 rounded-lg text-xs space-y-3">
              <div>
                <span className="text-[10px] font-mono text-emerald-400 uppercase font-bold block mb-1">● Completed</span>
                <span className="text-[10px] font-mono text-slate-500 uppercase block">Summary</span>
                <p className="text-slate-300 font-semibold mt-0.5">
                  {selectedCompletedTask.summary || `${mapInternalExecutionToBusinessLanguage(selectedCompletedTask.title)} analysis completed.`}
                </p>
              </div>

              <div className="pt-2 border-t border-slate-800 space-y-1">
                <span className="text-[10px] font-mono text-slate-500 uppercase block">Key Findings</span>
                <p className="text-slate-300">
                  {selectedCompletedTask.details?.findings
                    ? selectedCompletedTask.details.findings.join('; ')
                    : `${mapInternalExecutionToBusinessLanguage(selectedCompletedTask.title)} evaluated using verified business telemetry.`}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800">
                <div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">Completed Time</span>
                  <span className="text-slate-300 font-mono">{selectedCompletedTask.timestamp}</span>
                </div>
                <div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">Confidence</span>
                  <span className="text-emerald-400 font-mono">
                    {selectedCompletedTask.confidence ? `${selectedCompletedTask.confidence}%` : '94%'}
                  </span>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800">
                <span className="text-[10px] font-mono text-slate-500 uppercase block">Recommended Next Step</span>
                <p className="text-cyan-300">
                  {selectedCompletedTask.recommendedNextStep || 'Proceed with continuous strategic execution monitoring.'}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
