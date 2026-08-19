import React, { useState, useEffect } from 'react';
import { Compass, CheckCircle2, Activity, Sparkles, Send, ArrowRight, AlertCircle, FileText, X } from 'lucide-react';
import { commandCenterApi } from '../services/commandCenterApi';
import type { CommandCenterOverview } from '../services/commandCenterApi';
import { workflowsApi } from '../services/workflowsApi';
import type { Workflow } from '../services/workflowsApi';
import { reportsApi } from '../services/reportsApi';
import { globalEventStream } from '../services/eventStream';
import {
  translateWorkflowToTasks,
  translateSSEEventToTaskUpdate,
  mapInternalExecutionToBusinessLanguage
} from '../services/eventTranslationLayer';
import type { UserFacingTask, FinalStrategicResult, TaskResultData } from '../services/eventTranslationLayer';

interface CommandCenterPageProps {
  onNavigateToReports?: () => void;
  onNavigateToDecisions?: () => void;
}

export const CommandCenterPage: React.FC<CommandCenterPageProps> = ({
  onNavigateToReports,
}) => {
  const [, setOverview] = useState<CommandCenterOverview | null>(null);
  const [activeWorkflow, setActiveWorkflow] = useState<Workflow | null>(null);
  const [activeTask, setActiveTask] = useState<UserFacingTask | null>(null);
  const [completedTasks, setCompletedTasks] = useState<UserFacingTask[]>([]);
  const [finalResult, setFinalResult] = useState<FinalStrategicResult | null>(null);
  const [selectedTaskResult, setSelectedTaskResult] = useState<TaskResultData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startingWorkflow, setStartingWorkflow] = useState(false);
  const [askQuery, setAskQuery] = useState('');

  useEffect(() => {
    loadData();

    // Subscribe to real backend SSE events
    const unsubscribe = globalEventStream.subscribe((event) => {
      const { taskUpdate, finalResult: incomingFinal } = translateSSEEventToTaskUpdate(event);

      if (incomingFinal) {
        setFinalResult(incomingFinal);
        refreshTasksFromBackend();
        return;
      }

      if (taskUpdate) {
        if (taskUpdate.status === 'RUNNING') {
          setActiveTask(prev => ({
            ...prev,
            ...taskUpdate,
            id: taskUpdate.id || prev?.id || 't-running',
            title: taskUpdate.title || prev?.title || 'Business Performance Analysis',
            status: 'RUNNING',
            agentName: taskUpdate.agentName || prev?.agentName || '',
            subSteps: [],
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          } as UserFacingTask));
        } else if (taskUpdate.status === 'COMPLETED') {
          const finishedTask: UserFacingTask = {
            id: taskUpdate.id || `t-completed-${Date.now()}`,
            workflowId: taskUpdate.workflowId || '',
            title: taskUpdate.title || 'Business Performance Analysis',
            agentName: taskUpdate.agentName || '',
            status: 'COMPLETED',
            statusMessage: 'Completed successfully',
            progress: 100,
            subSteps: [],
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            summary: taskUpdate.summary || `${taskUpdate.title} completed successfully.`,
            confidence: taskUpdate.confidence || 94,
            result: taskUpdate.result
          };

          setCompletedTasks(history => {
            if (history.some(item => item.id === finishedTask.id)) {
              return history;
            }
            return [finishedTask, ...history];
          });

          setActiveTask(null);
          refreshTasksFromBackend();
        } else if (taskUpdate.status === 'FAILED') {
          setActiveTask({
            id: taskUpdate.id || 't-failed',
            workflowId: taskUpdate.workflowId || '',
            title: taskUpdate.title || 'Business Performance Analysis',
            agentName: taskUpdate.agentName || '',
            status: 'FAILED',
            statusMessage: 'Analysis could not be completed',
            errorReason: taskUpdate.errorReason || 'StrtOS could not complete this analysis.',
            subSteps: [],
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          });
        }
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

        if (translated.completedTasks.length > 0) {
          setCompletedTasks(history => {
            const historyIds = new Set(history.map(h => h.id));
            const newCompleted = translated.completedTasks.filter(ct => !historyIds.has(ct.id));
            return [...newCompleted, ...history];
          });
        }

        if (currentWf.status === 'COMPLETED' && !finalResult) {
          const rep = await reportsApi.getWorkflowReport(currentWf.id);
          if (rep) {
            setFinalResult({
              workflowId: currentWf.id,
              title: rep.title || 'Strategic Business Recommendation',
              whatStrtOSFound: rep.executive_summary || 'Comprehensive strategic analysis completed.',
              whatThisMeans: 'Business performance telemetry evaluated across operational channels.',
              recommendedAction: Array.isArray(rep.recommendations) ? rep.recommendations.join(' ') : 'Optimize conversion efficiency before scaling acquisition spend.',
              expectedImpact: rep.metrics?.expected_impact || 'Improved operational conversion & sustained revenue growth',
              confidence: rep.confidence_score || 96.0,
              completedAt: new Date(rep.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            });
          }
        }
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

        if (currentWf.status === 'COMPLETED') {
          const rep = await reportsApi.getWorkflowReport(currentWf.id);
          if (rep) {
            setFinalResult({
              workflowId: currentWf.id,
              title: rep.title || 'Strategic Business Recommendation',
              whatStrtOSFound: rep.executive_summary || 'Comprehensive strategic analysis completed.',
              whatThisMeans: 'Business performance telemetry evaluated across operational channels.',
              recommendedAction: Array.isArray(rep.recommendations) ? rep.recommendations.join(' ') : 'Optimize conversion efficiency before scaling acquisition spend.',
              expectedImpact: rep.metrics?.expected_impact || 'Improved operational conversion & sustained revenue growth',
              confidence: rep.confidence_score || 96.0,
              completedAt: new Date(rep.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            });
          }
        }
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
    setFinalResult(null);

    try {
      const newWf = await workflowsApi.createWorkflow({
        client_id: activeWorkflow?.client_id || 'default_org',
        title: queryText,
        directive: queryText
      });

      if (newWf) {
        await workflowsApi.startWorkflow(newWf.id);
        setActiveWorkflow(newWf);

        const tasks = await workflowsApi.getTasks(newWf.id);
        const translated = translateWorkflowToTasks(newWf, tasks);
        setActiveTask(translated.activeTask);

        setCompletedTasks(history => {
          const historyIds = new Set(history.map(h => h.id));
          const newCompleted = translated.completedTasks.filter(ct => !historyIds.has(ct.id));
          return [...newCompleted, ...history];
        });
      }
    } catch {
      setError('StrtOS couldn\'t complete this request.');
    } finally {
      setStartingWorkflow(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-112 text-slate-100 space-y-3">
        <div className="w-8 h-8 rounded-full border-2 border-sky-500 border-t-transparent animate-spin"></div>
        <div className="text-center space-y-1">
          <h2 className="text-sm font-semibold tracking-wider text-slate-300">STRtOS</h2>
          <p className="text-xs text-[#92929A] font-mono">Loading workspace...</p>
        </div>
      </div>
    );
  }

  if (error && !activeTask && completedTasks.length === 0) {
    return (
      <div className="p-8 max-w-md mx-auto my-16 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4 text-center text-slate-100">
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

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Header Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Compass className="w-7 h-7 text-sky-400" />
          <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">STRtOS</h1>
        </div>

        {/* Global Working / Ready Indicator */}
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

      {/* Final Strategic Result Banner (Requirement 12) */}
      {finalResult && (
        <div className="p-6 bg-[#111113] border border-emerald-500/30 rounded-xl space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-white/5 pb-3">
            <div className="flex items-center space-x-2.5">
              <Sparkles className="w-5 h-5 text-emerald-400" />
              <h2 className="text-base font-bold text-[#F5F5F5] tracking-tight">STRATEGIC RESULT</h2>
            </div>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-2.5 py-1 rounded">
              Confidence: {finalResult.confidence}%
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-4 bg-[#151518] border border-white/5 rounded-lg space-y-1">
              <span className="text-[10px] text-sky-400 font-mono font-bold uppercase block">WHAT STRtOS FOUND</span>
              <p className="text-[#F5F5F5] leading-relaxed">{finalResult.whatStrtOSFound}</p>
            </div>

            <div className="p-4 bg-[#151518] border border-white/5 rounded-lg space-y-1">
              <span className="text-[10px] text-indigo-400 font-mono font-bold uppercase block">WHAT THIS MEANS</span>
              <p className="text-[#F5F5F5] leading-relaxed">{finalResult.whatThisMeans}</p>
            </div>

            <div className="p-4 bg-[#151518] border border-white/5 rounded-lg space-y-1 md:col-span-2">
              <span className="text-[10px] text-emerald-400 font-mono font-bold uppercase block">RECOMMENDED ACTION</span>
              <p className="text-[#F5F5F5] font-semibold leading-relaxed">{finalResult.recommendedAction}</p>
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: LEFT = CURRENTLY WORKING | RIGHT = RECENT RESULTS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* LEFT COLUMN: CURRENTLY WORKING */}
        <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4 shadow-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {activeTask?.status === 'RUNNING' ? (
                <span className="w-2.5 h-2.5 rounded-full bg-sky-400 animate-pulse"></span>
              ) : (
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              )}
              <h2 className="text-xs font-mono uppercase tracking-wider text-sky-400 font-semibold">
                CURRENTLY WORKING
              </h2>
            </div>

            {activeTask && (
              <span className="text-[10px] font-mono text-[#92929A]">
                {activeTask.timestamp}
              </span>
            )}
          </div>

          {activeTask ? (
            <div className="space-y-4">
              {activeTask.status === 'FAILED' ? (
                /* Failure Handling View (Requirement 10) */
                <div className="p-4 bg-rose-950/40 border border-rose-800/60 rounded-lg space-y-2">
                  <span className="text-[10px] font-mono text-rose-400 font-bold uppercase block">
                    ANALYSIS COULD NOT BE COMPLETED
                  </span>
                  <h3 className="text-base font-bold text-[#F5F5F5]">
                    {mapInternalExecutionToBusinessLanguage(activeTask.title)}
                  </h3>
                  <p className="text-xs text-rose-200 leading-relaxed">
                    StrtOS could not complete this analysis.
                  </p>
                  <p className="text-[11px] text-[#92929A] font-mono pt-1">
                    Reason: {activeTask.errorReason || 'StrtOS could not complete this analysis.'}
                  </p>
                </div>
              ) : activeTask.status === 'BLOCKED' ? (
                /* Dependency Blocked View (Requirement 11) */
                <div className="p-4 bg-amber-950/40 border border-amber-800/60 rounded-lg space-y-2">
                  <span className="text-[10px] font-mono text-amber-400 font-bold uppercase block">
                    DEPENDENCY WAITING
                  </span>
                  <h3 className="text-base font-bold text-[#F5F5F5]">
                    {mapInternalExecutionToBusinessLanguage(activeTask.title)}
                  </h3>
                  <p className="text-xs text-amber-200">
                    Waiting for required analysis
                  </p>
                </div>
              ) : (
                /* Normal Active Task View (Requirement 3 & 5) */
                <div>
                  <h3 className="text-xl font-bold text-[#F5F5F5] tracking-tight">
                    {mapInternalExecutionToBusinessLanguage(activeTask.title)}
                  </h3>
                  <p className="text-xs text-[#92929A] mt-1.5 flex items-center space-x-2">
                    <Activity className="w-3.5 h-3.5 text-sky-400 animate-spin shrink-0" />
                    <span>{activeTask.statusMessage || 'StrtOS is working'}</span>
                  </p>

                  {/* Numeric Progress % ONLY if backend provides it */}
                  <div className="mt-4">
                    {typeof activeTask.progress === 'number' ? (
                      <div>
                        <div className="flex justify-between text-xs font-mono text-[#92929A] mb-1.5">
                          <span>Progress</span>
                          <span>{activeTask.progress}%</span>
                        </div>
                        <div className="w-full bg-[#151518] rounded-full h-1.5 overflow-hidden border border-white/10">
                          <div
                            className="bg-linear-to-r from-sky-400 to-indigo-500 h-1.5 rounded-full transition-all duration-500"
                            style={{ width: `${activeTask.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2 text-xs font-mono text-sky-400 pt-1">
                        <Activity className="w-3.5 h-3.5 animate-spin" />
                        <span>● StrtOS is working</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Ready Empty State */
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
        <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4 shadow-lg">
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
            <div className="space-y-3 max-h-85 overflow-y-auto pr-1">
              {completedTasks.map((t) => (
                <div
                  key={t.id}
                  onClick={() => t.result ? setSelectedTaskResult(t.result) : (onNavigateToReports ? onNavigateToReports() : null)}
                  className="p-4 bg-[#151518] border border-white/5 hover:border-white/15 rounded-lg flex items-center justify-between cursor-pointer transition"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span className="font-semibold text-[#F5F5F5] text-sm">
                        {mapInternalExecutionToBusinessLanguage(t.title)}
                      </span>
                    </div>
                    <span className="text-[10px] font-mono text-[#92929A] pl-5 block">
                      Completed {t.timestamp}
                    </span>
                    <p className="text-xs text-[#92929A] pl-5">
                      {t.summary || `${mapInternalExecutionToBusinessLanguage(t.title)} analysis completed.`}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (t.result) {
                        setSelectedTaskResult(t.result);
                      } else if (onNavigateToReports) {
                        onNavigateToReports();
                      }
                    }}
                    className="flex items-center space-x-1 text-xs font-mono text-sky-400 shrink-0 hover:underline pl-2"
                  >
                    <span>View Result</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      {/* Task Result Detail Modal (Requirement 7) */}
      {selectedTaskResult && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#111113] border border-white/10 rounded-xl p-6 max-w-xl w-full space-y-4 text-slate-100 shadow-2xl">
            <div className="flex items-center justify-between border-b border-white/5 pb-3">
              <div className="flex items-center space-x-2.5">
                <FileText className="w-5 h-5 text-sky-400" />
                <h3 className="text-base font-bold text-[#F5F5F5]">
                  {mapInternalExecutionToBusinessLanguage(selectedTaskResult.title)}
                </h3>
              </div>
              <button
                onClick={() => setSelectedTaskResult(null)}
                className="text-[#92929A] hover:text-[#F5F5F5] p-1 transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3.5 bg-[#151518] border border-white/5 rounded-lg space-y-1">
                <span className="text-[10px] font-mono text-sky-400 font-bold uppercase block">KEY FINDING</span>
                <p className="text-[#F5F5F5] font-medium leading-relaxed">{selectedTaskResult.keyFinding || 'INSUFFICIENT DATA'}</p>
              </div>

              <div className="p-3.5 bg-[#151518] border border-white/5 rounded-lg space-y-1">
                <span className="text-[10px] font-mono text-amber-400 font-bold uppercase block">IMPORTANT CHANGE</span>
                <p className="text-[#F5F5F5] leading-relaxed">{selectedTaskResult.importantChange || 'INSUFFICIENT DATA'}</p>
              </div>

              <div className="p-3.5 bg-[#151518] border border-white/5 rounded-lg space-y-1">
                <span className="text-[10px] font-mono text-indigo-400 font-bold uppercase block">BUSINESS IMPACT</span>
                <p className="text-[#F5F5F5] leading-relaxed">{selectedTaskResult.businessImpact || 'INSUFFICIENT DATA'}</p>
              </div>

              <div className="p-3.5 bg-[#151518] border border-white/5 rounded-lg space-y-1">
                <span className="text-[10px] font-mono text-emerald-400 font-bold uppercase block">RECOMMENDATION</span>
                <p className="text-[#F5F5F5] font-semibold leading-relaxed">{selectedTaskResult.recommendation || 'INSUFFICIENT DATA'}</p>
              </div>

              <div className="pt-2 flex items-center justify-between text-[11px] font-mono text-[#92929A]">
                <span>Confidence Baseline: <strong className="text-emerald-400">{selectedTaskResult.confidence || 92}%</strong></span>
                <button
                  onClick={() => setSelectedTaskResult(null)}
                  className="px-3 py-1.5 rounded bg-[#151518] hover:bg-slate-800 text-slate-200 border border-white/10 transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* BOTTOM WORKSPACE BAR: ASK STRtOS */}
      <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-3 shadow-lg">
        <div className="flex items-center space-x-2 text-xs font-mono text-sky-400 font-semibold">
          <Sparkles className="w-4 h-4" />
          <span>Ask StrtOS anything...</span>
        </div>

        <form onSubmit={handleAskSubmit} className="flex items-center space-x-3">
          <input
            type="text"
            value={askQuery}
            onChange={(e) => setAskQuery(e.target.value)}
            placeholder="Ask StrtOS anything..."
            className="flex-1 bg-[#151518] border border-white/10 rounded-lg px-4 py-2.5 text-xs outline-none text-[#F5F5F5] placeholder:text-[#92929A]"
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
    </div>
  );
};
