import React, { useState } from 'react';
import { Settings, Shield, HardDrive, Wifi, Palette, CheckCircle2 } from 'lucide-react';

const THEMES = [
  {
    id: 'dark',
    label: 'Quantum Midnight',
    description: 'Deep dark mode — maximum contrast for command-center operations.',
    accent: '#ff5719',
    bg: '#110b1b',
    text: '#f4f1e8',
  },
  {
    id: 'cosmic',
    label: 'Cosmic Dusk',
    description: 'Rich indigo-purple dark mode with softer contrast for extended use.',
    accent: '#a78bfa',
    bg: '#0e0b1f',
    text: '#ede9fe',
  },
  {
    id: 'light',
    label: 'Command Light',
    description: 'Warm off-white light mode with full AA contrast for bright environments.',
    accent: '#ff5719',
    bg: '#f6f4ef',
    text: '#1c1626',
  },
  {
    id: 'cyberpunk',
    label: 'Cyberpunk Neon',
    description: 'Pure black + hot pink neon — maximum edge, maximum contrast.',
    accent: '#ff2d78',
    bg: '#000000',
    text: '#ff9ec4',
  },
  {
    id: 'neonrain',
    label: 'Neon Rain',
    description: 'Tokyo night alley — deep navy with electric blue & magenta neon glow.',
    accent: '#e040fb',
    bg: '#060818',
    text: '#c8d8ff',
    swatch2: '#00bfff',
  },
];


interface SystemSettingsProps {
  theme: string;
  setTheme: (t: string) => void;
  distanceUnit: 'km' | 'mi';
  setDistanceUnit: (u: 'km' | 'mi') => void;
}

export const SystemSettings: React.FC<SystemSettingsProps> = ({
  theme,
  setTheme,
  distanceUnit,
  setDistanceUnit
}) => {
  const [wsRate, setWsRate] = useState<number>(50);
  const [cacheCleared, setCacheCleared] = useState<boolean>(false);

  const handleClearCache = () => {
    setCacheCleared(true);
    setTimeout(() => setCacheCleared(false), 3000);
  };

  return (
    <div className="max-w-[1000px] mx-auto px-6 py-10 space-y-8">
      
      <div className="pb-4" style={{ borderBottom: '1px solid color-mix(in srgb, var(--color-border) 30%, transparent)' }}>
        <h1 className="text-3xl font-light" style={{ color: 'var(--color-text-primary)' }}>System Settings</h1>
        <p className="text-sm mt-1" style={{ color: 'color-mix(in srgb, var(--color-text-muted) 70%, transparent)' }}>
          Configure platform defaults, map graph cache preferences, and WebSocket telemetry stream options.
        </p>
      </div>

      <div className="space-y-6">
        
        {/* Card 1: Distance Units & Display */}
        <div className="quantum-glow-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center gap-2 text-base font-medium pb-3" style={{ color: 'var(--color-text-primary)', borderBottom: '1px solid color-mix(in srgb, var(--color-border) 30%, transparent)' }}>
            <Settings className="w-4 h-4 text-[#ff5719]" />
            <span>Distance Units & Display</span>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>Measurement Unit</div>
              <div className="text-xs" style={{ color: 'color-mix(in srgb, var(--color-text-muted) 60%, transparent)' }}>Select default distance scale used in route manifests and KPIs.</div>
            </div>
            <div className="flex items-center p-1 rounded-lg" style={{ backgroundColor: 'var(--color-bg-primary)', border: '1px solid var(--color-border)' }}>
              <button
                onClick={() => setDistanceUnit('km')}
                className={`px-3 py-1.5 text-xs font-mono font-bold rounded-md transition ${
                  distanceUnit === 'km' ? 'bg-[#ff5719] text-white' : ''
                }`}
                style={distanceUnit !== 'km' ? { color: 'color-mix(in srgb, var(--color-text-muted) 60%, transparent)' } : {}}
              >
                Kilometers (km)
              </button>
              <button
                onClick={() => setDistanceUnit('mi')}
                className={`px-3 py-1.5 text-xs font-mono font-bold rounded-md transition ${
                  distanceUnit === 'mi' ? 'bg-[#ff5719] text-white' : ''
                }`}
                style={distanceUnit !== 'mi' ? { color: 'color-mix(in srgb, var(--color-text-muted) 60%, transparent)' } : {}}
              >
                Miles (mi)
              </button>
            </div>
          </div>
        </div>

        {/* Card 2: Vehicle Capacity Constraints */}
        <div className="quantum-glow-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between pb-3" style={{ borderBottom: '1px solid color-mix(in srgb, var(--color-border) 30%, transparent)' }}>
            <div className="flex items-center gap-2 text-base font-medium" style={{ color: 'var(--color-text-primary)' }}>
              <Shield className="w-4 h-4 text-[#9dcaff]" />
              <span>Vehicle Capacity Constraints</span>
            </div>
            <span className="bg-[#ff5719]/20 text-[#ffb59e] border border-[#ff5719]/30 text-[10px] font-mono px-2 py-0.5 rounded font-bold">
              FUTURE WORK (STATED)
            </span>
          </div>
          <p className="text-xs leading-relaxed" style={{ color: 'color-mix(in srgb, var(--color-text-muted) 70%, transparent)' }}>
            Vehicle demand payload capacity constraints are flagged as a stated future-work module per Section 5.6 to avoid introducing ungrounded demand assumptions into the core QPSO evaluation loop.
          </p>
        </div>

        {/* Card 3: Map Cache & GraphML Management */}
        <div className="quantum-glow-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center gap-2 text-base font-medium pb-3" style={{ color: 'var(--color-text-primary)', borderBottom: '1px solid color-mix(in srgb, var(--color-border) 30%, transparent)' }}>
            <HardDrive className="w-4 h-4 text-[#d0bcff]" />
            <span>Map Cache & GraphML Storage</span>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>Local GraphML Cache</div>
              <div className="text-xs" style={{ color: 'color-mix(in srgb, var(--color-text-muted) 60%, transparent)' }}>Currently storing 3 preset graphs + 5 scoped bbox extracts (~42 MB).</div>
            </div>
            <button
              onClick={handleClearCache}
              className="px-4 py-2 text-xs font-mono rounded-lg transition"
              style={{ backgroundColor: 'var(--color-bg-primary)', border: '1px solid var(--color-border)', color: 'var(--color-accent-soft)' }}
            >
              {cacheCleared ? 'Cache Purged!' : 'Purge Cached GraphML'}
            </button>
          </div>
        </div>

        {/* Card 4: WebSocket Telemetry Throttle */}
        <div className="quantum-glow-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center gap-2 text-base font-medium pb-3" style={{ color: 'var(--color-text-primary)', borderBottom: '1px solid color-mix(in srgb, var(--color-border) 30%, transparent)' }}>
            <Wifi className="w-4 h-4 text-[#44ff88]" />
            <span>WebSocket Telemetry Throttle Rate</span>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="" style={{ color: 'color-mix(in srgb, var(--color-text-muted) 70%, transparent)' }}>Iteration Broadcast Interval</span>
              <span className="font-bold" style={{ color: 'var(--color-accent-soft)' }}>Every {wsRate} ms</span>
            </div>
            <input
              type="range"
              min={10}
              max={200}
              step={10}
              value={wsRate}
              onChange={(e) => setWsRate(parseInt(e.target.value))}
              className="w-full accent-[#ffb59e] h-2 rounded-lg cursor-pointer"
              style={{ backgroundColor: 'var(--color-bg-primary)' }}
            />
          </div>
        </div>

        {/* Card 5: Theme Selector */}
        <div className="quantum-glow-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center gap-2 text-base font-medium pb-3" style={{ color: 'var(--color-text-primary)', borderBottom: '1px solid color-mix(in srgb, var(--color-border) 30%, transparent)' }}>
            <Palette className="w-4 h-4 text-[#d0bcff]" />
            <span>Interface Theme</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {THEMES.map((t) => {
              const isActive = theme === t.id;
              return (
                <button
                  key={t.id}
                  onClick={() => setTheme(t.id)}
                  className={`relative text-left p-4 rounded-xl border transition-all cursor-pointer ${
                    isActive
                      ? 'ring-2 border-transparent shadow-lg'
                      : 'border-[var(--color-border)] hover:border-[var(--color-border)]/80'
                  }`}
                  style={{
                    backgroundColor: t.bg,
                    borderColor: isActive ? t.accent : undefined,
                    boxShadow: isActive ? `0 0 15px ${t.accent}40` : undefined,
                  }}
                >
                  {isActive && (
                    <CheckCircle2 className="absolute top-3 right-3 w-4 h-4" style={{ color: t.accent }} />
                  )}
                  {/* Mini Colour Swatch Row */}
                  <div className="flex gap-1.5 mb-3">
                    <span className="w-4 h-4 rounded-full border border-white/10" style={{ backgroundColor: t.accent }} />
                    {t.swatch2 ? (
                      <span className="w-4 h-4 rounded-full border border-white/10" style={{ backgroundColor: t.swatch2 }} />
                    ) : (
                      <span className="w-4 h-4 rounded-full border border-white/10" style={{ backgroundColor: t.bg === '#f6f4ef' ? '#ddd3c2' : '#2d2738' }} />
                    )}
                    <span className="w-4 h-4 rounded-full border border-white/10" style={{ backgroundColor: t.text }} />
                  </div>
                  <div className="text-xs font-bold mb-1" style={{ color: t.text }}>{t.label}</div>
                  <div className="text-[11px] leading-relaxed" style={{ color: t.text, opacity: 0.6 }}>{t.description}</div>
                </button>
              );
            })}
          </div>
        </div>

      </div>

    </div>
  );
};

