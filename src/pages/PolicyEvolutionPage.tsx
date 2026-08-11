import React, { useEffect, useState } from 'react';
import { ArrowLeft, ArrowRight, Activity, GitCommit, Play } from 'lucide-react';
import { policiesApi } from '../services/policiesApi';
import type { PolicyRecord, AgentPerformanceMetricItem } from '../services/policiesApi';

interface PolicyEvolutionPageProps {
  onBack: () => void;
}

export const PolicyEvolutionPage: React.FC<PolicyEvolutionPageProps> = ({ onBack }) => {
  const [policies, setPolicies] = useState<PolicyRecord[]>([]);
  const [agentsPerf, setAgentsPerf] = useState<AgentPerformanceMetricItem[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>('Business Analysis');
  const [, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [pData, aData] = await Promise.all([
        policiesApi.listPolicies(),
        policiesApi.getAgentsPerformance(),
      ]);
      setPolicies(pData);
      setAgentsPerf(aData);
    } catch (err) {
      console.error('Failed to load policy evolution data:', err);
    } finally {
      setLoading(false);
    }
  };

  const selectedPerf = agentsPerf.find((a) => a.agent_name === selectedAgent) || {
    agent_name: selectedAgent,
    current_policy_version: '1.0.0',
    performance_score: 80.0,
    accuracy_score: 80.0,
    reliability_score: 85.0,
    success_rate: 85.0,
    sample_count: 5,
    trend: 'STABLE',
    last_evaluated_at: new Date().toISOString(),
  };

  const selectedPolicy = policies.find((p) => p.agent_name === selectedAgent);

  const handleRunEvolution = async () => {
    if (!selectedPolicy) {
      alert(`No policy found for ${selectedAgent}. Create one first or trigger agent execution.`);
      return;
    }
    try {
      setOptimizing(true);
      setStatusMsg(null);
      const res = await policiesApi.optimizePolicy(selectedPolicy.id, {
        reason: `Auto-evolution pipeline run for ${selectedAgent}`,
      });
      setStatusMsg(`Pipeline Execution Result: ${res.status}. Governance Approval Request Created.`);
      await loadData();
    } catch (err: any) {
      setStatusMsg(`Pipeline execution error: ${err.message}`);
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div style={{ padding: '24px', color: '#fff', backgroundColor: '#070709', minHeight: '100vh' }}>
      <button
        onClick={onBack}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          backgroundColor: 'transparent',
          border: 'none',
          color: '#94a3b8',
          fontSize: '14px',
          cursor: 'pointer',
          marginBottom: '20px',
        }}
      >
        <ArrowLeft size={16} /> Back to Policies
      </button>

      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, margin: 0, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <GitCommit style={{ color: '#818cf8' }} size={28} />
          Policy Evolution Pipeline
        </h1>
        <p style={{ margin: '4px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>
          Visualizing end-to-end policy lifecycle from historical outcome measurement to governance approval.
        </p>
      </div>

      {/* Agent Selector & Run Trigger */}
      <div style={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '16px', marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <label style={{ fontSize: '14px', color: '#94a3b8', fontWeight: 500 }}>Select Specialist Agent:</label>
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            style={{
              backgroundColor: '#1e293b',
              color: '#fff',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              padding: '8px 12px',
              fontSize: '14px',
              fontWeight: 600,
            }}
          >
            <option value="Business Analysis">Business Analysis</option>
            <option value="SEO Audit">SEO Audit</option>
            <option value="Competitor Research">Competitor Research</option>
            <option value="Marketing Strategy">Marketing Strategy</option>
            <option value="Campaign Planner">Campaign Planner</option>
          </select>
        </div>

        <button
          onClick={handleRunEvolution}
          disabled={optimizing}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: '#10b981',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            padding: '10px 18px',
            fontSize: '14px',
            fontWeight: 600,
            cursor: 'pointer',
            boxShadow: '0 4px 14px rgba(16, 185, 129, 0.4)',
          }}
        >
          <Play size={16} />
          {optimizing ? 'Executing Pipeline...' : 'Run Self-Optimization Step'}
        </button>
      </div>

      {statusMsg && (
        <div style={{ backgroundColor: 'rgba(59, 130, 246, 0.15)', border: '1px solid #3b82f6', borderRadius: '8px', padding: '12px 16px', marginBottom: '24px', color: '#93c5fd' }}>
          <Activity size={18} style={{ display: 'inline', marginRight: '8px' }} />
          {statusMsg}
        </div>
      )}

      {/* Visual Pipeline Flow */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '12px', alignItems: 'center', marginBottom: '32px' }}>
        {/* Step 1 */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid #38bdf8', borderRadius: '12px', padding: '16px', textAlign: 'center' }}>
          <div style={{ fontSize: '11px', color: '#38bdf8', fontWeight: 700, textTransform: 'uppercase' }}>STEP 1</div>
          <div style={{ fontSize: '14px', fontWeight: 700, margin: '6px 0', color: '#fff' }}>Current Policy</div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>v{selectedPerf.current_policy_version}</div>
        </div>

        <ArrowRight size={20} style={{ color: '#475569', margin: '0 auto' }} />

        {/* Step 2 */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid #818cf8', borderRadius: '12px', padding: '16px', textAlign: 'center' }}>
          <div style={{ fontSize: '11px', color: '#818cf8', fontWeight: 700, textTransform: 'uppercase' }}>STEP 2</div>
          <div style={{ fontSize: '14px', fontWeight: 700, margin: '6px 0', color: '#fff' }}>Performance</div>
          <div style={{ fontSize: '12px', color: '#34d399' }}>{selectedPerf.performance_score}% Score</div>
        </div>

        <ArrowRight size={20} style={{ color: '#475569', margin: '0 auto' }} />

        {/* Step 3 */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid #f59e0b', borderRadius: '12px', padding: '16px', textAlign: 'center' }}>
          <div style={{ fontSize: '11px', color: '#f59e0b', fontWeight: 700, textTransform: 'uppercase' }}>STEP 3</div>
          <div style={{ fontSize: '14px', fontWeight: 700, margin: '6px 0', color: '#fff' }}>Candidate</div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>+5% Bounded Delta</div>
        </div>

        <ArrowRight size={20} style={{ color: '#475569', margin: '0 auto' }} />

        {/* Step 4 */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid #a855f7', borderRadius: '12px', padding: '16px', textAlign: 'center' }}>
          <div style={{ fontSize: '11px', color: '#a855f7', fontWeight: 700, textTransform: 'uppercase' }}>STEP 4</div>
          <div style={{ fontSize: '14px', fontWeight: 700, margin: '6px 0', color: '#fff' }}>A/B Test</div>
          <div style={{ fontSize: '12px', color: '#c084fc' }}>Deterministic Valid</div>
        </div>

        <ArrowRight size={20} style={{ color: '#475569', margin: '0 auto' }} />

        {/* Step 5 */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid #ec4899', borderRadius: '12px', padding: '16px', textAlign: 'center' }}>
          <div style={{ fontSize: '11px', color: '#ec4899', fontWeight: 700, textTransform: 'uppercase' }}>STEP 5</div>
          <div style={{ fontSize: '14px', fontWeight: 700, margin: '6px 0', color: '#fff' }}>Risk Engine</div>
          <div style={{ fontSize: '12px', color: '#f472b6' }}>LOW / MEDIUM</div>
        </div>

        <ArrowRight size={20} style={{ color: '#475569', margin: '0 auto' }} />

        {/* Step 6 */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid #fbbf24', borderRadius: '12px', padding: '16px', textAlign: 'center' }}>
          <div style={{ fontSize: '11px', color: '#fbbf24', fontWeight: 700, textTransform: 'uppercase' }}>STEP 6</div>
          <div style={{ fontSize: '14px', fontWeight: 700, margin: '6px 0', color: '#fff' }}>Governance</div>
          <div style={{ fontSize: '12px', color: '#fde047' }}>Approval Req</div>
        </div>

        <ArrowRight size={20} style={{ color: '#475569', margin: '0 auto' }} />

        {/* Step 7 */}
        <div style={{ backgroundColor: '#0f172a', border: '1px solid #10b981', borderRadius: '12px', padding: '16px', textAlign: 'center' }}>
          <div style={{ fontSize: '11px', color: '#10b981', fontWeight: 700, textTransform: 'uppercase' }}>STEP 7</div>
          <div style={{ fontSize: '14px', fontWeight: 700, margin: '6px 0', color: '#fff' }}>Activation</div>
          <div style={{ fontSize: '12px', color: '#34d399' }}>Active Version</div>
        </div>
      </div>
    </div>
  );
};
