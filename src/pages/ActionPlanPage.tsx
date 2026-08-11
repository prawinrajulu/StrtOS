import React, { useState } from 'react';
import { decisionOptimizationApi } from '../services/decisionOptimizationApi';
import type { ActionPlan } from '../services/decisionOptimizationApi';
import { GitCommit } from 'lucide-react';

export const ActionPlanPage: React.FC = () => {
  const [candidateIdsInput, setCandidateIdsInput] = useState<string>('');
  const [plan, setPlan] = useState<ActionPlan | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreatePlan = async () => {
    try {
      setLoading(true);
      setError(null);
      const ids = candidateIdsInput.split(',').map((id) => id.trim()).filter(Boolean);
      const createdPlan = await decisionOptimizationApi.createPlan({ candidates: ids });
      setPlan(createdPlan);
    } catch (err: any) {
      setError(err.message || 'Failed to create action plan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 bg-slate-950 text-slate-100 min-h-screen">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2 text-cyan-400">
          <GitCommit className="h-6 w-6" /> Predictive Action Planning
        </h1>
        <p className="text-sm text-slate-400">
          Construct topologically ordered DAG execution plans with dependency cycle resolution and risk checks.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-900/30 border border-red-500/50 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4 backdrop-blur-md">
        <h2 className="text-sm font-semibold text-slate-200">Create Action Plan</h2>
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Enter candidate IDs (comma-separated)..."
            value={candidateIdsInput}
            onChange={(e) => setCandidateIdsInput(e.target.value)}
            className="flex-1 px-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
          />
          <button
            onClick={handleCreatePlan}
            disabled={loading || !candidateIdsInput.trim()}
            className="px-6 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm rounded-lg transition disabled:opacity-50"
          >
            {loading ? 'Building DAG Plan...' : 'Build Plan'}
          </button>
        </div>
      </div>

      {plan && (
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-6 backdrop-blur-md">
          <div className="flex justify-between items-center border-b border-slate-800 pb-4">
            <div>
              <span className="text-xs text-slate-500">Plan ID:</span>
              <div className="font-mono text-sm font-bold text-cyan-400">{plan.plan_id}</div>
            </div>
            <span className="px-3 py-1 bg-emerald-950 text-emerald-400 border border-emerald-800 rounded-full text-xs font-semibold">
              STATUS: {plan.status}
            </span>
          </div>

          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-300">Ordered Execution Steps</h3>
            {plan.steps.map((step) => (
              <div key={step.id} className="p-4 bg-slate-950/70 border border-slate-800 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center font-bold text-xs">
                    #{step.step_order}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-slate-200">Action Candidate ID: {step.action_id}</div>
                    {step.dependency && (
                      <div className="text-xs text-slate-500 mt-0.5">Predecessor Step: {step.dependency}</div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <span className={`text-xs px-2.5 py-1 rounded font-semibold ${
                    step.risk_level === 'LOW' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400 border border-amber-800'
                  }`}>
                    {step.risk_level} RISK
                  </span>
                  <span className="text-xs font-mono text-cyan-400">{step.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
