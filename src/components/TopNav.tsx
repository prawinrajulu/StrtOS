import React from 'react';
import { Search, Bell } from 'lucide-react';

interface TopNavProps {
  breadcrumbs: string[];
}

export const TopNav: React.FC<TopNavProps> = ({ breadcrumbs }) => {
  return (
    <header
      style={{
        height: '64px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
        backgroundColor: 'rgba(8, 8, 10, 0.8)',
        backdropFilter: 'blur(12px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 32px',
        position: 'sticky',
        top: 0,
        zIndex: 10,
      }}
    >
      {/* Breadcrumbs */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '11px',
          fontFamily: "'JetBrains Mono', monospace",
          color: '#6b7280',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
        }}
      >
        {breadcrumbs.map((crumb, idx) => (
          <React.Fragment key={crumb}>
            {idx > 0 && <span style={{ color: '#374151' }}>/</span>}
            <span style={{ color: idx === breadcrumbs.length - 1 ? '#f3f4f6' : '#6b7280', fontWeight: idx === breadcrumbs.length - 1 ? 600 : 400 }}>
              {crumb}
            </span>
          </React.Fragment>
        ))}
      </div>

      {/* Right Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Search Bar */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
            borderRadius: '8px',
            padding: '6px 12px',
            width: '240px',
          }}
        >
          <Search size={14} color="#6b7280" />
          <input
            type="text"
            placeholder="Search or ask anything..."
            style={{
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: '#e5e7eb',
              fontSize: '12px',
              width: '100%',
            }}
          />
          <kbd
            style={{
              fontSize: '9px',
              fontFamily: "'JetBrains Mono', monospace",
              backgroundColor: 'rgba(255, 255, 255, 0.06)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '4px',
              padding: '2px 4px',
              color: '#6b7280',
            }}
          >
            ⌘K
          </kbd>
        </div>

        {/* Notifications */}
        <button
          style={{
            position: 'relative',
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            backgroundColor: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#9ca3af',
            cursor: 'pointer',
          }}
        >
          <Bell size={16} />
          <span
            style={{
              position: 'absolute',
              top: '8px',
              right: '8px',
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: '#6366f1',
            }}
          />
        </button>

        {/* User Profile */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '34px',
              height: '34px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #00e599 0%, #3b82f6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '12px',
              fontWeight: 700,
              color: '#000000',
            }}
          >
            AC
          </div>
          <div>
            <div style={{ fontSize: '12px', fontWeight: 600, color: '#f3f4f6' }}>Ava Chen</div>
            <div style={{ fontSize: '9px', color: '#6b7280', fontFamily: "'JetBrains Mono', monospace" }}>
              FOUNDER
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
