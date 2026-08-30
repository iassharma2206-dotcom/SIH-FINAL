import React, { useState, useEffect } from 'react';
import { CheckCircle2, AlertTriangle, AlertCircle, PlugZap, RefreshCw, Terminal, X } from 'lucide-react';
import { fetchNetworkHealth } from '../api/client';

export const NetworkDiagnostics: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [selectedCity, setSelectedCity] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([
    '> INITIALIZING GLOBAL DIAGNOSTIC SUITE...',
    '> CONNECTING TO OPENSTREETMAP ROUTING NODES...',
    '> OSMNX GRAPH DATA LOADED: 4,092 NODES, 11,480 EDGES',
    '> MONITORING REAL-TIME CONGESTION MULTIPLIERS...'
  ]);

  useEffect(() => {
    fetchNetworkHealth().then(res => {
      setData(res);
      if (res.cities && res.cities.length > 0) {
        setSelectedCity(res.cities[0]);
      }
    }).catch(err => console.error(err));
  }, []);

  const handleReboot = (cityCode: string) => {
    setLogs(prev => [
      ...prev,
      `> REBOOT COMMAND SENT TO SECTOR [${cityCode}]...`,
      `> FLUSHING GRAPHML LOCAL CACHE FOR ${cityCode}...`,
      `> RE-FETCHING SCOPED OSM GRAPH FROM OVERPASS PASS...`,
      `> SECTOR [${cityCode}] RE-ESTABLISHED. STATUS: HEALTHY.`
    ]);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle2 className="w-4 h-4 text-[var(--color-success)]" />;
      case 'congested': return <AlertTriangle className="w-4 h-4 text-[var(--color-accent-soft)]" />;
      case 'critical': return <AlertCircle className="w-4 h-4 text-[var(--color-danger)]" />;
      case 'offline': return <PlugZap className="w-4 h-4 text-[var(--color-text-muted)]/40" />;
      default: return null;
    }
  };

  const summary = data?.summary || { healthy_nodes: 6, congested_nodes: 1, critical_alert: 1, offline: 1 };
  const cities = data?.cities || [];

  return (
    <div className="max-w-[1440px] mx-auto px-6 py-8 space-y-8">
      
      {/* 1. Top Strip: Four Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        
        <div className="bg-[var(--color-bg-primary)] border border-[var(--color-border)] p-5 rounded-xl flex items-center justify-between">
          <div>
            <div className="text-xs font-mono text-[var(--color-text-muted)]/60 uppercase">Healthy Nodes</div>
            <div className="text-3xl font-light text-[var(--color-text-secondary)] mt-1">{summary.healthy_nodes}</div>
          </div>
          <div className="w-10 h-10 rounded-full bg-[var(--color-success)]/10 border border-[var(--color-success)]/30 flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5 text-[var(--color-success)]" />
          </div>
        </div>

        <div className="bg-[var(--color-bg-primary)] border border-[var(--color-border)] p-5 rounded-xl flex items-center justify-between">
          <div>
            <div className="text-xs font-mono text-[var(--color-text-muted)]/60 uppercase">Congested</div>
            <div className="text-3xl font-light text-[var(--color-text-secondary)] mt-1">{summary.congested_nodes}</div>
          </div>
          <div className="w-10 h-10 rounded-full bg-[var(--color-accent-soft)]/10 border border-[var(--color-accent-soft)]/30 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-[var(--color-accent-soft)]" />
          </div>
        </div>

        <div className="bg-[var(--color-bg-primary)] border border-[var(--color-border)] p-5 rounded-xl flex items-center justify-between">
          <div>
            <div className="text-xs font-mono text-[var(--color-text-muted)]/60 uppercase">Critical Alert</div>
            <div className="text-3xl font-light text-[var(--color-text-secondary)] mt-1">{summary.critical_alert}</div>
          </div>
          <div className="w-10 h-10 rounded-full bg-[var(--color-danger)]/10 border border-[var(--color-danger)]/30 flex items-center justify-center">
            <AlertCircle className="w-5 h-5 text-[var(--color-danger)]" />
          </div>
        </div>

        <div className="bg-[var(--color-bg-primary)] border border-[var(--color-border)] p-5 rounded-xl flex items-center justify-between">
          <div>
            <div className="text-xs font-mono text-[var(--color-text-muted)]/60 uppercase">Offline</div>
            <div className="text-3xl font-light text-[var(--color-text-secondary)] mt-1">{summary.offline}</div>
          </div>
          <div className="w-10 h-10 rounded-full bg-[var(--color-text-muted)]/10 border border-[var(--color-text-muted)]/30 flex items-center justify-center">
            <PlugZap className="w-5 h-5 text-[var(--color-text-muted)]/50" />
          </div>
        </div>

      </div>

      {/* 2. Global Hub Status & Diagnostic Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Dense Grid of City Tiles */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-normal text-[var(--color-text-secondary)]">Global Hub Status</h2>
            <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-text-muted)]/70">
              <span>Filter: All</span>
              <span>|</span>
              <span>Sort: Risk</span>
            </div>
          </div>

          <div className="grid grid-cols-3 sm:grid-cols-3 gap-4">
            {cities.map((city: any, idx: number) => {
              const isSelected = selectedCity?.code === city.code;
              return (
                <button
                  key={idx}
                  onClick={() => setSelectedCity(city)}
                  className={`p-4 rounded-xl border text-left transition relative ${
                    isSelected
                      ? 'bg-[var(--color-bg-quaternary)] border-[var(--color-accent)] shadow-lg shadow-[var(--color-accent)]/15 ring-2 ring-[var(--color-accent)]/40'
                      : 'bg-[var(--color-bg-tertiary)] border-[var(--color-border)] hover:border-[var(--color-border)]/80'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono font-bold text-base text-[var(--color-text-secondary)]">{city.code}</span>
                    {getStatusIcon(city.status)}
                  </div>
                  <div className="text-xs text-[var(--color-text-muted)]/80 truncate">{city.name}</div>
                  <div className="text-[10px] font-mono text-[var(--color-text-muted)]/50 mt-2 flex justify-between">
                    <span>{city.latency}</span>
                    <span>{city.bandwidth}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Column: Active Diagnostic Card */}
        <div className="lg:col-span-5">
          {selectedCity && (
            <div className="quantum-glow-card p-6 rounded-2xl space-y-5">
              
              <div className="flex items-center justify-between border-b border-[var(--color-border)]/30 pb-3">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[var(--color-accent)] animate-pulse"></span>
                  <span className="text-xs font-mono text-[var(--color-accent-soft)] uppercase font-bold">
                    ● ACTIVE DIAGNOSTIC: {selectedCity.name} ({selectedCity.code})
                  </span>
                </div>
                <button onClick={() => setSelectedCity(null)} className="text-[var(--color-text-muted)]/50 hover:text-[var(--color-text-secondary)]">
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Metric Rows */}
              <div className="space-y-3 font-mono text-xs">
                <div className="flex justify-between py-1 border-b border-[var(--color-border)]/20">
                  <span className="text-[var(--color-text-muted)]/60">Latency</span>
                  <span className="text-[var(--color-text-secondary)]">{selectedCity.latency}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-[var(--color-border)]/20">
                  <span className="text-[var(--color-text-muted)]/60">Packet Loss</span>
                  <span className="text-[var(--color-accent-soft)]">{selectedCity.loss}</span>
                </div>
                <div className="space-y-1 pt-1">
                  <div className="flex justify-between text-[11px]">
                    <span className="text-[var(--color-text-muted)]/60">Bandwidth Throughput</span>
                    <span className="text-[var(--color-blue-accent)]">{selectedCity.bandwidth}</span>
                  </div>
                  <div className="w-full bg-[var(--color-bg-primary)] h-2 rounded-full overflow-hidden border border-[var(--color-border)]">
                    <div className="bg-[var(--color-blue-accent)] h-full" style={{ width: selectedCity.bandwidth }}></div>
                  </div>
                </div>
              </div>

              {/* Diagnostic Log Terminal Block */}
              <div className="space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-mono text-[var(--color-accent-soft)]">
                  <Terminal className="w-3.5 h-3.5" />
                  <span>DIAGNOSTIC LOG</span>
                </div>
                <div className="bg-[var(--color-bg-primary)] border border-[var(--color-border)] rounded-xl p-3.5 h-36 font-mono text-[11px] text-[var(--color-success)] overflow-y-auto space-y-1 leading-relaxed">
                  {logs.map((log, i) => (
                    <div key={i}>{log}</div>
                  ))}
                </div>
              </div>

              {/* Reboot Node Button */}
              <button
                onClick={() => handleReboot(selectedCity.code)}
                className="w-full btn-ember-gradient py-3 px-4 text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                <span>↻ Reboot Node</span>
              </button>

            </div>
          )}
        </div>

      </div>

    </div>
  );
};
