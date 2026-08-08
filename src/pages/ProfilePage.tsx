import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Building, Shield, LogOut, Key, Activity } from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div style={{ padding: '32px 40px', maxWidth: '1200px', margin: '0 auto', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ fontSize: '10px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: '8px' }}>
          STRTOS • TENANT SETTINGS
        </div>
        <h1 style={{ fontSize: '32px', fontWeight: 700, color: '#ffffff', letterSpacing: '-0.02em', marginBottom: '6px' }}>
          Organization & Profile
        </h1>
        <p style={{ fontSize: '13px', color: '#9ca3af' }}>
          Manage your multi-tenant session parameters and active RBAC permissions
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px' }}>
        {/* Main User Info Glass Card */}
        <div style={{ backgroundColor: '#08080a', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '16px', padding: '32px', backdropFilter: 'blur(16px)', boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '24px', marginBottom: '24px' }}>
            <div style={{ width: '60px', height: '60px', borderRadius: '18px', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(168, 85, 247, 0.25) 100%)', border: '1px solid rgba(99, 102, 241, 0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#a5b4fc', fontWeight: 800, fontSize: '24px' }}>
              {user?.full_name?.charAt(0) || 'E'}
            </div>
            <div>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#ffffff', letterSpacing: '-0.01em', marginBottom: '4px' }}>{user?.full_name || 'Executive Admin'}</h2>
              <p style={{ fontSize: '13px', color: '#9ca3af' }}>{user?.email}</p>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '32px' }}>
            <div style={{ backgroundColor: '#0d0d12', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Building size={20} style={{ color: '#818cf8' }} />
              <div>
                <div style={{ fontSize: '10px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280', textTransform: 'uppercase' }}>TENANT ID</div>
                <div style={{ fontSize: '13px', fontFamily: "'JetBrains Mono', monospace", color: '#e5e7eb', marginTop: '2px' }}>{user?.organization_id || 'org-strtos-primary'}</div>
              </div>
            </div>

            <div style={{ backgroundColor: '#0d0d12', border: '1px solid rgba(255, 255, 255, 0.06)', borderRadius: '12px', padding: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Shield size={20} style={{ color: '#c084fc' }} />
              <div>
                <div style={{ fontSize: '10px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280', textTransform: 'uppercase' }}>RBAC ROLE</div>
                <div style={{ fontSize: '13px', fontFamily: "'JetBrains Mono', monospace", color: '#e5e7eb', marginTop: '2px' }}>{user?.role || 'ORG_ADMIN'}</div>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid rgba(255, 255, 255, 0.08)', paddingTop: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#9ca3af' }}>
              <Activity size={14} style={{ color: '#10b981' }} />
              <span>JWT Session Active (15-min Access Token / 7-day Refresh Token)</span>
            </div>

            <button
              onClick={logout}
              style={{
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.25)',
                borderRadius: '8px',
                padding: '8px 16px',
                color: '#f87171',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                transition: 'background-color 0.15s'
              }}
            >
              <LogOut size={14} /> Revoke Session & Sign Out
            </button>
          </div>
        </div>

        {/* Security & System Info Side Panel */}
        <div style={{ backgroundColor: '#08080a', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '16px', padding: '24px', backdropFilter: 'blur(16px)' }}>
          <div style={{ fontSize: '11px', fontFamily: "'JetBrains Mono', monospace", color: '#818cf8', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Key size={14} /> SECURITY ARCHITECTURE
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '12px', color: '#9ca3af', lineHeight: 1.5 }}>
            <div>
              <strong style={{ color: '#e5e7eb' }}>Password Storage:</strong> Bcrypt (Cost 12) with automatic salt handling.
            </div>
            <div>
              <strong style={{ color: '#e5e7eb' }}>Token Revocation:</strong> Redis JTI Blacklist verification on every API request.
            </div>
            <div>
              <strong style={{ color: '#e5e7eb' }}>Tenant Isolation:</strong> Strict organization scope enforcement.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
