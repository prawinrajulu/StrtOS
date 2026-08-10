import React, { useState } from 'react';
import { ArrowLeft, Play, ShieldCheck, RefreshCw, Target } from 'lucide-react';
import { executionApi } from '../services/executionApi';
import type { ActionRecord, ClosedLoopOptimizationResponse } from '../services/executionApi';

interface ActionDetailsPageProps {
  action: ActionRecord;
  onBack: () => void;
}

export const ActionDetailsPage: React.FC<ActionDetailsPageProps> = ({ action, onBack }) => {
  const [currentAction, setCurrentAction] = useState<ActionRecord>(action);
  const [loading, setLoading] = useState(false);
  const [actualVal, setActualVal] = useState('3.8');
  const [measurementResult, setMeasurementResult] = useState<ClosedLoopOptimizationResponse | null>(null);

  const handleExecute = async () => {
    setLoading(true);
    try {
      const res = await executionApi.executeAction(currentAction.id);
      setCurrentAction(res);
    } catch (err: any) {
      alert(err.message || 'Execution failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveSubmit = async () => {
    setLoading(true);
    try {
      const res = await executionApi.approveAction(currentAction.id);
      setCurrentAction(res);
    } catch (err: any) {
      alert(err.message || 'Approval submission failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async () => {
    setLoading(true);
    try {
      const res = await executionApi.retryAction(currentAction.id);
      setCurrentAction(res);
    } catch (err: any) {
      alert(err.message || 'Retry failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleMeasureOutcome = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await executionApi.measureOutcome(currentAction.id, parseFloat(actualVal));
      setMeasurementResult(res);
    } catch (err: any) {
      alert(err.message || 'Outcome measurement failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '28px', maxWidth: '1100px', margin: '0 auto' }}>
      <button
        onClick={onBack}
        style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'none', border: 'none', color: '#9ca3af', fontSize: '14px', cursor: 'pointer', marginBottom: '20px' }}
      >
        <ArrowLeft size={16} /> Back to Actions
      </button>

      {/* Header Banner */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '28px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
            <span style={{ padding: '4px 10px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#8b5cf6', borderRadius: '8px', fontSize: '12px', fontWeight: '700' }}>
              TYPE: {currentAction.action_type}
            </span>
            <span style={{ padding: '4px 10px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981', borderRadius: '8px', fontSize: '12px', fontWeight: '700' }}>
              POLICY: {currentAction.policy_decision}
            </span>
            <span style={{ padding: '4px 10px', backgroundColor: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b', borderRadius: '8px', fontSize: '12px', fontWeight: '700' }}>
              MODE: {currentAction.autonomy_mode}
            </span>
          </div>

          <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#f9fafb', margin: '0 0 8px 0' }}>{currentAction.name}</h1>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>{currentAction.description || 'Policy-managed action execution'}</p>
        </div>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          {currentAction.policy_decision === 'REQUIRE_APPROVAL' && !currentAction.approval_id && (
            <button
              onClick={handleApproveSubmit}
              disabled={loading}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 20px', backgroundColor: '#6366f1', color: '#fff', border: 'none', borderRadius: '10px', fontWeight: '700', cursor: 'pointer' }}
            >
              <ShieldCheck size={18} /> Request Governance Approval
            </button>
          )}

          {['APPROVED', 'DRAFT', 'QUEUED'].includes(currentAction.status) && (
            <button
              onClick={handleExecute}
              disabled={loading}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 20px', backgroundColor: '#10b981', color: '#fff', border: 'none', borderRadius: '10px', fontWeight: '700', cursor: 'pointer' }}
            >
              <Play size={18} /> Execute Action Now
            </button>
          )}

          {currentAction.status === 'FAILED' && (
            <button
              onClick={handleRetry}
              disabled={loading || currentAction.retry_count >= currentAction.max_retries}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 20px', backgroundColor: '#f59e0b', color: '#fff', border: 'none', borderRadius: '10px', fontWeight: '700', cursor: 'pointer' }}
            >
              <RefreshCw size={18} /> Retry Action ({currentAction.retry_count}/{currentAction.max_retries})
            </button>
          )}
        </div>
      </div>

      {/* Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>ACTION STATUS</div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#8b5cf6' }}>{currentAction.status}</div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>RISK LEVEL</div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#60a5fa' }}>{currentAction.risk_level}</div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', fontWeight: '600', marginBottom: '6px' }}>RETRY COUNTER</div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#10b981' }}>{currentAction.retry_count} / {currentAction.max_retries}</div>
        </div>
      </div>

      {/* Payload & Output */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#f9fafb', marginBottom: '12px' }}>Input Payload</h3>
          <pre style={{ backgroundColor: '#1f2937', padding: '14px', borderRadius: '8px', color: '#d1d5db', fontSize: '12px', overflowX: 'auto' }}>
            {JSON.stringify(currentAction.input_payload || {}, null, 2)}
          </pre>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#f9fafb', marginBottom: '12px' }}>Output Payload</h3>
          <pre style={{ backgroundColor: '#1f2937', padding: '14px', borderRadius: '8px', color: '#d1d5db', fontSize: '12px', overflowX: 'auto' }}>
            {JSON.stringify(currentAction.output_payload || {}, null, 2)}
          </pre>
        </div>
      </div>

      {/* Closed-Loop Outcome Measurement Panel */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#f9fafb', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Target style={{ color: '#10b981' }} size={20} /> Closed-Loop Outcome Measurement
        </h3>

        {measurementResult ? (
          <div style={{ backgroundColor: '#1f2937', border: '1px solid #10b981', borderRadius: '12px', padding: '20px' }}>
            <h4 style={{ color: '#10b981', fontSize: '16px', fontWeight: '700', margin: '0 0 8px 0' }}>Closed-Loop Optimization Measured!</h4>
            <p style={{ color: '#d1d5db', fontSize: '14px', margin: '0 0 10px 0' }}>{measurementResult.lesson_summary}</p>
            <div style={{ fontSize: '12px', color: '#9ca3af' }}>
              Accuracy Score: {measurementResult.accuracy_score}% | Error: {measurementResult.percentage_error}% | Outcome Status: {measurementResult.outcome_status}
            </div>
          </div>
        ) : (
          <form onSubmit={handleMeasureOutcome} style={{ display: 'flex', gap: '14px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: '220px' }}>
              <label style={{ display: 'block', fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '6px' }}>ACTUAL PERFORMANCE KPI VALUE</label>
              <input
                type="number"
                step="0.01"
                value={actualVal}
                onChange={(e) => setActualVal(e.target.value)}
                required
                style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '10px', color: '#f9fafb', fontSize: '14px' }}
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              style={{ padding: '12px 24px', backgroundColor: '#10b981', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer' }}
            >
              Evaluate Closed-Loop Optimization
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
