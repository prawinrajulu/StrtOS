import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Cpu, Mail, ArrowRight, CheckCircle2 } from 'lucide-react';

export const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await fetch('/api/v1/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      setSubmitted(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#050507', color: '#f3f4f6', fontFamily: "'Plus Jakarta Sans', sans-serif", alignItems: 'center', justifyContent: 'center', padding: '40px 20px', position: 'relative', overflow: 'hidden' }}>
      <div style={{ width: '100%', maxWidth: '440px', backgroundColor: '#08080a', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '20px', padding: '40px', backdropFilter: 'blur(20px)', boxShadow: '0 24px 60px rgba(0, 0, 0, 0.6)', zIndex: 1 }}>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'center', marginBottom: '24px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(168, 85, 247, 0.2) 100%)', border: '1px solid rgba(99, 102, 241, 0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Cpu style={{ width: '20px', height: '20px', color: '#818cf8' }} />
          </div>
          <div style={{ fontSize: '20px', fontWeight: 800, letterSpacing: '-0.03em', color: '#ffffff' }}>
            Strt<span style={{ color: '#818cf8' }}>OS</span>
          </div>
        </div>

        <h2 style={{ fontSize: '22px', fontWeight: 700, textAlign: 'center', color: '#ffffff', letterSpacing: '-0.02em', marginBottom: '6px' }}>Reset Password</h2>
        <p style={{ fontSize: '13px', color: '#9ca3af', textAlign: 'center', marginBottom: '28px' }}>Enter work email to dispatch secure recovery token</p>

        {submitted ? (
          <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: '12px', padding: '16px', color: '#34d399', fontSize: '13px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
            <CheckCircle2 size={24} />
            <span>Instructions sent to <strong>{email}</strong> if registered in system.</span>
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>Work Email</label>
              <div style={{ position: 'relative' }}>
                <Mail size={16} style={{ position: 'absolute', left: '14px', top: '14px', color: '#6b7280' }} />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@organization.com"
                  style={{ width: '100%', backgroundColor: '#0d0d12', border: '1px solid rgba(255, 255, 255, 0.1)', borderRadius: '10px', padding: '12px 14px 12px 40px', fontSize: '13px', color: '#ffffff', outline: 'none', boxSizing: 'border-box' }}
                />
              </div>
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
                boxShadow: '0 4px 14px rgba(99, 102, 241, 0.35)'
              }}
            >
              {loading ? 'Dispatching...' : <>Send Instructions <ArrowRight size={16} /></>}
            </button>
          </form>
        )}

        <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.06)', marginTop: '28px', paddingTop: '20px', textAlign: 'center', fontSize: '12px', color: '#6b7280' }}>
          Back to{' '}
          <Link to="/login" style={{ color: '#818cf8', fontWeight: 600, textDecoration: 'none' }}>
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
