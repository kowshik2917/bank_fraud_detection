import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  TrendingUp,
  AlertOctagon,
  DollarSign,
  Activity,
  ArrowUpRight,
  Sparkles,
  Layers,
  Clock
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar, CartesianGrid, Legend
} from 'recharts';
import { getDashboardStats, getAlerts } from '../services/api';
import RiskBadge from '../components/RiskBadge';

export const DashboardOverview = ({ onOpenSimulator, onSelectAlert }) => {
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch dashboard stats and alerts count periodically
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, alertsData] = await Promise.all([
          getDashboardStats(),
          getAlerts({ limit: 6 })
        ]);
        setStats(statsData);
        setAlerts(alertsData.alerts || []);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 60000); // refresh every minute
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs text-slate-400 font-medium">Loading Real-Time Intelligence...</span>
        </div>
      </div>
    );
  }

  // Format Risk Distribution for Donut Chart
  const riskDist = stats?.risk_distribution || { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };
  const pieData = [
    { name: 'Low Risk', value: riskDist.LOW, color: '#10b981' },
    { name: 'Medium Risk', value: riskDist.MEDIUM, color: '#eab308' },
    { name: 'High Risk', value: riskDist.HIGH, color: '#f97316' },
    { name: 'Critical Risk', value: riskDist.CRITICAL, color: '#ef4444' },
  ];

  return (
    <div className="space-y-6">
      {/* New User Workspace Welcome Banner */}
      {stats?.total_transactions_scanned === 0 && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-blue-900/30 to-indigo-900/20 border border-blue-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center shrink-0">
              <Sparkles className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">Welcome to your Personal Fraud Intelligence Workspace!</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                This workspace is dedicated to your analyst account. Run your first simulation to start generating live threat metrics and alert feeds.
              </p>
            </div>
          </div>
          <button
            onClick={onOpenSimulator}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/30 transition shrink-0"
          >
            Launch First Simulation →
          </button>
        </div>
      )}

      {/* Top Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-950/40 via-slate-900 to-slate-900 border border-blue-900/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
              REAL-TIME MONITORING
            </span>
            <span className="text-xs text-slate-400">Model: {stats?.best_model_name || 'XGBoost'} Ensemble</span>
          </div>
          <h1 className="text-xl font-extrabold text-white tracking-tight">
            Banking Fraud Intelligence & Threat Operations
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Continuous transaction telemetry, automated risk tiering, and forensic SHAP attribution.
          </p>
        </div>

        <button
          onClick={onOpenSimulator}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/25 transition shrink-0"
        >
          <Sparkles className="w-4 h-4" />
          <span>Simulate Transaction</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Scanned */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Total Transactions</span>
            <Activity className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {(stats?.total_transactions_scanned ?? 0).toLocaleString()}
          </div>
          <div className="flex items-center gap-1 mt-1 text-[11px] text-emerald-400">
            <TrendingUp className="w-3 h-3" />
            <span>Live scored-transaction count</span>
          </div>
        </div>

        {/* Fraud Prevented ($) */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">High-Risk Amount Held (USD)</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 tracking-tight">
            ${(stats?.total_fraud_prevented_usd ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="flex items-center gap-1 mt-1 text-[11px] text-slate-400">
            <span>{stats?.total_fraud_detected ?? 0} high-risk transactions detected</span>
          </div>
        </div>

        {/* Active Alerts */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Active Alert Queue</span>
            <ShieldAlert className="w-4 h-4 text-orange-400" />
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {stats?.total_active_alerts ?? 0}
          </div>
          <div className="flex items-center gap-1 mt-1 text-[11px] text-orange-400">
            <span>Requires analyst review</span>
          </div>
        </div>

        {/* Mean Risk Index */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Fleet Fraud Rate</span>
            <AlertOctagon className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {stats?.fraud_rate_percentage ?? 0}%
          </div>
          <div className="flex items-center gap-1 mt-1 text-[11px] text-slate-400">
            <span>Avg Risk Score: {stats?.average_risk_score ?? 0} / 100</span>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 24-Hour Velocity Area Chart */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white">24-Hour Transaction & Fraud Velocity</h3>
              <p className="text-xs text-slate-400">Volume distribution vs fraud probability spikes</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <div className="flex items-center gap-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded bg-blue-500" />
                <span>Volume</span>
              </div>
              <div className="flex items-center gap-1.5 text-slate-300">
                <span className="w-2.5 h-2.5 rounded bg-red-500" />
                <span>Fraud Rate (%)</span>
              </div>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats?.hourly_trend || []}>
                <defs>
                  <linearGradient id="colorVol" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis dataKey="hour" stroke="#64748b" fontSize={11} />
                <YAxis yAxisId="left" stroke="#64748b" fontSize={11} />
                <YAxis yAxisId="right" orientation="right" stroke="#ef4444" fontSize={11} unit="%" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Area yAxisId="left" type="monotone" dataKey="total_volume" stroke="#3b82f6" fillOpacity={1} fill="url(#colorVol)" name="Volume" />
                <Area yAxisId="right" type="monotone" dataKey="fraud_rate" stroke="#ef4444" strokeWidth={2} fillOpacity={0} name="Fraud %" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Distribution Donut Chart */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white">Risk Tier Breakdown</h3>
            <p className="text-xs text-slate-400">Transactions grouped by calibrated severity</p>
          </div>

          <div className="h-48 w-full my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-1.5 text-xs">
            {pieData.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-slate-300">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                  <span>{item.name}</span>
                </div>
                <span className="font-mono text-slate-400">{item.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Active Alerts Queue Table */}
      <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white">High Priority Threat Alerts</h3>
            <p className="text-xs text-slate-400">Recent high & critical risk flags queued for review</p>
          </div>
          <button
  onClick={onSelectAlert}
  className="text-xs text-blue-400 font-medium cursor-pointer hover:underline focus:outline-none"
>
  View All in Alerts Center →
</button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                <th className="pb-3 font-semibold">Alert ID / Transaction</th>
                <th className="pb-3 font-semibold">Cardholder</th>
                <th className="pb-3 font-semibold">Amount</th>
                <th className="pb-3 font-semibold">Fraud Prob</th>
                <th className="pb-3 font-semibold">Risk Level</th>
                <th className="pb-3 font-semibold">Status</th>
                <th className="pb-3 font-semibold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-6 text-center text-slate-500">
                    No active high-risk alerts in queue.
                  </td>
                </tr>
              ) : (
                alerts.map((a) => (
                  <tr key={a.alert_id || a.transaction_id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 font-mono text-slate-200">
                      <div>{a.alert_id}</div>
                      <div className="text-[10px] text-slate-300">{a.transaction_id}</div>
                    </td>
                    <td className="py-3 text-slate-300 font-mono">{a.cardholder_id || 'CUST-88192'}</td>
                    <td className="py-3 font-bold text-white font-mono">
                      ${typeof a.amount === 'number' ? a.amount.toFixed(2) : a.amount}
                    </td>
                    <td className="py-3 text-red-400 font-semibold font-mono">
                      {((a.fraud_probability || 0.85) * 100).toFixed(1)}%
                    </td>
                    <td className="py-3">
                      <RiskBadge level={a.risk_level} score={a.risk_score} size="sm" />
                    </td>
                    <td className="py-3">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                        {a.status || 'OPEN'}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => onSelectAlert && onSelectAlert(a)}
                        className="px-2.5 py-1 rounded bg-blue-600/20 text-blue-400 border border-blue-500/30 hover:bg-blue-600/30 transition text-[11px]"
                      >
                        Investigate
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;
