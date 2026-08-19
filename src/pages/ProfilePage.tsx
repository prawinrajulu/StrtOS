import React from 'react';
import { useAuth } from '../context/AuthContext';
import { User as UserIcon, Shield, Key, LogOut } from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className="p-6 lg:p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Page Header */}
      <div>
        <div className="flex items-center space-x-3">
          <UserIcon className="w-7 h-7 text-sky-400" />
          <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Account & Security</h1>
        </div>
        <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
          Manage your StrtOS account details and session security.
        </p>
      </div>

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
              <span className="text-[10px] text-[#92929A] font-mono uppercase">ACCOUNT STATUS</span>
              <p className="font-semibold text-emerald-400">Active Enterprise Workspace</p>
            </div>

            <div className="p-4 bg-[#151518] border border-white/5 rounded-lg space-y-1">
              <span className="text-[10px] text-[#92929A] font-mono uppercase">ROLE PERMISSIONS</span>
              <p className="font-semibold text-[#F5F5F5] flex items-center space-x-1">
                <Shield className="w-3.5 h-3.5 text-sky-400" />
                <span>{user?.role || 'Administrator'}</span>
              </p>
            </div>
          </div>

          <div className="pt-2 border-t border-white/5 flex items-center justify-between">
            <span className="text-xs text-[#92929A] font-mono">Authenticated Session Active</span>
            <button
              onClick={logout}
              className="px-4 py-2 rounded-lg text-xs font-semibold bg-rose-950/60 hover:bg-rose-900 border border-rose-800 text-rose-300 flex items-center space-x-1.5 transition"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>

        {/* Security Overview */}
        <div className="p-6 bg-[#111113] border border-white/[0.06] rounded-xl space-y-4 text-xs">
          <div className="text-[10px] font-mono text-sky-400 font-bold uppercase tracking-wider flex items-center space-x-1.5">
            <Key className="w-3.5 h-3.5" />
            <span>SECURITY OVERVIEW</span>
          </div>
          <div className="space-y-3 text-[#92929A] leading-relaxed">
            <div>
              <strong className="text-[#F5F5F5] block">Access Protection:</strong> End-to-end encrypted session credentials & verified API authorization.
            </div>
            <div>
              <strong className="text-[#F5F5F5] block">Data Governance:</strong> Enterprise security standards and organization boundary isolation.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
