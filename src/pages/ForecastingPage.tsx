import React, { useEffect, useState } from 'react';
import { TrendingUp, BarChart2, Sliders, ShieldAlert, Sparkles, RefreshCw } from 'lucide-react';
import { forecastingApi } from '../services/forecastingApi';
import type {
  Forecast,
  SimulationResponse,
  FutureRisk,
  FutureOpportunity
} from '../services/forecastingApi';

export const ForecastingPage: React.FC = () => {
  const [forecasts, setForecasts] = useState<Forecast[]>([]);
  const [selectedForecast, setSelectedForecast] = useState<Forecast | null>(null);
  const [simulation, setSimulation] = useState<SimulationResponse | null>(null);
  const [risks, setRisks] = useState<FutureRisk[]>([]);
  const [opportunities, setOpportunities] = useState<FutureOpportunity[]>([]);
  const [budgetMultiplier, setBudgetMultiplier] = useState(1.0);
  const [, setLoading] = useState(true);
  const [selectedHorizon, setSelectedHorizon] = useState<'7_DAYS' | '30_DAYS' | '90_DAYS' | '365_DAYS'>('90_DAYS');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const fcList = await forecastingApi.listForecasts();
      setForecasts(Array.isArray(fcList) ? fcList : []);

      if (fcList && fcList.length > 0) {
        selectForecast(fcList[0]);
      }
    } catch {
      setForecasts([]);
    } finally {
      setLoading(false);
    }
  };

  const selectForecast = async (fc: Forecast) => {
    setSelectedForecast(fc);
    try {
      const [rData, oData] = await Promise.all([
        forecastingApi.getFutureRisks(fc.id),
        forecastingApi.getFutureOpportunities(fc.id)
      ]);
      setRisks(Array.isArray(rData) ? rData : []);
      setOpportunities(Array.isArray(oData) ? oData : []);
    } catch {
      setRisks([]);
      setOpportunities([]);
    }
  };

  const handleSimulate = async (multiplier: number) => {
    setBudgetMultiplier(multiplier);
    if (selectedForecast) {
      try {
        const sim = await forecastingApi.simulateForecast(selectedForecast.id, 2500, multiplier);
        setSimulation(sim);
      } catch {
        setSimulation(null);
      }
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <TrendingUp className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Strategic Forecast</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            See what StrtOS expects next.
          </p>
        </div>
        <button
          onClick={loadData}
          className="px-3 py-1.5 rounded-lg text-xs font-mono bg-[#151518] border border-white/10 hover:border-white/20 text-[#92929A] hover:text-[#F5F5F5] flex items-center space-x-2 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Horizon Tabs (7 DAYS, 30 DAYS, 90 DAYS, 365 DAYS) */}
      <div className="flex items-center space-x-2 border-b border-white/5 pb-2">
        {(['7_DAYS', '30_DAYS', '90_DAYS', '365_DAYS'] as const).map((hz) => (
          <button
            key={hz}
            onClick={() => setSelectedHorizon(hz)}
            className={`px-4 py-2 rounded-lg text-xs font-mono transition ${
              selectedHorizon === hz
                ? 'bg-sky-500 text-slate-950 font-bold'
                : 'bg-[#151518] text-[#92929A] hover:text-[#F5F5F5] border border-white/5'
            }`}
          >
            {hz.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Forecast Selector Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {forecasts.length === 0 ? (
          <div className="md:col-span-3 p-6 bg-[#111113] border border-white/[0.06] rounded-xl text-xs text-[#92929A] italic">
            No current data.
          </div>
        ) : (
          forecasts.map((fc) => (
            <div
              key={fc.id}
              onClick={() => selectForecast(fc)}
              className={`p-4 rounded-xl border transition cursor-pointer ${
                selectedForecast?.id === fc.id
                  ? 'bg-sky-950/40 border-sky-500/80 text-sky-200'
                  : 'bg-[#111113] border-white/[0.06] hover:border-white/15 text-[#F5F5F5]'
              }`}
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono text-sky-400 text-[10px]">{fc.horizon.replace('_', ' ')}</span>
                <span className="px-2 py-0.5 rounded font-mono bg-[#151518] text-[10px]">{fc.trend_direction}</span>
              </div>
              <h3 className="font-bold text-sm mt-1.5">{fc.title}</h3>
              <div className="mt-2 flex items-center justify-between text-xs text-[#92929A]">
                <span>Forecast Confidence: {fc.confidence_score}%</span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Selected Forecast & What-If Simulator Split */}
      {selectedForecast && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Active Forecast Metrics */}
          <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
            <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
              <BarChart2 className="w-4 h-4 text-sky-400" />
              <span>Forecast Metrics</span>
            </h2>
            <div className="space-y-3">
              {selectedForecast.metrics && selectedForecast.metrics.length > 0 ? (
                selectedForecast.metrics.map((m) => (
                  <div key={m.id} className="p-4 bg-[#151518] border border-white/5 rounded-lg space-y-1.5 text-xs">
                    <div className="flex justify-between">
                      <span className="font-semibold text-[#F5F5F5]">{m.metric_name}</span>
                      <span className="font-mono text-sky-300 font-bold">{m.forecast_value} {m.unit}</span>
                    </div>
                    <div className="flex justify-between text-[10px] text-[#92929A] font-mono">
                      <span>Expected Range: {m.lower_bound} – {m.upper_bound}</span>
                      <span>Forecast Confidence: {m.confidence_score}%</span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-[#92929A] italic">No metric bounds recorded.</p>
              )}
            </div>
          </div>

          {/* What-If Strategy Simulator Panel */}
          <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
            <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
              <Sliders className="w-4 h-4 text-indigo-400" />
              <span>What-If Strategy Simulation</span>
            </h2>
            <div className="space-y-4 text-xs">
              <div>
                <label className="text-xs font-mono text-[#92929A]">Investment Multiplier ({budgetMultiplier}x)</label>
                <input 
                  type="range" 
                  min="0.5" 
                  max="2.5" 
                  step="0.1"
                  value={budgetMultiplier}
                  onChange={(e) => handleSimulate(parseFloat(e.target.value))}
                  className="w-full mt-2 accent-sky-400"
                />
              </div>

              {simulation ? (
                <div className="p-4 bg-[#151518] border border-white/5 rounded-lg space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-[10px] text-[#92929A] font-mono">Baseline Outcome</span>
                      <p className="text-lg font-bold font-mono text-[#F5F5F5]">${simulation.baseline_outcome}</p>
                    </div>
                    <div>
                      <span className="text-[10px] text-sky-400 font-mono">Simulated Future</span>
                      <p className="text-lg font-bold font-mono text-sky-300">${simulation.simulated_outcome}</p>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-white/5 flex justify-between text-xs font-mono text-[#92929A]">
                    <span>Expected Change: +${simulation.delta_outcome}</span>
                    <span>Risk Level: {simulation.risk_score}</span>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-[#92929A] italic">Adjust slider to simulate future strategy impact.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Future Risks & Opportunities */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
          <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-rose-400" />
            <span>Future Risks</span>
          </h2>
          {risks.length === 0 ? (
            <p className="text-xs text-[#92929A] italic">No current data.</p>
          ) : (
            risks.map((r, idx) => (
              <div key={idx} className="p-4 bg-[#151518] border border-white/5 rounded-lg space-y-1 text-xs">
                <span className="text-[10px] font-mono text-rose-300 font-semibold">{r.risk_type}</span>
                <p className="text-[#92929A]">{r.evidence}</p>
                <p className="text-rose-300 pt-1 font-mono text-[11px]">Mitigation: {r.mitigation}</p>
              </div>
            ))
          )}
        </div>

        <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4">
          <h2 className="text-sm font-semibold text-[#F5F5F5] flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-sky-400" />
            <span>Future Opportunities</span>
          </h2>
          {opportunities.length === 0 ? (
            <p className="text-xs text-[#92929A] italic">No current data.</p>
          ) : (
            opportunities.map((o, idx) => (
              <div key={idx} className="p-4 bg-[#151518] border border-white/5 rounded-lg space-y-1 text-xs">
                <span className="text-[10px] font-mono text-sky-300 font-semibold">{o.opportunity_type}</span>
                <p className="text-[#92929A]">{o.evidence}</p>
                <p className="text-sky-300 pt-1 font-mono text-[11px]">Preparation: {o.recommended_preparation}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
