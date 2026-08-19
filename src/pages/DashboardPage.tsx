import React, { useEffect, useState } from 'react';
import { dashboardApi } from '../services/dashboardApi';
import type { DashboardOverview, AgentPerformanceItem, RecentActivityItem } from '../services/dashboardApi';
import { BarChart3, Sparkles, Activity, Users, ListChecks, Award, BarChart2 } from 'lucide-react';
import { mapInternalExecutionToBusinessLanguage } from '../services/eventTranslationLayer';

interface DashboardPageProps {
  onOpenCEO?: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onOpenCEO }) => {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const dashboardData = await dashboardApi.getOverview();
      setData(dashboardData);
    } catch (error) {
      console.error('Failed to fetch dashboard data', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <BarChart3 className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Dashboard</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            Live performance metrics across all business operations.
          </p>
        </div>

        {onOpenCEO && (
          <button
            onClick={onOpenCEO}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 flex items-center space-x-2 transition"
          >
            <Sparkles className="w-4 h-4" />
            <span>Strategic Workspace</span>
          </button>
        )}
      </div>

      {loading ? (
        <p className="text-xs text-[#92929A]">Loading metrics...</p>
      ) : !data ? (
        <div className="p-8 bg-[#111113] border border-white/[0.06] rounded-xl text-center text-xs text-[#92929A] italic">
          No current data.
        </div>
      ) : (
        <>
          {/* Top KPI Cards Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
              <div className="flex items-center justify-between text-xs text-[#92929A] font-mono uppercase">
                <span>Total Accounts</span>
                <Users className="w-4 h-4 text-sky-400" />
              </div>
              <div className="text-2xl font-bold text-[#F5F5F5] mt-1">{data.clients.total_clients}</div>
              <div className="text-[10px] text-emerald-400 font-mono">{data.clients.active_clients} Active Accounts</div>
            </div>

            <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
              <div className="flex items-center justify-between text-xs text-[#92929A] font-mono uppercase">
                <span>Total Workflows</span>
                <Activity className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-2xl font-bold text-[#F5F5F5] mt-1">{data.workflows.total_workflows}</div>
              <div className="text-[10px] text-indigo-400 font-mono">{data.workflows.completed_workflows} Completed</div>
            </div>

            <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
              <div className="flex items-center justify-between text-xs text-[#92929A] font-mono uppercase">
                <span>Success Rate</span>
                <ListChecks className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold text-emerald-400 mt-1">{data.tasks.task_success_rate}%</div>
              <div className="text-[10px] text-[#92929A] font-mono">{data.tasks.completed_tasks}/{data.tasks.total_tasks} Tasks Executed</div>
            </div>

            <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
              <div className="flex items-center justify-between text-xs text-[#92929A] font-mono uppercase">
                <span>Avg Confidence</span>
                <Award className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-2xl font-bold text-amber-400 mt-1">{data.workflows.average_confidence_score}%</div>
              <div className="text-[10px] text-[#92929A] font-mono">Report Intelligence Baseline</div>
            </div>
          </div>

          {/* Automated Executive Insights Banner */}
          {data.insights && data.insights.length > 0 && (
            <div className="p-5 bg-sky-950/30 border border-sky-500/20 rounded-xl space-y-2 text-xs">
              <h3 className="font-semibold text-sky-400 flex items-center space-x-2">
                <Sparkles className="w-4 h-4" />
                <span>Executive Insights</span>
              </h3>
              <div className="space-y-1 text-[#F5F5F5]">
                {data.insights.map((insight: string, idx: number) => (
                  <div key={idx} className="flex items-center space-x-2">
                    <span className="text-sky-400">•</span>
                    <span>{insight}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Grid Layout: Execution Performance & Audit Events */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Operational Execution Performance */}
            <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
              <h3 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
                <BarChart2 className="w-4 h-4 text-sky-400" />
                <span>Operational Execution Performance</span>
              </h3>

              {data.agent_performance.length === 0 ? (
                <p className="text-xs text-[#92929A] italic">No current data.</p>
              ) : (
                <div className="space-y-2.5">
                  {data.agent_performance.map((agent: AgentPerformanceItem) => (
                    <div key={agent.agent_name} className="p-3 bg-[#151518] border border-white/5 rounded-lg flex items-center justify-between text-xs">
                      <div>
                        <div className="font-semibold text-[#F5F5F5]">{mapInternalExecutionToBusinessLanguage(agent.agent_name)}</div>
                        <div className="text-[10px] text-[#92929A] font-mono">{agent.completed_executions} Completed / {agent.total_executions} Total</div>
                      </div>
                      <div className="text-right font-mono">
                        <div className="font-bold text-emerald-400">{agent.success_rate}% Success</div>
                        <div className="text-[10px] text-sky-400">{agent.average_confidence}% Conf.</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Recent Audit Trail Events */}
            <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
              <h3 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
                <Activity className="w-4 h-4 text-emerald-400" />
                <span>Recent Audit Trail Events</span>
              </h3>

              {data.recent_activities.length === 0 ? (
                <p className="text-xs text-[#92929A] italic">No current data.</p>
              ) : (
                <div className="space-y-2.5">
                  {data.recent_activities.map((act: RecentActivityItem) => (
                    <div key={act.id} className="p-3 bg-[#151518] border border-white/5 rounded-lg flex items-center justify-between text-xs">
                      <div>
                        <div className="font-semibold text-sky-400">{mapInternalExecutionToBusinessLanguage(act.event_type)}</div>
                        <div className="text-[10px] text-[#92929A] font-mono">Workflow ID: {act.workflow_id}</div>
                      </div>
                      <div className="text-[10px] font-mono text-[#92929A]">
                        {new Date(act.created_at).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
