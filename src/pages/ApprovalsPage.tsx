import React, { useState, useEffect } from 'react';
import { governanceApi } from '../services/governanceApi';
import type { ApprovalRequest } from '../services/governanceApi';
import { ShieldCheck, AlertTriangle, ShieldAlert, CheckCircle2, XCircle, Clock, Activity, Search, ChevronRight } from 'lucide-react';
import { mapInternalExecutionToBusinessLanguage } from '../services/eventTranslationLayer';

interface ApprovalsPageProps {
  onSelectApproval: (approval: ApprovalRequest) => void;
}

export const ApprovalsPage: React.FC<ApprovalsPageProps> = ({ onSelectApproval }) => {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');

  useEffect(() => {
    loadData();
  }, [search, statusFilter, riskFilter]);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await governanceApi.getApprovals({
        search: search || undefined,
        status: statusFilter || undefined,
        risk_level: riskFilter || undefined,
      });
      setApprovals(res && Array.isArray(res.approvals) ? res.approvals : []);
    } catch {
      setApprovals([]);
    } finally {
      setLoading(false);
    }
  };

  const getRiskBadge = (level: string, score: number) => {
    switch (level) {
      case 'CRITICAL':
      case 'HIGH':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-rose-950 text-rose-300 border border-rose-800 flex items-center space-x-1">
            <AlertTriangle className="w-3 h-3" />
            <span>High Risk ({score})</span>
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-950 text-amber-300 border border-amber-800 flex items-center space-x-1">
            <ShieldAlert className="w-3 h-3" />
            <span>Medium Risk ({score})</span>
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800 flex items-center space-x-1">
            <ShieldCheck className="w-3 h-3" />
            <span>Low Risk ({score})</span>
          </span>
        );
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return <span className="text-emerald-400 font-bold flex items-center space-x-1 text-xs"><CheckCircle2 className="w-3.5 h-3.5" /> <span>Approved</span></span>;
      case 'REJECTED':
        return <span className="text-rose-400 font-bold flex items-center space-x-1 text-xs"><XCircle className="w-3.5 h-3.5" /> <span>Rejected</span></span>;
      case 'CHANGES_REQUESTED':
        return <span className="text-amber-400 font-bold flex items-center space-x-1 text-xs"><Clock className="w-3.5 h-3.5" /> <span>Changes Requested</span></span>;
      default:
        return <span className="text-sky-400 font-bold flex items-center space-x-1 text-xs"><Activity className="w-3.5 h-3.5" /> <span>Pending Review</span></span>;
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <ShieldCheck className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Approvals</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            Review decisions that need your attention.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search approval title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#111113] border border-white/10 rounded-lg pl-9 pr-3 py-2 text-xs text-[#F5F5F5] outline-none placeholder:text-[#92929A]"
          />
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-[#111113] border border-white/10 rounded-lg px-3 py-2 text-xs text-[#F5F5F5] outline-none"
        >
          <option value="">All Statuses</option>
          <option value="PENDING_APPROVAL">Pending Review</option>
          <option value="APPROVED">Approved</option>
          <option value="REJECTED">Rejected</option>
        </select>

        <select
          value={riskFilter}
          onChange={(e) => setRiskFilter(e.target.value)}
          className="bg-[#111113] border border-white/10 rounded-lg px-3 py-2 text-xs text-[#F5F5F5] outline-none"
        >
          <option value="">All Risk Levels</option>
          <option value="HIGH">High Risk</option>
          <option value="MEDIUM">Medium Risk</option>
          <option value="LOW">Low Risk</option>
        </select>
      </div>

      {/* Approvals List */}
      {loading ? (
        <p className="text-xs text-[#92929A]">Loading approvals...</p>
      ) : approvals.length === 0 ? (
        <div className="p-8 bg-[#111113] border border-white/[0.06] rounded-xl text-center text-xs text-[#92929A] italic space-y-1">
          <p className="font-semibold text-slate-300">No decisions require your attention.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {approvals.map((req) => (
            <div
              key={req.id}
              onClick={() => onSelectApproval(req)}
              className="p-4 bg-[#111113] border border-white/[0.06] hover:border-white/15 rounded-xl cursor-pointer transition flex items-center justify-between text-xs space-x-4"
            >
              <div className="space-y-1 flex-1">
                <div className="flex items-center space-x-2">
                  {getRiskBadge(req.risk_level, req.risk_score)}
                  <span className="text-[10px] font-mono text-[#92929A]">{req.decision_type}</span>
                </div>
                <h3 className="font-semibold text-[#F5F5F5] text-sm mt-1">{mapInternalExecutionToBusinessLanguage(req.title)}</h3>
                {req.requested_action && (
                  <p className="text-[#92929A]">{req.requested_action}</p>
                )}
              </div>

              <div className="flex items-center space-x-4 shrink-0">
                <div className="text-right">
                  <span className="text-[10px] font-mono text-[#92929A] block">CONFIDENCE</span>
                  <span className="font-bold text-sky-400 font-mono text-sm">{req.ai_confidence_score}%</span>
                </div>

                <div className="text-right">
                  <span className="text-[10px] font-mono text-[#92929A] block">STATUS</span>
                  {getStatusBadge(req.status)}
                </div>

                <ChevronRight className="w-4 h-4 text-slate-500" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
