import React, { useEffect, useState } from 'react';
import {
  BellRing,
  Filter,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileText,
  UserCheck,
  RefreshCw,
  MessageSquare,
  ShieldAlert
} from 'lucide-react';
import { getAlerts, updateAlertStatus, generateReport, getDownloadUrl } from '../services/api';
import RiskBadge from '../components/RiskBadge';

export const AlertsCenter = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [activeAlert, setActiveAlert] = useState(null);
  const [notes, setNotes] = useState('');
  const [updating, setUpdating] = useState(false);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const data = await getAlerts({
        status: selectedStatus === 'ALL' ? undefined : selectedStatus,
      });
      setAlerts(data.alerts || []);
      if (data.alerts && data.alerts.length > 0 && !activeAlert) {
        setActiveAlert(data.alerts[0]);
        setNotes(data.alerts[0].investigator_notes || '');
      }
    } catch (err) {
      console.error('Error fetching alerts:', err);
    } finally {
      setLoading(false);
    }
  };

    useEffect(() => {
      fetchAlerts();
      const interval = setInterval(fetchAlerts, 30000); // refresh every 30 seconds
      return () => clearInterval(interval);
    }, [selectedStatus]);

  const handleStatusChange = async (newStatus) => {
    if (!activeAlert) return;
    try {
      setUpdating(true);
      await updateAlertStatus(activeAlert.alert_id, {
        status: newStatus,
        investigator_notes: notes,
        investigator_name: 'Lead Fraud Analyst #8142',
      });
      // Update local state
      setActiveAlert({ ...activeAlert, status: newStatus, investigator_notes: notes });
      setAlerts((prev) =>
        prev.map((a) =>
          a.alert_id === activeAlert.alert_id
            ? { ...a, status: newStatus, investigator_notes: notes }
            : a
        )
      );
    } catch (err) {
      console.error('Error updating status:', err);
    } finally {
      setUpdating(false);
    }
  };

  const handleGeneratePDF = async () => {
    if (!activeAlert) return;
    try {
      const rep = await generateReport({
        case_id: `CASE-${activeAlert.alert_id}`,
        transaction_id: activeAlert.transaction_id,
        amount: activeAlert.amount || 500.0,
        fraud_probability: activeAlert.fraud_probability || 0.9,
        anomaly_score: 85.0,
        risk_score: activeAlert.risk_score || 88.0,
        risk_level: activeAlert.risk_level || 'HIGH',
        investigator_notes: notes || 'Alert triage dossier.',
        reason_codes: activeAlert.reason_codes || [],
      });
      window.open(getDownloadUrl(rep.case_id), '_blank');
    } catch (err) {
      console.error('PDF error:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-tight">Threat & Alert Triage Operations</h1>
          <p className="text-xs text-slate-400">
            Real-time suspicious transaction triage queue and investigation case lifecycle
          </p>
        </div>

        <div className="flex items-center gap-2">
          {['ALL', 'OPEN', 'INVESTIGATING', 'CONFIRMED_FRAUD', 'RESOLVED', 'FALSE_POSITIVE'].map((st) => (
            <button
              key={st}
              onClick={() => setSelectedStatus(st)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                selectedStatus === st
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alerts List */}
        <div className="lg:col-span-2 space-y-3">
          {loading ? (
            <div className="p-12 text-center text-slate-500 rounded-2xl bg-slate-900/80 border border-slate-800">
              <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-500" />
              <span className="text-xs">Loading alert queue...</span>
            </div>
          ) : alerts.length === 0 ? (
            <div className="p-12 text-center text-slate-500 rounded-2xl bg-slate-900/80 border border-slate-800 text-xs">
              No alerts found for the selected status filter.
            </div>
          ) : (
            alerts.map((alert) => {
              const isSelected = activeAlert?.alert_id === alert.alert_id;
              return (
                <div
                  key={alert.alert_id}
                  onClick={() => {
                    setActiveAlert(alert);
                    setNotes(alert.investigator_notes || '');
                  }}
                  className={`p-4 rounded-2xl border transition cursor-pointer ${
                    isSelected
                      ? 'bg-slate-900/95 border-blue-500 shadow-md ring-1 ring-blue-500/30'
                      : 'bg-slate-900/70 border-slate-800 hover:bg-slate-900/90'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3 mb-2">
                    <div className="flex items-center gap-2">
                      <ShieldAlert className="w-4 h-4 text-red-400" />
                      <span className="font-mono font-bold text-xs text-white">{alert.alert_id}</span>
                      <span className="text-xs text-slate-400">({alert.transaction_id})</span>
                    </div>
                    <RiskBadge level={alert.risk_level} score={alert.risk_score} size="sm" />
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-xs text-slate-300 my-2">
                    <div>
                      <span className="text-slate-500 block text-[10px]">Amount</span>
                      <span className="font-bold text-white font-mono">
                        ${typeof alert.amount === 'number' ? alert.amount.toFixed(2) : alert.amount}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">Fraud Prob</span>
                      <span className="font-bold text-red-400 font-mono">
                        {((alert.fraud_probability || 0.85) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500 block text-[10px]">Current Status</span>
                      <span className="font-semibold text-slate-200">{alert.status}</span>
                    </div>
                  </div>

                  {alert.reason_codes && alert.reason_codes.length > 0 && (
                    <div className="text-[11px] text-slate-400 bg-slate-950/40 p-2 rounded-lg border border-slate-800/60 mt-2">
                      {alert.reason_codes[0]}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Action Panel & Case File */}
        <div className="rounded-2xl bg-slate-900/90 border border-slate-800 p-5 flex flex-col justify-between space-y-4">
          {activeAlert ? (
            <div className="space-y-4">
              <div className="pb-3 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-bold text-slate-500 uppercase">Selected Alert Dossier</span>
                  <h3 className="text-sm font-bold text-white">{activeAlert.alert_id}</h3>
                </div>
                <RiskBadge level={activeAlert.risk_level} score={activeAlert.risk_score} size="md" />
              </div>

              {/* Triage Status Control Buttons */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-2">
                  Update Triage Status
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => handleStatusChange('INVESTIGATING')}
                    disabled={updating}
                    className="py-1.5 px-2 rounded-lg text-xs font-medium bg-blue-600/20 text-blue-300 border border-blue-500/30 hover:bg-blue-600/30 transition text-center"
                  >
                    Investigating
                  </button>
                  <button
                    onClick={() => handleStatusChange('CONFIRMED_FRAUD')}
                    disabled={updating}
                    className="py-1.5 px-2 rounded-lg text-xs font-medium bg-red-600/20 text-red-300 border border-red-500/30 hover:bg-red-600/30 transition text-center"
                  >
                    Confirm Fraud
                  </button>
                  <button
                    onClick={() => handleStatusChange('FALSE_POSITIVE')}
                    disabled={updating}
                    className="py-1.5 px-2 rounded-lg text-xs font-medium bg-yellow-600/20 text-yellow-300 border border-yellow-500/30 hover:bg-yellow-600/30 transition text-center"
                  >
                    False Positive
                  </button>
                  <button
                    onClick={() => handleStatusChange('RESOLVED')}
                    disabled={updating}
                    className="py-1.5 px-2 rounded-lg text-xs font-medium bg-emerald-600/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-600/30 transition text-center"
                  >
                    Resolve Alert
                  </button>
                </div>
              </div>

              {/* Notes Area */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Analyst Findings & Investigation Notes
                </label>
                <textarea
                  rows={4}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Record customer contact, merchant query, or authorization notes..."
                  className="w-full p-2.5 rounded-xl bg-slate-950 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              {/* Export PDF Button */}
              <button
                onClick={handleGeneratePDF}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs transition shadow-md"
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Generate Official PDF Investigation Dossier</span>
              </button>
            </div>
          ) : (
            <div className="text-center py-20 text-slate-500 text-xs">
              Select an alert from the queue to start triage
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AlertsCenter;
