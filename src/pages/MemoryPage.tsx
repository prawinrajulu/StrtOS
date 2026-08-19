import React, { useState, useEffect } from 'react';
import { Brain, Search, ChevronRight, CheckCircle2, AlertTriangle, XCircle, Lightbulb, Sparkles } from 'lucide-react';
import { memoryApi } from '../services/memoryApi';
import type { MemoryRecord } from '../services/memoryApi';
import { globalEventStream } from '../services/eventStream';

interface MemoryPageProps {
  onSelectMemory: (memory: MemoryRecord) => void;
}

export const MemoryPage: React.FC<MemoryPageProps> = ({ onSelectMemory }) => {
  const [memories, setMemories] = useState<MemoryRecord[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('');

  const fetchMemories = async () => {
    setLoading(true);
    try {
      const data = await memoryApi.getMemories({
        memory_type: typeFilter,
        search: search
      });
      setMemories(data.memories || []);
      setTotal(data.total || 0);
    } catch {
      setMemories([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMemories();

    const unsubscribe = globalEventStream.subscribe((event) => {
      if (['memory.created', 'memory.updated', 'outcome.recorded', 'lesson.created'].includes(event.event_type)) {
        fetchMemories();
      }
    });
    return () => unsubscribe();
  }, [typeFilter, search]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <span className="text-emerald-400 font-medium inline-flex items-center gap-1 text-xs"><CheckCircle2 size={12} /> SUCCESS</span>;
      case 'PARTIAL':
        return <span className="text-amber-400 font-medium inline-flex items-center gap-1 text-xs"><AlertTriangle size={12} /> PARTIAL</span>;
      case 'FAILED':
        return <span className="text-rose-400 font-medium inline-flex items-center gap-1 text-xs"><XCircle size={12} /> FAILED</span>;
      default:
        return <span className="text-[#92929A] text-xs">RECORDED</span>;
    }
  };

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'LESSON':
        return <span className="px-2 py-0.5 bg-amber-950/60 text-amber-300 border border-amber-800/60 rounded text-[10px] font-mono inline-flex items-center gap-1"><Lightbulb size={11} /> LESSON</span>;
      case 'OUTCOME':
        return <span className="px-2 py-0.5 bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 rounded text-[10px] font-mono inline-flex items-center gap-1"><CheckCircle2 size={11} /> OUTCOME</span>;
      case 'DECISION':
        return <span className="px-2 py-0.5 bg-sky-950/60 text-sky-300 border border-sky-800/60 rounded text-[10px] font-mono inline-flex items-center gap-1"><Sparkles size={11} /> DECISION</span>;
      default:
        return <span className="px-2 py-0.5 bg-slate-800 text-slate-300 border border-white/10 rounded text-[10px] font-mono">{type}</span>;
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <Brain className="w-7 h-7 text-sky-400" />
            <h1 className="text-2xl font-bold text-[#F5F5F5] tracking-tight">Business Memory</h1>
          </div>
          <p className="text-[#92929A] mt-1 text-xs sm:text-sm">
            StrtOS remembers important context and decisions about your business ({total} Records).
          </p>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="p-4 bg-[#111113] border border-white/[0.06] rounded-xl flex flex-wrap items-center gap-4">
        <div className="flex-1 min-w-[240px] relative">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#92929A]" />
          <input
            type="text"
            placeholder="Search business memory, decisions, or historical context..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-[#151518] border border-white/10 rounded-lg pl-9 pr-3 py-2 text-xs text-[#F5F5F5] outline-none placeholder:text-[#92929A]"
          />
        </div>

        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="bg-[#151518] border border-white/10 rounded-lg px-3 py-2 text-xs text-[#F5F5F5] outline-none"
        >
          <option value="">All Memory Types</option>
          <option value="LESSON">Learned Lessons</option>
          <option value="OUTCOME">Measured Outcomes</option>
          <option value="DECISION">Historical Decisions</option>
          <option value="APPROVAL">Approvals</option>
          <option value="STRATEGY">Strategies</option>
          <option value="WORKFLOW">Workflows</option>
        </select>
      </div>

      {/* Memory Cards */}
      {loading ? (
        <div className="text-[#92929A] text-xs text-center py-12">Loading business memory records...</div>
      ) : memories.length === 0 ? (
        <div className="p-12 bg-[#111113] border border-white/[0.06] rounded-xl text-center text-xs text-[#92929A]">
          No business memory records found.
        </div>
      ) : (
        <div className="space-y-3">
          {memories.map((mem) => (
            <div
              key={mem.id}
              onClick={() => onSelectMemory(mem)}
              className="p-5 bg-[#111113] border border-white/[0.06] hover:border-white/15 rounded-xl cursor-pointer transition flex flex-wrap items-center justify-between gap-4"
            >
              <div className="flex-1 min-w-[280px] space-y-2">
                <div className="flex items-center space-x-3">
                  {getTypeBadge(mem.memory_type)}
                  {getStatusBadge(mem.outcome_status)}
                  <span className="text-[10px] font-mono text-slate-500">
                    {new Date(mem.occurred_at || mem.created_at).toLocaleDateString()}
                  </span>
                </div>
                <h3 className="text-base font-bold text-[#F5F5F5]">{mem.title}</h3>
                {mem.content && (
                  <p className="text-xs text-[#92929A] leading-relaxed">{mem.content}</p>
                )}
              </div>

              <div className="flex items-center space-x-6 shrink-0">
                <div className="text-right">
                  <div className="text-[10px] font-mono text-slate-500 uppercase">CONFIDENCE</div>
                  <div className="text-sm font-semibold font-mono text-sky-400">
                    {typeof mem.confidence_score === 'number' ? `${mem.confidence_score}%` : 'Not available yet'}
                  </div>
                </div>

                <ChevronRight size={18} className="text-[#92929A]" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
