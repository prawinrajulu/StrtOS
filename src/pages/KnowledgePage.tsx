import React, { useEffect, useState } from 'react';
import { Network, AlertTriangle, ArrowRight, RefreshCw, HelpCircle, ShieldAlert } from 'lucide-react';
import { knowledgeApi } from '../services/knowledgeApi';
import type {
  KnowledgeOverviewRecord,
  KnowledgeNodeRecord,
  KnowledgeRelationRecord
} from '../services/knowledgeApi';

interface KnowledgePageProps {
  onNavigateToExplainability?: (decisionId: string) => void;
  onNavigateToRootCause?: (outcomeId: string) => void;
}

export const KnowledgePage: React.FC<KnowledgePageProps> = ({
  onNavigateToExplainability,
  onNavigateToRootCause,
}) => {
  const [overview, setOverview] = useState<KnowledgeOverviewRecord | null>(null);
  const [, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<KnowledgeNodeRecord | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await knowledgeApi.getOverview();
      setOverview(data);
      if (data.nodes.length > 0) {
        setSelectedNode(data.nodes[0]);
      }
    } catch (err: any) {
      console.error('Error loading knowledge graph overview:', err);
      setError(err.message || 'Failed to load knowledge graph');
    } finally {
      setLoading(false);
    }
  };

  const handleRebuild = async () => {
    try {
      setLoading(true);
      await knowledgeApi.rebuildGraph();
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to rebuild graph');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'VALIDATED':
        return { bg: 'rgba(16, 185, 129, 0.2)', color: '#34d399' };
      case 'SUPPORTED':
        return { bg: 'rgba(56, 189, 248, 0.2)', color: '#38bdf8' };
      case 'HYPOTHESIS':
        return { bg: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24' };
      case 'CONTRADICTED':
        return { bg: 'rgba(239, 68, 68, 0.2)', color: '#f87171' };
      default:
        return { bg: 'rgba(148, 163, 184, 0.2)', color: '#94a3b8' };
    }
  };

  return (
    <div style={{ padding: '24px', color: '#fff', backgroundColor: '#070709', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, margin: 0, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Network style={{ color: '#a855f7' }} size={28} />
            Causal Intelligence & Knowledge Graph
          </h1>
          <p style={{ margin: '4px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>
            v1.8.0 — Grounded directed graph tracking causality across Evidence, Decisions, Predictions, Actions, Policies, Outcomes, and Lessons.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          {onNavigateToExplainability && (
            <button
              onClick={() => onNavigateToExplainability('dec_301')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                backgroundColor: '#1e293b',
                color: '#38bdf8',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
                padding: '10px 14px',
                fontSize: '14px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <HelpCircle size={16} /> Decision Explainability
            </button>
          )}

          {onNavigateToRootCause && (
            <button
              onClick={() => onNavigateToRootCause('out_801')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                backgroundColor: '#1e293b',
                color: '#f87171',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '8px',
                padding: '10px 14px',
                fontSize: '14px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <ShieldAlert size={16} /> Root Cause Analysis
            </button>
          )}

          <button
            onClick={handleRebuild}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: '#4f46e5',
              color: '#fff',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 16px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: '0 4px 14px rgba(79, 70, 229, 0.4)',
            }}
          >
            <RefreshCw size={16} /> Rebuild & Validate Graph
          </button>
        </div>
      </div>

      {error && (
        <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: '8px', padding: '12px 16px', marginBottom: '24px', color: '#fca5a5' }}>
          <AlertTriangle size={18} style={{ display: 'inline', marginRight: '8px' }} />
          {error}
        </div>
      )}

      {/* KPI Summary Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Total Nodes</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#f8fafc' }}>{overview?.total_nodes ?? 12}</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Total Relations</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#a855f7' }}>{overview?.total_relations ?? 11}</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Validated Causal Links</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#34d399' }}>{overview?.validated_causal_links ?? 9}</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Causal Hypotheses</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#fbbf24' }}>{overview?.causal_hypotheses ?? 2}</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Contradictions</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#ef4444' }}>{overview?.contradictions_count ?? 0}</div>
        </div>

        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '4px' }}>Avg Causal Confidence</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#38bdf8' }}>{overview?.average_causal_confidence ?? 89.2}%</div>
        </div>
      </div>

      {/* Visual Pipeline Flow */}
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px', marginBottom: '28px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 16px 0', color: '#f8fafc' }}>
          Standard Causal Graph Traversal Path
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(90px, 1fr))', gap: '8px', alignItems: 'center' }}>
          {['CLIENT', 'EVIDENCE', 'AGENT', 'DECISION', 'PREDICTION', 'POLICY', 'ACTION', 'OUTCOME', 'LESSON'].map((type, i, arr) => (
            <React.Fragment key={type}>
              <div style={{ backgroundColor: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '10px 4px', textAlign: 'center' }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#38bdf8' }}>{type}</div>
              </div>
              {i < arr.length - 1 && <ArrowRight size={14} style={{ color: '#475569', margin: '0 auto' }} />}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Graph Node Explorer & Relationship Matrix */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Knowledge Nodes */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 600, margin: '0 0 16px 0', color: '#f8fafc' }}>
            Knowledge Nodes Explorer
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '420px', overflowY: 'auto' }}>
            {overview?.nodes.map((node: KnowledgeNodeRecord) => (
              <div
                key={node.id}
                onClick={() => setSelectedNode(node)}
                style={{
                  backgroundColor: selectedNode?.id === node.id ? 'rgba(168, 85, 247, 0.15)' : 'rgba(255,255,255,0.02)',
                  border: selectedNode?.id === node.id ? '1px solid #a855f7' : '1px solid rgba(255,255,255,0.06)',
                  borderRadius: '8px',
                  padding: '12px',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#f1f5f9' }}>{node.label}</div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>
                    Type: <strong style={{ color: '#38bdf8' }}>{node.node_type}</strong> | Ref: #{node.entity_id.slice(0, 8)}
                  </div>
                </div>

                <div style={{ fontSize: '13px', fontWeight: 700, color: '#34d399' }}>
                  {node.confidence}%
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Knowledge Relations */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '20px' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 600, margin: '0 0 16px 0', color: '#f8fafc' }}>
            Directed Causal Relations
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '420px', overflowY: 'auto' }}>
            {overview?.relations.map((rel: KnowledgeRelationRecord) => {
              const badge = getStatusBadge(rel.causal_status);
              return (
                <div key={rel.id} style={{ backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '8px', padding: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontSize: '13px', fontWeight: 700, color: '#a855f7' }}>
                      {rel.relation_type}
                    </span>
                    <span style={{ backgroundColor: badge.bg, color: badge.color, padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700 }}>
                      {rel.causal_status}
                    </span>
                  </div>

                  <div style={{ fontSize: '12px', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span>Node #{rel.source_node_id.slice(0, 8)}</span>
                    <ArrowRight size={12} />
                    <span>Node #{rel.target_node_id.slice(0, 8)}</span>
                  </div>

                  <div style={{ fontSize: '12px', color: '#cbd5e1', marginTop: '6px' }}>
                    Confidence: <strong style={{ color: '#38bdf8' }}>{rel.confidence}%</strong> | Weight: {rel.weight}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
