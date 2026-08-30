import React from 'react';
import { Play, BarChart2, Activity, Clock, Cpu } from 'lucide-react';
import { RouteMap } from '../components/RouteMap';
import HeroLineNetwork from '../components/HeroLineNetwork';

interface MissionControlDashboardProps {
  onNavigateToSimulation: () => void;
  onNavigateToEngine: () => void;
  optimizationResult: any;
  startLocation: { name: string; coords: [number, number] };
}

export const MissionControlDashboard: React.FC<MissionControlDashboardProps> = ({
  onNavigateToSimulation,
  onNavigateToEngine,
  optimizationResult,
  startLocation,
}) => {

  return (
    <div className="max-w-[1440px] mx-auto px-6 py-8 space-y-10 font-sans">
      
      {/* 1. Hero Layout - Spacious Bold Uppercase Headline */}
      <div className="relative w-full max-w-5xl mx-auto text-center space-y-6 py-6">
        <HeroLineNetwork />
        <div className="relative z-10">
        <h1 className="font-display-bold text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-extrabold text-[var(--color-text-primary)] uppercase leading-snug tracking-wide">
          <span>INTELLIGENCE AT THE </span>
          <span className="text-[var(--color-accent)]">SPEED OF LIGHT</span>
        </h1>

        <p className="text-base sm:text-lg md:text-xl text-[var(--color-text-muted-alt)] leading-relaxed max-w-2xl mx-auto font-normal">
          Next-generation route optimization powered by quantum-inspired algorithms. Navigate chaos with pinpoint precision under real-world traffic dynamics.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-3">
          <button
            onClick={onNavigateToSimulation}
            className="btn-ember-gradient px-8 py-3.5 text-sm font-bold flex items-center gap-2 shadow-lg shadow-[var(--color-accent)]/25 hover:shadow-[var(--color-accent)]/40 transition cursor-pointer font-sans"
          >
            <Play className="w-4 h-4 fill-white" />
            <span className="uppercase tracking-wider">DEPLOY ENGINE</span>
          </button>
          <button
            onClick={onNavigateToEngine}
            className="px-8 py-3.5 text-sm font-bold rounded-lg border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-bg-quaternary)] transition flex items-center gap-2 cursor-pointer font-sans"
          >
            <BarChart2 className="w-4 h-4 text-[var(--color-blue-accent)]" />
            <span className="uppercase tracking-wider">VIEW ENGINE TUNING</span>
          </button>
        </div>
        </div>
      </div>

      {/* 2. Three Stat Cards Side-by-Side with Tabular Numerals */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Card 1: Global Flow */}
        <div className="quantum-glow-card p-6 rounded-xl space-y-3">
          <div className="flex items-center justify-between label-caps text-[var(--color-accent-soft)]">
            <span>Global Flow</span>
            <Activity className="w-4 h-4 text-[var(--color-accent)]" />
          </div>
          <div className="text-4xl font-extrabold text-[var(--color-text-primary)] stat-number font-sans">98.2%</div>
          <div className="text-xs text-[var(--color-blue-accent)] font-mono stat-number">+2.4% vs last hr</div>
        </div>

        {/* Card 2: Avg Latency */}
        <div className="quantum-glow-card p-6 rounded-xl space-y-3">
          <div className="flex items-center justify-between label-caps text-[var(--color-accent-soft)]">
            <span>Avg Latency</span>
            <Clock className="w-4 h-4 text-[var(--color-blue-accent)]" />
          </div>
          <div className="text-4xl font-extrabold text-[var(--color-text-primary)] stat-number font-sans">12ms</div>
          <div className="text-xs text-[var(--color-text-muted)]/70 font-mono">Optimal range</div>
        </div>

        {/* Card 3: Active Nodes */}
        <div className="quantum-glow-card p-6 rounded-xl space-y-3">
          <div className="flex items-center justify-between label-caps text-[var(--color-accent-soft)]">
            <span>Active Nodes</span>
            <Cpu className="w-4 h-4 text-[var(--color-purple-accent)]" />
          </div>
          <div className="text-4xl font-extrabold text-[var(--color-text-primary)] stat-number font-sans">4,092</div>
          <div className="text-xs text-[var(--color-accent)] font-mono flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[var(--color-accent)] animate-pulse"></span>
            <span>Live synchronization</span>
          </div>
        </div>

      </div>

      {/* 3. Workflow Canvas Card */}
      <div className="quantum-glow-card p-6 rounded-2xl space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[var(--color-border)]/30 pb-4">
          <div>
            <h2 className="font-display-bold text-2xl font-extrabold text-[var(--color-text-primary)] uppercase">WORKFLOW CANVAS</h2>
            <p className="text-xs text-[var(--color-text-muted)]/70 font-normal">Real-time visualization of routing topology across OpenStreetMap graph</p>
          </div>
        </div>

        {/* Live Route Map */}
        <RouteMap
          startLocation={startLocation}
          routes={optimizationResult?.routes || []}
          height="450px"
        />

        {/* Legend */}
        <div className="flex items-center gap-6 text-xs font-mono text-[var(--color-text-muted)]/70 pt-2">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[var(--color-accent)]"></span>
            <span>Node Alpha - Critical (Hub)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-[var(--color-blue-accent)]"></span>
            <span>Node Beta - Stable (Stops)</span>
          </div>
        </div>
      </div>

    </div>
  );
};
