import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { User as UserIcon, Shield, Key, LogOut, Terminal, Cpu, Sparkles, ShieldCheck, Network } from 'lucide-react';

interface ProfilePageProps {
  onNavigateDiagnostics?: (tab: string) => void;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({ onNavigateDiagnostics }) => {
  const { user, logout } = useAuth();
  const [activeSubTab, setActiveSubTab] = useState<'profile' | 'diagnostics'>('profile');

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <UserIcon className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">System Settings & Profile</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            Manage your StrtOS account, organizational credentials & system telemetry.
          </p>
        </div>

        {/* Sub Navigation */}
        <div className="flex items-center space-x-2 bg-[#111113] border border-white/[0.06] p-1 rounded-lg">
          <button
            onClick={() => setActiveSubTab('profile')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
              activeSubTab === 'profile'
                ? 'bg-[#151518] text-[#F5F5F5] border border-white/10'
                : 'text-[#92929A] hover:text-[#F5F5F5]'
            }`}
          >
            Account & Security
          </button>
          <button
            onClick={() => setActiveSubTab('diagnostics')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
              activeSubTab === 'diagnostics'
                ? 'bg-[#151518] text-[#F5F5F5] border border-white/10'
                : 'text-[#92929A] hover:text-[#F5F5F5]'
            }`}
          >
            System Telemetry
          </button>
        </div>
      </div>

      {activeSubTab === 'profile' ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Main Account Details */}
          <div className="md:col-span-2 p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-6">
            <div className="flex items-center space-x-4 border-b border-white/5 pb-4">
              <div className="w-12 h-12 rounded-full bg-sky-500/20 text-sky-400 text-lg font-bold flex items-center justify-center border border-sky-500/30">
                {user?.full_name ? user.full_name[0] : 'U'}
              </div>
              <div>
                <h2 className="text-base font-bold text-[#F5F5F5]">
                  {user?.full_name || 'Executive User'}
                </h2>
                <p className="text-xs text-[#92929A] font-mono">{user?.email}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-4 bg-[#151518] border border-white/5 rounded-lg space-y-1">
                <span className="text-[10px] text-[#92929A] font-mono uppercase">ORGANIZATION ID</span>
                <p className="font-semibold text-[#F5F5F5]">{user?.organization_id || 'org_default'}</p>
              </div>

              <div className="p-4 bg-[#151518] border border-white/5 rounded-lg space-y-1">
                <span className="text-[10px] text-[#92929A] font-mono uppercase">ROLE PERMISSIONS</span>
                <p className="font-semibold text-emerald-400 flex items-center space-x-1">
                  <Shield className="w-3.5 h-3.5" />
                  <span>{user?.role || 'SYSTEM_ADMIN'}</span>
                </p>
              </div>
            </div>

            <div className="pt-2 border-t border-white/5 flex items-center justify-between">
              <span className="text-xs text-[#92929A] font-mono">Session: Authenticated JWT Session Active</span>
              <button
                onClick={logout}
                className="px-4 py-2 rounded-lg text-xs font-semibold bg-rose-950/60 hover:bg-rose-900 border border-rose-800 text-rose-300 flex items-center space-x-1.5 transition"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>

          {/* Security & System Info Side Panel */}
          <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4 text-xs">
            <div className="text-[10px] font-mono text-sky-400 font-bold uppercase tracking-wider flex items-center space-x-1.5">
              <Key className="w-3.5 h-3.5" />
              <span>SECURITY ARCHITECTURE</span>
            </div>
            <div className="space-y-3 text-[#92929A] leading-relaxed">
              <div>
                <strong className="text-[#F5F5F5] block">Authentication Encryption:</strong> Bcrypt password security & verified authorization headers.
              </div>
              <div>
                <strong className="text-[#F5F5F5] block">Token Security:</strong> Active JTI Verification on all business endpoints.
              </div>
              <div>
                <strong className="text-[#F5F5F5] block">Tenant Isolation:</strong> Strict organizational boundary isolation.
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Telemetry Panel */
        <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-6">
          <div>
            <div className="flex items-center space-x-2">
              <Terminal className="w-5 h-5 text-emerald-400" />
              <h2 className="text-lg font-bold text-[#F5F5F5]">System Telemetry & Operational Diagnostics</h2>
            </div>
            <p className="text-xs text-[#92929A] mt-1">
              Diagnostic controls for operational telemetry, response latencies, and execution status.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div className="p-5 bg-[#151518] border border-white/5 rounded-xl space-y-3 flex flex-col justify-between">
              <div className="space-y-1">
                <div className="flex items-center space-x-2 text-sky-400 font-bold">
                  <Cpu className="w-4 h-4" />
                  <span>Execution Telemetry</span>
                </div>
                <p className="text-[#92929A] leading-relaxed">
                  Execution latencies, verification metrics, and system status across modules.
                </p>
              </div>
              <button
                onClick={() => onNavigateDiagnostics?.('dashboard')}
                className="w-full py-2 rounded-lg font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 transition"
              >
                Inspect Dashboard
              </button>
            </div>

            <div className="p-5 bg-[#151518] border border-white/5 rounded-xl space-y-3 flex flex-col justify-between">
              <div className="space-y-1">
                <div className="flex items-center space-x-2 text-indigo-400 font-bold">
                  <Sparkles className="w-4 h-4" />
                  <span>Optimization Controls</span>
                </div>
                <p className="text-[#92929A] leading-relaxed">
                  Operational optimization, performance tracking, and strategic recommendations.
                </p>
              </div>
              <button
                onClick={() => onNavigateDiagnostics?.('decision-optimization')}
                className="w-full py-2 rounded-lg font-semibold bg-indigo-500 hover:bg-indigo-400 text-slate-950 transition"
              >
                Inspect Decisions
              </button>
            </div>

            <div className="p-5 bg-[#151518] border border-white/5 rounded-xl space-y-3 flex flex-col justify-between">
              <div className="space-y-1">
                <div className="flex items-center space-x-2 text-emerald-400 font-bold">
                  <ShieldCheck className="w-4 h-4" />
                  <span>Policy Governance</span>
                </div>
                <p className="text-[#92929A] leading-relaxed">
                  Governance rules, version histories, and execution boundaries.
                </p>
              </div>
              <button
                onClick={() => onNavigateDiagnostics?.('policies')}
                className="w-full py-2 rounded-lg font-semibold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition"
              >
                Inspect Policies
              </button>
            </div>

            <div className="p-5 bg-[#151518] border border-white/5 rounded-xl space-y-3 flex flex-col justify-between">
              <div className="space-y-1">
                <div className="flex items-center space-x-2 text-amber-400 font-bold">
                  <Network className="w-4 h-4" />
                  <span>Decision Explainability</span>
                </div>
                <p className="text-[#92929A] leading-relaxed">
                  Evidence-based decision paths, outcome variance, and strategic knowledge.
                </p>
              </div>
              <button
                onClick={() => onNavigateDiagnostics?.('knowledge')}
                className="w-full py-2 rounded-lg font-semibold bg-amber-500 hover:bg-amber-400 text-slate-950 transition"
              >
                Inspect Knowledge
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
