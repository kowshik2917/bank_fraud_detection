import React, { useEffect, useState } from 'react';
import { Search, Filter, RefreshCw, FileText, ChevronRight, Eye, Sparkles } from 'lucide-react';
import { getTransactions, generateReport, getDownloadUrl, logSearch } from '../services/api';
import RiskBadge from '../components/RiskBadge';

export const TransactionExplorer = ({ onOpenSimulator }) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedRisk, setSelectedRisk] = useState('ALL');
  const [selectedTxn, setSelectedTxn] = useState(null);
  const [pdfGenerating, setPdfGenerating] = useState(false);

  const fetchTxns = async () => {
    setLoading(true);
    try {
      const data = await getTransactions({
        limit: 100,
        risk_level: selectedRisk === 'ALL' ? undefined : selectedRisk,
        search: search || undefined,
      });
      setTransactions(data.transactions || []);
      if (data.transactions && data.transactions.length > 0 && !selectedTxn) {
        setSelectedTxn(data.transactions[0]);
      }
    } catch (err) {
      console.error('Error loading transactions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTxns();
  }, [selectedRisk]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    // Log search to MongoDB
    const analyst = (() => { try { return JSON.parse(localStorage.getItem('sentinel_analyst')); } catch { return null; } })();
    if (analyst && search.trim()) {
      logSearch({ analyst_email: analyst.email, query: search.trim() });
    }
    fetchTxns();
  };

  const handleGeneratePDF = async (txn) => {
    try {
      setPdfGenerating(true);
      const res = await generateReport({
        case_id: `CASE-${txn.transaction_id}`,
        transaction_id: txn.transaction_id,
        amount: txn.amount,
        fraud_probability: txn.fraud_probability || 0.1,
        anomaly_score: txn.anomaly_score || 10.0,
        risk_score: txn.final_risk_score || 15.0,
        risk_level: txn.risk_level || 'LOW',
        investigator_notes: `Explorer review: Action recommendation ${txn.action || 'APPROVE'}`,
      });
      window.open(getDownloadUrl(res.case_id), '_blank');
    } catch (err) {
      console.error('Error generating PDF:', err);
    } finally {
      setPdfGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-tight">Transaction Explorer</h1>
          <p className="text-xs text-slate-400">
            Real-time audit log of incoming payment vectors and risk telemetry
          </p>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <form onSubmit={handleSearchSubmit} className="relative flex-1 md:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search TXN / Cardholder..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </form>

          <button
            onClick={fetchTxns}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>

          <button
            onClick={onOpenSimulator}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Simulate</span>
          </button>
        </div>
      </div>

      {/* Risk Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((tier) => (
          <button
            key={tier}
            onClick={() => setSelectedRisk(tier)}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
              selectedRisk === tier
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            {tier}
          </button>
        ))}
      </div>

      {/* Main Table + Inspector Drawer Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Transactions Table */}
        <div className="lg:col-span-2 rounded-2xl bg-slate-900/80 border border-slate-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-950/40 text-slate-400 uppercase text-[10px]">
                  <th className="py-3 px-4 font-semibold">Transaction ID</th>
                  <th className="py-3 px-4 font-semibold">Amount</th>
                  <th className="py-3 px-4 font-semibold">Risk Level</th>
                  <th className="py-3 px-4 font-semibold">Fraud Prob</th>
                  <th className="py-3 px-4 font-semibold">Action</th>
                  <th className="py-3 px-4 font-semibold text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-slate-500">
                      <div className="flex justify-center items-center gap-2">
                        <RefreshCw className="w-4 h-4 animate-spin text-blue-500" />
                        <span>Loading transactions...</span>
                      </div>
                    </td>
                  </tr>
                ) : transactions.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-slate-500">
                      No transactions matched the active filter criteria.
                    </td>
                  </tr>
                ) : (
                  transactions.map((t) => {
                    const isSelected = selectedTxn?.transaction_id === t.transaction_id;
                    return (
                      <tr
                        key={t.transaction_id}
                        onClick={() => setSelectedTxn(t)}
                        className={`cursor-pointer transition ${
                          isSelected
                            ? 'bg-blue-600/10 border-l-2 border-blue-500'
                            : 'hover:bg-slate-800/40'
                        }`}
                      >
                        <td className="py-3 px-4 font-mono text-slate-200">
                          <div>{t.transaction_id}</div>
                          <div className="text-[10px] text-slate-500">{t.cardholder_id || 'CUST-39210'}</div>
                        </td>
                        <td className="py-3 px-4 font-bold text-white font-mono">
                          ${typeof t.amount === 'number' ? t.amount.toFixed(2) : t.amount}
                        </td>
                        <td className="py-3 px-4">
                          <RiskBadge level={t.risk_level} score={t.final_risk_score} size="sm" />
                        </td>
                        <td className="py-3 px-4 font-mono font-semibold text-slate-300">
                          {((t.fraud_probability || 0.05) * 100).toFixed(1)}%
                        </td>
                        <td className="py-3 px-4">
                          <span className="text-[11px] font-mono text-slate-400">{t.action || 'APPROVE'}</span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <ChevronRight className="w-4 h-4 text-slate-500 inline" />
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Transaction Inspector Drawer */}
        <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-5 flex flex-col justify-between">
          {selectedTxn ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div>
                  <span className="text-[10px] font-bold text-slate-300 uppercase">Transaction Detail</span>
                  <h3 className="text-sm font-mono font-bold text-white">{selectedTxn.transaction_id}</h3>
                </div>
                <RiskBadge level={selectedTxn.risk_level} score={selectedTxn.final_risk_score} size="md" />
              </div>

              {/* Core Attributes */}
              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-800/40">
                  <span className="text-slate-400">Cardholder:</span>
                  <span className="font-mono text-slate-200">{selectedTxn.cardholder_id || 'CUST-84920'}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/40">
                  <span className="text-slate-400">Amount:</span>
                  <span className="font-mono font-bold text-emerald-400">
                    ${typeof selectedTxn.amount === 'number' ? selectedTxn.amount.toFixed(2) : selectedTxn.amount} USD
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/40">
                  <span className="text-slate-400">XGBoost Prob:</span>
                  <span className="font-mono text-red-400 font-bold">
                    {((selectedTxn.fraud_probability || 0.05) * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/40">
                  <span className="text-slate-400">Anomaly Index:</span>
                  <span className="font-mono text-purple-400 font-bold">
                    {selectedTxn.anomaly_score || 12.4} / 100
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-800/40">
                  <span className="text-slate-400">Recommended Action:</span>
                  <span className="font-semibold text-white">{selectedTxn.action || 'APPROVE'}</span>
                </div>
              </div>

              {/* Latent PCA Vector Samples */}
              {selectedTxn.features && (
                <div>
                  <h4 className="text-[11px] font-semibold text-slate-300 mb-2">Key PCA Latent Vectors</h4>
                  <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                    {['V14', 'V12', 'V10', 'V17', 'V4', 'V11'].map((k) => (
                      <div key={k} className="p-1.5 rounded bg-slate-950/60 border border-slate-800 flex justify-between">
                        <span className="text-slate-400">{k}:</span>
                        <span className={selectedTxn.features[k] < -2 || selectedTxn.features[k] > 2 ? 'text-red-400 font-bold' : 'text-slate-300'}>
                          {selectedTxn.features[k]?.toFixed(3) || '0.000'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Generate PDF Button */}
              <div className="pt-2">
                <button
                  onClick={() => handleGeneratePDF(selectedTxn)}
                  disabled={pdfGenerating}
                  className="w-full flex items-center justify-center gap-2 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs transition shadow-md"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>{pdfGenerating ? 'Generating Forensic Dossier...' : 'Export PDF Case Dossier'}</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-slate-500 text-xs">
              <Eye className="w-8 h-8 mb-2 opacity-40" />
              <span>Select any transaction to inspect AI telemetry</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TransactionExplorer;
