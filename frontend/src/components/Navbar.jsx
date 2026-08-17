import React from 'react';
import { Shield, Bell, Activity, Search, Sparkles } from 'lucide-react';

export const Navbar = ({ onOpenSimulator, activeAlertsCount = 0 }) => {
  return (
    <header className="h-16 border-b border-slate-800/80 bg-[#0a0f1d]/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20 ring-1 ring-blue-400/30">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-base tracking-tight text-white">SENTINEL</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded font-mono font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/30">
              v1.0 AI CORE
            </span>
          </div>
          <p className="text-xs text-slate-400 font-normal">Intelligent Banking Fraud Defense</p>
        </div>
      </div>

      {/* Right Action Bar */}
      <div className="flex items-center gap-3.5">
        {/* Live Simulator Button */}
        <button
          onClick={onOpenSimulator}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md shadow-blue-600/25 transition-all duration-200 border border-blue-400/30 hover:scale-[1.02] active:scale-[0.98]"
        >
          <Sparkles className="w-3.5 h-3.5 text-blue-200 animate-pulse" />
          <span>Simulate Live Transaction</span>
        </button>

        {/* System Health Pulse */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
          <span className="font-medium text-emerald-400">Models Online</span>
        </div>

        {/* Alerts Bell */}
        <div className="relative p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white cursor-pointer transition">
          <Bell className="w-4 h-4" />
          {activeAlertsCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-red-600 text-white text-[9px] font-bold flex items-center justify-center animate-bounce">
              {activeAlertsCount}
            </span>
          )}
        </div>

        {/* User Badge */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-slate-700 to-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-200">
            FA
          </div>
          <div className="hidden lg:block text-left">
            <div className="text-xs font-semibold text-slate-200">Lead Analyst #8142</div>
            <div className="text-[10px] text-slate-400">Risk Operations</div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
