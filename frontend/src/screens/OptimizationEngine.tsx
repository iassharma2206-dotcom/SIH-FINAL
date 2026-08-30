import React, { useState, useEffect } from 'react';
import { Sliders, Cpu, Rocket, CheckCircle2, Activity } from 'lucide-react';
import { HyperparameterSlider } from '../components/HyperparameterSlider';
import { runOptimization, fetchBenchmark } from '../api/client';

interface EngineProps {
  qpsoParams: any;
  setQpsoParams: (params: any) => void;
  onDeploy: () => void;
}

export const OptimizationEngine: React.FC<EngineProps> = ({
  qpsoParams,
  setQpsoParams,
  onDeploy
}) => {
  const [betaStart, setBetaStart] = useState<number>(qpsoParams.beta_start || 1.0);
  const [swarmSize, setSwarmSize] = useState<number>(qpsoParams.swarm_size || 30);
  const [maxIter, setMaxIter] = useState<number>(qpsoParams.max_iter || 300);
  const [plateauWindow, setPlateauWindow] = useState<number>(qpsoParams.plateau_window || 50);

  const [tpuAlloc, setTpuAlloc] = useState<number>(4);
  const [memAlloc, setMemAlloc] = useState<number>(16);
  const [saving, setSaving] = useState<boolean>(false);
  const [benchmarks, setBenchmarks] = useState<any[]>([]);
  const [benchmarkLoading, setBenchmarkLoading] = useState<boolean>(false);

  // Auto-load benchmark on mount instantly
  useEffect(() => {
    const autoLoadBenchmark = async () => {
      setBenchmarkLoading(true);
      try {
        const bRes = await fetchBenchmark('default');
        setBenchmarks(bRes.comparisons || []);
      } catch (err) {
        console.error('Auto benchmark load failed:', err);
      } finally {
        setBenchmarkLoading(false);
      }
    };
    autoLoadBenchmark();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);


  const handleRerunBenchmark = async () => {
    setBenchmarkLoading(true);
    try {
      const bRes = await fetchBenchmark('run-' + Date.now());
      setBenchmarks(bRes.comparisons || []);
    } catch (err) {
      console.error("Re-run benchmark failed:", err);
    } finally {
      setBenchmarkLoading(false);
    }
  };

  const handleSaveAndDeploy = async () => {
    setSaving(true);
    const updated = {
      beta_start: betaStart,
      swarm_size: swarmSize,
      max_iter: maxIter,
      plateau_window: plateauWindow
    };
    setQpsoParams(updated);
    
    try {
      const res = await runOptimization({ qpso_params: updated });
      if (res.run_id) {
        setBenchmarkLoading(true);
        const bRes = await fetchBenchmark(res.run_id);
        setBenchmarks(bRes.comparisons || []);
        setBenchmarkLoading(false);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
      onDeploy();
    }
  };


  return (
    <div className="max-w-[1440px] mx-auto px-6 py-10 space-y-12">
      
      {/* Centered Header */}
      <div className="text-center space-y-3 max-w-2xl mx-auto">
        <div className="w-12 h-1 bg-[#ff5719] mx-auto rounded-full"></div>
        <h1 className="text-3xl md:text-4xl font-light text-[var(--color-text-primary)]">Metaheuristic Engine Tuning</h1>
        <p className="text-sm text-[var(--color-text-muted)]/80 leading-relaxed">
          Configure advanced algorithmic parameters to optimize routing throughput and resolve critical network congestion.
        </p>
      </div>

      {/* Main Two-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Hyperparameters & Hardware */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* Card 1: Algorithm Hyperparameters */}
          <div className="quantum-glow-card p-6 rounded-2xl space-y-4">
            <div className="flex items-center gap-2 text-base font-medium text-[var(--color-text-primary)] border-b border-[var(--color-border)]/30 pb-3">
              <Sliders className="w-4 h-4 text-[#ff5719]" />
              <span>🌱 Algorithm Hyperparameters</span>
            </div>

            {/* Slider 1: Beta Contraction-Expansion */}
            <HyperparameterSlider
              label="β Contraction-Expansion (start)"
              value={betaStart}
              min={0.5}
              max={1.5}
              step={0.05}
              description="Initial quantum potential well scale governing global particle exploration energy."
              onChange={(val) => setBetaStart(val)}
            />

            {/* Slider 2: Swarm Size */}
            <HyperparameterSlider
              label="Swarm Size (M)"
              value={swarmSize}
              min={10}
              max={100}
              step={5}
              description="Number of quantum particles concurrently evaluating cluster visit permutations."
              onChange={(val) => setSwarmSize(val)}
            />

            {/* Slider 3: Max Iterations */}
            <HyperparameterSlider
              label="Max Iterations"
              value={maxIter}
              min={50}
              max={800}
              step={25}
              description="Maximum quantum annealing steps allocated per route cluster."
              onChange={(val) => setMaxIter(val)}
            />

            {/* Slider 4: Stopping Plateau Window */}
            <HyperparameterSlider
              label="Stopping Plateau Window"
              value={plateauWindow}
              min={10}
              max={100}
              step={5}
              description="Iterations without fitness improvement before triggering early convergence."
              onChange={(val) => setPlateauWindow(val)}
            />
          </div>

          {/* Card 2: Hardware Allocation */}
          <div className="quantum-glow-card p-6 rounded-2xl space-y-4">
            <div className="flex items-center gap-2 text-base font-medium text-[var(--color-text-primary)] border-b border-[var(--color-border)]/30 pb-3">
              <Cpu className="w-4 h-4 text-[#9dcaff]" />
              <span>⚙ Hardware Allocation</span>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-mono text-[#ffb59e] uppercase mb-1.5">TPU Worker Nodes</label>
                <input
                  type="number"
                  value={tpuAlloc}
                  onChange={(e) => setTpuAlloc(parseInt(e.target.value))}
                  className="w-full bg-[var(--color-bg-primary)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[#9dcaff]"
                />
              </div>

              <div>
                <label className="block text-xs font-mono text-[#ffb59e] uppercase mb-1.5">Memory Cache Limit (GB)</label>
                <input
                  type="number"
                  value={memAlloc}
                  onChange={(e) => setMemAlloc(parseInt(e.target.value))}
                  className="w-full bg-[var(--color-bg-primary)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[#9dcaff]"
                />
              </div>
            </div>
          </div>

        </div>

        {/* Right Column: Pipeline Diagram & Status */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Card 1: Optimization Pipeline */}
          <div className="quantum-glow-card p-6 rounded-2xl space-y-4">
            <div className="text-xs font-mono text-[#ffb59e] uppercase tracking-wider">OPTIMIZATION PIPELINE</div>
            
            {/* Minimal Node & S-curve SVG Diagram */}
            <div className="h-44 bg-[var(--color-bg-primary)] border border-[var(--color-border)]/50 rounded-xl p-4 flex items-center justify-between relative overflow-hidden">
              <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
                <path d="M 40 80 C 120 20, 200 140, 280 80" stroke="#ff5719" strokeWidth="2" fill="none" strokeDasharray="4 4" />
                <path d="M 280 80 C 340 40, 400 100, 460 80" stroke="#9dcaff" strokeWidth="2" fill="none" />
              </svg>
              <div className="relative z-10 text-center">
                <div className="w-10 h-10 rounded-full bg-[#ff5719]/20 border border-[#ff5719] mx-auto flex items-center justify-center text-xs font-mono text-[#ffb59e]">1</div>
                <div className="text-[10px] font-mono text-[var(--color-text-muted)]/70 mt-1">OSM Graph</div>
              </div>
              <div className="relative z-10 text-center">
                <div className="w-10 h-10 rounded-full bg-[#9dcaff]/20 border border-[#9dcaff] mx-auto flex items-center justify-center text-xs font-mono text-[#9dcaff]">2</div>
                <div className="text-[10px] font-mono text-[var(--color-text-muted)]/70 mt-1">N×N Matrix</div>
              </div>
              <div className="relative z-10 text-center">
                <div className="w-10 h-10 rounded-full bg-[#d0bcff]/20 border border-[#d0bcff] mx-auto flex items-center justify-center text-xs font-mono text-[#d0bcff]">3</div>
                <div className="text-[10px] font-mono text-[var(--color-text-muted)]/70 mt-1">QPSO Engine</div>
              </div>
            </div>
          </div>

          {/* Card 2: Engine Status */}
          <div className="bg-[var(--color-bg-primary)] border-l-4 border-l-[#ff5719] border border-[var(--color-border)] p-5 rounded-xl space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-[#ffb59e] uppercase">ENGINE STATUS</span>
              <span className="flex items-center gap-1.5 text-xs text-[#9dcaff]">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Ready</span>
              </span>
            </div>
            <p className="text-sm font-medium text-[var(--color-text-primary)]">QPSO Delta-Potential Well Active & Calibrated</p>
            <div className="text-[11px] font-mono text-[var(--color-text-muted)]/60 pt-2 border-t border-[var(--color-border)]/30">
              Last Run: {new Date().toLocaleTimeString()}
            </div>
          </div>

          {/* Deploy Button */}
          <button
            onClick={handleSaveAndDeploy}
            disabled={saving}
            className="w-full btn-ember-gradient py-3.5 px-6 text-sm uppercase tracking-wider font-bold flex items-center justify-center gap-2 rounded-xl"
          >
            {saving ? <Activity className="w-5 h-5 animate-spin" /> : <Rocket className="w-5 h-5 fill-white" />}
            <span>{saving ? 'Calibrating Engine...' : '🚀 Save & Deploy Engine'}</span>
          </button>

        </div>

      </div>

      {/* Benchmark Comparison Table (Section 8) */}
      <div className="quantum-glow-card p-6 rounded-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-[var(--color-border)]/30 pb-4">
          <div>
            <h2 className="text-xl font-normal text-[var(--color-text-primary)]">Algorithmic Benchmark Comparison</h2>
            <p className="text-xs text-[var(--color-text-muted)]/70">QPSO vs Simulated Annealing vs Classical PSO vs Held-Karp Exact DP</p>
          </div>
          <button
            onClick={handleRerunBenchmark}
            disabled={benchmarkLoading}
            className="px-4 py-2 bg-[var(--color-bg-primary)] border border-[var(--color-border)] rounded-lg text-xs font-mono text-[#ffb59e] hover:bg-[var(--color-bg-quaternary)] transition disabled:opacity-50"
          >
            {benchmarkLoading ? 'Calibrating...' : 'Re-run Benchmark'}
          </button>
        </div>

        {benchmarkLoading ? (
          <div className="text-center py-8 text-xs font-mono text-[#ffb59e]">
            Running live benchmark across QPSO, SA, Classical PSO, and Held-Karp Exact DP...
          </div>
        ) : benchmarks.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono border-collapse">
              <thead>
                <tr className="border-b border-[var(--color-border)]/50 text-[#ffb59e] uppercase">
                  <th className="py-3 px-4">Algorithm</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Route Cost</th>
                  <th className="py-3 px-4">Runtime (ms)</th>
                  <th className="py-3 px-4">Optimality Gap</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border)]/20">
                {benchmarks.map((row, idx) => (
                  <tr key={idx} className={row.algorithm.includes('QPSO') ? 'bg-[#ff5719]/10' : ''}>
                    <td className="py-3 px-4 font-bold text-[var(--color-text-primary)]">{row.algorithm}</td>
                    <td className="py-3 px-4 text-[var(--color-text-muted)]/70">{row.type}</td>
                    <td className="py-3 px-4 text-[#9dcaff] font-bold">{row.route_cost}</td>
                    <td className="py-3 px-4 text-[var(--color-text-primary)]">{row.execution_ms} ms</td>
                    <td className="py-3 px-4 text-[#ffb59e]">{row.optimality_gap_percent}%</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        row.status.includes('BEST') ? 'bg-[#ff5719] text-white' : 'bg-[var(--color-bg-primary)] text-[var(--color-text-muted)]/60'
                      }`}>
                        {row.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-xs font-mono text-[var(--color-text-muted)]/60">
            Click "Save & Deploy Engine" above to run live comparative benchmark suite across all 4 algorithms.
          </div>
        )}
      </div>

    </div>
  );
};
