import React from 'react';
import { StatusBadge } from './StatusBadge';
import type { StatusType } from './StatusBadge';
import { mapInternalExecutionToBusinessLanguage } from '../services/eventTranslationLayer';

export interface TaskItemProps {
  title: string;
  agent: string;
  eta: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  status: StatusType;
}

export const TaskItem: React.FC<TaskItemProps> = ({ title, agent, eta, priority, status }) => {
  const businessLabel = mapInternalExecutionToBusinessLanguage(agent);

  return (
    <div className="flex items-center justify-between p-3.5 bg-[#151518] border border-white/5 rounded-lg text-xs">
      <div className="space-y-0.5">
        <div className="font-semibold text-[#F5F5F5]">{title}</div>
        <div className="text-[10px] font-mono text-[#92929A] uppercase">
          {businessLabel} • {eta}
        </div>
      </div>

      <div className="flex items-center space-x-3">
        <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
          priority === 'HIGH' ? 'text-rose-300 bg-rose-950/80 border-rose-800' :
          priority === 'MEDIUM' ? 'text-amber-300 bg-amber-950/80 border-amber-800' :
          'text-slate-400 bg-slate-900 border-slate-700'
        }`}>
          {priority}
        </span>
        <StatusBadge status={status} />
      </div>
    </div>
  );
};
