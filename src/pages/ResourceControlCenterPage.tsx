import React, { useState, useEffect } from 'react';
import {
  Server, RefreshCw, AlertTriangle, CheckCircle, Zap,
  BarChart2, Users, Bot, DollarSign, Clock, Cpu, Wrench,
  TrendingUp, ShieldAlert, Play
} from 'lucide-react';
import {
  resourcesApi,
} from '../services/resourcesApi';
import type {
  ResourceOverview, CapacityInfo, BottleneckResponse,
  ConflictResponse, AllocationPlan, BottleneckSeverity, ResourceStatus
} from '../services/resourcesApi';

// ─── Constants ─────────────────────────────────────────────────────────────────

const RESOURCE_TYPE_ICONS: Record<string, React.ReactNode> = {
  HUMAN: <Users className="w-4 h-4" />,
  AI_AGENT: <Bot className="w-4 h-4" />,
  BUDGET: <DollarSign className="w-4 h-4" />,
  TIME: <Clock className="w-4 h-4" />,
  COMPUTE: <Cpu className="w-4 h-4" />,
  TOOL: <Wrench className="w-4 h-4" />,
  EXECUTION_CAPACITY: <Zap className="w-4 h-4" />,
  MARKETING_CAPACITY: <TrendingUp className="w-4 h-4" />,
  OPERATIONAL_CAPACITY: <Server className="w-4 h-4" />,
};

const SEVERITY_STYLE: Record<BottleneckSeverity, string> = {
  CRITICAL: 'text-red-300 bg-red-950 border-red-700',
  HIGH: 'text-rose-400 bg-rose-950 border-rose-800',
  MEDIUM: 'text-amber-400 bg-amber-950 border-amber-800',
  LOW: 'text-slate-400 bg-slate-900 border-slate-700',
};

const STATUS_STYLE: Record<ResourceStatus, string> = {
  AVAILABLE: 'text-emerald-400 bg-emerald-950 border-emerald-800',
  LIMITED: 'text-amber-400 bg-amber-950 border-amber-800',
  EXHAUSTED: 'text-red-300 bg-red-950 border-red-700',
  BLOCKED: 'text-rose-400 bg-rose-950 border-rose-800',
  DEGRADED: 'text-orange-400 bg-orange-950 border-orange-800',
  UNKNOWN: 'text-slate-400 bg-slate-900 border-slate-700',
};

const HEALTH_STYLE: Record<string, string> = {
  HEALTHY: 'text-emerald-400',
  WATCH: 'text-amber-400',
  AT_RISK: 'text-rose-400',
  CRITICAL: 'text-red-300',
  UNKNOWN: 'text-slate-400',
};

// ─── Utility Components ────────────────────────────────────────────────────────

const UtilBar: React.FC<{ pct: number; label?: string }> = ({ pct, label }) => {
  const color = pct >= 100 ? 'bg-red-500' : pct >= 90 ? 'bg-rose-500' : pct >= 75 ? 'bg-amber-500' : 'bg-cyan-500';
  return (
    <div className="space-y-0.5">
      <div className="flex justify-between text-xs font-mono text-slate-400">
        {label && <span>{label}</span>}
        <span className={pct >= 90 ? 'text-rose-400' : pct >= 75 ? 'text-amber-400' : 'text-slate-300'}>
          {pct.toFixed(1)}%
        </span>
      </div>
      <div className="w-full bg-slate-800 rounded-full h-1.5">
        <div className={`${color} h-1.5 rounded-full transition-all`} style={{ width: `${Math.min(100, pct)}%` }} />
      </div>
    </div>
  );
};

const StatCard: React.FC<{ label: string; value: string | number; icon: React.ReactNode; sub?: string; highlight?: string }> = ({ label, value, icon, sub, highlight }) => (
  <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl">
    <div className="flex justify-between items-start">
      <div className="text-slate-400">{icon}</div>
      <span className={`text-2xl font-bold font-mono ${highlight || 'text-slate-100'}`}>{value}</span>
    </div>
    <p className="text-xs text-slate-400 mt-2">{label}</p>
    {sub && <p className="text-xs text-slate-500 mt-0.5">{sub}</p>}
  </div>
);

// ─── Main Page ─────────────────────────────────────────────────────────────────

export const ResourceControlCenterPage: React.FC = () => {
  const [overview, setOverview] = useState<ResourceOverview | null>(null);
  const [capacity, setCapacity] = useState<CapacityInfo[]>([]);
  const [bottlenecks, setBottlenecks] = useState<BottleneckResponse | null>(null);
  const [conflicts, setConflicts] = useState<ConflictResponse | null>(null);
  const [plans, setPlans] = useState<AllocationPlan[]>([]);
  const [simResult, setSimResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [activeScenario, setActiveScenario] = useState<string>('CURRENT_CAPACITY');

  useEffect(() => { loadAll(); }, []);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [ov, , cap, btk, cfl, pln] = await Promise.all([
        resourcesApi.getOverview(),
        resourcesApi.listResources(),
        resourcesApi.getCapacity(),
        resourcesApi.getBottlenecks(),
        resourcesApi.getConflicts(),
        resourcesApi.listAllocationPlans(),
      ]);
      setOverview(ov);
      setCapacity(cap);
      setBottlenecks(btk);
      setConflicts(cfl);
      setPlans(pln);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const runSimulation = async (scenario: string) => {
    setSimulating(true);
    setActiveScenario(scenario);
    try {
      const result = await resourcesApi.simulateAllocation(scenario);
      setSimResult(result.recommendation);
    } catch (e) { console.error(e); }
    setSimulating(false);
  };

  if (loading) return (
    <div className="flex items-center justify-center h-64 text-cyan-400">
      <RefreshCw className="animate-spin mr-2 w-5 h-5" /> Loading Resource Intelligence...
    </div>
  );

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-3">
            <Server className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl font-bold tracking-tight">Resource & Capacity Control Center</h1>
          </div>
          <p className="text-slate-400 mt-1">
            Autonomous resource intelligence — bottleneck detection, conflict resolution, allocation optimization.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button onClick={loadAll} className="px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 flex items-center space-x-2 transition">
            <RefreshCw className="w-3.5 h-3.5" /><span>SYNC</span>
          </button>
          <span className="px-3 py-1.5 rounded-full text-xs font-mono bg-cyan-950/80 border border-cyan-800 text-cyan-300 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span>STRTOS v2.6.0 RESOURCE ENGINE</span>
          </span>
        </div>
      </div>

      {/* Overview Stats */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            label="Total Resources"
            value={overview.total_resources}
            icon={<Server className="w-5 h-5 text-cyan-400" />}
          />
          <StatCard
            label="Capacity Health"
            value={overview.overall_capacity_health}
            icon={<BarChart2 className="w-5 h-5 text-violet-400" />}
            highlight={HEALTH_STYLE[overview.overall_capacity_health] || 'text-slate-300'}
          />
          <StatCard
            label="Open Bottlenecks"
            value={bottlenecks?.total_count ?? 0}
            icon={<AlertTriangle className="w-5 h-5 text-amber-400" />}
            highlight={bottlenecks?.critical_count ? 'text-red-300' : 'text-slate-100'}
          />
          <StatCard
            label="Conflicts"
            value={conflicts?.total_count ?? 0}
            icon={<ShieldAlert className="w-5 h-5 text-rose-400" />}
            highlight={conflicts?.critical_count ? 'text-red-300' : 'text-slate-100'}
          />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Resource Capacity List */}
        <div className="md:col-span-1 space-y-3">
          <h2 className="text-sm font-mono font-semibold text-slate-400 uppercase tracking-wider">Resource Pool</h2>
          {capacity.length === 0 ? (
            <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl text-slate-500 text-xs">
              No resources registered. Create resources to begin capacity tracking.
            </div>
          ) : (
            capacity.map(r => (
              <div key={r.resource_id} className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-slate-300 text-sm font-semibold">
                    <span className="text-cyan-400">{RESOURCE_TYPE_ICONS[r.resource_type] || <Server className="w-4 h-4" />}</span>
                    <span className="truncate max-w-32">{r.resource_name}</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs font-mono border ${STATUS_STYLE[r.status]}`}>
                    {r.status}
                  </span>
                </div>
                <UtilBar pct={r.utilization_percentage} />
                <div className="flex justify-between text-xs font-mono text-slate-500">
                  <span>{r.allocated_capacity.toFixed(1)} alloc</span>
                  <span className="text-slate-400">
                    {r.total_capacity != null ? `${r.remaining_capacity.toFixed(1)} avail` : 'capacity unknown'}
                  </span>
                </div>
                {r.shortage_detected && (
                  <div className="flex items-center space-x-1 text-xs text-red-300">
                    <AlertTriangle className="w-3 h-3" />
                    <span>Shortage: {r.shortage_amount.toFixed(1)} units</span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Right Panel */}
        <div className="md:col-span-2 space-y-5">

          {/* Bottlenecks */}
          <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3">
            <h2 className="text-base font-semibold flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              <span>Top Bottlenecks</span>
              {bottlenecks?.critical_count ? (
                <span className="px-2 py-0.5 rounded text-xs font-mono bg-red-950 border border-red-700 text-red-300">
                  {bottlenecks.critical_count} CRITICAL
                </span>
              ) : null}
            </h2>
            {!bottlenecks?.bottlenecks.length ? (
              <div className="flex items-center space-x-2 text-xs text-emerald-400">
                <CheckCircle className="w-4 h-4" /><span>No bottlenecks detected.</span>
              </div>
            ) : (
              bottlenecks.bottlenecks.slice(0, 4).map((b, i) => (
                <div key={i} className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-sm text-slate-200 font-semibold">
                      {RESOURCE_TYPE_ICONS[b.resource_type] || <Server className="w-4 h-4" />}
                      <span>{b.resource_name}</span>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-xs font-mono border ${SEVERITY_STYLE[b.severity]}`}>
                      {b.severity}
                    </span>
                  </div>
                  <div className="text-xs font-mono text-slate-400">
                    Shortage: {b.shortage.toFixed(1)} ({b.shortage_pct.toFixed(1)}%) · {b.affected_mission_ids.length} mission(s) affected
                  </div>
                  <p className="text-xs text-amber-300/80 italic">{b.recommended_action}</p>
                </div>
              ))
            )}
          </div>

          {/* Conflicts */}
          <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3">
            <h2 className="text-base font-semibold flex items-center space-x-2">
              <ShieldAlert className="w-5 h-5 text-rose-400" />
              <span>Active Resource Conflicts</span>
            </h2>
            {!conflicts?.conflicts.length ? (
              <div className="flex items-center space-x-2 text-xs text-emerald-400">
                <CheckCircle className="w-4 h-4" /><span>No resource conflicts detected.</span>
              </div>
            ) : (
              conflicts.conflicts.map((c, i) => (
                <div key={i} className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-sm text-slate-200 font-semibold">
                      {RESOURCE_TYPE_ICONS[c.resource_type] || <Server className="w-4 h-4" />}
                      <span>{c.resource_name}</span>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-xs font-mono border ${SEVERITY_STYLE[c.severity]}`}>
                      {c.severity}
                    </span>
                  </div>
                  <div className="text-xs font-mono text-slate-400">
                    {c.mission_ids.length} missions competing · shortage {c.shortage.toFixed(1)} units
                  </div>
                  <div className="space-y-0.5">
                    {c.resolution_options.slice(0, 2).map((opt, j) => (
                      <p key={j} className="text-xs text-rose-300/80 italic">→ {opt}</p>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* What-If Simulation */}
          <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
            <h2 className="text-base font-semibold flex items-center space-x-2">
              <Zap className="w-5 h-5 text-violet-400" /><span>What-If Resource Simulation</span>
              <span className="text-xs font-mono text-slate-500">(side-effect free)</span>
            </h2>
            <div className="grid grid-cols-3 gap-2">
              {[
                'CURRENT_CAPACITY',
                '+10_PERCENT_CAPACITY',
                '-10_PERCENT_CAPACITY',
                '+20_PERCENT_BUDGET',
                '-20_PERCENT_BUDGET',
                'REDUCED_EXECUTION_CAPACITY',
              ].map(sc => (
                <button
                  key={sc}
                  onClick={() => runSimulation(sc)}
                  disabled={simulating}
                  className={`py-1.5 px-2 rounded-lg text-xs font-mono border transition ${
                    activeScenario === sc && simResult
                      ? 'bg-violet-900/60 border-violet-600 text-violet-200'
                      : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-600 hover:text-slate-300'
                  }`}
                >
                  {simulating && activeScenario === sc
                    ? <RefreshCw className="w-3 h-3 animate-spin inline mr-1" />
                    : null}
                  {sc.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
            {simResult && (
              <div className="p-3 bg-violet-950/30 border border-violet-800 rounded-lg text-xs text-violet-200 italic">
                {simResult}
              </div>
            )}
          </div>

          {/* Allocation Plans */}
          <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl space-y-3">
            <h2 className="text-base font-semibold flex items-center space-x-2">
              <Play className="w-5 h-5 text-emerald-400" /><span>Allocation Plans</span>
            </h2>
            {plans.length === 0 ? (
              <p className="text-xs text-slate-500">No allocation plans. Use the API to create plans.</p>
            ) : (
              plans.slice(0, 5).map(p => (
                <div key={p.id} className="flex items-center justify-between p-3 bg-slate-950 border border-slate-800 rounded-lg">
                  <div className="space-y-0.5">
                    <p className="text-sm text-slate-200 font-semibold">{p.title}</p>
                    <p className="text-xs font-mono text-slate-500">{p.version} · EV: ${(p.expected_value / 1000).toFixed(0)}K · Risk: {p.risk_score.toFixed(0)}</p>
                  </div>
                  <div className="text-right space-y-1">
                    <span className={`block px-2 py-0.5 rounded text-xs font-mono border ${
                      p.status === 'ACTIVE' ? 'text-emerald-400 bg-emerald-950 border-emerald-800' :
                      p.status === 'PENDING_GOVERNANCE' ? 'text-indigo-400 bg-indigo-950 border-indigo-800' :
                      p.status === 'APPROVED' ? 'text-cyan-400 bg-cyan-950 border-cyan-800' :
                      'text-slate-400 bg-slate-900 border-slate-700'
                    }`}>{p.status}</span>
                    <span className="block text-xs font-mono text-slate-500">{p.confidence_score.toFixed(0)}% conf</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
