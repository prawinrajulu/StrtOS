import React, { useEffect, useState } from 'react';
import { TrendingUp, Search, Sliders, ChevronRight } from 'lucide-react';
import { predictionsApi } from '../services/predictionsApi';
import type { PredictionRecord } from '../services/predictionsApi';
import { globalEventStream } from '../services/eventStream';

interface PredictionsPageProps {
  onSelectPrediction: (prediction: PredictionRecord) => void;
  onOpenSimulator: () => void;
}

export const PredictionsPage: React.FC<PredictionsPageProps> = ({
  onSelectPrediction,
  onOpenSimulator
}) => {
  const [predictions, setPredictions] = useState<PredictionRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('');

  const fetchPredictions = async () => {
    setLoading(true);
    const data = await predictionsApi.getPredictions({
      scenario_type: typeFilter,
      search: search
    });
    setPredictions(data.predictions);
    setTotal(data.total);
    setLoading(false);
  };

  useEffect(() => {
    fetchPredictions();

    const unsubscribe = globalEventStream.subscribe((event) => {
      if (['prediction.created', 'prediction.generated', 'prediction.scenario.created', 'prediction.approved'].includes(event.event_type)) {
        fetchPredictions();
      }
    });
    return () => unsubscribe();
  }, [typeFilter, search]);

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'LOW':
        return <span style={{ color: '#10b981', fontWeight: '700', fontSize: '11px' }}>LOW RISK</span>;
      case 'MEDIUM':
        return <span style={{ color: '#f59e0b', fontWeight: '700', fontSize: '11px' }}>MEDIUM RISK</span>;
      case 'HIGH':
        return <span style={{ color: '#ef4444', fontWeight: '700', fontSize: '11px' }}>HIGH RISK</span>;
      case 'CRITICAL':
        return <span style={{ color: '#dc2626', fontWeight: '800', fontSize: '11px' }}>CRITICAL RISK</span>;
      default:
        return null;
    }
  };

  const getScenarioBadge = (type: string) => {
    switch (type) {
      case 'CONSERVATIVE':
        return <span style={{ padding: '3px 8px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981', borderRadius: '6px', fontSize: '11px', fontWeight: '700' }}>CONSERVATIVE</span>;
      case 'AGGRESSIVE':
        return <span style={{ padding: '3px 8px', backgroundColor: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', borderRadius: '6px', fontSize: '11px', fontWeight: '700' }}>AGGRESSIVE</span>;
      case 'BALANCED':
      default:
        return <span style={{ padding: '3px 8px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#8b5cf6', borderRadius: '6px', fontSize: '11px', fontWeight: '700' }}>BALANCED</span>;
    }
  };

  return (
    <div style={{ padding: '28px', maxWidth: '1300px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '26px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <TrendingUp style={{ color: '#8b5cf6' }} size={28} /> Predictive Decision Intelligence & Scenarios
          </h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>
            Scenario simulation, range forecasting, and accuracy tracking ({total} Total Predictions)
          </p>
        </div>

        <button
          onClick={onOpenSimulator}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 20px', backgroundColor: '#6366f1', color: '#fff', border: 'none', borderRadius: '10px', fontWeight: '700', cursor: 'pointer' }}
        >
          <Sliders size={18} /> Open What-If Simulator
        </button>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>AVG PREDICTION CONFIDENCE</div>
          <div style={{ fontSize: '26px', fontWeight: '700', color: '#8b5cf6' }}>86.4%</div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>ACTIVE PREDICTIONS</div>
          <div style={{ fontSize: '26px', fontWeight: '700', color: '#60a5fa' }}>{total}</div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>CALIBRATION ACCURACY</div>
          <div style={{ fontSize: '26px', fontWeight: '700', color: '#10b981' }}>90.5%</div>
        </div>
      </div>

      {/* Search & Filters */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '16px', marginBottom: '24px', display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ flex: 1, minWidth: '240px', position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
          <input
            type="text"
            placeholder="Search decision scenarios, objectives, or metrics..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px 12px 10px 38px', color: '#f9fafb', fontSize: '14px' }}
          />
        </div>

        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          style={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px 14px', color: '#f9fafb', fontSize: '14px' }}
        >
          <option value="">All Scenario Types</option>
          <option value="CONSERVATIVE">Conservative</option>
          <option value="BALANCED">Balanced</option>
          <option value="AGGRESSIVE">Aggressive</option>
        </select>
      </div>

      {/* Prediction Cards */}
      {loading ? (
        <div style={{ color: '#9ca3af', textAlign: 'center', padding: '40px' }}>Loading predictive decision scenarios...</div>
      ) : predictions.length === 0 ? (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '40px', textAlign: 'center', color: '#9ca3af' }}>
          No decision predictions generated yet. Launch what-if simulator to generate scenarios!
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {predictions.map((pred) => (
            <div
              key={pred.id}
              onClick={() => onSelectPrediction(pred)}
              style={{
                backgroundColor: '#111827',
                border: '1px solid #1f2937',
                borderRadius: '14px',
                padding: '20px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '16px'
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#6366f1')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#1f2937')}
            >
              <div style={{ flex: 1, minWidth: '280px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  {getScenarioBadge(pred.scenario_type)}
                  {getRiskBadge(pred.risk_level)}
                  <span style={{ fontSize: '11px', color: '#6b7280' }}>
                    {new Date(pred.created_at).toLocaleDateString()}
                  </span>
                </div>
                <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#f9fafb', margin: '0 0 6px 0' }}>{pred.scenario_name}</h3>
                <p style={{ color: '#9ca3af', fontSize: '13px', margin: 0 }}>{pred.objective || 'Predictive Decision Model'}</p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '11px', color: '#6b7280', fontWeight: '600' }}>PREDICTED {pred.metric_name}</div>
                  <div style={{ fontSize: '18px', fontWeight: '700', color: '#8b5cf6' }}>
                    {pred.predicted_value}{pred.unit}
                    <span style={{ fontSize: '12px', color: '#9ca3af', marginLeft: '6px' }}>
                      ({pred.lower_bound}–{pred.upper_bound}{pred.unit})
                    </span>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '11px', color: '#6b7280', fontWeight: '600' }}>CONFIDENCE</div>
                  <div style={{ fontSize: '15px', fontWeight: '700', color: '#60a5fa' }}>{pred.confidence_score}%</div>
                </div>

                <ChevronRight size={20} style={{ color: '#6b7280' }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
