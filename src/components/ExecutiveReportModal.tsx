import React from 'react';
import { X, FileText, CheckCircle2 } from 'lucide-react';
import type { ExecutiveReportData } from '../services/ceoApi';

interface ExecutiveReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  report: ExecutiveReportData | null;
}

export const ExecutiveReportModal: React.FC<ExecutiveReportModalProps> = ({ isOpen, onClose, report }) => {
  if (!isOpen || !report) return null;

  const sections = [
    { title: 'Business Strategy', data: report.business_summary },
    { title: 'SEO Discovery', data: report.seo_summary },
    { title: 'Competitor Intelligence', data: report.competitor_summary },
    { title: 'Marketing Strategy', data: report.marketing_summary },
    { title: 'Campaign Plan', data: report.campaign_summary },
    { title: 'Analytics & Attribution', data: report.analytics_summary },
  ];

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(10px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 100,
        padding: '24px',
      }}
    >
      <div
        className="glass-card"
        style={{
          width: '800px',
          maxHeight: '85vh',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          boxShadow: '0 0 50px rgba(0, 229, 153, 0.2)',
          overflow: 'hidden',
        }}
      >
        {/* Top Bar */}
        <div
          style={{
            padding: '20px 28px',
            borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '10px',
                backgroundColor: 'rgba(0, 229, 153, 0.15)',
                color: '#00e599',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <FileText size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#ffffff' }}>Executive Summary Report</h3>
              <div style={{ fontSize: '10px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280' }}>
                CLIENT: {report.client_name} • CONFIDENCE: {report.overall_confidence}%
              </div>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#6b7280', cursor: 'pointer' }}>
            <X size={18} />
          </button>
        </div>

        {/* Scrollable Content */}
        <div style={{ padding: '28px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Directive Header Box */}
          <div
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.06)',
              borderRadius: '10px',
              padding: '16px',
            }}
          >
            <div style={{ fontSize: '10px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280', textTransform: 'uppercase', marginBottom: '4px' }}>
              DIRECTIVE OBJECTIVE
            </div>
            <div style={{ fontSize: '14px', color: '#e5e7eb', fontStyle: 'italic' }}>"{report.directive}"</div>
          </div>

          {/* CEO Recommendations */}
          <div>
            <h4 style={{ fontSize: '13px', fontFamily: "'JetBrains Mono', monospace", color: '#00e599', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '12px' }}>
              CEO FINAL RECOMMENDATIONS
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {report.ceo_final_recommendations.map((rec, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '13px', color: '#d1d5db' }}>
                  <CheckCircle2 size={16} color="#00e599" style={{ marginTop: '2px', flexShrink: 0 }} />
                  <span>{rec}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Specialist Summaries Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {sections.map((sec) => (
              <div
                key={sec.title}
                style={{
                  backgroundColor: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid rgba(255, 255, 255, 0.04)',
                  borderRadius: '10px',
                  padding: '16px',
                }}
              >
                <div style={{ fontSize: '11px', fontFamily: "'JetBrains Mono', monospace", color: '#a855f7', marginBottom: '8px' }}>
                  {sec.data.agent_name}
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#ffffff', marginBottom: '8px' }}>
                  {sec.data.title}
                </div>
                <ul style={{ paddingLeft: '16px', fontSize: '12px', color: '#9ca3af', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {sec.data.findings.map((f, idx) => (
                    <li key={idx}>{f}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
