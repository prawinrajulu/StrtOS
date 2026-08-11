import React, { useState, useEffect } from 'react';
import { TrendingUp, ShieldAlert, Sparkles, RefreshCw, BarChart2, Sliders } from 'lucide-react';
import { forecastingApi } from '../services/forecastingApi';
import type { Forecast, SimulationResponse, FutureRisk, FutureOpportunity } from '../services/forecastingApi';

export const ForecastingPage: React.FC = () => {
  const [forecasts, setForecasts] = useState<Forecast[]>([]);
  const [selectedForecast, setSelectedForecast] = useState<Forecast | null>(null);
  const [simulation, setSimulation] = useState<SimulationResponse | null>(null);
  const [risks, setRisks] = useState<FutureRisk[]>([]);
  const [opportunities, setOpportunities] = useState<FutureOpportunity[]>([]);
  const [budgetMultiplier, setBudgetMultiplier] = useState(1.2);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const data = await forecastingApi.listForecasts();
      setForecasts(data);
      if (data.length > 0) {
        selectForecast(data[0]);
      }
    } catch (e) {
      console.error('Failed to load forecasting data:', e);
    }
  };

  const selectForecast = async (fc: Forecast) => {
    setSelectedForecast(fc);
    try {
      const [sim, rks, opps] = await Promise.all([
        forecastingApi.simulateForecast(fc.id, 2500, budgetMultiplier),
        forecastingApi.getFutureRisks(fc.id),
        forecastingApi.getFutureOpportunities(fc.id)
      ]);
      setSimulation(sim);
      setRisks(rks);
      setOpportunities(opps);
    } catch (e) {
      console.error('Failed to fetch forecast details:', e);
    }
  };

  const handleSimulate = async (multiplier: number) => {
    setBudgetMultiplier(multiplier);
    if (selectedForecast) {
      const sim = await forecastingApi.simulateForecast(selectedForecast.id, 2500, multiplier);
      setSimulation(sim);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <TrendingUp className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl font-bold text-slate-100 tracking-tight">Strategic Forecasting & Simulation Control Center</h1>
          </div>
          <p className="text-slate-400 mt-1">Multi-horizon predictive forecasting, future risk/opportunity radar & what-if simulator.</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={loadData}
            className="px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 flex items-center space-x-2 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>RE-SIMULATE</span>
          </button>
          <span className="px-3 py-1.5 rounded-full text-xs font-mono bg-cyan-950/80 border border-cyan-800 text-cyan-300 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
            <span>STRTOS v2.2.0 FORECASTER</span>
          </span>
        </div>
      </div>

      {/* Forecast Selector Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {forecasts.map(fc => (
          <div 
            key={fc.id}
            onClick={() => selectForecast(fc)}
            className={`p-5 rounded-xl border transition cursor-pointer backdrop-blur-sm ${
              selectedForecast?.id === fc.id ? 'bg-cyan-950/40 border-cyan-500' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-cyan-300">{fc.horizon.replace('_', ' ')} HORIZON</span>
              <span className="px-2 py-0.5 rounded text-xs font-mono bg-slate-800 text-slate-300">{fc.trend_direction}</span>
            </div>
            <h3 className="font-bold text-slate-100 mt-2">{fc.title}</h3>
            <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
              <span>Confidence: {fc.confidence_score}%</span>
              <span>{fc.metrics.length} Metrics</span>
            </div>
          </div>
        ))}
      </div>

      {/* Selected Forecast & What-If Simulator Split */}
      {selectedForecast && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Active Forecast Metrics */}
          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
            <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
              <BarChart2 className="w-5 h-5 text-cyan-400" />
              <span>Forecasted Metric Bounds</span>
            </h2>
            <div className="space-y-3">
              {selectedForecast.metrics.map(m => (
                <div key={m.id} className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-semibold text-slate-200">{m.metric_name}</span>
                    <span className="font-mono text-cyan-300">{m.forecast_value} {m.unit}</span>
                  </div>
                  <div className="flex justify-between text-xs text-slate-400 font-mono">
                    <span>Lower: {m.lower_bound}</span>
                    <span>Upper: {m.upper_bound}</span>
                    <span>Conf: {m.confidence_score}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* What-If Simulator Panel */}
          <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
            <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
              <Sliders className="w-5 h-5 text-indigo-400" />
              <span>What-If Strategy Simulator</span>
            </h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-mono text-slate-400">Resource & Investment Multiplier ({budgetMultiplier}x)</label>
                <input 
                  type="range" 
                  min="0.5" 
                  max="2.5" 
                  step="0.1"
                  value={budgetMultiplier}
                  onChange={(e) => handleSimulate(parseFloat(e.target.value))}
                  className="w-full mt-2 accent-cyan-400"
                />
              </div>

              {simulation && (
                <div className="p-4 bg-slate-950/90 border border-cyan-800/60 rounded-lg space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-xs text-slate-400 font-mono">Baseline Outcome</span>
                      <p className="text-xl font-bold font-mono text-slate-200">${simulation.baseline_outcome}</p>
                    </div>
                    <div>
                      <span className="text-xs text-cyan-400 font-mono">Simulated Future</span>
                      <p className="text-xl font-bold font-mono text-cyan-300">${simulation.simulated_outcome}</p>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-slate-800 flex justify-between text-xs font-mono text-slate-300">
                    <span>Delta: +${simulation.delta_outcome}</span>
                    <span>Risk Score: {simulation.risk_score}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Future Risks & Opportunities */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            <span>Future Risk Radar</span>
          </h2>
          {risks.length === 0 ? (
            <p className="text-slate-400 text-sm">No future risk vectors detected.</p>
          ) : (
            risks.map((r, idx) => (
              <div key={idx} className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-1">
                <span className="text-xs font-mono text-rose-300 font-semibold">{r.risk_type}</span>
                <p className="text-xs text-slate-400">{r.evidence}</p>
                <p className="text-xs text-slate-300 pt-1">Mitigation: {r.mitigation}</p>
              </div>
            ))
          )}
        </div>

        <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
          <h2 className="text-lg font-semibold text-slate-100 flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-cyan-400" />
            <span>Future Opportunities</span>
          </h2>
          {opportunities.length === 0 ? (
            <p className="text-slate-400 text-sm">No future growth opportunities detected.</p>
          ) : (
            opportunities.map((o, idx) => (
              <div key={idx} className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-1">
                <span className="text-xs font-mono text-cyan-300 font-semibold">{o.opportunity_type}</span>
                <p className="text-xs text-slate-400">{o.evidence}</p>
                <p className="text-xs text-slate-300 pt-1">Preparation: {o.recommended_preparation}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
