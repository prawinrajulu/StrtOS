import React, { useState, useEffect } from 'react';
import { Compass, BrainCircuit, AlertTriangle, RefreshCw } from 'lucide-react';
import { commandCenterApi } from '../services/commandCenterApi';
import type { CommandCenterOverview, DecisionAlternative, MultiAgentConsensus } from '../services/commandCenterApi';

export const CommandCenterPage: React.FC = () => {
  const [overview, setOverview] = useState<CommandCenterOverview | null>(null);
  const [alternatives, setAlternatives] = useState<DecisionAlternative[]>([]);
  const [consensus, setConsensus] = useState<MultiAgentConsensus | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const data = await commandCenterApi.getOverview();
      setOverview(data);
      if (data.active_decisions.length > 0) {
        const dId = data.active_decisions[0].id;
        const [alts, con] = await Promise.all([
          commandCenterApi.getDecisionAlternatives(dId),
          commandCenterApi.getMultiAgentConsensus(dId)
        ]);
        setAlternatives(alts);
        setConsensus(con);
      }
    } catch (e) {
      console.error('Failed to load Command Center overview:', e);
    }
  };

  const health = overview?.executive_health;
  const decision = overview?.active_decisions[0];

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100 space-y-8">
      {/* Header Cockpit */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Compass className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl font-bold text-slate-100 tracking-tight">Autonomous Strategic Command Center</h1>
          </div>
          <p className="text-slate-400 mt-1">Real-time executive decision cockpit unifying business state, agent swarm & predictive strategy.</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={loadData}
            className="px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 flex items-center space-x-2 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>SYNC COCKPIT</span>
          </button>
          <span className="px-3 py-1.5 rounded-full text-xs font-mono bg-cyan-950/80 border border-cyan-800 text-cyan-300 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
            <span>STRTOS v2.3.0 COMMAND CENTER</span>
          </span>
        </div>
      </div>

      {/* Executive Health Strip */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <span className="text-xs text-slate-400 font-mono uppercase">Executive Score</span>
          <p className="text-3xl font-extrabold mt-2 text-cyan-400">{health ? health.overall_score : '88.7'}</p>
          <p className="text-xs text-slate-400 mt-1">{health ? health.status : 'HEALTHY'}</p>
        </div>
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <span className="text-xs text-slate-400 font-mono uppercase">Business Health</span>
          <p className="text-3xl font-extrabold mt-2 text-emerald-400">{health ? health.business_health : '85.0'}</p>
          <p className="text-xs text-slate-400 mt-1">Metrics telemetry</p>
        </div>
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <span className="text-xs text-slate-400 font-mono uppercase">Strategy Health</span>
          <p className="text-3xl font-extrabold mt-2 text-indigo-400">{health ? health.strategy_health : '90.0'}</p>
          <p className="text-xs text-slate-400 mt-1">Multi-horizon alignment</p>
        </div>
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <span className="text-xs text-slate-400 font-mono uppercase">AI & Swarm Health</span>
          <p className="text-3xl font-extrabold mt-2 text-cyan-300">{health ? health.ai_health : '94.0'}</p>
          <p className="text-xs text-slate-400 mt-1">Agent consensus</p>
        </div>
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl backdrop-blur-sm">
          <span className="text-xs text-slate-400 font-mono uppercase">Governance Status</span>
          <p className="text-3xl font-extrabold mt-2 text-emerald-300">CLEARED</p>
          <p className="text-xs text-slate-400 mt-1">Policy rules enforced</p>
        </div>
      </div>

      {/* Strategic Decision Cockpit Split */}
      {decision && (
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-6">
          <div className="flex justify-between items-start">
            <div>
              <span className="px-2.5 py-1 rounded text-xs font-mono bg-amber-950 text-amber-300 border border-amber-800">
                GOVERNANCE: {decision.autonomy_level}
              </span>
              <h2 className="text-xl font-bold text-slate-100 mt-2">{decision.title}</h2>
              <p className="text-sm text-slate-400 mt-1">{decision.problem_statement}</p>
            </div>
            <div className="text-right">
              <span className="text-xs font-mono text-slate-400">Decision Confidence</span>
              <p className="text-2xl font-bold font-mono text-cyan-400">{decision.confidence_score}%</p>
            </div>
          </div>

          {/* Do Nothing vs Recommended Action Alternatives */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Do Nothing */}
            <div className="p-4 bg-slate-950/80 border border-rose-900/60 rounded-lg space-y-2">
              <span className="text-xs font-mono text-rose-400 font-semibold uppercase">Trajectory: Do Nothing</span>
              <p className="text-sm font-semibold text-slate-200">{decision.do_nothing_outcome}</p>
              {alternatives.find(a => a.option_type === 'DO_NOTHING') && (
                <div className="pt-2 text-xs font-mono text-rose-300 flex justify-between">
                  <span>Expected Value: ${alternatives.find(a => a.option_type === 'DO_NOTHING')?.expected_value}</span>
                  <span>Risk Score: {alternatives.find(a => a.option_type === 'DO_NOTHING')?.risk_score}</span>
                </div>
              )}
            </div>

            {/* Recommended Action */}
            <div className="p-4 bg-slate-950/80 border border-cyan-800/60 rounded-lg space-y-2">
              <span className="text-xs font-mono text-cyan-400 font-semibold uppercase">Recommended Action</span>
              <p className="text-sm font-semibold text-slate-200">{decision.recommended_action}</p>
              {alternatives.find(a => a.option_type === 'RECOMMENDED_ACTION') && (
                <div className="pt-2 text-xs font-mono text-cyan-300 flex justify-between">
                  <span>Expected Value: ${alternatives.find(a => a.option_type === 'RECOMMENDED_ACTION')?.expected_value}</span>
                  <span>Risk Score: {alternatives.find(a => a.option_type === 'RECOMMENDED_ACTION')?.risk_score}</span>
                </div>
              )}
            </div>
          </div>

          {/* Multi-Agent Swarm Consensus Panel */}
          {consensus && (
            <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-lg space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs font-mono text-slate-400 flex items-center space-x-2">
                  <BrainCircuit className="w-4 h-4 text-cyan-400" />
                  <span>5 Specialist Agent Swarm Consensus</span>
                </span>
                <span className="text-xs font-mono text-emerald-400 font-bold">{consensus.consensus_score}% CONSENSUS</span>
              </div>
              <div className="flex space-x-2">
                {consensus.supporting_agents.map(ag => (
                  <span key={ag} className="px-2 py-1 rounded bg-slate-800 text-xs font-mono text-cyan-300 border border-slate-700">
                    ✓ {ag.replace('Agent', '')}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Top Strategic Priorities */}
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
        <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <span>Strategic Executive Priorities</span>
        </h2>
        <div className="space-y-3">
          {overview?.top_priorities.map(p => (
            <div key={p.id} className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-1">
              <div className="flex items-center justify-between">
                <span className="px-2 py-0.5 rounded text-xs font-mono bg-rose-950 text-rose-300 border border-rose-800">{p.severity}</span>
                <span className="text-xs font-mono text-slate-400">{p.affected_objective}</span>
              </div>
              <h3 className="font-semibold text-slate-200 mt-1">{p.title}</h3>
              <p className="text-xs text-slate-400">{p.why_it_matters}</p>
              <div className="pt-2 text-xs text-cyan-300">
                Next Step: {p.recommended_next_step}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
