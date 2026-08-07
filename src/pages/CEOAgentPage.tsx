import React from 'react';
import { StatusBadge } from '../components/StatusBadge';
import { TaskItem } from '../components/TaskItem';
import type { TaskItemProps } from '../components/TaskItem';
import { Brain, Pause, Plus, ShieldCheck, Cpu, Search, Target, Megaphone, Send, BarChart2, FileText } from 'lucide-react';

const mockTasks: TaskItemProps[] = [
  {
    title: 'Synthesize Northwind competitive matrix',
    agent: 'COMPETITOR SCOUT',
    eta: 'ETA 2 MIN',
    priority: 'HIGH',
    status: 'RUNNING',
  },
  {
    title: 'Draft Lumen Studios Q1 narrative',
    agent: 'MARKETING STRATEGIST',
    eta: 'ETA 6 MIN',
    priority: 'HIGH',
    status: 'WAITING',
  },
  {
    title: 'SEO technical audit - orbitalabs.io',
    agent: 'SEO SPECIALIST',
    eta: 'ETA 4 MIN',
    priority: 'MEDIUM',
    status: 'RUNNING',
  },
  {
    title: 'Kite & Loom holiday media mix',
    agent: 'CAMPAIGN PLANNER',
    eta: 'ETA 9 MIN',
    priority: 'MEDIUM',
    status: 'WAITING',
  },
  {
    title: 'Halcyon Hotels attribution rebuild',
    agent: 'ANALYTICS ENGINE',
    eta: 'ETA 12 MIN',
    priority: 'LOW',
    status: 'WAITING',
  },
];

const workflowStages = [
  { name: 'CLIENT BRIEF', icon: ShieldCheck },
  { name: 'CEO AGENT', icon: Brain, active: true },
  { name: 'BUSINESS', icon: Cpu },
  { name: 'SEO', icon: Search },
  { name: 'COMPETITOR', icon: Target, highlighted: true },
  { name: 'MARKETING', icon: Megaphone },
  { name: 'CAMPAIGN', icon: Send },
  { name: 'ANALYTICS', icon: BarChart2 },
  { name: 'REPORT', icon: FileText },
];

export const CEOAgentPage: React.FC = () => {
  return (
    <div style={{ padding: '32px 40px', maxWidth: '1600px', margin: '0 auto' }}>
      {/* Top Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: '28px',
        }}
      >
        <div>
          <div
            style={{
              fontSize: '10px',
              fontFamily: "'JetBrains Mono', monospace",
              color: '#6b7280',
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              marginBottom: '8px',
            }}
          >
            AUTONOMOUS ORCHESTRATOR • CLAUDE-SONNET-5
          </div>
          <h1
            style={{
              fontSize: '36px',
              fontWeight: 700,
              color: '#ffffff',
              letterSpacing: '-0.02em',
              marginBottom: '8px',
            }}
          >
            CEO Agent
          </h1>
          <p style={{ fontSize: '13px', color: '#9ca3af', maxWidth: '550px', lineHeight: '1.5' }}>
            Live thought stream, running agents, task queue, and workflow graph — the intelligence at the center of StrtOS.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              padding: '8px 16px',
              color: '#e5e7eb',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Pause size={14} /> Pause
          </button>
          <button
            style={{
              background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
              border: 'none',
              borderRadius: '8px',
              padding: '8px 16px',
              color: '#ffffff',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              boxShadow: '0 0 16px rgba(168, 85, 247, 0.3)',
            }}
          >
            <Plus size={14} /> New directive
          </button>
        </div>
      </div>

      {/* Current Thought Card */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <span
            style={{
              fontSize: '10px',
              fontFamily: "'JetBrains Mono', monospace",
              color: '#6b7280',
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
            }}
          >
            CURRENT THOUGHT
          </span>
          <StatusBadge status="THINKING" />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              backgroundColor: 'rgba(168, 85, 247, 0.15)',
              border: '1px solid rgba(168, 85, 247, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#c084fc',
            }}
          >
            <Brain size={18} />
          </div>
          <div
            style={{
              fontSize: '15px',
              fontFamily: "'JetBrains Mono', monospace",
              color: '#e5e7eb',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <span style={{ color: '#00e599' }}>›</span> Reviewing Northwind Capital brief – enterprise FinTech, EMEA focus.
            <span
              style={{
                display: 'inline-block',
                width: '8px',
                height: '16px',
                backgroundColor: '#a855f7',
                marginLeft: '4px',
                animation: 'pulse 1s infinite',
              }}
            />
          </div>
        </div>
      </div>

      {/* Multi-Agent Execution Graph */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '20px',
          }}
        >
          <div>
            <div
              style={{
                fontSize: '10px',
                fontFamily: "'JetBrains Mono', monospace",
                color: '#6b7280',
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                marginBottom: '4px',
              }}
            >
              MULTI-AGENT EXECUTION
            </div>
            <div style={{ fontSize: '16px', fontWeight: 600, color: '#ffffff' }}>
              Workflow • Lumen Studios Q1
            </div>
          </div>
          <div style={{ fontSize: '11px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280' }}>
            4 / 9 stages
          </div>
        </div>

        {/* Stages Track */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(9, 1fr)', gap: '8px', position: 'relative' }}>
          {workflowStages.map((stage) => {
            const Icon = stage.icon;
            return (
              <div
                key={stage.name}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '8px',
                  opacity: stage.active || stage.highlighted ? 1 : 0.4,
                }}
              >
                <div
                  style={{
                    width: '44px',
                    height: '44px',
                    borderRadius: '12px',
                    backgroundColor: stage.highlighted
                      ? 'rgba(0, 229, 153, 0.15)'
                      : stage.active
                      ? 'rgba(168, 85, 247, 0.15)'
                      : 'rgba(255, 255, 255, 0.03)',
                    border: stage.highlighted
                      ? '1px solid rgba(0, 229, 153, 0.4)'
                      : stage.active
                      ? '1px solid rgba(168, 85, 247, 0.4)'
                      : '1px solid rgba(255, 255, 255, 0.06)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: stage.highlighted ? '#00e599' : stage.active ? '#c084fc' : '#6b7280',
                    position: 'relative',
                  }}
                >
                  <Icon size={18} />
                  {stage.highlighted && (
                    <span
                      style={{
                        position: 'absolute',
                        top: '-3px',
                        right: '-3px',
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: '#00e599',
                        boxShadow: '0 0 8px #00e599',
                      }}
                    />
                  )}
                </div>
                <div
                  style={{
                    fontSize: '9px',
                    fontFamily: "'JetBrains Mono', monospace",
                    color: '#6b7280',
                    textAlign: 'center',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}
                >
                  {stage.name}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom Grid: Task Queue + Confidence gauge */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        {/* Task Queue */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ fontSize: '16px', fontWeight: 600, color: '#ffffff' }}>Task queue</div>
            <div style={{ fontSize: '10px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280' }}>
              5 TASKS
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {mockTasks.map((t) => (
              <TaskItem key={t.title} {...t} />
            ))}
          </div>
        </div>

        {/* Overall Confidence Dial */}
        <div
          className="glass-card"
          style={{
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            position: 'relative',
          }}
        >
          <div
            style={{
              fontSize: '10px',
              fontFamily: "'JetBrains Mono', monospace",
              color: '#6b7280',
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              marginBottom: '24px',
            }}
          >
            OVERALL CONFIDENCE
          </div>

          {/* Dial SVG Ring */}
          <div style={{ position: 'relative', width: '160px', height: '160px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="160" height="160" viewBox="0 0 160 160" style={{ transform: 'rotate(-90deg)' }}>
              <circle cx="80" cy="80" r="70" stroke="rgba(255, 255, 255, 0.05)" strokeWidth="8" fill="transparent" />
              <circle
                cx="80"
                cy="80"
                r="70"
                stroke="url(#purpleGrad)"
                strokeWidth="8"
                fill="transparent"
                strokeDasharray="440"
                strokeDashoffset="40"
                strokeLinecap="round"
              />
              <defs>
                <linearGradient id="purpleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#6366f1" />
                  <stop offset="100%" stopColor="#a855f7" />
                </linearGradient>
              </defs>
            </svg>
            <div style={{ position: 'absolute', textAlign: 'center' }}>
              <div style={{ fontSize: '38px', fontWeight: 700, color: '#ffffff' }}>92</div>
              <div style={{ fontSize: '9px', fontFamily: "'JetBrains Mono', monospace", color: '#00e599', letterSpacing: '0.1em' }}>
                HIGH
              </div>
            </div>
          </div>

          {/* Stats below dial */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', width: '100%', marginTop: '32px', textAlign: 'center' }}>
            <div>
              <div style={{ fontSize: '18px', fontWeight: 700, color: '#ffffff' }}>3</div>
              <div style={{ fontSize: '9px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280' }}>RUNNING</div>
            </div>
            <div>
              <div style={{ fontSize: '18px', fontWeight: 700, color: '#ffffff' }}>12</div>
              <div style={{ fontSize: '9px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280' }}>COMPLETED</div>
            </div>
            <div>
              <div style={{ fontSize: '18px', fontWeight: 700, color: '#ffffff' }}>4</div>
              <div style={{ fontSize: '9px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280' }}>WAITING</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
