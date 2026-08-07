import React from 'react';

export type StatusType = 'THINKING' | 'RUNNING' | 'COMPLETED' | 'WAITING' | 'IDLE';

interface StatusBadgeProps {
  status: StatusType;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  const getColors = () => {
    switch (status) {
      case 'THINKING':
        return { dot: '#a855f7', bg: 'rgba(168, 85, 247, 0.12)', text: '#c084fc' };
      case 'RUNNING':
        return { dot: '#00e599', bg: 'rgba(0, 229, 153, 0.12)', text: '#00e599' };
      case 'COMPLETED':
        return { dot: '#10b981', bg: 'rgba(16, 185, 129, 0.12)', text: '#34d399' };
      case 'WAITING':
        return { dot: '#f59e0b', bg: 'rgba(245, 158, 11, 0.12)', text: '#fbbf24' };
      case 'IDLE':
      default:
        return { dot: '#64748b', bg: 'rgba(100, 116, 139, 0.12)', text: '#94a3b8' };
    }
  };

  const style = getColors();

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono tracking-wider font-semibold uppercase ${className}`}
      style={{ backgroundColor: style.bg, color: style.text }}
    >
      <span
        className="w-1.5 h-1.5 rounded-full animate-pulse"
        style={{ backgroundColor: style.dot }}
      />
      {status}
    </span>
  );
};
