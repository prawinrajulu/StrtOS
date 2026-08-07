import React from 'react';
import { StatusBadge } from './StatusBadge';
import type { StatusType } from './StatusBadge';
import { Bot } from 'lucide-react';

export interface AgentCardData {
  id: string;
  name: string;
  role: string;
  status: StatusType;
  activity: string;
  model: string;
  memory: string;
  latency: string;
  successRate: string;
  health: string;
}

export const AgentCard: React.FC<{ agent: AgentCardData }> = ({ agent }) => {
  return (
    <div
      className="glass-card"
      style={{
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Top Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              backgroundColor: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#9ca3af',
            }}
          >
            <Bot size={20} />
          </div>
          <div>
            <div style={{ fontSize: '15px', fontWeight: 600, color: '#f3f4f6' }}>{agent.name}</div>
            <div
              style={{
                fontSize: '10px',
                fontFamily: "'JetBrains Mono', monospace",
                color: '#6b7280',
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                marginTop: '2px',
              }}
            >
              {agent.role}
            </div>
          </div>
        </div>
        <StatusBadge status={agent.status} />
      </div>

      {/* Activity Description */}
      <div
        style={{
          fontSize: '13px',
          color: '#d1d5db',
          lineHeight: '1.4',
          minHeight: '36px',
          fontFamily: "'Plus Jakarta Sans', sans-serif",
        }}
      >
        {agent.activity}
      </div>

      {/* Model & Memory Box */}
      <div
        style={{
          backgroundColor: 'rgba(0, 0, 0, 0.3)',
          border: '1px solid rgba(255, 255, 255, 0.04)',
          borderRadius: '8px',
          padding: '12px',
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '12px',
        }}
      >
        <div>
          <div
            style={{
              fontSize: '9px',
              fontFamily: "'JetBrains Mono', monospace",
              color: '#4b5563',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              marginBottom: '4px',
            }}
          >
            MODEL
          </div>
          <div
            style={{
              fontSize: '12px',
              fontFamily: "'JetBrains Mono', monospace",
              color: '#9ca3af',
            }}
          >
            {agent.model}
          </div>
        </div>

        <div>
          <div
            style={{
              fontSize: '9px',
              fontFamily: "'JetBrains Mono', monospace",
              color: '#4b5563',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              marginBottom: '4px',
            }}
          >
            MEMORY
          </div>
          <div
            style={{
              fontSize: '12px',
              fontFamily: "'JetBrains Mono', monospace",
              color: '#9ca3af',
            }}
          >
            {agent.memory}
          </div>
        </div>
      </div>

      {/* Footer Metrics */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '11px',
          fontFamily: "'JetBrains Mono', monospace",
          color: '#6b7280',
          paddingTop: '4px',
        }}
      >
        <span>{agent.latency}</span>
        <span>{agent.successRate}</span>
        <span>{agent.health}</span>
      </div>
    </div>
  );
};
