import React, { useEffect, useState } from 'react';
import {
  Brain, Search, CheckCircle2, AlertTriangle, XCircle,
  Lightbulb, Sparkles, ChevronRight
} from 'lucide-react';
import { memoryApi } from '../services/memoryApi';
import type { MemoryRecord } from '../services/memoryApi';
import { globalEventStream } from '../services/eventStream';

interface MemoryPageProps {
  onSelectMemory: (memory: MemoryRecord) => void;
}

export const MemoryPage: React.FC<MemoryPageProps> = ({ onSelectMemory }) => {
  const [memories, setMemories] = useState<MemoryRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('');

  const fetchMemories = async () => {
    setLoading(true);
    const data = await memoryApi.getMemories({
      memory_type: typeFilter,
      search: search
    });
    setMemories(data.memories);
    setTotal(data.total);
    setLoading(false);
  };

  useEffect(() => {
    fetchMemories();

    const unsubscribe = globalEventStream.subscribe((event) => {
      if (['memory.created', 'memory.updated', 'outcome.recorded', 'lesson.created'].includes(event.event_type)) {
        fetchMemories();
      }
    });
    return () => unsubscribe();
  }, [typeFilter, search]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <span style={{ color: '#10b981', fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}><CheckCircle2 size={13} /> SUCCESS</span>;
      case 'PARTIAL':
        return <span style={{ color: '#f59e0b', fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}><AlertTriangle size={13} /> PARTIAL</span>;
      case 'FAILED':
        return <span style={{ color: '#ef4444', fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}><XCircle size={13} /> FAILED</span>;
      default:
        return <span style={{ color: '#9ca3af', fontWeight: '600', fontSize: '11px' }}>UNVALUATED</span>;
    }
  };

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'LESSON':
        return <span style={{ padding: '3px 8px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b', borderRadius: '6px', fontSize: '11px', fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px' }}><Lightbulb size={12} /> LESSON</span>;
      case 'OUTCOME':
        return <span style={{ padding: '3px 8px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981', borderRadius: '6px', fontSize: '11px', fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px' }}><CheckCircle2 size={12} /> OUTCOME</span>;
      case 'DECISION':
        return <span style={{ padding: '3px 8px', backgroundColor: 'rgba(139, 92, 246, 0.15)', color: '#8b5cf6', borderRadius: '6px', fontSize: '11px', fontWeight: '700', display: 'inline-flex', alignItems: 'center', gap: '4px' }}><Sparkles size={12} /> DECISION</span>;
      default:
        return <span style={{ padding: '3px 8px', backgroundColor: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', borderRadius: '6px', fontSize: '11px', fontWeight: '600' }}>{type}</span>;
    }
  };

  return (
    <div style={{ padding: '28px', maxWidth: '1300px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Brain style={{ color: '#8b5cf6' }} size={28} /> Client Adaptive Memory & Intelligence
          </h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>
            Historical decision memory, variance calibration, and learned signals ({total} Total Records)
          </p>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '16px', marginBottom: '24px', display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ flex: 1, minWidth: '240px', position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
          <input
            type="text"
            placeholder="Search historical memory, decisions, or learned signals..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px 12px 10px 38px', color: '#f9fafb', fontSize: '14px' }}
          />
        </div>

        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          style={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px 14px', color: '#f9fafb', fontSize: '14px' }}
        >
          <option value="">All Memory Types</option>
          <option value="LESSON">Learned Lessons</option>
          <option value="OUTCOME">Measured Outcomes</option>
          <option value="DECISION">Historical Decisions</option>
          <option value="APPROVAL">Approvals</option>
          <option value="STRATEGY">Strategies</option>
          <option value="WORKFLOW">Workflows</option>
        </select>
      </div>

      {/* Memory Cards */}
      {loading ? (
        <div style={{ color: '#9ca3af', textAlign: 'center', padding: '40px' }}>Loading adaptive memory records...</div>
      ) : memories.length === 0 ? (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '40px', textAlign: 'center', color: '#9ca3af' }}>
          No historical memory records found matching criteria.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {memories.map((mem) => (
            <div
              key={mem.id}
              onClick={() => onSelectMemory(mem)}
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
                  {getTypeBadge(mem.memory_type)}
                  {getStatusBadge(mem.outcome_status)}
                  <span style={{ fontSize: '11px', color: '#6b7280' }}>
                    {new Date(mem.occurred_at || mem.created_at).toLocaleDateString()}
                  </span>
                </div>
                <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0' }}>{mem.title}</h3>
                {mem.content && (
                  <p style={{ color: '#9ca3af', fontSize: '13px', margin: 0, lineHeight: '1.4' }}>{mem.content}</p>
                )}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '11px', color: '#6b7280', fontWeight: '600' }}>CONFIDENCE</div>
                  <div style={{ fontSize: '15px', fontWeight: '700', color: '#8b5cf6' }}>{mem.confidence_score}%</div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '11px', color: '#6b7280', fontWeight: '600' }}>IMPORTANCE</div>
                  <div style={{ fontSize: '15px', fontWeight: '700', color: '#60a5fa' }}>{mem.importance_score}</div>
                </div>

                <ChevronRight size={20} style={{ color: '#6b7280' }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
