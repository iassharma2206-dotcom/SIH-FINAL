import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { MissionControlDashboard } from './screens/MissionControlDashboard';
import { LiveSimulationControl } from './screens/LiveSimulationControl';
import { OptimizationEngine } from './screens/OptimizationEngine';
import { QPSOImplementation } from './screens/QPSOImplementation';
import { SystemSettings } from './screens/SystemSettings';
import { ReportModal } from './components/ReportModal';
import { runOptimization } from './api/client';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');

  const [startLocation, setStartLocation] = useState<{ name: string; coords: [number, number] }>({
    name: 'Mumbai, India',
    coords: [19.0760, 72.8777]
  });

  const [qpsoParams, setQpsoParams] = useState({
    beta_start: 1.0,
    swarm_size: 30,
    max_iter: 300,
    plateau_window: 50
  });

  const [theme, setTheme] = useState<string>('dark');
  const [distanceUnit, setDistanceUnit] = useState<'km' | 'mi'>('km');

  useEffect(() => {
    const el = document.documentElement;
    // Clear all theme attributes first
    el.removeAttribute('data-theme-cosmic');
    el.removeAttribute('data-theme-cyberpunk');
    el.removeAttribute('data-theme-neonrain');

    if (theme === 'light') {
      el.setAttribute('data-theme', 'light');
    } else if (theme === 'cosmic') {
      el.setAttribute('data-theme', 'dark');
      el.setAttribute('data-theme-cosmic', 'true');
    } else if (theme === 'cyberpunk') {
      el.setAttribute('data-theme', 'dark');
      el.setAttribute('data-theme-cyberpunk', 'true');
    } else if (theme === 'neonrain') {
      el.setAttribute('data-theme', 'dark');
      el.setAttribute('data-theme-neonrain', 'true');
    } else {
      el.setAttribute('data-theme', 'dark');
    }
  }, [theme]);

  const [optimizationResult, setOptimizationResult] = useState<any>(null);
  const [globalReportModalOpen, setGlobalReportModalOpen] = useState<boolean>(false);

  const handleStartOptimizationFromNav = () => {
    setCurrentTab('live-simulation');
  };

  const handleOpenGlobalReport = async () => {
    if (!optimizationResult) {
      try {
        const res = await runOptimization({ preset: 'manhattan-core', qpso_params: qpsoParams });
        setOptimizationResult(res);
      } catch (err) {
        console.error("Auto-run for report failed:", err);
      }
    }
    setGlobalReportModalOpen(true);
  };

  return (
    <div className="min-h-screen flex flex-col justify-between" style={{ backgroundColor: 'var(--color-bg-primary)', color: 'var(--color-text-primary)' }}>
      <div>
        <Navbar
          currentTab={currentTab}
          onSelectTab={(tab) => setCurrentTab(tab)}
          onStartOptimization={handleStartOptimizationFromNav}
          onOpenReport={handleOpenGlobalReport}
        />

        <main>
          {currentTab === 'dashboard' && (
            <MissionControlDashboard
              optimizationResult={optimizationResult}
              startLocation={startLocation}
              onNavigateToSimulation={() => setCurrentTab('live-simulation')}
              onNavigateToEngine={() => setCurrentTab('optimization-engine')}
            />
          )}

          {currentTab === 'live-simulation' && (
            <LiveSimulationControl
              startLocation={startLocation}
              setStartLocation={setStartLocation}
              optimizationResult={optimizationResult}
              setOptimizationResult={setOptimizationResult}
              qpsoParams={qpsoParams}
              distanceUnit={distanceUnit}
            />
          )}

          {currentTab === 'optimization-engine' && (
            <OptimizationEngine
              qpsoParams={qpsoParams}
              setQpsoParams={setQpsoParams}
              onDeploy={() => setCurrentTab('live-simulation')}
            />
          )}

          {currentTab === 'qpso-implementation' && (
            <QPSOImplementation
              optimizationResult={optimizationResult}
              startLocation={startLocation}
              distanceUnit={distanceUnit}
            />
          )}

          {currentTab === 'system-settings' && (
            <SystemSettings
              theme={theme}
              setTheme={setTheme}
              distanceUnit={distanceUnit}
              setDistanceUnit={setDistanceUnit}
            />
          )}
        </main>
      </div>

      <ReportModal
        isOpen={globalReportModalOpen}
        onClose={() => setGlobalReportModalOpen(false)}
        runId={optimizationResult?.run_id}
        optimizationResult={optimizationResult}
        startLocation={startLocation}
        distanceUnit={distanceUnit}
      />


      <Footer
        onSelectTab={setCurrentTab}
        onOpenReport={() => setGlobalReportModalOpen(true)}
      />
    </div>
  );
}

export default App;
