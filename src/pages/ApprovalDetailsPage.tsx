import React, { useState } from 'react';
import {
  ArrowLeft, CheckCircle2, XCircle, Clock, MessageSquare, Briefcase
} from 'lucide-react';
import { governanceApi } from '../services/governanceApi';
import type { ApprovalRequest } from '../services/governanceApi';

interface ApprovalDetailsPageProps {
  approval: ApprovalRequest;
  onBack: () => void;
  onUpdated: () => void;
}

export const ApprovalDetailsPage: React.FC<ApprovalDetailsPageProps> = ({ approval: initialApp, onBack, onUpdated }) => {
  const [approval, setApproval] = useState<ApprovalRequest>(initialApp);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const storedUserJson = localStorage.getItem('strtos_user') || sessionStorage.getItem('strtos_user');
  const currentUser = storedUserJson ? JSON.parse(storedUserJson) : null;
  const isRequestor = currentUser && currentUser.id === approval.requested_by;

  const handleApprove = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const updated = await governanceApi.approve(approval.id, comment);
      if (updated) {
        setApproval(updated);
        setSuccessMessage('Governance decision APPROVED successfully!');
        onUpdated();
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to approve request');
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const updated = await governanceApi.reject(approval.id, comment || 'Rejected by governance reviewer');
      if (updated) {
        setApproval(updated);
        setSuccessMessage('Governance decision REJECTED.');
        onUpdated();
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to reject request');
    } finally {
      setLoading(false);
    }
  };

  const handleRequestChanges = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const updated = await governanceApi.requestChanges(approval.id, comment || 'Changes requested');
      if (updated) {
        setApproval(updated);
        setSuccessMessage('Changes requested successfully.');
        onUpdated();
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to request changes');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '28px', maxWidth: '1200px', margin: '0 auto' }}>
      <button
        onClick={onBack}
        style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'none', border: 'none', color: '#9ca3af', fontSize: '14px', cursor: 'pointer', marginBottom: '20px' }}
      >
        <ArrowLeft size={16} /> Back to Approvals List
      </button>

      {/* Banner */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '28px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#f9fafb', margin: 0 }}>{approval.title}</h1>
            <span style={{ padding: '4px 10px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#8b5cf6', borderRadius: '8px', fontSize: '12px', fontWeight: '700' }}>
              {approval.status}
            </span>
          </div>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>
            Requested on {new Date(approval.requested_at).toLocaleDateString()} | Decision Type: {approval.decision_type}
          </p>
        </div>
      </div>

      {/* Messages */}
      {errorMessage && (
        <div style={{ padding: '14px', backgroundColor: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', color: '#ef4444', borderRadius: '10px', marginBottom: '20px', fontSize: '14px', fontWeight: '600' }}>
          {errorMessage}
        </div>
      )}
      {successMessage && (
        <div style={{ padding: '14px', backgroundColor: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10b981', color: '#10b981', borderRadius: '10px', marginBottom: '20px', fontSize: '14px', fontWeight: '600' }}>
          {successMessage}
        </div>
      )}

      {/* AI Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '8px' }}>DETERMINISTIC RISK SCORE</div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: approval.risk_level === 'CRITICAL' ? '#ef4444' : approval.risk_level === 'HIGH' ? '#f59e0b' : '#10b981' }}>
            {approval.risk_level} ({approval.risk_score}/100)
          </div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '8px' }}>AI CONFIDENCE SCORE</div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#8b5cf6' }}>
            {approval.ai_confidence_score}%
          </div>
        </div>

        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '8px' }}>VERIFIED EVIDENCE</div>
          <div style={{ fontSize: '28px', fontWeight: '700', color: '#60a5fa' }}>
            {approval.evidence_count} Items
          </div>
        </div>
      </div>

      {/* AI Recommendation & Details */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f9fafb', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Briefcase style={{ color: '#8b5cf6' }} size={20} /> AI Decision Recommendation
        </h3>
        <p style={{ color: '#d1d5db', fontSize: '15px', lineHeight: '1.6', margin: '0 0 16px 0' }}>
          {approval.ai_recommendation || approval.description || 'No direct recommendation snippet provided.'}
        </p>

        {approval.requested_action && (
          <div style={{ padding: '14px', backgroundColor: '#1f2937', borderRadius: '10px', fontSize: '14px', color: '#9ca3af' }}>
            <strong style={{ color: '#f9fafb' }}>Requested Action:</strong> {approval.requested_action}
          </div>
        )}
      </div>

      {/* Governance Review Action Panel */}
      {approval.status === 'PENDING_APPROVAL' && (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px', marginBottom: '24px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f9fafb', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <MessageSquare style={{ color: '#8b5cf6' }} size={20} /> Reviewer Governance Action
          </h3>

          {isRequestor ? (
            <div style={{ padding: '14px', backgroundColor: 'rgba(245, 158, 11, 0.15)', border: '1px solid #f59e0b', color: '#f59e0b', borderRadius: '8px', fontSize: '14px', fontWeight: '600' }}>
              Self-Approval Warning: As the requestor of this governance approval, backend security policy prohibits you from approving your own request.
            </div>
          ) : (
            <div>
              <textarea
                rows={3}
                placeholder="Enter reviewer comment or rejection reason..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                style={{ width: '100%', backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px', padding: '12px', color: '#f9fafb', fontSize: '14px', marginBottom: '16px', resize: 'vertical' }}
              />

              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                <button
                  onClick={handleApprove}
                  disabled={loading}
                  style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 22px', backgroundColor: '#10b981', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer' }}
                >
                  <CheckCircle2 size={18} /> Approve Decision
                </button>

                <button
                  onClick={handleReject}
                  disabled={loading}
                  style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 22px', backgroundColor: '#ef4444', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer' }}
                >
                  <XCircle size={18} /> Reject Decision
                </button>

                <button
                  onClick={handleRequestChanges}
                  disabled={loading}
                  style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 22px', backgroundColor: '#f59e0b', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer' }}
                >
                  <Clock size={18} /> Request Changes
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Review Summary if Reviewed */}
      {approval.reviewed_by && (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f9fafb', marginBottom: '12px' }}>Audit Trail Review</h3>
          <div style={{ color: '#9ca3af', fontSize: '14px', lineHeight: '1.5' }}>
            <div><strong style={{ color: '#f9fafb' }}>Reviewed By User ID:</strong> {approval.reviewed_by}</div>
            <div><strong style={{ color: '#f9fafb' }}>Reviewed At:</strong> {approval.reviewed_at ? new Date(approval.reviewed_at).toLocaleString() : 'N/A'}</div>
            {approval.reviewer_comment && <div><strong style={{ color: '#f9fafb' }}>Comment:</strong> {approval.reviewer_comment}</div>}
            {approval.rejection_reason && <div><strong style={{ color: '#ef4444' }}>Rejection Reason:</strong> {approval.rejection_reason}</div>}
          </div>
        </div>
      )}
    </div>
  );
};
