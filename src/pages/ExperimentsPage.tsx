import React, { useEffect, useState } from 'react';
import { experimentsApi } from '../services/experimentsApi';
import type { Experiment } from '../services/experimentsApi';
import { FlaskConical, RefreshCw } from 'lucide-react';

export const ExperimentsPage: React.FC = () => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchExperiments = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await experimentsApi.listExperiments();
      setExperiments(data);
    } catch (err: any) {
      console.error(err);
      setError('Failed to fetch experiments. Displaying mock data for demonstration.');
      setExperiments([
        {
          id: 'exp-101',
          organization_id: 'org-demo',
          experiment_name: 'Campaign Budget Optimization Variant A',
          objective: 'Test 5% budget increase effect on overall conversion rates',
          hypothesis: 'Allocating 5% more budget to high-performing keywords yields 12% higher conversion',
          metric_name: 'conversion_rate',
          baseline_value: 10.0,
          target_value: 12.0,
          minimum_detectable_effect: 5.0,
          confidence_threshold: 95.0,
          control_sample_size: 45,
          variant_sample_size: 48,
          status: 'RUNNING',
          result: 'INCONCLUSIVE',
          confidence: 88.5,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 'exp-102',
          organization_id: 'org-demo',
          experiment_name: 'SEO Metadata Tone Adaptation Variant B',
          objective: 'Evaluate technical vs creative metadata titles on CTR',
          hypothesis: 'Action-oriented metadata titles increase organic CTR by 8%',
          metric_name: 'ctr_percentage',
          baseline_value: 4.2,
          target_value: 5.0,
          minimum_detectable_effect: 4.0,
          confidence_threshold: 95.0,
          control_sample_size: 120,
          variant_sample_size: 125,
          status: 'COMPLETED',
          result: 'WIN',
          winner: 'VARIANT_A',
          confidence: 96.8,
          created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
          updated_at: new Date(Date.now() - 86400000 * 1).toISOString(),
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExperiments();
  }, []);

  return (
    <div style={{ padding: '24px', color: '#f3f4f6', backgroundColor: '#090a0f', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#f3f4f6', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FlaskConical size={24} color="#6366f1" />
            Experiments & Continuous Optimization
          </h1>
          <p style={{ fontSize: '13px', color: '#9ca3af', marginTop: '4px' }}>
            Controlled A/B strategy experimentation, statistical significance measurement, & safe policy optimization.
          </p>
        </div>
        <button
          onClick={fetchExperiments}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 14px',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            borderRadius: '8px',
            color: '#818cf8',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {error && (
        <div style={{ backgroundColor: 'rgba(245, 158, 11, 0.15)', border: '1px solid #f59e0b', borderRadius: '8px', padding: '10px 14px', marginBottom: '20px', color: '#fbbf24', fontSize: '13px' }}>
          {error}
        </div>
      )}

      {/* Overview Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <div style={{ padding: '16px', backgroundColor: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '12px' }}>
          <div style={{ fontSize: '11px', color: '#9ca3af', marginBottom: '4px' }}>Total Experiments</div>
          <div style={{ fontSize: '22px', fontWeight: 700, color: '#f3f4f6' }}>{experiments.length}</div>
        </div>
        <div style={{ padding: '16px', backgroundColor: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '12px' }}>
          <div style={{ fontSize: '11px', color: '#9ca3af', marginBottom: '4px' }}>Active Running</div>
          <div style={{ fontSize: '22px', fontWeight: 700, color: '#60a5fa' }}>
            {experiments.filter((e) => e.status === 'RUNNING' || e.status === 'MEASURING').length}
          </div>
        </div>
        <div style={{ padding: '16px', backgroundColor: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '12px' }}>
          <div style={{ fontSize: '11px', color: '#9ca3af', marginBottom: '4px' }}>Winning Variants</div>
          <div style={{ fontSize: '22px', fontWeight: 700, color: '#34d399' }}>
            {experiments.filter((e) => e.result === 'WIN').length}
          </div>
        </div>
        <div style={{ padding: '16px', backgroundColor: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '12px' }}>
          <div style={{ fontSize: '11px', color: '#9ca3af', marginBottom: '4px' }}>Avg Confidence</div>
          <div style={{ fontSize: '22px', fontWeight: 700, color: '#a78bfa' }}>
            {experiments.length > 0 ? (experiments.reduce((acc, e) => acc + (e.confidence || 0), 0) / experiments.length).toFixed(1) : 0}%
          </div>
        </div>
      </div>

      {/* Experiments List */}
      <div style={{ backgroundColor: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '12px', padding: '20px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 600, color: '#f3f4f6', marginBottom: '16px' }}>Experiment Matrix</h2>
        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#9ca3af' }}>Loading experiments...</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {experiments.map((exp) => (
              <div
                key={exp.id}
                style={{
                  padding: '16px',
                  backgroundColor: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.05)',
                  borderRadius: '10px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '15px', fontWeight: 600, color: '#f3f4f6' }}>{exp.experiment_name}</span>
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '10px',
                        fontWeight: 700,
                        backgroundColor:
                          exp.status === 'COMPLETED'
                            ? 'rgba(52, 211, 153, 0.15)'
                            : exp.status === 'RUNNING' || exp.status === 'MEASURING'
                            ? 'rgba(96, 165, 250, 0.15)'
                            : 'rgba(156, 163, 175, 0.15)',
                        color:
                          exp.status === 'COMPLETED'
                            ? '#34d399'
                            : exp.status === 'RUNNING' || exp.status === 'MEASURING'
                            ? '#60a5fa'
                            : '#9ca3af',
                      }}
                    >
                      {exp.status}
                    </span>
                  </div>
                  <p style={{ fontSize: '12px', color: '#9ca3af', marginTop: '4px' }}>{exp.objective}</p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '11px', color: '#9ca3af' }}>Sample Size</div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#e5e7eb' }}>
                      Ctrl: {exp.control_sample_size} | Var: {exp.variant_sample_size}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '11px', color: '#9ca3af' }}>Confidence</div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#a78bfa' }}>{exp.confidence}%</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '11px', color: '#9ca3af' }}>Result</div>
                    <div
                      style={{
                        fontSize: '13px',
                        fontWeight: 700,
                        color: exp.result === 'WIN' ? '#34d399' : exp.result === 'LOSS' ? '#f87171' : '#fbbf24',
                      }}
                    >
                      {exp.result}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
