import React, { useState } from 'react';
import { Play, RefreshCw, Layers, Truck, Clock, ShieldAlert, FileText, Download } from 'lucide-react';
import { RouteMap } from '../components/RouteMap';
import { LocationSearchInput } from '../components/LocationSearchInput';
import { ReportModal } from '../components/ReportModal';
import { runOptimization } from '../api/client';

interface LiveSimulationProps {
  startLocation: { name: string; coords: [number, number] };
  setStartLocation: (loc: { name: string; coords: [number, number] }) => void;
  optimizationResult: any;
  setOptimizationResult: (res: any) => void;
  qpsoParams: any;
  distanceUnit?: 'km' | 'mi';
}

export const LiveSimulationControl: React.FC<LiveSimulationProps> = ({
  startLocation,
  setStartLocation,
  optimizationResult,
  setOptimizationResult,
  qpsoParams,
  distanceUnit = 'km'
}) => {
  const [destinationLocation, setDestinationLocation] = useState<{ name: string; coords: [number, number] }>({
    name: 'New Delhi, India',
    coords: [28.6139, 77.2090]
  });
  const [vehicleCount, setVehicleCount] = useState<number>(1);
  const [roundTrip] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [showReportModal, setShowReportModal] = useState<boolean>(false);

  const [intermediateStops, setIntermediateStops] = useState<{ name: string; coords: [number, number] }[]>([]);

  const handleAddStop = () => {
    setIntermediateStops([
      ...intermediateStops,
      { name: 'Central Park, NY', coords: [40.785091, -73.968285] }
    ]);
  };

  const handleRemoveStop = (idx: number) => {
    setIntermediateStops(intermediateStops.filter((_, i) => i !== idx));
  };

  const handleUpdateStop = (idx: number, loc: { name: string; coords: [number, number] }) => {
    const updated = [...intermediateStops];
    updated[idx] = loc;
    setIntermediateStops(updated);
  };

  const handleRunOptimization = async (presetOverride?: string) => {
    setLoading(true);
    try {
      if (presetOverride) {
        // Run preset optimization
        const res = await runOptimization({
          preset: presetOverride,
          vehicle_count: vehicleCount,
          round_trip: roundTrip,
          qpso_params: qpsoParams
        });
        setOptimizationResult(res);
        return res;
      } else {
        // Build custom stops list from intermediateStops + destinationLocation
        const allStops = [
          ...intermediateStops,
          { name: destinationLocation.name, coords: destinationLocation.coords }
        ];

        const res = await runOptimization({
          start_location: startLocation,
          stops: allStops,
          vehicle_count: vehicleCount,
          round_trip: roundTrip,
          qpso_params: qpsoParams
        });
        setOptimizationResult(res);
        return res;
      }
    } catch (err) {
      console.error("Optimization error:", err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const handleOpenReport = async () => {
    if (!optimizationResult) {
      await handleRunOptimization();
    }
    setShowReportModal(true);
  };

  const metrics = optimizationResult?.metrics || {
    total_distance_km: 142.8,
    total_time_min: 118,
    fuel_liters: 11.9,
    cost_inr: 1142,
    time_saved_hrs: 2.4,
    co2_reduction_kg: 18.5
  };

  return (
    <div className="max-w-[1440px] mx-auto px-6 py-8 space-y-6 font-sans">
      
      {/* Search Header Bar (Section 4.1 Global Search) */}
      <div className="quantum-glow-card p-4 rounded-xl space-y-4">
        <div className="flex flex-col md:flex-row items-center gap-4">
          <div className="w-full md:w-5/12">
            <LocationSearchInput
              label="Origin (From)"
              placeholder="Type any origin address or city on Earth..."
              value={startLocation.name}
              onSelectLocation={(loc) => setStartLocation(loc)}
            />
          </div>
          <div className="w-full md:w-5/12">
            <LocationSearchInput
              label="Destination (To)"
              placeholder="Type destination..."
              value={destinationLocation.name}
              onSelectLocation={(loc) => setDestinationLocation(loc)}
            />
          </div>
          <div className="w-full md:w-auto flex items-end gap-2.5">
            <button
              onClick={() => handleRunOptimization()}
              disabled={loading}
              className="flex-1 md:flex-initial btn-ember-gradient px-5 py-2.5 text-xs uppercase font-bold flex items-center justify-center gap-2 mt-4 md:mt-0 shadow-lg shadow-[#ff5719]/20 cursor-pointer"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-white" />}
              <span>{loading ? 'Optimizing...' : 'Run Quantum Router'}</span>
            </button>

            <button
              onClick={handleOpenReport}
              disabled={loading}
              className="flex-1 md:flex-initial bg-[var(--color-bg-tertiary)] hover:bg-[#251f33] border border-[#ff5719]/60 hover:border-[#ff5719] text-[var(--color-text-primary)] px-4 py-2.5 rounded-lg text-xs font-semibold uppercase flex items-center justify-center gap-2 mt-4 md:mt-0 transition shadow-sm cursor-pointer"
              title="Generate & View Fleet Optimization Report"
            >
              <FileText className="w-4 h-4 text-[#ff5719]" />
              <span>Report</span>
            </button>
          </div>
        </div>

        {/* Intermediate Waypoints (if any) */}
        {intermediateStops.length > 0 && (
          <div className="space-y-3 pt-3 border-t border-[var(--color-border)]/30">
            <div className="label-caps text-[#ffb59e]">Intermediate Waypoints</div>
            {intermediateStops.map((stop, idx) => (
              <div key={idx} className="flex items-center gap-3">
                <div className="flex-1">
                  <LocationSearchInput
                    label={`Waypoint ${idx + 1}`}
                    placeholder="Type intermediate stop address..."
                    value={stop.name}
                    onSelectLocation={(loc) => handleUpdateStop(idx, loc)}
                  />
                </div>
                <button
                  onClick={() => handleRemoveStop(idx)}
                  className="mt-5 p-2 rounded-lg bg-[var(--color-bg-primary)] border border-[#ff4444]/40 text-[#ff6666] hover:bg-[#ff4444]/10 transition cursor-pointer"
                  title="Remove Waypoint"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="flex justify-start">
          <button
            onClick={handleAddStop}
            className="text-xs font-mono text-[#9dcaff] hover:text-[var(--color-text-primary)] flex items-center gap-1.5 transition cursor-pointer"
          >
            <span>+ Add Intermediate Waypoint</span>
          </button>
        </div>
      </div>

      {/* Fleet & Preset Controls Bar */}
      <div className="quantum-glow-card p-4 rounded-xl">
        <div className="flex flex-wrap items-center gap-4">

          {/* Fleet Size */}
          <div className="flex items-center gap-3">
            <label className="label-caps text-[#ffb59e] whitespace-nowrap">Fleet Size</label>
            <span className="text-xs font-mono font-bold text-[var(--color-text-primary)] bg-[var(--color-bg-primary)] px-2 py-0.5 rounded border border-[var(--color-border)] stat-number">
              {vehicleCount} Vehicle{vehicleCount > 1 ? 's' : ''}
            </span>
            <input
              type="range"
              min={1}
              max={4}
              value={vehicleCount}
              onChange={(e) => setVehicleCount(parseInt(e.target.value))}
              className="w-28 accent-[#ffb59e] bg-[var(--color-bg-primary)] h-2 rounded-lg cursor-pointer"
            />
          </div>

          {/* Global Controls */}
          <div className="flex items-center gap-2 ml-auto">
            <button
              onClick={() => handleRunOptimization()}
              className="btn-ember-gradient py-2 px-4 text-xs uppercase font-bold flex items-center gap-1.5 cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Re-route All</span>
            </button>
            <button
              onClick={handleOpenReport}
              className="bg-[var(--color-bg-primary)] hover:bg-[var(--color-bg-quaternary)] border border-[#ff5719]/60 hover:border-[#ff5719] text-[#ffb59e] py-2 px-4 rounded-lg text-xs font-mono font-semibold uppercase flex items-center gap-1.5 transition cursor-pointer"
            >
              <FileText className="w-3.5 h-3.5 text-[#ff5719]" />
              <span>Export Report</span>
            </button>
            <button
              onClick={() => alert("Emergency Override Initiated: All vehicles holding position.")}
              className="bg-[var(--color-bg-primary)] border border-[#ff4444] text-[#ff6666] hover:bg-[#ff4444]/10 py-2 px-4 rounded-lg text-xs font-mono font-semibold uppercase flex items-center gap-1.5 transition cursor-pointer"
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Emergency Override</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Full-Width Map Pane */}
      <div className="space-y-4">
        <div className="lg:col-span-12 space-y-4">
          <div className="quantum-glow-card rounded-2xl p-4 relative">
            
            {/* Top Floating Status Chips */}
            <div className="absolute top-7 left-7 z-10 flex flex-wrap items-center gap-2">
              <div className="bg-[var(--color-bg-primary)]/90 border border-[var(--color-border)] px-3 py-1.5 rounded-lg text-xs font-mono text-[#ffb59e] backdrop-blur-md stat-number">
                ● NODE: {optimizationResult?.run_id || 'RUN-4092'}
              </div>
              <div className="bg-[var(--color-bg-primary)]/90 border border-[var(--color-border)] px-3 py-1.5 rounded-lg text-xs font-mono text-[#9dcaff] backdrop-blur-md stat-number">
                LATENCY: {optimizationResult?.telemetry?.execution_ms || 12}ms
              </div>
              <div className="bg-[var(--color-bg-primary)]/90 border border-[var(--color-border)] px-3 py-1.5 rounded-lg text-xs font-mono text-[#ffb59e] backdrop-blur-md flex items-center gap-1.5 stat-number">
                <Clock className="w-3.5 h-3.5 text-[#ff5719]" />
                <span>TIME TAKEN: {metrics.total_time_min || 118} min ({((metrics.total_time_min || 118) / 60).toFixed(1)} hrs)</span>
              </div>
              <button
                onClick={handleOpenReport}
                className="bg-[var(--color-bg-primary)]/90 hover:bg-[var(--color-bg-tertiary)] border border-[#ff5719]/60 hover:border-[#ff5719] px-3 py-1.5 rounded-lg text-xs font-mono text-[#ffb59e] backdrop-blur-md flex items-center gap-1.5 transition cursor-pointer"
                title="Download Optimization PDF/JSON Report"
              >
                <Download className="w-3.5 h-3.5 text-[#ff5719]" />
                <span>Download Report</span>
              </button>
            </div>

            <RouteMap
              startLocation={startLocation}
              routes={optimizationResult?.routes || []}
              height="550px"
            />

            {/* Bottom-Overlaid KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
              
              {/* Card 1: Time Taken */}
              <div className="bg-[var(--color-bg-primary)] border border-[var(--color-border)] p-4 rounded-xl space-y-2">
                <div className="flex items-center justify-between label-caps text-[#ffb59e]">
                  <span>Time Taken</span>
                  <Clock className="w-3.5 h-3.5 text-[#ff5719]" />
                </div>
                <div className="text-2xl font-extrabold text-[var(--color-text-primary)] stat-number">
                  {metrics.total_time_min || 118} min ({((metrics.total_time_min || 118) / 60).toFixed(1)} hrs)
                </div>
                <div className="w-full bg-[var(--color-bg-quaternary)] h-1.5 rounded-full overflow-hidden">
                  <div className="bg-[#ff5719] h-full w-[80%]"></div>
                </div>
                <div className="text-[10px] font-mono text-[var(--color-text-muted)]/60 stat-number">
                  {distanceUnit === 'mi'
                    ? `${((metrics.total_distance_km || 142.8) * 0.621371).toFixed(1)} mi`
                    : `${metrics.total_distance_km || 142.8} km`
                  } estimated route
                </div>
              </div>

              {/* Card 2: Time Saved */}
              <div className="bg-[var(--color-bg-primary)] border border-[var(--color-border)] p-4 rounded-xl space-y-2">
                <div className="flex items-center justify-between label-caps text-[#ffb59e]">
                  <span>Time Saved</span>
                  <Clock className="w-3.5 h-3.5 text-[#9dcaff]" />
                </div>
                <div className="text-2xl font-extrabold text-[var(--color-text-primary)] stat-number">{metrics.time_saved_hrs || 2.4} hrs</div>
                <div className="w-full bg-[var(--color-bg-quaternary)] h-1.5 rounded-full overflow-hidden">
                  <div className="bg-[#ff5719] h-full w-[75%]"></div>
                </div>
                <div className="text-[10px] font-mono text-[var(--color-text-muted)]/60 stat-number">+14% vs avg</div>
              </div>

              {/* Card 3: CO2 Reduction */}
              <div className="bg-[var(--color-bg-primary)] border border-[var(--color-border)] p-4 rounded-xl space-y-2">
                <div className="flex items-center justify-between label-caps text-[#9dcaff]">
                  <span>CO2 Reduction</span>
                  <Layers className="w-3.5 h-3.5" />
                </div>
                <div className="text-2xl font-extrabold text-[var(--color-text-primary)] stat-number">{metrics.co2_reduction_kg || 18.5} kg</div>
                <div className="w-full bg-[var(--color-bg-quaternary)] h-1.5 rounded-full overflow-hidden">
                  <div className="bg-[#9dcaff] h-full w-[85%]"></div>
                </div>
                <div className="text-[10px] font-mono text-[#9dcaff]">Optimal Zone</div>
              </div>

              {/* Card 4: Active Vehicles */}
              <div className="bg-[var(--color-bg-primary)] border border-[var(--color-border)] p-4 rounded-xl space-y-2">
                <div className="flex items-center justify-between label-caps text-[#d0bcff]">
                  <span>Active Vehicles</span>
                  <Truck className="w-3.5 h-3.5" />
                </div>
                <div className="text-2xl font-extrabold text-[var(--color-text-primary)] stat-number">{vehicleCount} units</div>
                <div className="text-[10px] font-mono text-[#d0bcff] flex items-center justify-between">
                  <span>Mixed Fleet Active</span>
                  <button
                    onClick={handleOpenReport}
                    className="text-[#ffb59e] hover:underline flex items-center gap-0.5 cursor-pointer"
                  >
                    View Report &rarr;
                  </button>
                </div>
              </div>

            </div>

          </div>
        </div>
      </div>

      {/* Interactive Report Modal */}
      <ReportModal
        isOpen={showReportModal}
        onClose={() => setShowReportModal(false)}
        runId={optimizationResult?.run_id}
        optimizationResult={optimizationResult}
        startLocation={startLocation}
        distanceUnit={distanceUnit}
      />

    </div>
  );
};
