import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Cpu, ArrowRight, ShieldCheck, Zap, Lock, Mail, Sparkles, CheckCircle2 } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const result = await response.json();
      if (result.success) {
        login(result.data.access_token, result.data.refresh_token, {
          id: 'usr-1',
          organization_id: 'org-strtos-primary',
          full_name: 'Executive Director',
          email,
          role: 'ORG_ADMIN'
        });
        navigate('/');
      } else {
        setError(result.message || 'Authentication failed. Please verify credentials.');
      }
    } catch (err) {
      setError('Connection timeout. Unable to reach StrtOS Auth Gateway.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#050507', color: '#f3f4f6', fontFamily: "'Plus Jakarta Sans', sans-serif", position: 'relative', overflow: 'hidden' }}>
      {/* Background Mesh Lighting Glow */}
      <div style={{ position: 'absolute', top: '-10%', left: '-10%', width: '50vw', height: '50vw', background: 'radial-gradient(circle, rgba(99, 102, 241, 0.12) 0%, rgba(5, 5, 7, 0) 70%)', pointerEvents: 'none' }} />
      <div style={{ position: 'absolute', bottom: '-10%', right: '-10%', width: '50vw', height: '50vw', background: 'radial-gradient(circle, rgba(168, 85, 247, 0.12) 0%, rgba(5, 5, 7, 0) 70%)', pointerEvents: 'none' }} />
      
      {/* Grid Overlay */}
      <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px), linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px)', backgroundSize: '40px 40px', pointerEvents: 'none' }} />

      {/* LEFT COLUMN - Brand & Interactive AI Preview */}
      <div style={{ flex: 1.1, padding: '60px 80px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', zIndex: 1, borderRight: '1px solid rgba(255, 255, 255, 0.06)' }}>
        <div>
          {/* Logo Brand Header */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '64px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%)', border: '1px solid rgba(99, 102, 241, 0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Cpu style={{ width: '22px', height: '22px', color: '#818cf8' }} />
            </div>
            <div style={{ fontSize: '22px', fontWeight: 800, letterSpacing: '-0.03em', color: '#ffffff' }}>
              Strt<span style={{ color: '#818cf8' }}>OS</span>
            </div>
            <div style={{ backgroundColor: 'rgba(99, 102, 241, 0.15)', border: '1px solid rgba(99, 102, 241, 0.3)', borderRadius: '100px', padding: '2px 10px', fontSize: '10px', fontFamily: "'JetBrains Mono', monospace", color: '#818cf8', fontWeight: 600 }}>
              v0.9.0 ALIGNMENT
            </div>
          </div>

          {/* Large Headline */}
          <h1 style={{ fontSize: '46px', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.03em', lineHeight: 1.15, marginBottom: '20px' }}>
            Welcome to <br />
            <span style={{ background: 'linear-gradient(135deg, #ffffff 0%, #a5b4fc 50%, #c084fc 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Autonomous Strategy.
            </span>
          </h1>

          <p style={{ fontSize: '15px', color: '#9ca3af', lineHeight: 1.6, maxWidth: '480px', marginBottom: '48px' }}>
            The Chief Executive AI Operating System. Orchestrate business analysis, SEO audits, competitor matrices, and digital campaign execution seamlessly.
          </p>

          {/* Animated Glass Capabilities Card */}
          <div style={{ backgroundColor: 'rgba(8, 8, 10, 0.75)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '16px', padding: '24px', backdropFilter: 'blur(16px)', boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5)', maxWidth: '520px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', fontFamily: "'JetBrains Mono', monospace", color: '#818cf8', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '16px' }}>
              <Sparkles size={14} /> LIVE ORCHESTRATION ENGINE
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px', color: '#e5e7eb' }}>
                <CheckCircle2 size={16} style={{ color: '#10b981' }} />
                <span>CEO Decision Engine & Task Planning</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px', color: '#e5e7eb' }}>
                <CheckCircle2 size={16} style={{ color: '#10b981' }} />
                <span>Multi-LLM Router (Gemini Pro, Claude 3.5, GPT-4o)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px', color: '#e5e7eb' }}>
                <CheckCircle2 size={16} style={{ color: '#10b981' }} />
                <span>Real-Time SSE Event Stream & React Flow Visualizer</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px', fontSize: '12px', color: '#6b7280' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><ShieldCheck size={14} /> SOC2 Type II Certified</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><Zap size={14} /> Multi-Tenant Isolation</span>
        </div>
      </div>

      {/* RIGHT COLUMN - Centered Glass Login Card */}
      <div style={{ flex: 0.9, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px', zIndex: 1 }}>
        <div style={{ width: '100%', maxWidth: '440px', backgroundColor: '#08080a', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '20px', padding: '40px', backdropFilter: 'blur(20px)', boxShadow: '0 24px 60px rgba(0, 0, 0, 0.6)' }}>
          
          <div style={{ marginBottom: '28px' }}>
            <h2 style={{ fontSize: '24px', fontWeight: 700, color: '#ffffff', letterSpacing: '-0.02em', marginBottom: '6px' }}>Sign in to StrtOS</h2>
            <p style={{ fontSize: '13px', color: '#9ca3af' }}>Access your executive multi-agent workspace</p>
          </div>

          {error && (
            <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: '10px', padding: '12px', color: '#f87171', fontSize: '12px', textAlign: 'center', marginBottom: '20px' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
                Corporate Email
              </label>
              <div style={{ position: 'relative' }}>
                <Mail size={16} style={{ position: 'absolute', left: '14px', top: '14px', color: '#6b7280' }} />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="executive@organization.com"
                  style={{ width: '100%', backgroundColor: '#0d0d12', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '10px', padding: '12px 14px 12px 40px', fontSize: '13px', color: '#ffffff', outline: 'none', transition: 'border-color 0.2s', boxSizing: 'border-box' }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{ position: 'absolute', left: '14px', top: '14px', color: '#6b7280' }} />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  style={{ width: '100%', backgroundColor: '#0d0d12', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '10px', padding: '12px 14px 12px 40px', fontSize: '13px', color: '#ffffff', outline: 'none', transition: 'border-color 0.2s', boxSizing: 'border-box' }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#9ca3af', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  style={{ accentColor: '#6366f1', borderRadius: '4px' }}
                />
                Remember 30 days
              </label>
              <Link to="/forgot-password" style={{ color: '#818cf8', textDecoration: 'none', fontWeight: 500 }}>Forgot password?</Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                border: 'none',
                borderRadius: '10px',
                padding: '12px 20px',
                color: '#ffffff',
                fontSize: '13px',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: '0 4px 14px rgba(99, 102, 241, 0.35)',
                transition: 'transform 0.15s, opacity 0.15s',
                opacity: loading ? 0.7 : 1
              }}
            >
              {loading ? 'Authenticating Workspace...' : <>Sign in to Workspace <ArrowRight size={16} /></>}
            </button>
          </form>

          <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.06)', marginTop: '28px', paddingTop: '20px', textAlign: 'center', fontSize: '12px', color: '#6b7280' }}>
            New to StrtOS?{' '}
            <Link to="/register" style={{ color: '#818cf8', fontWeight: 600, textDecoration: 'none' }}>
              Register Organization
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
