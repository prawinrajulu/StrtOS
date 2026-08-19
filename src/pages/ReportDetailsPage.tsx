import React, { useState } from 'react';
import {
  ArrowLeft, FileText, Award, Activity, Download, CheckCircle2,
  TrendingUp, Search, Target, Megaphone, Calendar, ShieldCheck, Briefcase
} from 'lucide-react';
import { reportsApi } from '../services/reportsApi';
import type { ExecutiveReport } from '../services/reportsApi';

interface ReportDetailsPageProps {
  report: ExecutiveReport;
  onBack: () => void;
}

export const ReportDetailsPage: React.FC<ReportDetailsPageProps> = ({ report, onBack }) => {
  const [downloading, setDownloading] = useState(false);

  const handleExport = async () => {
    setDownloading(true);
    const data = await reportsApi.exportReport(report.id);
    setDownloading(false);
    if (data) {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${report.title.toLowerCase().replace(/\s+/g, '-')}-report.json`;
      a.click();
    }
  };

  const agentSections = [
    { title: 'Business & TAM Analysis', key: 'Business Analysis Agent', icon: TrendingUp, color: '#3b82f6' },
    { title: 'Technical & SEO Audit', key: 'SEO Audit Agent', icon: Search, color: '#10b981' },
    { title: 'Competitor Landscape Matrix', key: 'Competitor Research Agent', icon: Target, color: '#f59e0b' },
    { title: 'Omnichannel Marketing Strategy', key: 'Marketing Strategy Agent', icon: Megaphone, color: '#8b5cf6' },
    { title: '90-Day Execution Campaign Plan', key: 'Campaign Planner Agent', icon: Calendar, color: '#ec4899' },
  ];

  return (
    <div style={{ padding: '24px', maxWidth: '1300px', margin: '0 auto' }}>
      <button
        onClick={onBack}
        style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'none', border: 'none', color: '#9ca3af', fontSize: '14px', cursor: 'pointer', marginBottom: '20px' }}
      >
        <ArrowLeft size={16} /> Back to Reports
      </button>

      {/* Header Banner */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '16px', padding: '28px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <h1 style={{ fontSize: '26px', fontWeight: '700', color: '#f9fafb', margin: 0 }}>{report.title}</h1>
            <span style={{ padding: '4px 10px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981', borderRadius: '12px', fontSize: '12px', fontWeight: '700' }}>
              {report.status}
            </span>
          </div>
          <p style={{ color: '#9ca3af', fontSize: '14px', margin: 0 }}>
            Generated on {new Date(report.created_at).toLocaleDateString()} | Workflow ID: {report.workflow_id}
          </p>
        </div>

        <button
          onClick={handleExport}
          disabled={downloading}
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 22px', background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer' }}
        >
          <Download size={18} /> {downloading ? 'Exporting...' : 'Export Intelligence Report'}
        </button>
      </div>

      {/* Strategic Scores */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '8px' }}>OVERALL STRATEGIC SCORE</div>
          <div style={{ fontSize: '32px', fontWeight: '700', color: '#10b981', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Award size={28} /> {report.overall_score}/100
          </div>
        </div>
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '20px' }}>
          <div style={{ fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '8px' }}>CONFIDENCE SCORE</div>
          <div style={{ fontSize: '32px', fontWeight: '700', color: '#8b5cf6', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Activity size={28} /> {report.confidence_score}%
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      {report.executive_summary && (
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px', marginBottom: '24px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f9fafb', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText style={{ color: '#8b5cf6' }} size={20} /> Executive Summary
          </h3>
          <p style={{ color: '#d1d5db', fontSize: '15px', lineHeight: '1.6', margin: 0 }}>
            {report.executive_summary}
          </p>
        </div>
      )}

      {/* Key Takeaways & Recommendations */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px', marginBottom: '24px' }}>
        {/* Key Findings */}
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
          <h3 style={{ fontSize: '17px', fontWeight: '600', color: '#f9fafb', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck style={{ color: '#10b981' }} size={20} /> Key Takeaways
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {(report.key_findings || []).map((finding: any, idx: number) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '14px', color: '#d1d5db', lineHeight: '1.4' }}>
                <CheckCircle2 size={16} style={{ color: '#10b981', flexShrink: 0, marginTop: '2px' }} />
                <span>{typeof finding === 'string' ? finding : JSON.stringify(finding)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Strategic Roadmap Recommendations */}
        <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
          <h3 style={{ fontSize: '17px', fontWeight: '600', color: '#f9fafb', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Briefcase style={{ color: '#6366f1' }} size={20} /> Strategic Recommendations
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {(report.recommendations || []).map((rec: any, idx: number) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '14px', color: '#d1d5db', lineHeight: '1.4' }}>
                <span style={{ width: '22px', height: '22px', borderRadius: '50%', backgroundColor: 'rgba(99, 102, 241, 0.2)', color: '#8b5cf6', fontSize: '12px', fontWeight: '700', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  {idx + 1}
                </span>
                <span>{typeof rec === 'string' ? rec : JSON.stringify(rec)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Specialist Agent Results Breakdown */}
      <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '14px', padding: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f9fafb', marginBottom: '20px' }}>
          Strategic Intelligence Findings
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {agentSections.map((sec, idx) => {
            const Icon = sec.icon;
            const res = report.agent_results ? report.agent_results[sec.key] : null;
            const status = res?.status || 'COMPLETED';
            const confidence = res?.confidence_score ?? res?.confidence;
            const evidenceCount = res?.evidence ? res.evidence.length : 0;
            const provider = res?.provider;
            const model = res?.model;
            const latency = res?.latency_ms ? `${res.latency_ms}ms` : res?.execution_time_seconds ? `${res.execution_time_seconds}s` : null;

            return (
              <div key={idx} style={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '12px', padding: '18px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Icon size={20} style={{ color: sec.color }} />
                    <span style={{ fontSize: '15px', fontWeight: '700', color: '#f9fafb' }}>{sec.title}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {confidence !== undefined && (
                      <span style={{ padding: '2px 8px', backgroundColor: 'rgba(139, 92, 246, 0.15)', color: '#a78bfa', borderRadius: '6px', fontSize: '11px', fontWeight: '600' }}>
                        {confidence}% Confidence
                      </span>
                    )}
                    {evidenceCount > 0 && (
                      <span style={{ padding: '2px 8px', backgroundColor: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', borderRadius: '6px', fontSize: '11px', fontWeight: '600' }}>
                        {evidenceCount} Evidence Items
                      </span>
                    )}
                    <span style={{
                      padding: '2px 8px',
                      backgroundColor: status === 'COMPLETED' ? 'rgba(16, 185, 129, 0.15)' : status === 'DEGRADED' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                      color: status === 'COMPLETED' ? '#10b981' : status === 'DEGRADED' ? '#f59e0b' : '#ef4444',
                      borderRadius: '6px',
                      fontSize: '11px',
                      fontWeight: '700'
                    }}>
                      {status}
                    </span>
                  </div>
                </div>

                {(provider || model || latency) && (
                  <div style={{ fontSize: '11px', color: '#9ca3af', marginBottom: '10px', display: 'flex', gap: '12px' }}>
                    {provider && <span>AI Provider: <strong style={{ color: '#d1d5db' }}>{provider}</strong></span>}
                    {model && <span>Model: <strong style={{ color: '#d1d5db' }}>{model}</strong></span>}
                    {latency && <span>Latency: <strong style={{ color: '#d1d5db' }}>{latency}</strong></span>}
                  </div>
                )}

                <div style={{ fontSize: '13px', color: '#9ca3af', lineHeight: '1.5' }}>
                  {res && res.findings ? (
                    <ul style={{ margin: 0, paddingLeft: '20px' }}>
                      {res.findings.map((f: string, i: number) => <li key={i}>{f}</li>)}
                    </ul>
                  ) : res && res.business_summary ? (
                    <p style={{ margin: 0, color: '#d1d5db' }}>{res.business_summary}</p>
                  ) : res && res.campaign_summary ? (
                    <p style={{ margin: 0, color: '#d1d5db' }}>{res.campaign_summary}</p>
                  ) : (
                    <span>Specialist intelligence synthesis verified and integrated into Executive Report summary.</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
