/**
 * Sentinel API Service Client
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getDashboardStats = async () => {
  const res = await api.get('/api/v1/dashboard/stats');
  return res.data;
};

export const getTransactions = async (params = {}) => {
  const res = await api.get('/api/v1/transactions', { params });
  return res.data;
};

export const getSampleTransaction = async (type = 'fraud') => {
  const res = await api.get(`/api/v1/transactions/sample/${type}`);
  return res.data;
};

export const predictTransaction = async (transactionData) => {
  const res = await api.post('/api/v1/predict', transactionData);
  return res.data;
};

export const scanAnomalies = async (transactions) => {
  const res = await api.post('/api/v1/anomaly', { transactions });
  return res.data;
};

export const getAlerts = async (params = {}) => {
  const res = await api.get('/api/v1/alerts', { params });
  return res.data;
};

export const updateAlertStatus = async (alertId, payload) => {
  const res = await api.patch(`/api/v1/alerts/${alertId}`, payload);
  return res.data;
};

export const getReports = async () => {
  const res = await api.get('/api/v1/reports');
  return res.data;
};

export const generateReport = async (payload) => {
  const res = await api.post('/api/v1/report', payload);
  return res.data;
};

export const getDownloadUrl = (caseId) => {
  return `${API_BASE_URL}/api/v1/reports/${caseId}/download`;
};

export default api;
