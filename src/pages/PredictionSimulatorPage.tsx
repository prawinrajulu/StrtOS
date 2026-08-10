import React, { useState } from 'react';
import { ArrowLeft, Sliders, TrendingUp } from 'lucide-react';
import { predictionsApi } from '../services/predictionsApi';
import type { WhatIfSimulationResponse, PredictionRecord } from '../services/predictionsApi';

interface PredictionSimulatorPageProps {
  onBack: () => void;
  onSelectPrediction: (prediction: PredictionRecord) => void;
}

export const PredictionSimulatorPage: React.FC<PredictionSimulatorPageProps> = ({
  onBack,
  onSelectPrediction
}) => {
  const [metricName, setMetricName] = useState('ROAS');
  const [currentBudget, setCurrentBudget] = useState(10000);
  const [simulatedBudget, setSimulatedBudget] = useState(15000);
  const [timelineDays, setTimelineDays] = useState(90);

  const [simulation, setSimulation] = useState<WhatIfSimulationResponse | null>(null);
  const [scenarios, setScenarios] = useState<PredictionRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const simRes = await predictionsApi.simulateWhatIf({
        metric_name: metricName,
        current_budget: currentBudget,
        simulated_budget: simulatedBudget,
        timeline_days: timelineDays
      });
      setSimulation(simRes);
    } catch (err: any) {
      alert(err.message || 'Simulation failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateScenarios = async () => {
    setGenerating(true);
    try {
      const res = await predictionsApi.generateScenarios({
        metric_name: metricName,
        monthly_budget: simulatedBudget,
        timeline_days: timelineDays,
        objective: `Simulated decision flight for $${simulatedBudget.toLocaleString()}/mo budget`
      });
      setScenarios(res.scenarios);
    } catch (err: any) {
      alert(err.message || 'Scenario generation failed.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div style={{ padding: '28px', maxWidth: '1200px', margin: '0 auto' }}>
      <button
        onClick={onBack}
        style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'none', border: 'none', color: '#9ca3af', fontSize: '14px', cursor: 'pointer', marginBottom: '20px' }}
      >
        <ArrowLeft size={16} /> Back to Predictions
      </button>

      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '26px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Sliders style={{ color: '#6366f1' }} size={28} /> What-If Decision & Budget Simulator
        </h1>
        <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>
          Simulate performance ranges and compare Conservative, Balanced, and Aggressive decision scenarios
        </p>
      </div>

      {/* Simulator Inputs */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '24px', marginBottom: '28px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginBottom: '20px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '8px' }}>TARGET METRIC</label>
            <input
              type="text"
              value={metricName}
              onChange={(e) => setMetricName(e.target.value)}
              style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px', color: '#f9fafb', fontSize: '14px' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '8px' }}>
              CURRENT BUDGET: ${currentBudget.toLocaleString()} / mo
            </label>
            <input
              type="range"
              min="2000"
              max="50000"
              step="1000"
              value={currentBudget}
              onChange={(e) => setCurrentBudget(Number(e.target.value))}
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '8px' }}>
              SIMULATED BUDGET: ${simulatedBudget.toLocaleString()} / mo
            </label>
            <input
              type="range"
              min="2000"
              max="100000"
              step="1000"
              value={simulatedBudget}
              onChange={(e) => setSimulatedBudget(Number(e.target.value))}
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '8px' }}>TIMELINE DAYS</label>
            <select
              value={timelineDays}
              onChange={(e) => setTimelineDays(Number(e.target.value))}
              style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px', color: '#f9fafb', fontSize: '14px' }}
            >
              <option value={30}>30 Days</option>
              <option value={60}>60 Days</option>
              <option value={90}>90 Days</option>
              <option value={180}>180 Days</option>
            </select>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
          <button
            onClick={handleSimulate}
            disabled={loading}
            style={{ padding: '12px 24px', backgroundColor: '#6366f1', color: '#fff', border: 'none', borderRadius: '10px', fontWeight: '700', cursor: 'pointer' }}
          >
            Run What-If Simulation
          </button>

          <button
            onClick={handleGenerateScenarios}
            disabled={generating}
            style={{ padding: '12px 24px', backgroundColor: '#8b5cf6', color: '#fff', border: 'none', borderRadius: '10px', fontWeight: '700', cursor: 'pointer' }}
          >
            Generate Decision Scenarios
          </button>
        </div>
      </div>

      {/* Simulation Result */}
      {simulation && (
        <div style={{ backgroundColor: '#111827', border: '1px solid #6366f1', borderRadius: '16px', padding: '24px', marginBottom: '28px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f9fafb', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingUp style={{ color: '#10b981' }} size={20} /> Simulation Output Summary
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '16px' }}>
            <div style={{ backgroundColor: '#1f2937', padding: '16px', borderRadius: '10px' }}>
              <div style={{ fontSize: '11px', color: '#9ca3af', fontWeight: '600' }}>BASELINE EXPECTED</div>
              <div style={{ fontSize: '22px', fontWeight: '700', color: '#60a5fa' }}>{simulation.baseline.predicted_value}x</div>
            </div>

            <div style={{ backgroundColor: '#1f2937', padding: '16px', borderRadius: '10px' }}>
              <div style={{ fontSize: '11px', color: '#9ca3af', fontWeight: '600' }}>SIMULATED EXPECTED</div>
              <div style={{ fontSize: '22px', fontWeight: '700', color: '#10b981' }}>{simulation.simulated_scenario.predicted_value}x</div>
            </div>

            <div style={{ backgroundColor: '#1f2937', padding: '16px', borderRadius: '10px' }}>
              <div style={{ fontSize: '11px', color: '#9ca3af', fontWeight: '600' }}>PROJECTED DELTA</div>
              <div style={{ fontSize: '22px', fontWeight: '700', color: '#8b5cf6' }}>+{simulation.delta.percentage_delta}%</div>
            </div>
          </div>
        </div>
      )}

      {/* Scenario Comparison Cards */}
      {scenarios.length > 0 && (
        <div>
          <h3 style={{ fontSize: '20px', fontWeight: '700', color: '#f9fafb', marginBottom: '16px' }}>Side-by-Side Decision Scenario Comparison</h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
            {scenarios.map((scen) => (
              <div
                key={scen.id}
                onClick={() => onSelectPrediction(scen)}
                style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '24px', cursor: 'pointer', transition: 'all 0.2s ease' }}
                onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#6366f1')}
                onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#1f2937')}
              >
                <div style={{ fontSize: '12px', fontWeight: '700', color: '#8b5cf6', marginBottom: '6px' }}>{scen.scenario_type}</div>
                <h4 style={{ fontSize: '18px', fontWeight: '700', color: '#f9fafb', margin: '0 0 10px 0' }}>{scen.scenario_name}</h4>

                <div style={{ marginBottom: '14px' }}>
                  <div style={{ fontSize: '12px', color: '#9ca3af' }}>EXPECTED {scen.metric_name}</div>
                  <div style={{ fontSize: '28px', fontWeight: '700', color: '#10b981' }}>
                    {scen.predicted_value}{scen.unit}
                    <span style={{ fontSize: '13px', color: '#9ca3af', marginLeft: '6px' }}>
                      ({scen.lower_bound}–{scen.upper_bound}{scen.unit})
                    </span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', borderTop: '1px solid #1f2937', paddingTop: '12px' }}>
                  <span style={{ color: '#9ca3af' }}>Confidence: <strong style={{ color: '#60a5fa' }}>{scen.confidence_score}%</strong></span>
                  <span style={{ color: '#9ca3af' }}>Risk: <strong style={{ color: '#f59e0b' }}>{scen.risk_level}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
