import React, { useEffect, useState } from 'react';
import {
  FileText,
  Download,
  Search,
  ExternalLink,
  ShieldCheck,
  Clock,
  RefreshCw,
  FolderOpen
} from 'lucide-react';
import { getReports, getDownloadUrl } from '../services/api';
import RiskBadge from '../components/RiskBadge';

export const ReportsPage = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchReportsList = async () => {
    setLoading(true);
    try {
      const data = await getReports();
      setReports(data.reports || []);
    } catch (err) {
      console.error('Error fetching reports:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReportsList();
  }, []);

  const filteredReports = reports.filter((r) => {
    if (!search) return true;
    const s = search.toLowerCase();
    return (
      (r.case_id || '').toLowerCase().includes(s) ||
      (r.transaction_id || '').toLowerCase().includes(s) ||
      (r.investigator || '').toLowerCase().includes(s)
    );
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-tight">Forensic PDF Investigation Dossiers</h1>
          <p className="text-xs text-slate-400">
            Archived compliance reports, SHAP risk attributions, and legal audit trails
          </p>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search Case / TXN ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <button
            onClick={fetchReportsList}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-full py-16 text-center text-slate-500">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
            <span className="text-xs">Loading case archive...</span>
          </div>
        ) : filteredReports.length === 0 ? (
          <div className="col-span-full py-16 text-center text-slate-500 p-8 rounded-2xl bg-slate-900/60 border border-slate-800">
            <FolderOpen className="w-10 h-10 mx-auto mb-3 opacity-40 text-slate-400" />
            <p className="text-sm font-semibold text-slate-300">No Forensic Dossiers Found</p>
            <p className="text-xs text-slate-500 mt-1">
              Generate a dossier from the Simulator or Explorer to view archived cases.
            </p>
          </div>
        ) : (
          filteredReports.map((rep) => (
            <div
              key={rep.case_id}
              className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between space-y-4"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-1.5">
                    <FileText className="w-4 h-4 text-blue-400" />
                    <span className="font-mono font-bold text-xs text-white">{rep.case_id}</span>
                  </div>
                  <RiskBadge level={rep.risk_level} score={rep.risk_score} size="sm" />
                </div>

                <div className="space-y-1.5 text-xs text-slate-300">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Transaction ID:</span>
                    <span className="font-mono text-slate-200">{rep.transaction_id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Amount:</span>
                    <span className="font-mono font-bold text-emerald-400">
                      ${typeof rep.amount === 'number' ? rep.amount.toFixed(2) : rep.amount} USD
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Investigator:</span>
                    <span className="text-slate-300">{rep.investigator || 'Lead Fraud Analyst'}</span>
                  </div>
                  <div className="flex justify-between text-[11px] text-slate-500 pt-1">
                    <span>Generated:</span>
                    <span>{new Date(rep.created_at || Date.now()).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              <a
                href={getDownloadUrl(rep.case_id)}
                target="_blank"
                rel="noreferrer"
                className="w-full flex items-center justify-center gap-2 py-2 rounded-xl bg-blue-600/20 border border-blue-500/40 hover:bg-blue-600/30 text-blue-300 text-xs font-semibold transition"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download PDF Dossier</span>
              </a>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ReportsPage;
