import React, { useState, useEffect } from 'react';
import { reportsApi } from '../services/reportsApi';
import type { ExecutiveReport, ReportMetrics } from '../services/reportsApi';
import { clientsApi } from '../services/clientsApi';
import type { Client } from '../services/clientsApi';
import { FileText, Search, ChevronRight, Award, Activity, Calendar } from 'lucide-react';
import { mapInternalExecutionToBusinessLanguage } from '../services/eventTranslationLayer';

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
    try {
      const [repList, clientList, metData] = await Promise.all([
        reportsApi.listReports({
          search: search || undefined,
          client_id: selectedClientFilter || undefined
        }),
        clientsApi.listClients(),
        reportsApi.getReportMetrics()
      ]);
      setReports(repList || []);
      setClients(clientList || []);
      setMetrics(metData);
    } catch {
      setReports([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [search, selectedClientFilter]);

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <FileText className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Reports</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            Review completed business intelligence.
          </p>
        </div>
      </div>

      {/* Metrics Overview */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
            <span className="text-xs text-[#92929A] font-mono uppercase">Total Reports</span>
            <p className="text-2xl font-bold text-[#F5F5F5]">{metrics.total_reports}</p>
          </div>
          <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
            <span className="text-xs text-[#92929A] font-mono uppercase">Average Strategic Score</span>
            <p className="text-2xl font-bold text-emerald-400 flex items-center space-x-1.5">
              <Award className="w-5 h-5" />
              <span>{metrics.average_score}/100</span>
            </p>
          </div>
          <div className="p-5 bg-[#111113] border border-white/[0.06] rounded-xl space-y-1">
            <span className="text-xs text-[#92929A] font-mono uppercase">Average Confidence</span>
            <p className="text-2xl font-bold text-sky-400 flex items-center space-x-1.5">
              <Activity className="w-5 h-5" />
              <span>{metrics.average_confidence}%</span>
            </p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search reports by title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#111113] border border-white/10 rounded-lg pl-9 pr-3 py-2 text-xs text-[#F5F5F5] outline-none placeholder:text-[#92929A]"
          />
        </div>

        <select
          value={selectedClientFilter}
          onChange={(e) => setSelectedClientFilter(e.target.value)}
          className="bg-[#111113] border border-white/10 rounded-lg px-3 py-2 text-xs text-[#F5F5F5] outline-none"
        >
          <option value="">All Accounts</option>
          {clients.map(c => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      {/* Reports List */}
      {loading ? (
        <p className="text-xs text-[#92929A]">Loading reports...</p>
      ) : reports.length === 0 ? (
        <div className="p-8 bg-[#111113] border border-white/[0.06] rounded-xl text-center space-y-2 text-xs text-[#92929A] italic">
          <p className="font-semibold text-slate-300">NO RECENT RESULTS</p>
          <p>Completed intelligence will appear here.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports.map((rep) => (
            <div
              key={rep.id}
              onClick={() => onSelectReport && onSelectReport(rep)}
              className="p-5 bg-[#111113] border border-white/[0.06] hover:border-white/15 rounded-xl cursor-pointer transition space-y-3 flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex justify-between items-start">
                  <h3 className="text-sm font-semibold text-[#F5F5F5]">{mapInternalExecutionToBusinessLanguage(rep.title)}</h3>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950/80 border border-emerald-800 text-emerald-300">
                    {rep.overall_score}/100
                  </span>
                </div>

                {rep.executive_summary && (
                  <p className="text-xs text-[#92929A] line-clamp-3">
                    {rep.executive_summary}
                  </p>
                )}
              </div>

              <div className="pt-3 border-t border-white/5 flex justify-between items-center text-xs">
                <div className="flex items-center space-x-1 text-[#92929A] text-[10px]">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>{new Date(rep.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center space-x-1 text-sky-400 font-mono text-[10px] hover:underline">
                  <span>View Report</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
