import React, { useEffect, useState } from 'react';
import { Network, AlertCircle, RefreshCw, HelpCircle } from 'lucide-react';
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
    } catch {
      setError('Knowledge engine is temporarily unavailable.');
    } finally {
      setLoading(false);
    }
  };

  const handleRebuild = async () => {
    try {
      setLoading(true);
      await knowledgeApi.rebuildGraph();
      await loadData();
    } catch {
      setError('Knowledge rebuild process failed.');
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
            <Network className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Business Knowledge</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            Important information, evidence & strategic relationships across your organization.
          </p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={handleRebuild}
            className="px-3 py-1.5 rounded-lg text-xs bg-[#151518] border border-white/10 hover:border-white/20 text-[#92929A] hover:text-[#F5F5F5] flex items-center space-x-2 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh Knowledge</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-950/60 border border-rose-800 rounded-xl flex items-center space-x-3 text-rose-200">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <span className="text-xs">{error}</span>
        </div>
      )}

      {/* KPI Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl">
          <span className="text-xs text-[#92929A] font-mono uppercase">Knowledge Entities</span>
          <p className="text-2xl font-bold mt-1 text-sky-400">
            {typeof overview?.total_nodes === 'number' ? overview.total_nodes : 'No current data'}
          </p>
        </div>
        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl">
          <span className="text-xs text-[#92929A] font-mono uppercase">Strategic Relations</span>
          <p className="text-2xl font-bold mt-1 text-indigo-400">
            {typeof overview?.total_relations === 'number' ? overview.total_relations : 'No current data'}
          </p>
        </div>
        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl">
          <span className="text-xs text-[#92929A] font-mono uppercase">Validated Evidence</span>
          <p className="text-2xl font-bold mt-1 text-emerald-400">
            {typeof overview?.validated_causal_links === 'number' ? overview.validated_causal_links : 'No current data'}
          </p>
        </div>
        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl">
          <span className="text-xs text-[#92929A] font-mono uppercase">Attention Required</span>
          <p className="text-2xl font-bold mt-1 text-amber-400">
            {typeof overview?.contradictions_count === 'number' ? overview.contradictions_count : 'No current data'}
          </p>
        </div>
      </div>

      {/* Knowledge Explorer / Nodes */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
          <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
            <Network className="w-4 h-4 text-sky-400" />
            <span>Business Knowledge Items</span>
          </h2>
          {nodes.length === 0 ? (
            <p className="text-xs text-[#92929A] italic">No knowledge items recorded.</p>
          ) : (
            <div className="grid grid-cols-2 gap-3 max-h-96 overflow-y-auto pr-2">
              {nodes.map((node) => (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`p-3 rounded-lg border cursor-pointer transition ${
                    selectedNode?.id === node.id
                      ? 'bg-sky-950/40 border-sky-500/80 text-sky-200'
                      : 'bg-[#151518] border-white/5 hover:border-white/15 text-[#F5F5F5]'
                  }`}
                >
                  <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                    {node.node_type}
                  </span>
                  <p className="text-xs font-semibold mt-1.5 truncate">{node.label}</p>
                  <span className="text-[10px] text-[#92929A] mt-1 block">
                    Confidence: {typeof node.confidence === 'number' ? `${node.confidence}%` : 'No current data'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Knowledge Item Inspector */}
        <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
          <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
            <HelpCircle className="w-4 h-4 text-indigo-400" />
            <span>Item Details</span>
          </h2>
          {selectedNode ? (
            <div className="space-y-3 text-xs text-[#F5F5F5]">
              <div>
                <span className="text-[#92929A] block font-mono text-[10px]">ITEM LABEL</span>
                <p className="font-semibold text-[#F5F5F5] text-sm mt-0.5">{selectedNode.label}</p>
              </div>
              <div>
                <span className="text-[#92929A] block font-mono text-[10px]">CATEGORY</span>
                <span className="px-2 py-0.5 rounded bg-[#151518] border border-white/10 text-sky-300 font-mono text-[10px]">
                  {selectedNode.node_type}
                </span>
              </div>
              <div>
                <span className="text-[#92929A] block font-mono text-[10px]">CONFIDENCE</span>
                <p className="text-emerald-400 font-mono font-bold">
                  {typeof selectedNode.confidence === 'number' ? `${selectedNode.confidence}%` : 'Not available yet'}
                </p>
              </div>
            </div>
          ) : (
            <p className="text-xs text-[#92929A] italic">Select a knowledge item to view details.</p>
          )}
        </div>
      </div>
    </div>
  );
};
