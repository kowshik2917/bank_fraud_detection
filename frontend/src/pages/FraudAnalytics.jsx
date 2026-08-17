import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  Award,
  Layers,
  BarChart3,
  CheckCircle2,
  Sliders,
  Scale
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid, Legend
} from 'recharts';
import { getDashboardStats } from '../services/api';

export const FraudAnalytics = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getDashboardStats();
        setStats(data);
      } catch (err) {
        console.error('Error fetching analytics:', err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const featureImportanceData = [
    { feature: 'V14 (Identity / Risk)', importance: 0.284, type: 'Latent Vector' },
    { feature: 'V10 (Behavioral Shift)', importance: 0.192, type: 'Latent Vector' },
    { feature: 'V12 (Account Delta)', importance: 0.165, type: 'Latent Vector' },
    { feature: 'V17 (Card Usage Mode)', importance: 0.118, type: 'Latent Vector' },
    { feature: 'Amount_Deviation_Z', importance: 0.082, type: 'Engineered Domain' },
    { feature: 'V4 (Velocity Component)', importance: 0.054, type: 'Latent Vector' },
    { feature: 'Risk_Indicator_Index', importance: 0.041, type: 'Engineered Domain' },
    { feature: 'Is_Night_Transaction', importance: 0.035, type: 'Temporal Cyclical' },
    { feature: 'V_Extreme_Count', importance: 0.029, type: 'Anomaly Index' },
  ];

  const prCurveData = [
    { recall: 0.0, precision: 1.0 },
    { recall: 0.2, precision: 0.98 },
    { recall: 0.4, precision: 0.96 },
    { recall: 0.6, precision: 0.92 },
    { recall: 0.75, precision: 0.89 },
    { recall: 0.84, precision: 0.85 },
    { recall: 0.90, precision: 0.72 },
    { recall: 0.95, precision: 0.48 },
    { recall: 1.0, precision: 0.18 },
  ];

  const rocCurveData = [
    { fpr: 0.0, tpr: 0.0 },
    { fpr: 0.0001, tpr: 0.65 },
    { fpr: 0.0005, tpr: 0.82 },
    { fpr: 0.001, tpr: 0.89 },
    { fpr: 0.005, tpr: 0.94 },
    { fpr: 0.01, tpr: 0.97 },
    { fpr: 0.05, tpr: 0.99 },
    { fpr: 1.0, tpr: 1.0 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-extrabold text-white tracking-tight">Fraud Model Analytics & Benchmarks</h1>
        <p className="text-xs text-slate-400">
          Supervised classifier evaluations, Precision-Recall curves, and feature importance rankings
        </p>
      </div>

      {/* Model Benchmark Leaderboard */}
      <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
        <div className="flex items-center gap-2 mb-4">
          <Award className="w-4 h-4 text-yellow-400" />
          <h2 className="text-sm font-bold text-white">Algorithm Benchmark Leaderboard</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/40 text-slate-400 uppercase text-[10px]">
                <th className="py-3 px-4 font-semibold">Algorithm</th>
                <th className="py-3 px-4 font-semibold">PR-AUC (Target)</th>
                <th className="py-3 px-4 font-semibold">ROC-AUC</th>
                <th className="py-3 px-4 font-semibold">Precision</th>
                <th className="py-3 px-4 font-semibold">Recall</th>
                <th className="py-3 px-4 font-semibold">F1-Score</th>
                <th className="py-3 px-4 font-semibold text-right">Production Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {(stats?.model_leaderboard || []).map((m, idx) => {
                const isChampion = idx === 0;
                return (
                  <tr key={m.Model} className={`hover:bg-slate-800/40 transition ${isChampion ? 'bg-blue-600/5 font-medium' : ''}`}>
                    <td className="py-3 px-4 font-bold text-white flex items-center gap-2">
                      {isChampion && <span className="px-1.5 py-0.5 rounded text-[9px] font-extrabold bg-blue-500/20 text-blue-400 border border-blue-500/40">CHAMPION</span>}
                      <span>{m.Model}</span>
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-blue-400">{m.PR_AUC}</td>
                    <td className="py-3 px-4 font-mono text-slate-300">{m.ROC_AUC}</td>
                    <td className="py-3 px-4 font-mono text-emerald-400">{m.Precision}</td>
                    <td className="py-3 px-4 font-mono text-red-400">{m.Recall}</td>
                    <td className="py-3 px-4 font-mono text-purple-400">{m.F1_Score}</td>
                    <td className="py-3 px-4 text-right">
                      {isChampion ? (
                        <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-800">
                          Active In Production
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full text-[10px] bg-slate-800 text-slate-400">
                          Standby Candidate
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Curves Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Precision-Recall Curve */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="mb-4">
            <h3 className="text-sm font-bold text-white">Precision-Recall Curve (PR-AUC = 0.884)</h3>
            <p className="text-xs text-slate-400">Essential metric for extreme class imbalance (0.17% fraud prevalence)</p>
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={prCurveData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="recall" stroke="#64748b" fontSize={11} label={{ value: 'Recall', position: 'insideBottomRight', offset: -5, fill: '#64748b', fontSize: 10 }} />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 1.05]} label={{ value: 'Precision', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                <Line type="monotone" dataKey="precision" stroke="#10b981" strokeWidth={2.5} dot={false} name="Precision" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* ROC Curve */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="mb-4">
            <h3 className="text-sm font-bold text-white">Receiver Operating Characteristic (ROC-AUC = 0.981)</h3>
            <p className="text-xs text-slate-400">True Positive Rate vs False Positive Rate across all decision cutoffs</p>
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={rocCurveData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="fpr" stroke="#64748b" fontSize={11} label={{ value: 'False Positive Rate', position: 'insideBottomRight', offset: -5, fill: '#64748b', fontSize: 10 }} />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 1.05]} label={{ value: 'True Positive Rate', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                <Line type="monotone" dataKey="tpr" stroke="#3b82f6" strokeWidth={2.5} dot={false} name="TPR" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Feature Importance Bar Chart */}
      <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
        <div className="mb-4">
          <h3 className="text-sm font-bold text-white">Top 9 Predictive Features (MDI / Gain Importance)</h3>
          <p className="text-xs text-slate-400">Relative contribution weights in the XGBoost decision ensemble</p>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={featureImportanceData} layout="vertical" margin={{ left: 40, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" horizontal={false} />
              <XAxis type="number" stroke="#64748b" fontSize={11} />
              <YAxis dataKey="feature" type="category" stroke="#cbd5e1" fontSize={11} width={170} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
              <Bar dataKey="importance" fill="#3b82f6" radius={[0, 4, 4, 0]} name="Importance Score" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Imbalance Strategy Analysis Card */}
      <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
        <div className="flex items-center gap-2 mb-3">
          <Scale className="w-4 h-4 text-purple-400" />
          <h3 className="text-sm font-bold text-white">Imbalance Strategy Benchmarks (SMOTE vs ADASYN vs Weighted Loss)</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="font-bold text-emerald-400 mb-1">1. Cost-Sensitive Boosting (Recommended)</div>
            <p className="text-slate-400 leading-relaxed">
              Maintains true sample density without synthetic artifacts. Delivers the lowest False Positive Rate in high-frequency production transaction streams.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="font-bold text-blue-400 mb-1">2. Targeted SMOTE (10% Ratio)</div>
            <p className="text-slate-400 leading-relaxed">
              Interpolates synthetic samples between minority k-nearest neighbors. Elevates recall on small cohorts but slightly increases operational false alerts.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="font-bold text-yellow-400 mb-1">3. ADASYN (Boundary Adaptive)</div>
            <p className="text-slate-400 leading-relaxed">
              Focuses generation around difficult decision boundaries. Effective for overlapping clusters, though sensitive to outliers.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FraudAnalytics;
