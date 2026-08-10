import React from 'react';
import { ArrowLeft, Brain, Database } from 'lucide-react';
import type { MemoryRecord } from '../services/memoryApi';

interface MemoryDetailsPageProps {
  memory: MemoryRecord;
  onBack: () => void;
}

export const MemoryDetailsPage: React.FC<MemoryDetailsPageProps> = ({ memory, onBack }) => {
  return (
    <div style={{ padding: '28px', maxWidth: '1100px', margin: '0 auto' }}>
      <button
        onClick={onBack}
        style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'none', border: 'none', color: '#9ca3af', fontSize: '14px', cursor: 'pointer', marginBottom: '20px' }}
      >
        <ArrowLeft size={16} /> Back to Memory List
      </button>

      {/* Header Banner */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '28px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
          <span style={{ padding: '4px 10px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#8b5cf6', borderRadius: '8px', fontSize: '12px', fontWeight: '700' }}>
            HISTORICAL MEMORY ({memory.memory_type})
          </span>
          <span style={{ padding: '4px 10px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981', borderRadius: '8px', fontSize: '12px', fontWeight: '700' }}>
            STATUS: {memory.outcome_status}
          </span>
        </div>

        <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#f9fafb', margin: '0 0 8px 0' }}>{memory.title}</h1>
        <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>
          Occurred on {new Date(memory.occurred_at || memory.created_at).toLocaleString()} | Source: {memory.source || 'internal'}
        </p>
      </div>

      {/* Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>CONFIDENCE SCORE</div>
          <div style={{ fontSize: '26px', fontWeight: '700', color: '#8b5cf6' }}>{memory.confidence_score}%</div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>IMPORTANCE SCORE</div>
          <div style={{ fontSize: '26px', fontWeight: '700', color: '#60a5fa' }}>{memory.importance_score} / 100</div>
        </div>
      </div>

      {/* Content */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f9fafb', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Brain style={{ color: '#8b5cf6' }} size={20} /> Memory Narrative Content
        </h3>
        <p style={{ color: '#d1d5db', fontSize: '15px', lineHeight: '1.6', margin: 0 }}>
          {memory.content || 'No additional text content stored.'}
        </p>
      </div>

      {/* Structured Data */}
      {memory.structured_data && Object.keys(memory.structured_data).length > 0 && (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f9fafb', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database style={{ color: '#60a5fa' }} size={20} /> Structured Information
          </h3>
          <pre style={{ backgroundColor: '#1f2937', padding: '16px', borderRadius: '10px', color: '#e5e7eb', fontSize: '13px', overflowX: 'auto', margin: 0 }}>
            {JSON.stringify(memory.structured_data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
