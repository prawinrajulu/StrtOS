import React, { useEffect, useState } from 'react';
import { Brain, ChevronRight } from 'lucide-react';
import { learningApi } from '../services/learningApi';
import type { LearningOverviewRecord, AgentPerformanceRecord } from '../services/learningApi';
import { globalEventStream } from '../services/eventStream';

interface LearningPageProps {
  onSelectAgent: (agent: AgentPerformanceRecord) => void;
  onOpenPolicies: (agentName: string) => void;
}

export const LearningPage: React.FC<LearningPageProps> = ({ onSelectAgent, onOpenPolicies }) => {
  const [overview, setOverview] = useState<LearningOverviewRecord | null>(null);
  const [activeTab, setActiveTab] = useState<'agents' | 'tools' | 'providers'>('agents');

  const fetchLearningData = async () => {
    const data = await learningApi.getOverview();
    setOverview(data);
  };

  useEffect(() => {
    fetchLearningData();

    const unsubscribe = globalEventStream.subscribe((event) => {
      if (event.event_type.startsWith('learning.')) {
        fetchLearningData();
      }
    });
    return () => unsubscribe();
  }, []);

  const getReliabilityBadge = (relClass: string) => {
    switch (relClass) {
      case 'EXCELLENT':
        return <span style={{ padding: '3px 8px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981', borderRadius: '6px', fontSize: '11px', fontWeight: '700' }}>EXCELLENT</span>;
      case 'GOOD':
        return <span style={{ padding: '3px 8px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#8b5cf6', borderRadius: '6px', fontSize: '11px', fontWeight: '700' }}>GOOD</span>;
      case 'MODERATE':
        return <span style={{ padding: '3px 8px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b', borderRadius: '6px', fontSize: '11px', fontWeight: '700' }}>MODERATE</span>;
      default:
        return <span style={{ padding: '3px 8px', backgroundColor: 'rgba(156, 163, 175, 0.15)', color: '#9ca3af', borderRadius: '6px', fontSize: '11px', fontWeight: '700' }}>INSUFFICIENT DATA</span>;
    }
  };

  return (
    <div style={{ padding: '28px', maxWidth: '1300px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '26px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Brain style={{ color: '#10b981' }} size={28} /> Adaptive Agent Learning & Self-Optimization
        </h1>
        <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>
          Deterministic reliability scoring, versioned policy management, tool health telemetry, and grounded optimization
        </p>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>SYSTEM RELIABILITY SCORE</div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#10b981' }}>{overview?.overall_system_reliability || 80.0}%</div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>PREDICTION ACCURACY AVG</div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#6366f1' }}>{overview?.prediction_accuracy_avg || 80.0}%</div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>ACTIVE AGENT POLICIES</div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#8b5cf6' }}>{overview?.active_policies_count || 5}</div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>TOTAL ADAPTATIONS APPLIED</div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#f59e0b' }}>{overview?.total_adaptations_applied || 0}</div>
        </div>
      </div>

      {/* Sub-Navigation Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', borderBottom: '1px solid #1f2937', paddingBottom: '12px' }}>
        {[
          { label: '5 Core Specialist Agents', value: 'agents' },
          { label: 'Tool Reliability Telemetry', value: 'tools' },
          { label: 'LLM Provider Health', value: 'providers' }
        ].map((tab) => (
          <button
            key={tab.value}
            onClick={() => setActiveTab(tab.value as any)}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === tab.value ? '#6366f1' : '#111827',
              color: activeTab === tab.value ? '#ffffff' : '#9ca3af',
              fontSize: '13px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Agents View */}
      {activeTab === 'agents' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {overview?.agent_performance.map((ag) => (
            <div
              key={ag.id}
              onClick={() => onSelectAgent(ag)}
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
                  {getReliabilityBadge(ag.reliability_class)}
                  <span style={{ fontSize: '11px', color: '#6b7280' }}>VERSION {ag.agent_version}</span>
                </div>
                <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0' }}>{ag.agent_name}</h3>
                <div style={{ display: 'flex', gap: '16px', color: '#9ca3af', fontSize: '12px' }}>
                  <span>Prediction Accuracy: {ag.prediction_accuracy}%</span>
                  <span>Human Approval: {ag.human_approval_rate}%</span>
                  <span>Executions: {ag.total_executions}</span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '11px', color: '#6b7280', fontWeight: '600' }}>RELIABILITY SCORE</div>
                  <div style={{ fontSize: '22px', fontWeight: '700', color: '#10b981' }}>{ag.current_reliability_score}%</div>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenPolicies(ag.agent_name);
                  }}
                  style={{ padding: '8px 14px', backgroundColor: '#1f2937', color: '#6366f1', border: '1px solid #374151', borderRadius: '8px', fontWeight: '700', fontSize: '12px', cursor: 'pointer' }}
                >
                  Version Policies
                </button>

                <ChevronRight size={20} style={{ color: '#6b7280' }} />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tools View */}
      {activeTab === 'tools' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {overview?.tool_reliability.map((t) => (
            <div key={t.id} style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <span style={{ fontSize: '15px', fontWeight: '700', color: '#f9fafb', textTransform: 'uppercase' }}>{t.tool_name}</span>
                <span style={{ fontSize: '14px', fontWeight: '700', color: '#10b981' }}>{t.reliability_score}%</span>
              </div>
              <div style={{ fontSize: '12px', color: '#9ca3af', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div>Availability: {t.availability_rate}%</div>
                <div>Evidence Quality: {t.evidence_quality}%</div>
                <div>Average Latency: {t.average_latency_ms} ms</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Providers View */}
      {activeTab === 'providers' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          {overview?.provider_performance.map((p) => (
            <div key={p.id} style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <span style={{ fontSize: '15px', fontWeight: '700', color: '#f9fafb', textTransform: 'uppercase' }}>{p.provider} ({p.model})</span>
                <span style={{ fontSize: '14px', fontWeight: '700', color: '#6366f1' }}>{p.confidence_score}%</span>
              </div>
              <div style={{ fontSize: '12px', color: '#9ca3af', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div>Structured Output Accuracy: {p.structured_output_success_rate}%</div>
                <div>Success Count: {p.success_count}</div>
                <div>Average Latency: {p.average_latency_ms} ms</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
