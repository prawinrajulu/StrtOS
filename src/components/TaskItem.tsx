import React from 'react';
import { StatusBadge } from './StatusBadge';
import type { StatusType } from './StatusBadge';
import { MoveVertical } from 'lucide-react';

export interface TaskItemProps {
  title: string;
  agent: string;
  eta: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  status: StatusType;
}

export const TaskItem: React.FC<TaskItemProps> = ({ title, agent, eta, priority, status }) => {
  const getPriorityColor = () => {
    switch (priority) {
      case 'HIGH':
        return '#ef4444';
      case 'MEDIUM':
        return '#f59e0b';
      case 'LOW':
      default:
        return '#64748b';
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 16px',
        backgroundColor: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid rgba(255, 255, 255, 0.05)',
        borderRadius: '8px',
        transition: 'all 0.15s ease',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{ color: '#4b5563', cursor: 'grab' }}>
          <MoveVertical size={14} />
        </div>
        <div>
          <div style={{ fontSize: '13px', fontWeight: 500, color: '#e5e7eb' }}>{title}</div>
          <div
            style={{
              fontSize: '10px',
              fontFamily: "'JetBrains Mono', monospace",
              color: '#6b7280',
              marginTop: '3px',
              textTransform: 'uppercase',
            }}
          >
            {agent} • {eta}
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span
          style={{
            fontSize: '9px',
            fontFamily: "'JetBrains Mono', monospace",
            color: getPriorityColor(),
            border: `1px solid ${getPriorityColor()}33`,
            backgroundColor: `${getPriorityColor()}11`,
            padding: '2px 6px',
            borderRadius: '4px',
            fontWeight: 600,
          }}
        >
          {priority}
        </span>
        <StatusBadge status={status} />
      </div>
    </div>
  );
};
