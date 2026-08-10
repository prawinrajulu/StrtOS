import React, { useEffect, useState } from 'react';
import { Network, Search, Plus, Play, ChevronRight } from 'lucide-react';
import { swarmApi } from '../services/swarmApi';
import type { SwarmSessionRecord } from '../services/swarmApi';
import { globalEventStream } from '../services/eventStream';

interface SwarmPageProps {
  onSelectSwarm: (swarm: SwarmSessionRecord) => void;
}

export const SwarmPage: React.FC<SwarmPageProps> = ({ onSelectSwarm }) => {
  const [sessions, setSessions] = useState<SwarmSessionRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newObjective, setNewObjective] = useState('');

  const fetchSessions = async () => {
    setLoading(true);
    const data = await swarmApi.getSessions({
      status: statusFilter,
      search: search
    });
    setSessions(data.sessions);
    setTotal(data.total);
    setLoading(false);
  };

  useEffect(() => {
    fetchSessions();

    const unsubscribe = globalEventStream.subscribe((event) => {
      if (event.event_type.startsWith('swarm.')) {
        fetchSessions();
      }
    });
    return () => unsubscribe();
  }, [statusFilter, search]);

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newObjective.trim()) return;
    try {
      const created = await swarmApi.createSession(newObjective);
      setShowCreateModal(false);
      setNewObjective('');
      fetchSessions();
      onSelectSwarm(created);
    } catch (err: any) {
      alert(err.message || 'Failed to create swarm session');
    }
  };

  const handleStartSession = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await swarmApi.startSession(id);
      fetchSessions();
    } catch (err: any) {
      alert(err.message || 'Swarm execution failed');
    }
  };

  return (
    <div style={{ padding: '28px', maxWidth: '1300px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Network style={{ color: '#6366f1' }} size={28} /> Multi-Agent Swarm Orchestration
          </h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>
            Parallel specialist agent collaboration, debate rounds, conflict matrix, and consensus engine ({total} Swarms)
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 18px', backgroundColor: '#6366f1', color: '#fff', border: 'none', borderRadius: '10px', fontWeight: '700', cursor: 'pointer' }}
        >
          <Plus size={16} /> New Swarm Session
        </button>
      </div>

      {/* Sub-Navigation Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '1px solid #1f2937', paddingBottom: '12px' }}>
        {[
          { label: 'All Sessions', value: '' },
          { label: 'Running', value: 'RUNNING' },
          { label: 'Debating', value: 'DEBATING' },
          { label: 'Completed', value: 'COMPLETED' }
        ].map((tab) => (
          <button
            key={tab.value}
            onClick={() => setStatusFilter(tab.value)}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: statusFilter === tab.value ? '#6366f1' : '#111827',
              color: statusFilter === tab.value ? '#ffffff' : '#9ca3af',
              fontSize: '13px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Search Bar */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '16px', marginBottom: '24px' }}>
        <div style={{ position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
          <input
            type="text"
            placeholder="Search swarm objectives or participating agents..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px 12px 10px 38px', color: '#f9fafb', fontSize: '14px' }}
          />
        </div>
      </div>

      {/* Swarm Cards */}
      {loading ? (
        <div style={{ color: '#9ca3af', textAlign: 'center', padding: '40px' }}>Loading swarm sessions...</div>
      ) : sessions.length === 0 ? (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '40px', textAlign: 'center', color: '#9ca3af' }}>
          No multi-agent swarm sessions found matching criteria.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {sessions.map((sess) => (
            <div
              key={sess.id}
              onClick={() => onSelectSwarm(sess)}
              style={{
                backgroundColor: '#111827',
                border: '1px solid #1f2937',
                borderRadius: '14px',
                padding: '20px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '16px'
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#6366f1')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#1f2937')}
            >
              <div style={{ flex: 1, minWidth: '280px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  <span style={{ padding: '3px 8px', backgroundColor: sess.status === 'COMPLETED' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(99, 102, 241, 0.15)', color: sess.status === 'COMPLETED' ? '#10b981' : '#8b5cf6', borderRadius: '6px', fontSize: '11px', fontWeight: '700' }}>
                    {sess.status}
                  </span>
                  <span style={{ fontSize: '11px', color: '#6b7280' }}>
                    5 SPECIALIST AGENTS • {sess.debate_rounds} DEBATE ROUNDS
                  </span>
                </div>
                <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0' }}>{sess.objective}</h3>
                <div style={{ color: '#9ca3af', fontSize: '12px', display: 'flex', gap: '12px' }}>
                  <span>Conflicts: {sess.conflict_count}</span>
                  <span>Confidence: {sess.confidence_score}%</span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '11px', color: '#6b7280', fontWeight: '600' }}>CONSENSUS SCORE</div>
                  <div style={{ fontSize: '20px', fontWeight: '700', color: sess.consensus_score >= 70 ? '#10b981' : '#f59e0b' }}>
                    {sess.consensus_score}%
                  </div>
                </div>

                {sess.status === 'DRAFT' && (
                  <button
                    onClick={(e) => handleStartSession(e, sess.id)}
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', backgroundColor: '#10b981', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '700', fontSize: '13px', cursor: 'pointer' }}
                  >
                    <Play size={14} /> Start Swarm
                  </button>
                )}

                <ChevronRight size={20} style={{ color: '#6b7280' }} />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal for Creating Swarm */}
      {showCreateModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50, padding: '20px' }}>
          <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '28px', maxWidth: '500px', width: '100%' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#f9fafb', margin: '0 0 16px 0' }}>Create Swarm Session</h2>
            <form onSubmit={handleCreateSession}>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '6px' }}>EXECUTIVE SWARM OBJECTIVE</label>
                <textarea
                  rows={4}
                  value={newObjective}
                  onChange={(e) => setNewObjective(e.target.value)}
                  placeholder="e.g. Optimize full-funnel acquisition, keyword positioning, and campaign allocation for Q3 flight"
                  required
                  style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '12px', color: '#f9fafb', fontSize: '14px' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  style={{ padding: '10px 16px', backgroundColor: '#1f2937', color: '#9ca3af', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{ padding: '10px 20px', backgroundColor: '#6366f1', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '700' }}
                >
                  Initialize Swarm
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
