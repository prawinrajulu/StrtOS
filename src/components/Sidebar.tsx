import React from 'react';
import {
  Compass,
  BarChart3,
  Activity,
  TrendingUp,
  Target,
  GitFork,
  Network,
  Zap,
  Server,
  ShieldCheck,
  Brain,
  FileText,
  Building2,
  Settings,
  ChevronDown,
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const sections = [
    {
      group: 'MAIN',
      items: [
        { id: 'command-center', label: 'Command Center', icon: Compass },
        { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
      ],
    },
    {
      group: 'INTELLIGENCE',
      items: [
        { id: 'business-state', label: 'Business State', icon: Activity },
        { id: 'strategy', label: 'Strategy', icon: Target },
        { id: 'forecasting', label: 'Forecasting', icon: TrendingUp },
        { id: 'decision-optimization', label: 'Decisions', icon: GitFork },
        { id: 'knowledge', label: 'Knowledge', icon: Network },
      ],
    },
    {
      group: 'EXECUTION',
      items: [
        { id: 'missions', label: 'Missions', icon: Target },
        { id: 'resources', label: 'Resources', icon: Server },
        { id: 'workflows', label: 'Workflows', icon: Zap },
      ],
    },
    {
      group: 'INSIGHTS',
      items: [
        { id: 'reports', label: 'Reports', icon: FileText },
        { id: 'memory', label: 'Memory', icon: Brain },
        { id: 'outcomes', label: 'Outcomes', icon: FileText },
      ],
    },
    {
      group: 'GOVERNANCE',
      items: [
        { id: 'approvals', label: 'Approvals', icon: ShieldCheck },
        { id: 'policies', label: 'Policies', icon: ShieldCheck },
      ],
    },
    {
      group: 'SYSTEM',
      items: [
        { id: 'clients', label: 'Business Accounts', icon: Building2 },
        { id: 'settings', label: 'Settings', icon: Settings },
      ],
    },
  ];

  return (
    <aside className="w-64 bg-[#0D0D0F] border-r border-white/[0.06] flex flex-col justify-between h-screen sticky top-0 z-20 select-none">
      <div>
        {/* Top Brand Logo */}
        <div className="p-5 border-b border-white/[0.06] flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-sky-500 flex items-center justify-center font-bold text-slate-950 text-sm shadow-md">
            S
          </div>
          <div>
            <div className="text-base font-bold text-[#F5F5F5] tracking-tight">
              STRtOS
            </div>
            <div className="text-[9px] font-mono text-[#92929A] tracking-widest uppercase">
              INTELLIGENCE ENGINE
            </div>
          </div>
        </div>

        {/* Account Selector */}
        <div className="p-4 pb-2">
          <div className="bg-[#111113] border border-white/[0.06] rounded-lg p-2.5 flex items-center justify-between cursor-pointer hover:border-white/15 transition">
            <div className="flex items-center gap-2.5">
              <div className="w-6 h-6 rounded bg-sky-500/20 text-sky-400 text-xs font-bold flex items-center justify-center">
                EA
              </div>
              <div>
                <div className="text-xs font-semibold text-[#F5F5F5]">Enterprise Account</div>
                <div className="text-[9px] text-[#92929A] font-mono">ORGANIZATION</div>
              </div>
            </div>
            <ChevronDown size={14} className="text-[#92929A]" />
          </div>
        </div>

        {/* Navigation Sections */}
        <div className="p-4 space-y-4 max-h-[calc(100vh-210px)] overflow-y-auto">
          {sections.map((sec) => (
            <div key={sec.group}>
              <div className="text-[9px] font-mono text-[#92929A] tracking-widest mb-1.5 pl-2">
                {sec.group}
              </div>
              <div className="space-y-0.5">
                {sec.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveTab(item.id)}
                      className={`flex items-center justify-between w-full px-3 py-2 rounded-lg text-xs font-medium transition ${
                        isActive
                          ? 'bg-[#151518] text-[#F5F5F5] font-semibold border border-white/10'
                          : 'text-[#92929A] hover:text-[#F5F5F5] hover:bg-[#111113]'
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <Icon size={16} className={isActive ? 'text-sky-400' : 'text-[#92929A]'} />
                        <span>{item.label}</span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Health Bar */}
      <div className="p-4 border-t border-white/[0.06] bg-[#111113]/50">
        <div className="flex items-center gap-2 mb-0.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-medium text-[#F5F5F5]">StrtOS Operational</span>
        </div>
        <div className="text-[9px] font-mono text-[#92929A] tracking-wide pl-3.5">
          SYSTEM ACTIVE
        </div>
      </div>
    </aside>
  );
};
