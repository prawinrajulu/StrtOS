import React, { useEffect, useState } from 'react';
import {
  ArrowLeft, BrainCircuit, Play, Pause, RefreshCw, XCircle, CheckCircle2,
  Clock, Activity, ListChecks
} from 'lucide-react';
import { workflowsApi } from '../services/workflowsApi';
import type { Workflow, TaskItem } from '../services/workflowsApi';

interface WorkflowDetailsPageProps {
  workflow: Workflow;
  onBack: () => void;
}

export const WorkflowDetailsPage: React.FC<WorkflowDetailsPageProps> = ({ workflow: initialWf, onBack }) => {
  const [workflow, setWorkflow] = useState<Workflow>(initialWf);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loadingAction, setLoadingAction] = useState(false);

  const refreshData = async () => {
    const [wf, taskList] = await Promise.all([
      workflowsApi.getWorkflow(workflow.id),
      workflowsApi.getTasks(workflow.id)
    ]);
    if (wf) setWorkflow(wf);
    setTasks(taskList);
  };

  useEffect(() => {
    refreshData();
  }, [workflow.id]);

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

  const stages = [
    { name: 'CLIENT BRIEF', agent: 'Client Onboarding Agent' },
    { name: 'CEO AGENT', agent: 'CEO Orchestrator' },
    { name: 'BUSINESS ANALYSIS', agent: 'Business Analysis Agent' },
    { name: 'SEO AUDIT', agent: 'SEO Audit Agent' },
    { name: 'COMPETITOR RESEARCH', agent: 'Competitor Research Agent' },
    { name: 'MARKETING STRATEGY', agent: 'Marketing Strategy Agent' },
    { name: 'CAMPAIGN PLANNER', agent: 'Campaign Planner Agent' },
    { name: 'REPORT GENERATION', agent: 'Report Generator Agent' },
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1300px', margin: '0 auto' }}>
      <button
        onClick={onBack}
        style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'none', border: 'none', color: '#9ca3af', fontSize: '14px', cursor: 'pointer', marginBottom: '20px' }}
      >
        <ArrowLeft size={16} /> Back to Workflows List
      </button>

      {/* Header Banner */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '28px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <h1 style={{ fontSize: '26px', fontWeight: '700', color: '#f9fafb', margin: 0 }}>{workflow.title}</h1>
            <span style={{ padding: '4px 10px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#8b5cf6', borderRadius: '12px', fontSize: '12px', fontWeight: '600' }}>
              {workflow.status}
            </span>
          </div>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>{workflow.directive}</p>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', gap: '12px' }}>
          {workflow.status === 'DRAFT' && (
            <button
              onClick={handleStart}
              disabled={loadingAction}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 22px', background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer' }}
            >
              <Play size={18} /> Start Execution
            </button>
          )}

          {workflow.status === 'RUNNING' && (
            <button
              onClick={handlePause}
              disabled={loadingAction}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 22px', backgroundColor: '#f59e0b', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer' }}
            >
              <Pause size={18} /> Pause Workflow
            </button>
          )}

          {workflow.status === 'PAUSED' && (
            <button
              onClick={handleResume}
              disabled={loadingAction}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 22px', backgroundColor: '#6366f1', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer' }}
            >
              <RefreshCw size={18} /> Resume Workflow
            </button>
          )}

          {(workflow.status === 'RUNNING' || workflow.status === 'PAUSED') && (
            <button
              onClick={handleCancel}
              disabled={loadingAction}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 18px', backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', border: '1px solid #ef4444', borderRadius: '8px', fontWeight: '600', cursor: 'pointer' }}
            >
              <XCircle size={18} /> Cancel
            </button>
          )}
        </div>
      </div>

      {/* Execution Graph / Stages */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f9fafb', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BrainCircuit style={{ color: '#8b5cf6' }} size={20} /> Execution Stage Graph
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
          {stages.map((stg, idx) => {
            const isCompleted = workflow.status === 'COMPLETED' || idx < workflow.completed_stages;
            const isRunning = workflow.status === 'RUNNING' && idx === workflow.completed_stages;
            return (
              <div
                key={idx}
                style={{
                  backgroundColor: isCompleted ? 'rgba(16, 185, 129, 0.08)' : isRunning ? 'rgba(99, 102, 241, 0.12)' : '#1f2937',
                  border: isCompleted ? '1px solid #10b981' : isRunning ? '1px solid #6366f1' : '1px solid #374151',
                  borderRadius: '10px',
                  padding: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px'
                }}
              >
                {isCompleted ? (
                  <CheckCircle2 style={{ color: '#10b981' }} size={20} />
                ) : isRunning ? (
                  <Activity style={{ color: '#8b5cf6' }} size={20} />
                ) : (
                  <Clock style={{ color: '#6b7280' }} size={20} />
                )}
                <div>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: '#f3f4f6' }}>{stg.name}</div>
                  <div style={{ fontSize: '11px', color: '#9ca3af' }}>{stg.agent}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Task Queue Panel */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f9fafb', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ListChecks style={{ color: '#8b5cf6' }} size={20} /> Task Execution Log ({tasks.length} Tasks)
        </h3>

        {tasks.length === 0 ? (
          <div style={{ color: '#9ca3af', fontSize: '14px', textAlign: 'center', padding: '20px' }}>
            No tasks logged yet. Start workflow to trigger agent execution.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {tasks.map((task) => (
              <div key={task.id} style={{ padding: '14px', backgroundColor: '#1f2937', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: '600', color: '#f9fafb' }}>{task.title}</div>
                  <div style={{ fontSize: '12px', color: '#8b5cf6' }}>Agent: {task.agent_name} | Priority: {task.priority}</div>
                </div>
                <span style={{ fontSize: '12px', fontWeight: '700', color: task.status === 'COMPLETED' ? '#10b981' : '#f59e0b' }}>
                  {task.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
