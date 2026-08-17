import React, { useState } from 'react';
import {
  BrainCircuit,
  HelpCircle,
  TrendingUp,
  TrendingDown,
  Sparkles,
  Info,
  Layers,
  SlidersHorizontal
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  ReferenceLine, Cell
} from 'recharts';

export const ShapExplainability = () => {
  const [selectedScenario, setSelectedScenario] = useState('fraud_dossier');

  // Interactive waterfall attributions
  const scenarios = {
    fraud_dossier: {
      title: 'High-Risk Account Takeover & Rapid Cashout',
      baseValue: 0.0017,
      predictedProb: 0.942,
      riskLevel: 'CRITICAL',
      reasonCodes: [
        'Critical latent identity deviation (V14 = -6.42, SHAP impact +0.384)',
        'Unusual account access pattern (V12 = -4.89, SHAP impact +0.291)',
        'Extreme transaction velocity surge (V4 = +3.99, SHAP impact +0.185)',
        'Off-hours night execution window (Is_Night = 1, SHAP impact +0.089)',
      ],
      attributions: [
        { feature: 'V14 (Identity / Risk)', shap: 0.384, raw: -6.42, dir: 'POS' },
        { feature: 'V12 (Account Delta)', shap: 0.291, raw: -4.89, dir: 'POS' },
        { feature: 'V4 (Velocity Proxy)', shap: 0.185, raw: 3.99, dir: 'POS' },
        { feature: 'V10 (Behavioral Latent)', shap: 0.125, raw: -3.22, dir: 'POS' },
        { feature: 'Is_Night_Transaction', shap: 0.089, raw: 1, dir: 'POS' },
        { feature: 'Amount_Deviation_Z', shap: 0.045, raw: 2.85, dir: 'POS' },
        { feature: 'V8 (Card Type)', shap: -0.052, raw: 1.56, dir: 'NEG' },
        { feature: 'V1 (Device Token)', shap: -0.126, raw: -2.31, dir: 'NEG' },
      ],
    },
    legit_dossier: {
      title: 'Normal Grocery Store In-Store Purchase',
      baseValue: 0.0017,
      predictedProb: 0.002,
      riskLevel: 'LOW',
      reasonCodes: [
        'Normal latent identity signature (V14 = -0.31, SHAP impact -0.142)',
        'Standard daytime operational window (Hour = 14.5, SHAP impact -0.085)',
        'Consistent transaction amount with historical pattern ($42.50)',
      ],
      attributions: [
        { feature: 'V14 (Identity / Risk)', shap: -0.142, raw: -0.31, dir: 'NEG' },
        { feature: 'V12 (Account Delta)', shap: -0.098, raw: -0.62, dir: 'NEG' },
        { feature: 'Is_Night_Transaction', shap: -0.085, raw: 0, dir: 'NEG' },
        { feature: 'V10 (Behavioral Latent)', shap: -0.064, raw: 0.09, dir: 'NEG' },
        { feature: 'Amount_Log', shap: -0.038, raw: 3.75, dir: 'NEG' },
        { feature: 'V4 (Velocity Proxy)', shap: 0.021, raw: 1.38, dir: 'POS' },
      ],
    },
  };

  const activeData = scenarios[selectedScenario];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-extrabold text-white tracking-tight">
          Explainable AI & Forensic SHAP Attribution
        </h1>
        <p className="text-xs text-slate-400">
          Shapley Additive exPlanations (SHAP) quantifying exact feature-level credit and blame for every transaction
        </p>
      </div>

      {/* Scenario Selector Tabs */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setSelectedScenario('fraud_dossier')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            selectedScenario === 'fraud_dossier'
              ? 'bg-red-600/20 text-red-300 border border-red-500/40 shadow-sm'
              : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
          }`}
        >
          Scenario A: Critical Fraud Transaction
        </button>
        <button
          onClick={() => setSelectedScenario('legit_dossier')}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
            selectedScenario === 'legit_dossier'
              ? 'bg-emerald-600/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
              : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
          }`}
        >
          Scenario B: Legitimate Transaction
        </button>
      </div>

      {/* Main Waterfall Chart Card */}
      <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
          <div>
            <h2 className="text-sm font-bold text-white">{activeData.title}</h2>
            <div className="flex items-center gap-3 text-xs text-slate-400 mt-0.5">
              <span>Base Rate E[f(x)]: <b>0.17%</b></span>
              <span>→</span>
              <span>
                Final Model Prediction f(x):{' '}
                <b className={activeData.predictedProb > 0.5 ? 'text-red-400' : 'text-emerald-400'}>
                  {(activeData.predictedProb * 100).toFixed(1)}%
                </b>
              </span>
            </div>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-xs font-bold ${
              activeData.riskLevel === 'CRITICAL'
                ? 'bg-red-950 text-red-400 border border-red-800'
                : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
            }`}
          >
            {activeData.riskLevel} RISK TIER
          </span>
        </div>

        {/* Waterfall Bar Chart */}
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={activeData.attributions} layout="vertical" margin={{ left: 50, right: 30 }}>
              <XAxis type="number" stroke="#64748b" fontSize={11} domain={[-0.2, 0.45]} />
              <YAxis dataKey="feature" type="category" stroke="#cbd5e1" fontSize={11} width={180} />
              <Tooltip
                content={({ payload }) => {
                  if (payload && payload.length > 0) {
                    const d = payload[0].payload;
                    return (
                      <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs shadow-xl space-y-1">
                        <div className="font-bold text-white">{d.feature}</div>
                        <div className="text-slate-400">Observed Value: <span className="text-white font-mono">{d.raw}</span></div>
                        <div className="text-slate-400">SHAP Impact (Δ): <span className={d.shap > 0 ? 'text-red-400 font-mono font-bold' : 'text-emerald-400 font-mono font-bold'}>{d.shap > 0 ? `+${d.shap}` : d.shap}</span></div>
                        <div className="text-[10px] text-slate-500">{d.shap > 0 ? 'Pushes prediction toward FRAUD' : 'Pushes prediction toward LEGITIMATE'}</div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <ReferenceLine x={0} stroke="#475569" strokeWidth={1.5} />
              <Bar dataKey="shap" radius={[4, 4, 4, 4]}>
                {activeData.attributions.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.shap > 0 ? '#ef4444' : '#10b981'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="flex items-center justify-center gap-6 text-xs text-slate-400 pt-2 border-t border-slate-800/60">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-red-500" />
            <span>Positive SHAP (Increases Fraud Probability)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-emerald-500" />
            <span>Negative SHAP (Decreases Fraud Probability)</span>
          </div>
        </div>
      </div>

      {/* Human-Readable Reason Codes Card */}
      <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-blue-400" />
          <h3 className="text-sm font-bold text-white">Automated Forensic Reason Codes for Investigators</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {activeData.reasonCodes.map((rc, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-start gap-2.5 text-xs text-slate-300">
              <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 font-bold flex items-center justify-center shrink-0 text-[10px]">
                {idx + 1}
              </span>
              <span>{rc}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ShapExplainability;
