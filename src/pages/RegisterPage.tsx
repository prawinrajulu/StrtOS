import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Cpu, Building, User, Mail, Lock, ArrowRight } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  const [orgName, setOrgName] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const getPasswordStrength = () => {
    if (!password) return { score: 0, label: 'None', color: '#374151' };
    let score = 0;
    if (password.length >= 8) score += 25;
    if (/[A-Z]/.test(password)) score += 25;
    if (/[0-9]/.test(password)) score += 25;
    if (/[!@#$%^&*()]/.test(password)) score += 25;

    if (score <= 25) return { score, label: 'Weak', color: '#ef4444' };
    if (score <= 75) return { score, label: 'Medium', color: '#f59e0b' };
    return { score, label: 'Strong (Enterprise Ready)', color: '#10b981' };
  };

  const strength = getPasswordStrength();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ organization_name: orgName, full_name: fullName, email, password })
      });
      const result = await response.json();
      if (response.ok && result.success !== false) {
        navigate('/login');
      } else {
        setError(result.message || result.detail || 'Registration failed.');
      }
    } catch (err) {
      setError('Connection failed. Please check network.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#050507', color: '#f3f4f6', fontFamily: "'Plus Jakarta Sans', sans-serif", alignItems: 'center', justifyContent: 'center', padding: '40px 20px', position: 'relative', overflow: 'hidden' }}>
      {/* Background Mesh Lighting Glow */}
      <div style={{ position: 'absolute', top: '-10%', right: '-10%', width: '50vw', height: '50vw', background: 'radial-gradient(circle, rgba(168, 85, 247, 0.12) 0%, rgba(5, 5, 7, 0) 70%)', pointerEvents: 'none' }} />

      <div style={{ width: '100%', maxWidth: '480px', backgroundColor: '#08080a', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '20px', padding: '40px', backdropFilter: 'blur(20px)', boxShadow: '0 24px 60px rgba(0, 0, 0, 0.6)', zIndex: 1 }}>
        
        {/* Header Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'center', marginBottom: '24px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%)', border: '1px solid rgba(99, 102, 241, 0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Cpu style={{ width: '20px', height: '20px', color: '#818cf8' }} />
          </div>
          <div style={{ fontSize: '20px', fontWeight: 800, letterSpacing: '-0.03em', color: '#ffffff' }}>
            Strt<span style={{ color: '#818cf8' }}>OS</span>
          </div>
        </div>

        <h2 style={{ fontSize: '22px', fontWeight: 700, textAlign: 'center', color: '#ffffff', letterSpacing: '-0.02em', marginBottom: '6px' }}>Register Organization</h2>
        <p style={{ fontSize: '13px', color: '#9ca3af', textAlign: 'center', marginBottom: '28px' }}>Create an isolated Multi-Tenant AI Operating System instance</p>

        {error && (
          <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: '10px', padding: '12px', color: '#f87171', fontSize: '12px', textAlign: 'center', marginBottom: '20px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>Organization Name</label>
            <div style={{ position: 'relative' }}>
              <Building size={16} style={{ position: 'absolute', left: '14px', top: '13px', color: '#6b7280' }} />
              <input
                type="text"
                required
                value={orgName}
                onChange={(e) => setOrgName(e.target.value)}
                placeholder="Acme Corp"
                style={{ width: '100%', backgroundColor: '#0d0d12', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '10px', padding: '10px 14px 10px 40px', fontSize: '13px', color: '#ffffff', outline: 'none', boxSizing: 'border-box' }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>Administrator Full Name</label>
            <div style={{ position: 'relative' }}>
              <User size={16} style={{ position: 'absolute', left: '14px', top: '13px', color: '#6b7280' }} />
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Jane Doe"
                style={{ width: '100%', backgroundColor: '#0d0d12', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '10px', padding: '10px 14px 10px 40px', fontSize: '13px', color: '#ffffff', outline: 'none', boxSizing: 'border-box' }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>Work Email</label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} style={{ position: 'absolute', left: '14px', top: '13px', color: '#6b7280' }} />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="jane@company.com"
                style={{ width: '100%', backgroundColor: '#0d0d12', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '10px', padding: '10px 14px 10px 40px', fontSize: '13px', color: '#ffffff', outline: 'none', boxSizing: 'border-box' }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>Password</label>
            <div style={{ position: 'relative' }}>
              <Lock size={16} style={{ position: 'absolute', left: '14px', top: '13px', color: '#6b7280' }} />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="SecurePass123!"
                style={{ width: '100%', backgroundColor: '#0d0d12', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '10px', padding: '10px 14px 10px 40px', fontSize: '13px', color: '#ffffff', outline: 'none', boxSizing: 'border-box' }}
              />
            </div>

            {/* Password Strength Indicator */}
            {password && (
              <div style={{ marginTop: '8px' }}>
                <div style={{ height: '4px', width: '100%', backgroundColor: '#1f1f2e', borderRadius: '2px', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${strength.score}%`, backgroundColor: strength.color, transition: 'all 0.3s' }} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: strength.color, marginTop: '4px', fontWeight: 600 }}>
                  <span>Strength: {strength.label}</span>
                  <span>Requires Uppercase, Number & Special Char</span>
                </div>
              </div>
            )}
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
              marginTop: '8px'
            }}
          >
            {loading ? 'Initializing Tenant...' : <>Create Workspace <ArrowRight size={16} /></>}
          </button>
        </form>

        <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.06)', marginTop: '24px', paddingTop: '18px', textAlign: 'center', fontSize: '12px', color: '#6b7280' }}>
          Already registered?{' '}
          <Link to="/login" style={{ color: '#818cf8', fontWeight: 600, textDecoration: 'none' }}>
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
