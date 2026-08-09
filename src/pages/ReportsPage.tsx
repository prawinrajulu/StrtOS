import React, { useEffect, useState } from 'react';
import {
  FileText, Search, Activity, Award, Calendar, ChevronRight
} from 'lucide-react';
import { reportsApi } from '../services/reportsApi';
import type { ExecutiveReport, ReportMetrics } from '../services/reportsApi';
import { clientsApi } from '../services/clientsApi';
import type { Client } from '../services/clientsApi';

interface ReportsPageProps {
  onSelectReport?: (report: ExecutiveReport) => void;
}

export const ReportsPage: React.FC<ReportsPageProps> = ({ onSelectReport }) => {
  const [reports, setReports] = useState<ExecutiveReport[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [metrics, setMetrics] = useState<ReportMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedClientFilter, setSelectedClientFilter] = useState('');

  const loadData = async () => {
    setLoading(true);
    const [repList, clientList, metData] = await Promise.all([
      reportsApi.listReports({
        search: search || undefined,
        client_id: selectedClientFilter || undefined
      }),
      clientsApi.listClients(),
      reportsApi.getReportMetrics()
    ]);
    setReports(repList);
    setClients(clientList);
    setMetrics(metData);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [search, selectedClientFilter]);

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Page Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '26px', fontWeight: '700', color: '#f9fafb', margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <FileText style={{ color: '#8b5cf6' }} size={28} />
          Executive Intelligence Reports
        </h1>
        <p style={{ color: '#9ca3af', fontSize: '14px', marginTop: '4px', margin: 0 }}>
          Consolidated strategic intelligence synthesized by CEO Agent & Specialist Agents.
        </p>
      </div>

      {/* Metrics Banner */}
      {metrics && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '18px' }}>
            <div style={{ fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '6px' }}>TOTAL REPORTS</div>
            <div style={{ fontSize: '26px', fontWeight: '700', color: '#f9fafb' }}>{metrics.total_reports}</div>
          </div>
          <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '18px' }}>
            <div style={{ fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '6px' }}>AVG STRATEGIC SCORE</div>
            <div style={{ fontSize: '26px', fontWeight: '700', color: '#10b981', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Award size={22} /> {metrics.average_score}/100
            </div>
          </div>
          <div style={{ backgroundColor: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '18px' }}>
            <div style={{ fontSize: '12px', color: '#9ca3af', fontWeight: '600', marginBottom: '6px' }}>AVG CONFIDENCE SCORE</div>
            <div style={{ fontSize: '26px', fontWeight: '700', color: '#8b5cf6', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Activity size={22} /> {metrics.average_confidence}%
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '260px', position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
          <input
            type="text"
            placeholder="Search reports by title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 12px 10px 40px',
              backgroundColor: '#111827',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#f9fafb',
              fontSize: '14px',
              outline: 'none'
            }}
          />
        </div>

        <select
          value={selectedClientFilter}
          onChange={(e) => setSelectedClientFilter(e.target.value)}
          style={{
            padding: '10px 16px',
            backgroundColor: '#111827',
            border: '1px solid #374151',
            borderRadius: '8px',
            color: '#f9fafb',
            fontSize: '14px'
          }}
        >
          <option value="">All Clients</option>
          {clients.map(c => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      {/* Reports List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#9ca3af' }}>Loading executive reports...</div>
      ) : reports.length === 0 ? (
        <div style={{ backgroundColor: '#111827', border: '1px dashed #374151', borderRadius: '12px', padding: '60px 20px', textAlign: 'center', color: '#9ca3af' }}>
          <FileText size={48} style={{ color: '#4b5563', marginBottom: '16px' }} />
          <h3 style={{ color: '#f3f4f6', fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>No Executive Reports Generated Yet</h3>
          <p style={{ fontSize: '14px' }}>Execute an executive workflow to automatically generate structured intelligence reports.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '20px' }}>
          {reports.map((rep) => {
            const clientObj = clients.find(c => c.id === rep.client_id);
            return (
              <div
                key={rep.id}
                onClick={() => onSelectReport && onSelectReport(rep)}
                style={{
                  backgroundColor: '#111827',
                  border: '1px solid #1f2937',
                  borderRadius: '12px',
                  padding: '22px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between'
                }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#8b5cf6'; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#1f2937'; }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <div>
                      <h3 style={{ fontSize: '17px', fontWeight: '600', color: '#f9fafb', margin: 0 }}>{rep.title}</h3>
                      <span style={{ fontSize: '12px', color: '#8b5cf6', fontWeight: '500' }}>
                        Client: {clientObj ? clientObj.name : 'Enterprise Client'}
                      </span>
                    </div>
                    <span style={{ padding: '4px 10px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981', borderRadius: '12px', fontSize: '11px', fontWeight: '700' }}>
                      SCORE: {rep.overall_score}/100
                    </span>
                  </div>

                  {rep.executive_summary && (
                    <p style={{ fontSize: '13px', color: '#9ca3af', marginBottom: '16px', lineHeight: '1.4' }}>
                      {rep.executive_summary.length > 110 ? rep.executive_summary.substring(0, 110) + '...' : rep.executive_summary}
                    </p>
                  )}
                </div>

                <div style={{ paddingTop: '14px', borderTop: '1px solid #1f2937', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#9ca3af', fontSize: '12px' }}>
                    <Calendar size={14} /> {new Date(rep.created_at).toLocaleDateString()}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#8b5cf6', fontSize: '13px', fontWeight: '600' }}>
                    View Full Intelligence Brief <ChevronRight size={16} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
