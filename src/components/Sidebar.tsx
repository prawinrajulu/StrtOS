import React from 'react';
import {
  Compass,
  BarChart3,
  Activity,
  TrendingUp,
  Target,
  GitFork,
  Network,
  Briefcase,
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
      group: 'STRTOS ENGINE',
      items: [
        { id: 'command-center', label: 'Command Center', icon: Compass, badgeDot: true },
        { id: 'dashboard', label: 'Executive Dashboard', icon: BarChart3 },
      ],
    },
    {
      group: 'INTELLIGENCE',
      items: [
        { id: 'business-state', label: 'Business State', icon: Activity, badgeDot: true },
        { id: 'forecasting', label: 'Strategic Forecasting', icon: TrendingUp },
        { id: 'strategy', label: 'Strategy Engine', icon: Target, badgeDot: true },
        { id: 'decision-optimization', label: 'Decision Optimization', icon: GitFork, badgeDot: true },
        { id: 'knowledge', label: 'Knowledge Graph', icon: Network, badgeDot: true },
      ],
    },
    {
      group: 'EXECUTION',
      items: [
        { id: 'missions', label: 'Missions', icon: Target, badgeDot: true },
        { id: 'portfolio', label: 'Portfolio Control', icon: Briefcase },
        { id: 'workflows', label: 'Workflows', icon: Zap },
        { id: 'resources', label: 'Resource Intelligence', icon: Server, badgeDot: true },
      ],
    },
    {
      group: 'GOVERNANCE & AUDIT',
      items: [
        { id: 'approvals', label: 'Approvals', icon: ShieldCheck },
        { id: 'policies', label: 'Policies', icon: ShieldCheck },
        { id: 'memory', label: 'Memory Engine', icon: Brain },
        { id: 'outcomes', label: 'Outcomes & Reports', icon: FileText },
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
    <aside className="w-64 bg-[#0b0b0e] border-r border-white/10 flex flex-col justify-between h-screen sticky top-0 z-20 select-none">
      <div>
        {/* Top Logo */}
        <div className="p-5 border-b border-white/5 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center font-bold text-white text-sm shadow-[0_0_16px_rgba(99,102,241,0.5)]">
            S
          </div>
          <div>
            <div className="text-base font-bold text-slate-100 tracking-tight">
              StrtOS
            </div>
            <div className="text-[9px] font-mono text-slate-500 tracking-widest uppercase">
              STRATEGIC AI ENGINE • v2.6
            </div>
          </div>
        </div>

        {/* Enterprise Selector */}
        <div className="p-4 pb-2">
          <div className="bg-white/5 border border-white/10 rounded-lg p-2.5 flex items-center justify-between cursor-pointer hover:border-white/20 transition">
            <div className="flex items-center gap-2.5">
              <div className="w-6 h-6 rounded bg-emerald-400 text-black text-xs font-bold flex items-center justify-center">
                AV
              </div>
              <div>
                <div className="text-xs font-semibold text-slate-200">Arcadia Ventures</div>
                <div className="text-[9px] text-slate-500 font-mono">ENTERPRISE</div>
              </div>
            </div>
            <ChevronDown size={14} className="text-slate-500" />
          </div>
        </div>

        {/* Navigation Sections */}
        <div className="p-4 space-y-5 max-h-[calc(100vh-210px)] overflow-y-auto">
          {sections.map((sec) => (
            <div key={sec.group}>
              <div className="text-[9px] font-mono text-slate-500 tracking-widest mb-2 pl-2">
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
                          ? 'bg-white/10 text-white font-semibold'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <Icon size={16} className={isActive ? 'text-cyan-400' : 'text-slate-500'} />
                        <span>{item.label}</span>
                      </div>
                      {item.badgeDot && (
                        <span className="w-1.5 h-1.5 rounded-full bg-purple-500 shadow-[0_0_8px_#a855f7]" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Health Bar */}
      <div className="p-4 border-t border-white/5 bg-black/20">
        <div className="flex items-center gap-2 mb-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-medium text-slate-200">StrtOS Engine Operational</span>
        </div>
        <div className="text-[9px] font-mono text-slate-500 tracking-wide pl-3.5">
          INTELLIGENCE ENGINE • 128K CTX
        </div>
      </div>
    </aside>
  );
};
