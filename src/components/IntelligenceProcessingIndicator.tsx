import { Activity, CheckCircle, AlertTriangle, RefreshCw, Sparkles, ShieldCheck } from 'lucide-react';

export type IntelligenceState =
  | 'IDLE'
  | 'ANALYZING'
  | 'EVALUATING'
  | 'SYNTHESIZING'
  | 'WAITING_FOR_APPROVAL'
  | 'COMPLETED'
  | 'DEGRADED'
  | 'FAILED';

export interface IntelligenceProcessingProps {
  state: IntelligenceState;
  title?: string;
  stageMessage?: string;
  progressPct?: number;
  compact?: boolean;
}

const STATE_CONFIG: Record<IntelligenceState, { label: string; color: string; icon: React.ReactNode }> = {
  IDLE: {
    label: 'SYSTEM READY',
    color: 'text-slate-400 border-slate-700 bg-slate-900',
    icon: <Activity className="w-4 h-4 text-slate-400" />,
  },
  ANALYZING: {
    label: 'ANALYZING EVIDENCE',
    color: 'text-cyan-400 border-cyan-800 bg-cyan-950/60',
    icon: <RefreshCw className="w-4 h-4 text-cyan-400 animate-spin" />,
  },
  EVALUATING: {
    label: 'EVALUATING SCENARIOS',
    color: 'text-violet-400 border-violet-800 bg-violet-950/60',
    icon: <Sparkles className="w-4 h-4 text-violet-400 animate-pulse" />,
  },
  SYNTHESIZING: {
    label: 'SYNTHESIZING STRATEGY',
    color: 'text-indigo-400 border-indigo-800 bg-indigo-950/60',
    icon: <RefreshCw className="w-4 h-4 text-indigo-400 animate-spin" />,
  },
  WAITING_FOR_APPROVAL: {
    label: 'GOVERNANCE PENDING',
    color: 'text-amber-400 border-amber-800 bg-amber-950/60',
    icon: <ShieldCheck className="w-4 h-4 text-amber-400" />,
  },
  COMPLETED: {
    label: 'INTELLIGENCE READY',
    color: 'text-emerald-400 border-emerald-800 bg-emerald-950/60',
    icon: <CheckCircle className="w-4 h-4 text-emerald-400" />,
  },
  DEGRADED: {
    label: 'ANALYSIS DEGRADED',
    color: 'text-orange-400 border-orange-800 bg-orange-950/60',
    icon: <AlertTriangle className="w-4 h-4 text-orange-400" />,
  },
  FAILED: {
    label: 'ANALYSIS DEFERRED',
    color: 'text-rose-400 border-rose-800 bg-rose-950/60',
    icon: <AlertTriangle className="w-4 h-4 text-rose-400" />,
  },
};

/**
 * Maps SSE and raw runtime event names to user-facing generic intelligence stages.
 */
export function mapEventToIntelligenceStage(eventType: string): {
  state: IntelligenceState;
  message: string;
} {
  const evt = (eventType || '').toLowerCase();
  if (evt.includes('started') || evt.includes('tool.started')) {
    return {
      state: 'ANALYZING',
      message: 'Gathering verified business evidence and market signals...',
    };
  }
  if (evt.includes('llm.started') || evt.includes('reasoning')) {
    return {
      state: 'SYNTHESIZING',
      message: 'Synthesizing strategic intelligence and evaluating causal tradeoffs...',
    };
  }
  if (evt.includes('pending') || evt.includes('approval')) {
    return {
      state: 'WAITING_FOR_APPROVAL',
      message: 'Decision formulated. Awaiting governance review and human approval...',
    };
  }
  if (evt.includes('completed') || evt.includes('approved')) {
    return {
      state: 'COMPLETED',
      message: 'Strategic analysis completed. Intelligence updated.',
    };
  }
  if (evt.includes('degraded') || evt.includes('warning')) {
    return {
      state: 'DEGRADED',
      message: 'Intelligence analysis completed with partial evidence constraints.',
    };
  }
  if (evt.includes('failed') || evt.includes('error')) {
    return {
      state: 'FAILED',
      message: 'Strategic processing deferred due to unavailable data telemetry.',
    };
  }
  return {
    state: 'EVALUATING',
    message: 'Evaluating continuous business state and predictive scenarios...',
  };
}

export const IntelligenceProcessingIndicator: React.FC<IntelligenceProcessingProps> = ({
  state,
  title = 'STRtOS INTELLIGENCE ENGINE',
  stageMessage,
  progressPct,
  compact = false,
}) => {
  const config = STATE_CONFIG[state] || STATE_CONFIG.IDLE;
  const message = stageMessage || 'Evaluating continuous business state and strategic alignment...';

  if (compact) {
    return (
      <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-full border text-xs font-mono ${config.color}`}>
        {config.icon}
        <span className="font-semibold">{config.label}</span>
      </div>
    );
  }

  return (
    <div className={`p-4 rounded-xl border backdrop-blur-sm ${config.color} space-y-3`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {config.icon}
          <span className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">{title}</span>
        </div>
        <span className="px-2 py-0.5 rounded text-xs font-mono border font-semibold">
          {config.label}
        </span>
      </div>

      <p className="text-xs text-slate-300 font-mono">{message}</p>

      {typeof progressPct === 'number' && (
        <div className="space-y-1">
          <div className="flex justify-between text-xs font-mono text-slate-400">
            <span>Processing Progress</span>
            <span>{Math.min(100, Math.max(0, progressPct)).toFixed(0)}%</span>
          </div>
          <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-800">
            <div
              className="bg-cyan-400 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(100, Math.max(0, progressPct))}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};
