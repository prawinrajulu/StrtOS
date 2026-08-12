import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Building, Shield, LogOut, Key, Activity, Cpu, ShieldCheck, Network, Sparkles, Terminal } from 'lucide-react';

interface ProfilePageProps {
  onNavigateDiagnostics?: (tab: string) => void;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({ onNavigateDiagnostics }) => {
  const { user, logout } = useAuth();
  const [activeSubTab, setActiveSubTab] = useState<'overview' | 'diagnostics'>('overview');

  return (
    <div style={{ padding: '32px 40px', maxWidth: '1200px', margin: '0 auto', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      {/* Header */}
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <div style={{ fontSize: '10px', fontFamily: "'JetBrains Mono', monospace", color: '#6b7280', letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: '8px' }}>
            STRTOS • SYSTEM & TENANT CONTROL
          </div>
          <h1 style={{ fontSize: '32px', fontWeight: 700, color: '#ffffff', letterSpacing: '-0.02em', margin: 0 }}>
            Settings & System Diagnostics
          </h1>
          <p style={{ fontSize: '13px', color: '#9ca3af', marginTop: '4px' }}>
            Manage multi-tenant session parameters, RBAC permissions, and internal system runtime diagnostics
          </p>
        </div>

        {/* Sub-tab Switcher */}
        <div style={{ display: 'flex', gap: '8px', backgroundColor: '#0f172a', padding: '4px', borderRadius: '10px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <button
            onClick={() => setActiveSubTab('overview')}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: 600,
              border: 'none',
              cursor: 'pointer',
              color: activeSubTab === 'overview' ? '#ffffff' : '#9ca3af',
              backgroundColor: activeSubTab === 'overview' ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              transition: 'all 0.15s ease',
            }}
          >
            Organization & Profile
          </button>
          <button
            onClick={() => setActiveSubTab('diagnostics')}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: 600,
              border: 'none',
              cursor: 'pointer',
              color: activeSubTab === 'diagnostics' ? '#ffffff' : '#9ca3af',
              backgroundColor: activeSubTab === 'diagnostics' ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.15s ease',
            }}
          >
            <Terminal size={14} style={{ color: '#00e599' }} /> Internal Runtime Diagnostics
          </button>
        </div>
      </div>

      {activeSubTab === 'overview' ? (
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
      ) : (
        /* Internal Runtime Diagnostics Panel (Requirement 17) */
        <div style={{ backgroundColor: '#08080a', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '16px', padding: '32px', backdropFilter: 'blur(16px)' }}>
          <div style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
              <Terminal size={22} style={{ color: '#00e599' }} />
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#ffffff', margin: 0 }}>
                Internal System Diagnostics & Telemetry
              </h2>
            </div>
            <p style={{ fontSize: '13px', color: '#9ca3af', margin: 0 }}>
              Operational debugging tools for system administrators and engineering teams. Inspect low-level agent runtime telemetry, latency logs, model benchmark scores, policy evolution, and swarm consensus logs.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
            <div style={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#38bdf8', marginBottom: '8px' }}>
                  <Cpu size={18} />
                  <span style={{ fontSize: '15px', fontWeight: 700, color: '#f8fafc' }}>Intelligence Telemetry</span>
                </div>
                <p style={{ fontSize: '12px', color: '#94a3b8', lineHeight: 1.5, marginBottom: '16px' }}>
                  Detailed execution telemetry, latency ms, token consumption, and error rates per internal processing module.
                </p>
              </div>
              <button
                onClick={() => onNavigateDiagnostics?.('agent-intelligence')}
                style={{ width: '100%', padding: '9px', backgroundColor: '#0284c7', color: '#ffffff', border: 'none', borderRadius: '8px', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
              >
                Inspect Telemetry Dashboard →
              </button>
            </div>

            <div style={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#a855f7', marginBottom: '8px' }}>
                  <Sparkles size={18} />
                  <span style={{ fontSize: '15px', fontWeight: 700, color: '#f8fafc' }}>Runtime Optimization</span>
                </div>
                <p style={{ fontSize: '12px', color: '#94a3b8', lineHeight: 1.5, marginBottom: '16px' }}>
                  Optimization control center, weakness detection, anomaly logs, and bounded model adjustment recommendations.
                </p>
              </div>
              <button
                onClick={() => onNavigateDiagnostics?.('agent-optimization')}
                style={{ width: '100%', padding: '9px', backgroundColor: '#7e22ce', color: '#ffffff', border: 'none', borderRadius: '8px', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
              >
                Inspect Optimization Controls →
              </button>
            </div>

            <div style={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#10b981', marginBottom: '8px' }}>
                  <ShieldCheck size={18} />
                  <span style={{ fontSize: '15px', fontWeight: '700', color: '#f8fafc' }}>Policy Evolution Pipeline</span>
                </div>
                <p style={{ fontSize: '12px', color: '#94a3b8', lineHeight: 1.5, marginBottom: '16px' }}>
                  Review policy rules, candidates, version histories, and autonomy thresholds enforced across the system.
                </p>
              </div>
              <button
                onClick={() => onNavigateDiagnostics?.('policies')}
                style={{ width: '100%', padding: '9px', backgroundColor: '#059669', color: '#ffffff', border: 'none', borderRadius: '8px', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
              >
                Inspect Policy Evolution →
              </button>
            </div>

            <div style={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#f59e0b', marginBottom: '8px' }}>
                  <Network size={18} />
                  <span style={{ fontSize: '15px', fontWeight: 700, color: '#f8fafc' }}>Swarm Debate Diagnostics</span>
                </div>
                <p style={{ fontSize: '12px', color: '#94a3b8', lineHeight: 1.5, marginBottom: '16px' }}>
                  Inspect raw multi-agent debate logs, conflict resolutions, and consensus scoring parameters.
                </p>
              </div>
              <button
                onClick={() => onNavigateDiagnostics?.('swarm')}
                style={{ width: '100%', padding: '9px', backgroundColor: '#d97706', color: '#ffffff', border: 'none', borderRadius: '8px', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
              >
                Inspect Swarm Diagnostics →
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
