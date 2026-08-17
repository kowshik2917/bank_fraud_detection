import React, { useState, useEffect } from 'react';
import { X, Sparkles, AlertOctagon, CheckCircle2, FileDown, ArrowRight, ShieldCheck, RefreshCw, Layers } from 'lucide-react';
import { predictTransaction, getSampleTransaction, generateReport, getDownloadUrl } from '../services/api';
import RiskBadge from './RiskBadge';

export const TransactionSimulatorModal = ({ isOpen, onClose, onTransactionCreated }) => {
  const [loading, setLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [formData, setFormData] = useState({
    Amount: 149.50,
    Time: 3600.0,
    cardholder_id: 'CUST-84920',
    merchant_name: 'Electronics Direct Online',
    V1: -1.3598, V2: -0.0727, V3: 2.5363, V4: 1.3781, V5: -0.3383,
    V6: 0.4623, V7: 0.2395, V8: 0.0986, V9: 0.3637, V10: 0.0907,
    V11: -0.5516, V12: -0.6178, V13: 0.9913, V14: -0.3111, V15: 1.4681,
    V16: -0.4704, V17: 0.2079, V18: 0.0257, V19: 0.4039, V20: 0.2514,
    V21: -0.0183, V22: 0.2778, V23: -0.1104, V24: 0.0669, V25: 0.1285,
    V26: -0.1891, V27: 0.1335, V28: -0.0210
  });

  // Always clear previous result when opening the simulator modal
  useEffect(() => {
    if (isOpen) {
      setResult(null);
      setErrorMsg('');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleClose = () => {
    setResult(null);
    setErrorMsg('');
    onClose();
  };

  const updateField = (key, value) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
    if (result) setResult(null);
    if (errorMsg) setErrorMsg('');
  };

  const handleLoadPreset = async (type) => {
    try {
      setLoading(true);
      const sample = await getSampleTransaction(type);
      setFormData((prev) => ({
        ...prev,
        ...sample,
      }));
      setResult(null);
      setErrorMsg('');
    } catch (err) {
      console.error('Error loading preset:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    try {
      setLoading(true);
      const response = await predictTransaction(formData);
      setResult(response);
      if (onTransactionCreated) {
        onTransactionCreated(response);
      }
    } catch (err) {
      console.error('Prediction failed:', err);
      setErrorMsg(err?.response?.data?.detail || 'Scoring failed. Please check the backend connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!result) return;
    try {
      setReportLoading(true);
      const rep = await generateReport({
        case_id: `CASE-${result.transaction_id}`,
        transaction_id: result.transaction_id,
        amount: formData.Amount,
        fraud_probability: result.fraud_probability,
        anomaly_score: result.anomaly_score,
        risk_score: result.final_risk_score,
        risk_level: result.risk_level,
        investigator_notes: `Real-time simulator evaluation. Triggered actions: ${result.recommended_action}`,
        reason_codes: result.reason_codes,
        top_risk_drivers: result.top_risk_drivers,
      });
      window.open(getDownloadUrl(rep.case_id), '_blank');
    } catch (err) {
      console.error('PDF generation error:', err);
    } finally {
      setReportLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm overflow-y-auto">
      <div className="bg-[#111827] border border-slate-700/80 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Interactive Fraud AI Simulator</h2>
              <p className="text-xs text-slate-400">Score transactions with XGBoost, Isolation Forest & SHAP</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleLoadPreset('legit')}
              className="px-3 py-1 text-xs rounded-lg bg-emerald-950/60 border border-emerald-800/80 text-emerald-300 hover:bg-emerald-900/60 transition"
            >
              Preset: Legitimate
            </button>
            <button
              onClick={() => handleLoadPreset('fraud')}
              className="px-3 py-1 text-xs rounded-lg bg-red-950/60 border border-red-800/80 text-red-300 hover:bg-red-900/60 transition"
            >
              Preset: High Fraud Risk
            </button>
            <button
              onClick={handleClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Primary Attributes */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Transaction Amount ($ USD)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.Amount}
                  onChange={(e) => updateField('Amount', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white font-mono text-sm focus:border-blue-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Time (Elapsed Seconds)
                </label>
                <input
                  type="number"
                  value={formData.Time}
                  onChange={(e) => updateField('Time', parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white font-mono text-sm focus:border-blue-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Merchant Description
                </label>
                <input
                  type="text"
                  value={formData.merchant_name}
                  onChange={(e) => updateField('merchant_name', e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white text-sm focus:border-blue-500 focus:outline-none"
                />
              </div>
            </div>

            {/* Key PCA Latent Drivers */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-300">
                  Critical Latent Vectors (Top Fraud Predictors: V14, V12, V10, V17, V4, V11)
                </span>
                <span className="text-[11px] text-slate-400">PCA Transformed Features</span>
              </div>
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2.5">
                {['V14', 'V12', 'V10', 'V17', 'V4', 'V11'].map((vKey) => (
                  <div key={vKey}>
                    <label className="block text-[11px] font-mono text-slate-400 mb-0.5">{vKey}</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData[vKey] ?? 0}
                      onChange={(e) => updateField(vKey, parseFloat(e.target.value) || 0)}
                      className="w-full px-2 py-1 rounded bg-slate-900/90 border border-slate-700 text-xs font-mono text-white focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Submit Action */}
            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={loading}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-lg shadow-blue-600/30 transition disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Scoring Transaction...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Run Multi-Factor AI Risk Scoring</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {errorMsg && (
            <div className="p-3.5 rounded-xl bg-red-950/60 border border-red-800/80 text-xs text-red-300">
              {errorMsg}
            </div>
          )}

          {/* AI Result Card */}
          {result && (
            <div className="mt-4 p-5 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-4 animate-fadeIn">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-slate-400">{result.transaction_id}</span>
                    <RiskBadge level={result.risk_level} score={result.final_risk_score} size="md" />
                  </div>
                  <h3 className="text-sm font-bold text-white mt-1">
                    Action: {result.recommended_action} — {result.action_description}
                  </h3>
                </div>

                <button
                  onClick={handleDownloadPDF}
                  disabled={reportLoading}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 hover:bg-indigo-600/30 text-xs font-medium transition"
                >
                  <FileDown className="w-3.5 h-3.5" />
                  <span>{reportLoading ? 'Generating PDF...' : 'Download Official PDF Dossier'}</span>
                </button>
              </div>

              {/* Diagnostic Scores Breakdown */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <div className="text-[11px] text-slate-400">Supervised XGBoost Prob</div>
                  <div className="text-lg font-bold text-white mt-0.5">
                    {(result.fraud_probability * 100).toFixed(1)}%
                  </div>
                  <div className="text-[10px] text-slate-300 mt-0.5">Weighted Weight: 65%</div>
                </div>

                <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <div className="text-[11px] text-slate-400">Isolation Forest Anomaly</div>
                  <div className="text-lg font-bold text-white mt-0.5">
                    {result.anomaly_score.toFixed(1)} / 100
                  </div>
                  <div className="text-[10px] text-slate-300 mt-0.5">Weighted Weight: 25%</div>
                </div>

                <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <div className="text-[11px] text-slate-400">Composite Risk Index</div>
                  <div className="text-lg font-bold text-white mt-0.5" style={{ color: result.color }}>
                    {result.final_risk_score} / 100
                  </div>
                  <div className="text-[10px] text-slate-300 mt-0.5">{result.risk_level} Severity Tier</div>
                </div>
              </div>

              {/* SHAP Reason Codes */}
              {result.reason_codes && result.reason_codes.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-slate-300 mb-1.5">
                    Top Forensic Reason Codes (SHAP Attribution)
                  </h4>
                  <ul className="space-y-1">
                    {result.reason_codes.map((rc, idx) => (
                      <li key={idx} className="text-xs text-slate-400 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-red-400 shrink-0" />
                        <span>{rc}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TransactionSimulatorModal;
