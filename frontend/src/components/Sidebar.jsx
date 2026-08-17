import React from 'react';
import {
  LayoutDashboard,
  Receipt,
  TrendingUp,
  BrainCircuit,
  BellRing,
  FileText,
  Database,
  ExternalLink,
  Lock
} from 'lucide-react';

export const Sidebar = ({ activeTab, setActiveTab, alertCount = 0 }) => {
  const navItems = [
    { id: 'overview', label: 'Dashboard Overview', icon: LayoutDashboard },
    { id: 'explorer', label: 'Transaction Explorer', icon: Receipt },
    { id: 'analytics', label: 'Fraud Analytics', icon: TrendingUp },
    { id: 'shap', label: 'SHAP Explainability', icon: BrainCircuit },
    { id: 'alerts', label: 'Alerts Center', icon: BellRing, badge: alertCount },
    { id: 'reports', label: 'Forensic Reports', icon: FileText },
  ];

  return (
    <aside className="w-64 border-r border-slate-800/80 bg-[#0d1326]/60 backdrop-blur-md flex flex-col justify-between p-4 shrink-0 min-h-[calc(100vh-4rem)]">
      <div>
        <div className="px-3 pb-3 text-[11px] font-bold text-slate-300 uppercase tracking-wider">
          Platform Navigation
        </div>
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 ${
                      isActive ? 'text-blue-400' : 'text-slate-400'
                    }`}
                  />
                  <span>{item.label}</span>
                </div>
                {item.badge > 0 && (
                  <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-red-500/20 text-red-400 border border-red-500/40">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* System Architecture & Status Card */}
        <div className="mt-8 p-3.5 rounded-xl bg-slate-900/90 border border-slate-800">
          <div className="flex items-center gap-2 mb-2">
            <Database className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-xs font-semibold text-slate-300">Data & ML Engine</span>
          </div>
          <div className="space-y-1.5 text-[11px] text-slate-400">
            <div className="flex justify-between">
              <span>Supervised Model:</span>
              <span className="font-mono text-emerald-400 font-medium">XGBoost</span>
            </div>
            <div className="flex justify-between">
              <span>Anomaly Detector:</span>
              <span className="font-mono text-blue-400 font-medium">IsoForest</span>
            </div>
            <div className="flex justify-between">
              <span>Explainability:</span>
              <span className="font-mono text-purple-400 font-medium">TreeSHAP</span>
            </div>
            <div className="flex justify-between">
              <span>Database Layer:</span>
              <span className="font-mono text-amber-400 font-medium">Mongo Atlas</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Security Badge */}
      <div className="pt-4 border-t border-slate-800/80 px-2 flex items-center justify-between text-[11px] text-slate-300">
        <div className="flex items-center gap-1.5">
          <Lock className="w-3 h-3 text-emerald-400" />
          <span>256-Bit SSL Secured</span>
        </div>
        <span className="font-mono text-[10px]">PCI-DSS v4</span>
      </div>
    </aside>
  );
};

export default Sidebar;
