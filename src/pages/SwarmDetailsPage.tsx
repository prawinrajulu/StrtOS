import React, { useEffect, useState } from 'react';
import { ArrowLeft, Play, ShieldAlert, CheckCircle2, Users, MessageSquare, Brain } from 'lucide-react';
import { swarmApi } from '../services/swarmApi';
import type { SwarmSessionRecord, SwarmConflictRecord, SwarmDebateRecord } from '../services/swarmApi';

interface SwarmDetailsPageProps {
  swarm: SwarmSessionRecord;
  onBack: () => void;
}

export const SwarmDetailsPage: React.FC<SwarmDetailsPageProps> = ({ swarm, onBack }) => {
  const [currentSwarm, setCurrentSwarm] = useState<SwarmSessionRecord>(swarm);
  const [conflicts, setConflicts] = useState<SwarmConflictRecord[]>([]);
  const [debates, setDebates] = useState<SwarmDebateRecord[]>([]);
  const [loading, setLoading] = useState(false);

  const loadDetails = async () => {
    const cData = await swarmApi.getConflicts(currentSwarm.id);
    const dData = await swarmApi.getDebates(currentSwarm.id);
    setConflicts(cData);
    setDebates(dData);
  };

  useEffect(() => {
    loadDetails();
  }, [currentSwarm.id]);

  const handleStartSwarm = async () => {
    setLoading(true);
    try {
      const res = await swarmApi.startSession(currentSwarm.id);
      setCurrentSwarm(res);
      loadDetails();
    } catch (err: any) {
      alert(err.message || 'Swarm execution failed');
    } finally {
      setLoading(false);
    }
  };

  const agents = [
    { name: 'Business Analysis Agent', role: 'Stage 1 Parallel' },
    { name: 'SEO Audit Agent', role: 'Stage 1 Parallel' },
    { name: 'Competitor Research Agent', role: 'Stage 1 Parallel' },
    { name: 'Marketing Strategy Agent', role: 'Stage 2 Dependent' },
    { name: 'Campaign Planner Agent', role: 'Stage 3 Dependent' }
  ];

  return (
    <div style={{ padding: '28px', maxWidth: '1200px', margin: '0 auto' }}>
      <button
        onClick={onBack}
        style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'none', border: 'none', color: '#9ca3af', fontSize: '14px', cursor: 'pointer', marginBottom: '20px' }}
      >
        <ArrowLeft size={16} /> Back to Swarm Sessions
      </button>

      {/* Header Banner */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '28px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
            <span style={{ padding: '4px 10px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#8b5cf6', borderRadius: '8px', fontSize: '12px', fontWeight: '700' }}>
              STATUS: {currentSwarm.status}
            </span>
            <span style={{ padding: '4px 10px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981', borderRadius: '8px', fontSize: '12px', fontWeight: '700' }}>
              CONSENSUS: {currentSwarm.consensus_score}%
            </span>
          </div>

          <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#f9fafb', margin: '0 0 8px 0' }}>{currentSwarm.objective}</h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>5 Core Specialist Agents • Bounded Debate Engine • Deterministic Consensus</p>
        </div>

        {currentSwarm.status === 'DRAFT' && (
          <button
            onClick={handleStartSwarm}
            disabled={loading}
            style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 24px', backgroundColor: '#10b981', color: '#fff', border: 'none', borderRadius: '10px', fontWeight: '700', cursor: 'pointer' }}
          >
            <Play size={18} /> Execute Swarm Engine
          </button>
        )}
      </div>

      {/* Specialist Agent Grid */}
      <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f9fafb', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Users style={{ color: '#6366f1' }} size={20} /> 5 Core Specialist Agent Swarm Status
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '14px', marginBottom: '28px' }}>
        {agents.map((ag) => (
          <div key={ag.name} style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '16px' }}>
            <div style={{ fontSize: '11px', color: '#6b7280', fontWeight: '600', marginBottom: '4px' }}>{ag.role}</div>
            <div style={{ fontSize: '14px', fontWeight: '700', color: '#f9fafb', marginBottom: '8px' }}>{ag.name}</div>
            <div style={{ fontSize: '12px', color: '#10b981', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <CheckCircle2 size={13} /> Active & Verified
            </div>
          </div>
        ))}
      </div>

      {/* Consensus & Synthesis Output */}
      {currentSwarm.synthesis_output && (
        <div style={{ backgroundColor: '#111827', border: '1px solid #6366f1', borderRadius: '16px', padding: '24px', marginBottom: '28px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f9fafb', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Brain style={{ color: '#6366f1' }} size={20} /> CEO Final Strategic Synthesis
          </h3>
          <p style={{ color: '#d1d5db', fontSize: '14px', margin: '0 0 16px 0' }}>
            {currentSwarm.synthesis_output.rationale}
          </p>
          <div style={{ display: 'flex', gap: '20px', fontSize: '13px', color: '#9ca3af' }}>
            <span>Supporting Agents: {currentSwarm.synthesis_output.supporting_agents?.length || 0}</span>
            <span>Conflicts Detected: {currentSwarm.synthesis_output.conflicts_count || 0}</span>
            <span>Critic Score: {currentSwarm.synthesis_output.critic_score}/100</span>
          </div>
        </div>
      )}

      {/* Debate Rounds */}
      {debates.length > 0 && (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '24px', marginBottom: '28px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f9fafb', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MessageSquare style={{ color: '#8b5cf6' }} size={20} /> Bounded Agent Debate Timeline ({debates.length} Rounds)
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {debates.map((d) => (
              <div key={d.id} style={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '12px', padding: '16px' }}>
                <div style={{ fontSize: '12px', color: '#8b5cf6', fontWeight: '700', marginBottom: '4px' }}>DEBATE ROUND #{d.round_number}</div>
                <div style={{ fontSize: '14px', fontWeight: '700', color: '#f9fafb', marginBottom: '6px' }}>Claim: {d.claim}</div>
                <div style={{ fontSize: '13px', color: '#9ca3af', marginBottom: '6px' }}>{d.challenge}</div>
                <div style={{ fontSize: '12px', color: '#10b981', fontWeight: '600' }}>{d.resolution}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Conflict Matrix */}
      {conflicts.length > 0 && (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '24px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f9fafb', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert style={{ color: '#f59e0b' }} size={20} /> Cross-Agent Conflict Resolution Matrix ({conflicts.length})
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {conflicts.map((c) => (
              <div key={c.id} style={{ backgroundColor: '#1f2937', border: '1px solid #f59e0b', borderRadius: '12px', padding: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <span style={{ fontSize: '14px', fontWeight: '700', color: '#f9fafb' }}>{c.subject}</span>
                  <span style={{ padding: '2px 8px', backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#f59e0b', borderRadius: '6px', fontSize: '11px', fontWeight: '700' }}>{c.severity} SEVERITY</span>
                </div>
                <div style={{ fontSize: '12px', color: '#9ca3af', marginBottom: '4px' }}>{c.agent_a}: {c.claim_a}</div>
                <div style={{ fontSize: '12px', color: '#9ca3af', marginBottom: '8px' }}>{c.agent_b}: {c.claim_b}</div>
                <div style={{ fontSize: '12px', color: '#10b981', fontWeight: '600' }}>{c.resolution}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
