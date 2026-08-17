import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import { getAlerts } from './services/api';
import Sidebar from './components/Sidebar';
import TransactionSimulatorModal from './components/TransactionSimulatorModal';
import DashboardOverview from './pages/DashboardOverview';
import TransactionExplorer from './pages/TransactionExplorer';
import FraudAnalytics from './pages/FraudAnalytics';
import ShapExplainability from './pages/ShapExplainability';
import AlertsCenter from './pages/AlertsCenter';
import ReportsPage from './pages/ReportsPage';
import LoginScreen from './components/LoginScreen';


export const App = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isSimulatorOpen, setIsSimulatorOpen] = useState(false);
  const [activeAlertsCount, setActiveAlertsCount] = useState(0);
  const [analyst, setAnalyst] = useState(() => {
    try { return JSON.parse(localStorage.getItem('sentinel_analyst')); } catch { return null; }
  });

  // Fetch real-time alerts count on mount and whenever analyst changes
  useEffect(() => {
    const fetchAlertsCount = async () => {
      try {
        const data = await getAlerts({ limit: 0 }); // request count only
        setActiveAlertsCount(data.count);
      } catch (e) {
        console.error('Failed to fetch alerts count', e);
      }
    };
    if (analyst) {
      fetchAlertsCount();
    }
    const interval = setInterval(fetchAlertsCount, 30000);
    return () => clearInterval(interval);
  }, [analyst]);


  if (!analyst) return <LoginScreen onLogin={(profile) => { localStorage.setItem('sentinel_analyst', JSON.stringify(profile)); setAnalyst(profile); }} />;

  return (
    <div className="min-h-screen bg-[#0a0f1d] text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar
        onOpenSimulator={() => setIsSimulatorOpen(true)}
        activeAlertsCount={activeAlertsCount}
        analyst={analyst}
        onLogout={() => { localStorage.removeItem('sentinel_analyst'); setAnalyst(null); }}
      />

      {/* Main Layout Body */}
      <div className="flex flex-1">
        {/* Left Navigation Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          alertCount={activeAlertsCount}
        />

        {/* Content Viewport */}
        <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full overflow-y-auto">
          {activeTab === 'overview' && (
            <DashboardOverview
              key={analyst?.email}
              onOpenSimulator={() => setIsSimulatorOpen(true)}
              onSelectAlert={() => setActiveTab('alerts')}
            />
          )}

          {activeTab === 'explorer' && (
            <TransactionExplorer
              key={analyst?.email}
              onOpenSimulator={() => setIsSimulatorOpen(true)}
            />
          )}

          {activeTab === 'analytics' && <FraudAnalytics key={analyst?.email} />}

          {activeTab === 'shap' && <ShapExplainability key={analyst?.email} />}

          {activeTab === 'alerts' && (
            <AlertsCenter
              key={analyst?.email}
              onAlertStatusChanged={(previousStatus, nextStatus) => {
                const wasActive = ['OPEN', 'INVESTIGATING'].includes(previousStatus);
                const isActive = ['OPEN', 'INVESTIGATING'].includes(nextStatus);
                if (wasActive && !isActive) setActiveAlertsCount((count) => Math.max(0, count - 1));
                if (!wasActive && isActive) setActiveAlertsCount((count) => count + 1);
              }}
            />
          )}

          {activeTab === 'reports' && <ReportsPage key={analyst?.email} />}
        </main>
      </div>

      {/* Live Transaction AI Simulator Modal */}
      <TransactionSimulatorModal
        isOpen={isSimulatorOpen}
        onClose={() => setIsSimulatorOpen(false)}
        onTransactionCreated={(response) => {
          if (response.final_risk_score >= 60) setActiveAlertsCount((prev) => prev + 1);
        }}
      />
    </div>
  );
};

export default App;
