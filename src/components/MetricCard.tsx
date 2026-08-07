import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({ title, value, change }) => {
  return (
    <div
      className="glass-card"
      style={{
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        height: '100%',
      }}
    >
      <div
        style={{
          fontSize: '10px',
          fontFamily: "'JetBrains Mono', monospace",
          letterSpacing: '0.1em',
          color: '#6b7280',
          textTransform: 'uppercase',
          marginBottom: '12px',
        }}
      >
        {title}
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '28px', fontWeight: 700, color: '#ffffff', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
          {value}
        </span>
        {change && (
          <span
            style={{
              fontSize: '11px',
              color: '#00e599',
              fontFamily: "'JetBrains Mono', monospace",
              backgroundColor: 'rgba(0, 229, 153, 0.1)',
              padding: '2px 6px',
              borderRadius: '4px',
            }}
          >
            {change}
          </span>
        )}
      </div>
    </div>
  );
};
