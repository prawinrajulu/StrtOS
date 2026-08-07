import React from 'react';

interface FilterPillProps {
  label: string;
  active?: boolean;
  onClick?: () => void;
}

export const FilterPill: React.FC<FilterPillProps> = ({ label, active = false, onClick }) => {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '6px 14px',
        borderRadius: '9999px',
        fontSize: '11px',
        fontWeight: 600,
        letterSpacing: '0.05em',
        textTransform: 'uppercase',
        fontFamily: "'JetBrains Mono', monospace",
        border: active ? '1px solid rgba(255, 255, 255, 0.25)' : '1px solid rgba(255, 255, 255, 0.06)',
        backgroundColor: active ? 'rgba(255, 255, 255, 0.15)' : 'rgba(255, 255, 255, 0.03)',
        color: active ? '#ffffff' : '#9ca3af',
        cursor: 'pointer',
        transition: 'all 0.15s ease',
      }}
    >
      {label}
    </button>
  );
};
