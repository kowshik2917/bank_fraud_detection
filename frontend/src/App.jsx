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


export const App = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isSimulatorOpen, setIsSimulatorOpen] = useState(false);
  const [activeAlertsCount, setActiveAlertsCount] = useState(0);

  // Fetch real-time alerts count on mount and refresh every 30 seconds
  useEffect(() => {
    const fetchAlertsCount = async () => {
      try {
        const data = await getAlerts({ limit: 0 }); // request count only
        setActiveAlertsCount(data.count);
      } catch (e) {
        console.error('Failed to fetch alerts count', e);
      }
    };
    fetchAlertsCount();
    const interval = setInterval(fetchAlertsCount, 30000);
    return () => clearInterval(interval);
  }, []);


  return (
    <div className="min-h-screen bg-[#0a0f1d] text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar
        onOpenSimulator={() => setIsSimulatorOpen(true)}
        activeAlertsCount={activeAlertsCount}
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
              onOpenSimulator={() => setIsSimulatorOpen(true)}
              onSelectAlert={() => setActiveTab('alerts')}
            />
          )}

          {activeTab === 'explorer' && (
            <TransactionExplorer
              onOpenSimulator={() => setIsSimulatorOpen(true)}
            />
          )}

          {activeTab === 'analytics' && <FraudAnalytics />}

          {activeTab === 'shap' && <ShapExplainability />}

          {activeTab === 'alerts' && <AlertsCenter />}

          {activeTab === 'reports' && <ReportsPage />}
        </main>
      </div>

      {/* Live Transaction AI Simulator Modal */}
      <TransactionSimulatorModal
        isOpen={isSimulatorOpen}
        onClose={() => setIsSimulatorOpen(false)}
        onTransactionCreated={() => {
          setActiveAlertsCount((prev) => prev + 1);
        }}
      />
    </div>
  );
};

export default App;
