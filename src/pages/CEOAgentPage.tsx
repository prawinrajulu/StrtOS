import React, { useState, useEffect } from 'react';
import { StatusBadge } from '../components/StatusBadge';
import { TaskItem } from '../components/TaskItem';
import type { TaskItemProps } from '../components/TaskItem';
import { Compass, Plus, FileText } from 'lucide-react';
import { DirectiveModal } from '../components/DirectiveModal';
import { ExecutiveReportModal } from '../components/ExecutiveReportModal';
import { CEOApiService } from '../services/ceoApi';
import type { ExecutionStateData, ExecutiveReportData } from '../services/ceoApi';
import { mapInternalExecutionToBusinessLanguage } from '../services/eventTranslationLayer';

export const CEOAgentPage: React.FC = () => {
  const [executionState, setExecutionState] = useState<ExecutionStateData | null>(null);
  const [report, setReport] = useState<ExecutiveReportData | null>(null);
  const [isDirectiveOpen, setIsDirectiveOpen] = useState(false);
  const [isReportOpen, setIsReportOpen] = useState(false);

  useEffect(() => {
    const unsubscribe = CEOApiService.subscribeToStream((state) => {
      if (state) setExecutionState(state);
    });
    return () => unsubscribe();
  }, []);

  const handleDirectiveSubmit = async (directive: string, clientName: string) => {
    try {
      await CEOApiService.submitDirective(directive, clientName);
    } catch (err) {
      console.error('Failed submitting directive:', err);
    }
  };

  const handleOpenReport = async () => {
    try {
      const rep = await CEOApiService.fetchReport();
      if (rep) setReport(rep);
    } catch (err) {
      console.warn('Failed to fetch report:', err);
    }
    setIsReportOpen(true);
  };

  const displayTasks: TaskItemProps[] = executionState?.tasks
    ? executionState.tasks.map((t) => ({
        title: t.title,
        agent: mapInternalExecutionToBusinessLanguage(t.agent_name),
        eta: t.eta,
        priority: t.priority,
        status: t.status,
      }))
    : [];

  const displayStages = executionState?.stages && executionState.stages.length > 0
    ? executionState.stages.map((stg) => ({
        name: mapInternalExecutionToBusinessLanguage(stg.name || stg.agent_name),
        status: stg.status,
      }))
    : [];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Compass className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl font-bold text-slate-100 tracking-tight">Strategic Intelligence</h1>
          </div>
          <p className="text-slate-400 mt-1">Autonomous business state monitoring, predictive strategy & executive alignment.</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsDirectiveOpen(true)}
            className="px-4 py-2 rounded-lg text-xs font-mono font-bold bg-linear-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-black flex items-center space-x-2 transition shadow-lg shadow-cyan-500/20"
          >
            <Plus className="w-4 h-4" />
            <span>NEW DIRECTIVE</span>
          </button>
          <button
            onClick={handleOpenReport}
            className="px-4 py-2 rounded-lg text-xs font-mono font-bold bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 flex items-center space-x-2 transition"
          >
            <FileText className="w-4 h-4" />
            <span>EXECUTIVE REPORT</span>
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
            <h2 className="text-sm font-semibold text-slate-100 uppercase font-mono tracking-wider">Current Activity</h2>
            {displayTasks.length === 0 ? (
              <div className="py-6 text-center text-xs text-slate-400 italic">
                No active intelligence tasks in queue.
              </div>
            ) : (
              <div className="space-y-3">
                {displayTasks.map((task, idx) => (
                  <TaskItem key={idx} {...task} />
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
            <h2 className="text-sm font-semibold text-slate-100 uppercase font-mono tracking-wider">Recent Activity</h2>
            {displayStages.length === 0 ? (
              <div className="py-6 text-center text-xs text-slate-400 italic space-y-1">
                <p className="font-semibold text-slate-300">No active intelligence workflow.</p>
                <p className="text-[10px]">Trigger a strategic directive to initiate execution.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {displayStages.map((stg, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2.5 bg-slate-950/60 border border-slate-800/80 rounded-lg text-xs">
                    <span className="text-slate-300 font-medium">{stg.name}</span>
                    <StatusBadge status={stg.status} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <DirectiveModal
        isOpen={isDirectiveOpen}
        onClose={() => setIsDirectiveOpen(false)}
        onSubmit={handleDirectiveSubmit}
      />
      <ExecutiveReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        report={report}
      />
    </div>
  );
};
