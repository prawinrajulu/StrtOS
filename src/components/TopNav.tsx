import React, { useState, useEffect } from 'react';
import { Search, Bell, Activity } from 'lucide-react';
import { globalEventStream } from '../services/eventStream';
import { mapInternalExecutionToBusinessLanguage } from '../services/eventTranslationLayer';

interface TopNavProps {
  breadcrumbs: string[];
}

export const TopNav: React.FC<TopNavProps> = ({ breadcrumbs }) => {
  const [activeTaskTitle, setActiveTaskTitle] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = globalEventStream.subscribe((event) => {
      if (event.event_type.includes('completed')) {
        setActiveTaskTitle(null);
      } else if (event.agent_name || event.message) {
        const title = mapInternalExecutionToBusinessLanguage(event.agent_name);
        setActiveTaskTitle(title);
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  return (
    <header className="h-16 border-b border-white/[0.06] bg-[#0D0D0F]/80 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-10 select-none">
      {/* Breadcrumbs */}
      <div className="flex items-center gap-2 text-xs font-mono text-[#92929A] uppercase tracking-wider">
        {breadcrumbs.map((crumb, idx) => (
          <React.Fragment key={crumb}>
            {idx > 0 && <span className="text-slate-600">/</span>}
            <span className={idx === breadcrumbs.length - 1 ? 'text-[#F5F5F5] font-semibold' : 'text-[#92929A]'}>
              {crumb}
            </span>
          </React.Fragment>
        ))}
      </div>

      {/* Center Status / Active Task Indicator (Requirement 17) */}
      {activeTaskTitle && (
        <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-sky-950/60 border border-sky-800/60 text-sky-300 text-xs font-mono">
          <Activity className="w-3.5 h-3.5 animate-spin text-sky-400" />
          <span className="font-semibold">● StrtOS is working:</span>
          <span>{activeTaskTitle}</span>
        </div>
      )}

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* Search Bar */}
        <div className="hidden sm:flex items-center gap-2 bg-[#111113] border border-white/[0.06] rounded-lg px-3 py-1.5 w-56">
          <Search size={14} className="text-[#92929A]" />
          <input
            type="text"
            placeholder="Search analysis..."
            className="bg-transparent border-none outline-none text-[#F5F5F5] text-xs w-full placeholder:text-[#92929A]"
          />
          <kbd className="text-[9px] font-mono bg-white/[0.06] border border-white/10 rounded px-1 text-[#92929A]">
            ⌘K
          </kbd>
        </div>

        {/* Notifications */}
        <button className="relative w-9 h-9 rounded-lg bg-[#111113] border border-white/[0.06] flex items-center justify-center text-[#92929A] hover:text-[#F5F5F5] transition">
          <Bell size={16} />
          <span className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-sky-400" />
        </button>

        {/* User Profile */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-sky-500 text-slate-950 font-bold flex items-center justify-center text-xs">
            AC
          </div>
          <div className="hidden sm:block">
            <div className="text-xs font-semibold text-[#F5F5F5]">Ava Chen</div>
            <div className="text-[9px] text-[#92929A] font-mono">EXECUTIVE</div>
          </div>
        </div>
      </div>
    </header>
  );
};
