import React, { useEffect, useState } from 'react';
import { Network, AlertTriangle, RefreshCw, HelpCircle } from 'lucide-react';
import { knowledgeApi } from '../services/knowledgeApi';
import type {
  KnowledgeOverviewRecord,
  KnowledgeNodeRecord
} from '../services/knowledgeApi';

interface KnowledgePageProps {
  onNavigateToExplainability?: (decisionId: string) => void;
  onNavigateToRootCause?: (outcomeId: string) => void;
}

export const KnowledgePage: React.FC<KnowledgePageProps> = () => {
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
      setOverview(data || null);
      if (data?.nodes && data.nodes.length > 0) {
        setSelectedNode(data.nodes[0]);
      }
    } catch (err: any) {
      console.error('Error loading knowledge graph overview:', err);
      setError(err?.message || 'Failed to load knowledge graph');
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
      console.error('Error rebuilding graph:', err);
      setError(err?.message || 'Failed to rebuild graph');
      setLoading(false);
    }
  };

  const nodes = overview?.nodes || [];

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Network className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl font-bold text-slate-100 tracking-tight">Enterprise Knowledge & Causal Graph</h1>
          </div>
          <p className="text-slate-400 mt-1">Multi-entity causal links, evidence validation, contradictions & decision trace paths.</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={handleRebuild}
            className="px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 flex items-center space-x-2 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>REBUILD GRAPH</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-950/60 border border-rose-800 rounded-xl flex items-center space-x-3 text-rose-200">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span className="text-sm font-mono">{error}</span>
        </div>
      )}

      {/* KPI Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <span className="text-xs text-slate-400 font-mono uppercase">Total Entities/Nodes</span>
          <p className="text-3xl font-extrabold mt-2 text-cyan-400">{overview?.total_nodes || 0}</p>
        </div>
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <span className="text-xs text-slate-400 font-mono uppercase">Total Causal Relations</span>
          <p className="text-3xl font-extrabold mt-2 text-indigo-400">{overview?.total_relations || 0}</p>
        </div>
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <span className="text-xs text-slate-400 font-mono uppercase">Validated Causal Links</span>
          <p className="text-3xl font-extrabold mt-2 text-emerald-400">{overview?.validated_causal_links || 0}</p>
        </div>
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <span className="text-xs text-slate-400 font-mono uppercase">Graph Contradictions</span>
          <p className="text-3xl font-extrabold mt-2 text-amber-400">{overview?.contradictions_count || 0}</p>
        </div>
      </div>

      {/* Graph Visualizer Placeholder / Nodes Explorer */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
            <Network className="w-5 h-5 text-cyan-400" />
            <span>Knowledge Graph Explorer</span>
          </h2>
          {nodes.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No knowledge nodes stored in graph.</p>
          ) : (
            <div className="grid grid-cols-2 gap-3 max-h-96 overflow-y-auto pr-2">
              {nodes.map((node) => (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedNode?.id === node.id
                      ? 'bg-cyan-950/60 border-cyan-500/80 text-cyan-200'
                      : 'bg-slate-950/80 border-slate-800 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                    {node.node_type}
                  </span>
                  <p className="text-xs font-semibold mt-1 truncate">{node.label}</p>
                  <span className="text-[10px] text-slate-400 mt-1 block">Confidence: {node.confidence}%</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Node Inspector */}
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
            <HelpCircle className="w-5 h-5 text-indigo-400" />
            <span>Node Inspector</span>
          </h2>
          {selectedNode ? (
            <div className="space-y-3 text-xs text-slate-300">
              <div>
                <span className="text-slate-400 block font-mono text-[10px]">ENTITY LABEL</span>
                <p className="font-semibold text-slate-100 text-sm">{selectedNode.label}</p>
              </div>
              <div>
                <span className="text-slate-400 block font-mono text-[10px]">NODE TYPE</span>
                <span className="px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 font-mono">{selectedNode.node_type}</span>
              </div>
              <div>
                <span className="text-slate-400 block font-mono text-[10px]">CONFIDENCE SCORE</span>
                <p className="text-emerald-400 font-mono font-bold">{selectedNode.confidence}%</p>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic">Select a node from the explorer to inspect details.</p>
          )}
        </div>
      </div>
    </div>
  );
};
