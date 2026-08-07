import React from 'react';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';
import { Plus, Sparkles } from 'lucide-react';

export const DashboardPage: React.FC<{ onOpenCEO: () => void }> = ({ onOpenCEO }) => {
  return (
    <div style={{ padding: '32px 40px', maxWidth: '1600px', margin: '0 auto' }}>
      {/* Top Welcome Section */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '28px' }}>
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
            WED • FEB 26 • 2026
          </div>
          <h1 style={{ fontSize: '36px', fontWeight: 700, color: '#ffffff', letterSpacing: '-0.02em', marginBottom: '8px' }}>
            Good evening, Ava.
          </h1>
          <p style={{ fontSize: '13px', color: '#9ca3af' }}>
            Your CEO Agent orchestrated 218 tasks across 6 clients today. Confidence is trending upward.
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
            <Plus size={14} /> New workflow
          </button>
          <button
            onClick={onOpenCEO}
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
              boxShadow: '0 0 16px rgba(168, 85, 247, 0.4)',
            }}
          >
            <Sparkles size={14} /> Open CEO Agent
          </button>
        </div>
      </div>

      {/* Top 4 Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '28px' }}>
        <MetricCard title="ACTIVE WORKFLOWS" value="18" change="↗ +12%" />
        <MetricCard title="AGENTS ONLINE" value="8/8" change="↗ 100%" />
        <MetricCard title="AVG CONFIDENCE" value="92.4" change="↗ +3.1" />
        <MetricCard title="TASKS TODAY" value="2,481" change="↗ +218" />
      </div>

      {/* Middle Section: Chart + Live Queue */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '28px' }}>
        {/* Chart Card */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
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
                AGENT THROUGHPUT
              </div>
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#ffffff' }}>
                Tasks completed · last 6mo
              </div>
            </div>
            <span
              style={{
                fontSize: '10px',
                fontFamily: "'JetBrains Mono', monospace",
                color: '#00e599',
                backgroundColor: 'rgba(0, 229, 153, 0.1)',
                padding: '3px 8px',
                borderRadius: '4px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#00e599' }} /> LIVE
            </span>
          </div>

          {/* Canvas SVG Area Chart */}
          <div style={{ height: '220px', width: '100%', position: 'relative' }}>
            <svg width="100%" height="100%" viewBox="0 0 500 200" preserveAspectRatio="none">
              <defs>
                <linearGradient id="chartArea" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
                </linearGradient>
              </defs>

              {/* Grid Lines */}
              <line x1="0" y1="50" x2="500" y2="50" stroke="rgba(255,255,255,0.04)" strokeDasharray="4 4" />
              <line x1="0" y1="100" x2="500" y2="100" stroke="rgba(255,255,255,0.04)" strokeDasharray="4 4" />
              <line x1="0" y1="150" x2="500" y2="150" stroke="rgba(255,255,255,0.04)" strokeDasharray="4 4" />

              {/* Area Fill */}
              <path d="M 0,140 Q 125,120 250,90 T 500,40 L 500,200 L 0,200 Z" fill="url(#chartArea)" />

              {/* Line Curve */}
              <path d="M 0,140 Q 125,120 250,90 T 500,40" fill="none" stroke="#a855f7" strokeWidth="2.5" />
            </svg>

            {/* X-Axis labels */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '10px',
                fontFamily: "'JetBrains Mono', monospace",
                color: '#6b7280',
                marginTop: '8px',
              }}
            >
              <span>Sep</span>
              <span>Oct</span>
              <span>Nov</span>
              <span>Dec</span>
              <span>Jan</span>
              <span>Feb</span>
            </div>
          </div>
        </div>

        {/* Live Queue Box */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ fontSize: '16px', fontWeight: 600, color: '#ffffff' }}>Live queue</div>
            <span
              style={{
                fontSize: '9px',
                fontFamily: "'JetBrains Mono', monospace",
                color: '#00e599',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <span style={{ width: '5px', height: '5px', borderRadius: '50%', backgroundColor: '#00e599' }} /> STREAMING
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {[
              { title: 'Synthesize Northwind competitive matrix', agent: 'COMPETITOR SCOUT', status: 'RUNNING' as const },
              { title: 'Draft Lumen Studios Q1 narrative', agent: 'MARKETING STRATEGIST', status: 'WAITING' as const },
              { title: 'SEO technical audit – orbitalabs.io', agent: 'SEO SPECIALIST', status: 'RUNNING' as const },
              { title: 'Kite & Loom holiday media mix', agent: 'CAMPAIGN PLANNER', status: 'WAITING' as const },
            ].map((q) => (
              <div
                key={q.title}
                style={{
                  padding: '10px 12px',
                  backgroundColor: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid rgba(255, 255, 255, 0.04)',
                  borderRadius: '6px',
                }}
              >
                <div style={{ fontSize: '12px', color: '#e5e7eb', marginBottom: '4px' }}>{q.title}</div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '9px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280' }}>
                    {q.agent}
                  </span>
                  <StatusBadge status={q.status} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Section: Client Portfolio + Active Agents */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        {/* Client Portfolio */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <div style={{ fontSize: '16px', fontWeight: 600, color: '#ffffff' }}>Client portfolio</div>
            <span style={{ fontSize: '10px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280', cursor: 'pointer' }}>
              VIEW ALL →
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            {[
              { id: 'LS', name: 'Lumen Studios', type: 'D2C SKINCARE', health: 92, color: '#6366f1' },
              { id: 'NC', name: 'Northwind Capital', type: 'FINTECH', health: 88, color: '#00e599' },
              { id: 'KL', name: 'Kite & Loom', type: 'HOME & LIVING', health: 95, color: '#f59e0b' },
            ].map((client) => (
              <div
                key={client.name}
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                  borderRadius: '10px',
                  padding: '16px',
                }}
              >
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '8px',
                    backgroundColor: client.color,
                    color: '#000000',
                    fontSize: '11px',
                    fontWeight: 700,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: '12px',
                  }}
                >
                  {client.id}
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#ffffff' }}>{client.name}</div>
                <div
                  style={{
                    fontSize: '9px',
                    fontFamily: "'JetBrains Mono', monospace",
                    color: '#6b7280',
                    marginTop: '2px',
                    marginBottom: '16px',
                  }}
                >
                  {client.type}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '10px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280', marginBottom: '6px' }}>
                  <span>HEALTH</span>
                  <span style={{ color: '#ffffff' }}>{client.health}</span>
                </div>
                <div style={{ width: '100%', height: '4px', backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: '2px', overflow: 'hidden' }}>
                  <div style={{ width: `${client.health}%`, height: '100%', backgroundColor: client.color }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Active Agents list */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <div style={{ fontSize: '16px', fontWeight: 600, color: '#ffffff' }}>Active agents</div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[
              { name: 'CEO Agent', role: 'STRATEGIC ORCHESTRATOR', status: 'THINKING' as const },
              { name: 'Business Analyst', role: 'MARKET INTELLIGENCE', status: 'RUNNING' as const },
              { name: 'SEO Specialist', role: 'SEARCH & DISCOVERY', status: 'RUNNING' as const },
              { name: 'Competitor Scout', role: 'RIVAL INTELLIGENCE', status: 'COMPLETED' as const },
            ].map((a) => (
              <div
                key={a.name}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '8px 10px',
                  borderRadius: '6px',
                  backgroundColor: 'rgba(255, 255, 255, 0.02)',
                }}
              >
                <div>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: '#e5e7eb' }}>{a.name}</div>
                  <div style={{ fontSize: '9px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280' }}>
                    {a.role}
                  </div>
                </div>
                <StatusBadge status={a.status} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
