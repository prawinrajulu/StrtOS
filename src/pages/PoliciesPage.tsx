import React, { useEffect, useState } from 'react';
import { ShieldCheck, Cpu, RefreshCw, AlertTriangle, ChevronRight } from 'lucide-react';
import { policiesApi } from '../services/policiesApi';
import type {
  PolicyAnalytics,
  AgentPerformanceMetricItem,
  PolicyRecord,
} from '../services/policiesApi';
import { mapInternalExecutionToBusinessLanguage } from '../services/eventTranslationLayer';

interface PoliciesPageProps {
  onSelectPolicy?: (policyId: string) => void;
  onNavigateToEvolution?: () => void;
}

export const PoliciesPage: React.FC<PoliciesPageProps> = ({
  onSelectPolicy,
  onNavigateToEvolution,
}) => {
  const [analytics, setAnalytics] = useState<PolicyAnalytics | null>(null);
  const [policies, setPolicies] = useState<PolicyRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [anaData, polData] = await Promise.all([
        policiesApi.getAnalytics().catch(() => null),
        policiesApi.listPolicies().catch(() => []),
      ]);

      setAnalytics(anaData);
      setPolicies(polData || []);
    } catch {
      setError('Policy engine is temporarily unavailable.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <ShieldCheck className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Policies</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            Understand how StrtOS makes governed decisions.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          {onNavigateToEvolution && (
            <button
              onClick={onNavigateToEvolution}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 flex items-center space-x-1 transition"
            >
              <span>Governance Evolution</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          )}
          <button
            onClick={loadData}
            className="px-3 py-1.5 rounded-lg text-xs font-mono bg-[#151518] border border-white/10 hover:border-white/20 text-[#92929A] hover:text-[#F5F5F5] flex items-center space-x-2 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-950/60 border border-rose-800 rounded-xl text-xs text-rose-200 flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* KPI Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
          <span className="text-xs text-[#92929A] font-mono uppercase">Active Policies</span>
          <p className="text-2xl font-bold text-sky-400 mt-1">{analytics?.active_policies ?? 'No current data'}</p>
        </div>
        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
          <span className="text-xs text-[#92929A] font-mono uppercase">Avg Policy Score</span>
          <p className="text-2xl font-bold text-emerald-400 mt-1">
            {typeof analytics?.average_policy_score === 'number' ? `${analytics.average_policy_score}%` : 'No current data'}
          </p>
        </div>
        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
          <span className="text-xs text-[#92929A] font-mono uppercase">Policy Improvement</span>
          <p className="text-2xl font-bold text-indigo-400 mt-1">
            {typeof analytics?.policy_improvement_percent === 'number' ? `+${analytics.policy_improvement_percent}%` : 'No current data'}
          </p>
        </div>
        <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
          <span className="text-xs text-[#92929A] font-mono uppercase">Governance Status</span>
          <p className="text-2xl font-bold text-amber-400 mt-1">
            {analytics?.governance_pending_count ? 'Needs Review' : 'Active'}
          </p>
        </div>
      </div>

      {/* Performance Breakdown */}
      <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
        <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-sky-400" />
          <span>Business Decision Strategy Performance</span>
        </h2>

        {loading ? (
          <p className="text-xs text-[#92929A]">Loading policies...</p>
        ) : !analytics || analytics.agents_performance.length === 0 ? (
          <p className="text-xs text-[#92929A] italic">No current data.</p>
        ) : (
          <div className="space-y-3">
            {analytics.agents_performance.map((ap: AgentPerformanceMetricItem, idx: number) => (
              <div key={idx} className="p-4 bg-[#151518] border border-white/5 rounded-lg flex items-center justify-between text-xs space-x-4">
                <div className="space-y-0.5">
                  <h3 className="font-semibold text-[#F5F5F5]">{mapInternalExecutionToBusinessLanguage(ap.agent_name)}</h3>
                  <span className="text-[10px] font-mono text-[#92929A]">Version: {ap.current_policy_version}</span>
                </div>

                <div className="flex items-center space-x-4 font-mono text-right">
                  <div>
                    <span className="text-[10px] text-[#92929A] block">SCORE</span>
                    <span className="text-emerald-400 font-bold">{ap.performance_score}%</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-[#92929A] block">RELIABILITY</span>
                    <span className="text-sky-300 font-bold">{ap.reliability_score}%</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-[#92929A] block">STATUS</span>
                    <span className={ap.trend === 'IMPROVING' ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'}>
                      {ap.trend === 'IMPROVING' ? 'Active' : 'Improving'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Registered Policies */}
      <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
        <h2 className="text-sm font-semibold text-[#F5F5F5]">Registered Governance Policies</h2>

        {policies.length === 0 ? (
          <p className="text-xs text-[#92929A] italic">No current data.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {policies.map((p) => (
              <div
                key={p.id}
                onClick={() => onSelectPolicy && onSelectPolicy(p.id)}
                className="p-4 bg-[#151518] border border-white/5 hover:border-white/15 rounded-lg cursor-pointer transition space-y-2 text-xs"
              >
                <div className="flex justify-between items-center">
                  <h3 className="font-semibold text-[#F5F5F5]">{mapInternalExecutionToBusinessLanguage(p.policy_name || p.agent_name)}</h3>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800">
                    {p.status}
                  </span>
                </div>
                <div className="flex justify-between text-[10px] font-mono text-[#92929A] pt-1">
                  <span>Version: {p.current_version}</span>
                  <span>Updated: {new Date(p.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
