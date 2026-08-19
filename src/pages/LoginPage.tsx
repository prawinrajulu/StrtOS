import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, ArrowRight, ShieldCheck, Sparkles, CheckCircle2, Zap } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await login(email, password, rememberMe);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0D0D0F] flex flex-col md:flex-row text-slate-100 relative overflow-hidden font-sans">
      {/* LEFT COLUMN - Brand Showcase */}
      <div className="flex-1 p-8 lg:p-16 flex flex-col justify-between z-10">
        <div>
          <div className="flex items-center space-x-3 mb-12">
            <div className="w-9 h-9 rounded-full bg-sky-500 flex items-center justify-center font-bold text-slate-950 text-base shadow-md">
              S
            </div>
            <span className="text-xl font-bold text-[#F5F5F5] tracking-tight">STRtOS</span>
          </div>

          <h1 className="text-4xl lg:text-5xl font-extrabold text-[#F5F5F5] tracking-tight leading-tight mb-4">
            Welcome to <br />
            <span className="bg-linear-to-r from-sky-400 to-indigo-400 bg-clip-text text-transparent">
              Autonomous Business Strategy.
            </span>
          </h1>

          <p className="text-sm text-[#92929A] leading-relaxed max-w-md mb-8">
            An intelligent system continuously working for your business. Monitor performance, review strategic decisions, and track real-time results.
          </p>

          <div className="bg-[#111113] border border-white/[0.06] rounded-xl p-6 space-y-3 max-w-md">
            <div className="text-[10px] font-mono text-sky-400 uppercase tracking-widest flex items-center space-x-1.5 font-bold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>LIVE INTELLIGENCE ENGINE</span>
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex items-center space-x-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Strategic Performance & Decision Planning</span>
              </div>
              <div className="flex items-center space-x-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Deterministic Risk Governance & Approvals</span>
              </div>
              <div className="flex items-center space-x-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Real-Time Task Stream & Executive Reports</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-6 text-xs text-[#92929A] pt-8">
          <span className="flex items-center space-x-1.5"><ShieldCheck className="w-4 h-4 text-emerald-400" /> <span>Enterprise Encryption</span></span>
          <span className="flex items-center space-x-1.5"><Zap className="w-4 h-4 text-sky-400" /> <span>Multi-Tenant Isolation</span></span>
        </div>
      </div>

      {/* RIGHT COLUMN - Login Card */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12 z-10">
        <div className="w-full max-w-md bg-[#111113] border border-white/[0.06] rounded-2xl p-8 space-y-6">
          <div>
            <h2 className="text-xl font-bold text-[#F5F5F5] tracking-tight">Sign in to StrtOS</h2>
            <p className="text-xs text-[#92929A] mt-1">Access your business workspace</p>
          </div>

          {error && (
            <div className="p-3 bg-rose-950/60 border border-rose-800 rounded-lg text-xs text-rose-200 text-center">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block text-[#92929A] font-mono text-[10px] uppercase mb-1.5">
                Corporate Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="executive@organization.com"
                  className="w-full bg-[#151518] border border-white/10 rounded-lg pl-9 pr-3 py-2.5 text-xs text-[#F5F5F5] outline-none placeholder:text-[#92929A]"
                />
              </div>
            </div>

            <div>
              <label className="block text-[#92929A] font-mono text-[10px] uppercase mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full bg-[#151518] border border-white/10 rounded-lg pl-9 pr-3 py-2.5 text-xs text-[#F5F5F5] outline-none placeholder:text-[#92929A]"
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-xs pt-1">
              <label className="flex items-center space-x-2 text-[#92929A] cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="accent-sky-500 rounded"
                />
                <span>Remember 30 days</span>
              </label>
              <Link to="/forgot-password" className="text-sky-400 hover:underline">Forgot password?</Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 flex items-center justify-center space-x-2 transition disabled:opacity-50"
            >
              <span>{loading ? 'Authenticating Workspace...' : 'Sign in to Workspace'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="border-t border-white/5 pt-4 text-center text-xs text-[#92929A]">
            New to StrtOS?{' '}
            <Link to="/register" className="text-sky-400 font-semibold hover:underline">
              Register Organization
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
