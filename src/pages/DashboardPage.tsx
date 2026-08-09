import React, { useEffect, useState } from 'react';
import {
  Users, BrainCircuit, Activity, Award, Sparkles,
  ListChecks, BarChart2
} from 'lucide-react';
import { dashboardApi } from '../services/dashboardApi';
import type { DashboardOverview } from '../services/dashboardApi';

export const DashboardPage: React.FC<{ onOpenCEO: () => void }> = ({ onOpenCEO }) => {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  const loadData = async () => {
    setLoading(true);
    const overview = await dashboardApi.getOverview(days);
    setData(overview);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [days]);

  return (
    <div style={{ padding: '32px 40px', maxWidth: '1600px', margin: '0 auto' }}>
      {/* Top Welcome Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '28px' }}>
        <div>
          <div
            style={{
              fontSize: '11px',
              fontFamily: "'JetBrains Mono', monospace",
              color: '#6b7280',
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              marginBottom: '6px',
            }}
          >
            STRTOS EXECUTIVE DASHBOARD • REAL-TIME INTELLIGENCE
          </div>
          <h1 style={{ fontSize: '32px', fontWeight: 700, color: '#ffffff', letterSpacing: '-0.02em', margin: 0 }}>
            Executive Operations Brief
          </h1>
          <p style={{ fontSize: '14px', color: '#9ca3af', marginTop: '4px' }}>
            Live performance metrics aggregated from Supabase PostgreSQL & CEO Orchestrator Engine.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            style={{
              backgroundColor: '#111827',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              padding: '8px 14px',
              color: '#e5e7eb',
              fontSize: '13px'
            }}
          >
            <option value={7}>Last 7 Days</option>
            <option value={30}>Last 30 Days</option>
            <option value={90}>Last 90 Days</option>
          </select>

          <button
            onClick={onOpenCEO}
            style={{
              background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 18px',
              color: '#ffffff',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: '0 4px 14px rgba(99, 102, 241, 0.35)',
            }}
          >
            <Sparkles size={16} /> Open CEO Agent
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ padding: '80px', textAlign: 'center', color: '#9ca3af' }}>Loading real-time executive metrics...</div>
      ) : !data ? (
        <div style={{ padding: '60px', textAlign: 'center', color: '#ef4444' }}>
          Failed loading dashboard metrics. Ensure backend server is running.
        </div>
      ) : (
        <>
          {/* Top KPI Cards Row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '18px', marginBottom: '28px' }}>
            <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
              <div style={{ fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
                <span>TOTAL CLIENTS</span>
                <Users size={16} style={{ color: '#6366f1' }} />
              </div>
              <div style={{ fontSize: '28px', fontWeight: '700', color: '#ffffff' }}>{data.clients.total_clients}</div>
              <div style={{ fontSize: '12px', color: '#10b981', marginTop: '6px' }}>{data.clients.active_clients} Active Accounts</div>
            </div>

            <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
              <div style={{ fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
                <span>WORKFLOWS</span>
                <BrainCircuit size={16} style={{ color: '#8b5cf6' }} />
              </div>
              <div style={{ fontSize: '28px', fontWeight: '700', color: '#ffffff' }}>{data.workflows.total_workflows}</div>
              <div style={{ fontSize: '12px', color: '#8b5cf6', marginTop: '6px' }}>{data.workflows.completed_workflows} Completed Campaigns</div>
            </div>

            <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
              <div style={{ fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
                <span>TASK SUCCESS RATE</span>
                <ListChecks size={16} style={{ color: '#10b981' }} />
              </div>
              <div style={{ fontSize: '28px', fontWeight: '700', color: '#10b981' }}>{data.tasks.task_success_rate}%</div>
              <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '6px' }}>{data.tasks.completed_tasks}/{data.tasks.total_tasks} Tasks Executed</div>
            </div>

            <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
              <div style={{ fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
                <span>AVG CONFIDENCE</span>
                <Award size={16} style={{ color: '#f59e0b' }} />
              </div>
              <div style={{ fontSize: '28px', fontWeight: '700', color: '#f59e0b' }}>{data.workflows.average_confidence_score}%</div>
              <div style={{ fontSize: '12px', color: '#9ca3af', marginTop: '6px' }}>Based on Report Intelligence</div>
            </div>
          </div>

          {/* Automated Executive Insights Banner */}
          {data.insights.length > 0 && (
            <div style={{ backgroundColor: 'rgba(99, 102, 241, 0.08)', border: '1px solid rgba(99, 102, 241, 0.25)', borderRadius: '14px', padding: '20px', marginBottom: '28px' }}>
              <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#8b5cf6', margin: '0 0 10px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkles size={18} /> Automated Backend Executive Insights
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {data.insights.map((insight, idx) => (
                  <div key={idx} style={{ fontSize: '13.5px', color: '#e5e7eb', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ color: '#8b5cf6' }}>•</span> {insight}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Grid Layout: Agent Performance & Recent Activity */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '24px', marginBottom: '28px' }}>
            {/* Agent Performance Table */}
            <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
              <h3 style={{ fontSize: '17px', fontWeight: '600', color: '#ffffff', marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BarChart2 size={18} style={{ color: '#6366f1' }} /> Specialist Agent Execution Performance
              </h3>

              {data.agent_performance.length === 0 ? (
                <div style={{ color: '#9ca3af', fontSize: '13px' }}>No agent executions logged yet.</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {data.agent_performance.map((agent) => (
                    <div key={agent.agent_name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 14px', backgroundColor: '#1f2937', borderRadius: '8px' }}>
                      <div>
                        <div style={{ fontSize: '14px', fontWeight: '600', color: '#f3f4f6' }}>{agent.agent_name}</div>
                        <div style={{ fontSize: '12px', color: '#9ca3af' }}>{agent.completed_executions} Completed / {agent.total_executions} Total</div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '14px', fontWeight: '700', color: '#10b981' }}>{agent.success_rate}% Success</div>
                        <div style={{ fontSize: '12px', color: '#8b5cf6' }}>{agent.average_confidence}% Conf.</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Recent Audit Activities */}
            <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
              <h3 style={{ fontSize: '17px', fontWeight: '600', color: '#ffffff', marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Activity size={18} style={{ color: '#10b981' }} /> Recent Audit Trail Events
              </h3>

              {data.recent_activities.length === 0 ? (
                <div style={{ color: '#9ca3af', fontSize: '13px' }}>No audit events logged yet.</div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {data.recent_activities.map((act) => (
                    <div key={act.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', borderBottom: '1px solid #1f2937' }}>
                      <div>
                        <div style={{ fontSize: '13px', fontWeight: '600', color: '#8b5cf6' }}>{act.event_type}</div>
                        <div style={{ fontSize: '11px', color: '#6b7280' }}>Workflow: {act.workflow_id}</div>
                      </div>
                      <div style={{ fontSize: '11px', color: '#9ca3af' }}>
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
