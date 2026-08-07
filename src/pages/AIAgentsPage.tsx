import React, { useState } from 'react';
import { FilterPill } from '../components/FilterPill';
import { AgentCard } from '../components/AgentCard';
import type { AgentCardData } from '../components/AgentCard';
import { Filter } from 'lucide-react';

const mockAgents: AgentCardData[] = [
  {
    id: '1',
    name: 'CEO Agent',
    role: 'STRATEGIC ORCHESTRATOR',
    status: 'THINKING',
    activity: 'Coordinating Q1 campaign for Lumen Studios',
    model: 'claude-sonnet-5',
    memory: '128k',
    latency: '⚡ 412ms',
    successRate: '📈 99%',
    health: '⚙️ 98%',
  },
  {
    id: '2',
    name: 'Business Analyst',
    role: 'MARKET INTELLIGENCE',
    status: 'RUNNING',
    activity: 'Analyzing D2C skincare TAM',
    model: 'gpt-5.6-terra',
    memory: '64k',
    latency: '⚡ 780ms',
    successRate: '📈 97%',
    health: '⚙️ 88%',
  },
  {
    id: '3',
    name: 'SEO Specialist',
    role: 'SEARCH & DISCOVERY',
    status: 'RUNNING',
    activity: 'Crawling 1,284 pages on lumenstudios.co',
    model: 'claude-sonnet-5',
    memory: '32k',
    latency: '⚡ 340ms',
    successRate: '📈 94%',
    health: '⚙️ 91%',
  },
  {
    id: '4',
    name: 'Competitor Scout',
    role: 'RIVAL INTELLIGENCE',
    status: 'COMPLETED',
    activity: 'Mapped 12 direct competitors',
    model: 'gemini-3-flash',
    memory: '48k',
    latency: '⚡ 610ms',
    successRate: '📈 98%',
    health: '⚙️ 93%',
  },
  {
    id: '5',
    name: 'Marketing Strategist',
    role: 'GROWTH & POSITIONING',
    status: 'WAITING',
    activity: 'Awaiting competitor synthesis',
    model: 'claude-sonnet-5',
    memory: '64k',
    latency: '⏱️ 0ms',
    successRate: '📈 100%',
    health: '⚙️ 0%',
  },
  {
    id: '6',
    name: 'Campaign Planner',
    role: 'MEDIA & CHANNELS',
    status: 'WAITING',
    activity: 'Queued after strategy phase',
    model: 'gpt-5.6-terra',
    memory: '32k',
    latency: '⏱️ 0ms',
    successRate: '📈 100%',
    health: '⚙️ 0%',
  },
  {
    id: '7',
    name: 'Analytics Engine',
    role: 'ATTRIBUTION & INSIGHT',
    status: 'IDLE',
    activity: 'Standby - awaiting live data',
    model: 'claude-sonnet-5',
    memory: '96k',
    latency: '⏱️ 0ms',
    successRate: '📈 100%',
    health: '⚙️ 0%',
  },
  {
    id: '8',
    name: 'Report Composer',
    role: 'EXECUTIVE NARRATOR',
    status: 'IDLE',
    activity: 'Standby - final synthesis',
    model: 'claude-sonnet-5',
    memory: '128k',
    latency: '⏱️ 0ms',
    successRate: '📈 100%',
    health: '⚙️ 0%',
  },
];

export const AIAgentsPage: React.FC = () => {
  const [activeFilter, setActiveFilter] = useState('ALL');

  const filters = ['ALL', 'THINKING', 'RUNNING', 'COMPLETED', 'WAITING', 'IDLE'];

  const filteredAgents =
    activeFilter === 'ALL'
      ? mockAgents
      : mockAgents.filter((a) => a.status === activeFilter);

  return (
    <div style={{ padding: '32px 40px', maxWidth: '1600px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
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
          TEAM OF 8
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
          AI Agents
        </h1>
        <p style={{ fontSize: '13px', color: '#9ca3af', maxWidth: '600px' }}>
          Every agent is an employee. Each one has a role, a model, memory, and a live health signal.
        </p>
      </div>

      {/* Filter Bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          marginBottom: '32px',
          paddingBottom: '16px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
        }}
      >
        <div style={{ color: '#6b7280', paddingRight: '4px' }}>
          <Filter size={16} />
        </div>
        {filters.map((filter) => (
          <FilterPill
            key={filter}
            label={filter}
            active={activeFilter === filter}
            onClick={() => setActiveFilter(filter)}
          />
        ))}
      </div>

      {/* Agents Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
          gap: '20px',
        }}
      >
        {filteredAgents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </div>
  );
};
