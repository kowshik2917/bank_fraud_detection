import React, { useState } from 'react';
import { LockKeyhole, ShieldCheck, Loader2 } from 'lucide-react';
import { loginUser } from '../services/api';

export default function LoginScreen({ onLogin }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setError('');

    if (!email.trim() || !password) {
      setError('Enter your work email and password to continue.');
      return;
    }

    setLoading(true);
    try {
      const data = await loginUser({ email: email.trim(), password, name: name.trim() });
      // data.profile comes from MongoDB (or in-memory fallback)
      const profile = data.profile || {};
      onLogin({
        name: profile.name || name.trim() || email,
        email: profile.email || email.trim(),
        role: profile.role || 'analyst',
        initials: profile.initials ||
          (profile.name || name || email)
            .trim()
            .split(/\s+/)
            .map((p) => p[0])
            .slice(0, 2)
            .join('')
            .toUpperCase()
      });
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Login failed. Check your credentials.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#0a0f1d] flex items-center justify-center p-6 text-slate-100">
      <form onSubmit={submit} className="w-full max-w-md rounded-3xl border border-slate-700 bg-slate-900/90 p-8 shadow-2xl">
        <div className="w-12 h-12 rounded-2xl bg-blue-600/20 border border-blue-400/30 flex items-center justify-center mb-5">
          <ShieldCheck className="w-6 h-6 text-blue-300" />
        </div>
        <h1 className="text-2xl font-extrabold">Sign in to Sentinel</h1>
        <p className="mt-2 text-sm text-slate-400">Access the fraud investigation workspace.</p>

        <div className="mt-6 space-y-4">
          <input
            aria-label="Full name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Full name (required for first login)"
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm outline-none focus:border-blue-500"
          />
          <input
            aria-label="Work email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Work email"
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm outline-none focus:border-blue-500"
          />
          <input
            aria-label="Password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm outline-none focus:border-blue-500"
          />
        </div>

        {error && <p className="mt-3 text-xs text-red-400">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="mt-6 w-full rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-bold hover:bg-blue-500 flex justify-center gap-2 disabled:opacity-60"
        >
          {loading
            ? <Loader2 className="w-4 h-4 animate-spin" />
            : <LockKeyhole className="w-4 h-4" />}
          {loading ? 'Signing in...' : 'Sign in'}
        </button>

        <p className="mt-4 text-center text-[11px] text-slate-500">
          First-time users are auto-registered. Credentials stored in MongoDB.
        </p>
      </form>
    </main>
  );
}
