import React from 'react';
import { Zap } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

interface NavbarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  onStartOptimization: () => void;
  onOpenReport?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, onSelectTab, onStartOptimization, onOpenReport }) => {

  const navLinks = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'live-simulation', label: 'Live Simulation' },
    { id: 'optimization-engine', label: 'Optimization Engine' },
    { id: 'qpso-implementation', label: 'QPSO Implementation' },
    { id: 'system-settings', label: 'System Settings' }
  ];

  return (
    <header className="sticky top-0 z-50 px-6 py-3 backdrop-blur-md" style={{ backgroundColor: 'var(--color-bg-primary)', borderBottom: '1px solid color-mix(in srgb, var(--color-border) 30%, transparent)' }}>
      <div className="max-w-[1440px] mx-auto flex items-center justify-between">
        
        {/* Brand logo & Wordmark */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => onSelectTab('dashboard')}>
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#ff5719] to-[#ffb59e] p-0.5 flex items-center justify-center shadow-lg shadow-[#ff5719]/20">
            <div className="w-full h-full rounded-[7px] flex items-center justify-center" style={{ backgroundColor: 'var(--color-bg-primary)' }}>
              {/* Hexagonal 6-node glyph with bolt */}
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L20 7V17L12 22L4 17V7L12 2Z" stroke="#ffb59e" strokeWidth="1.5" strokeLinejoin="round"/>
                <circle cx="12" cy="2" r="1.5" fill="#ff5719" />
                <circle cx="20" cy="7" r="1.5" fill="#ffb59e" />
                <circle cx="20" cy="17" r="1.5" fill="#ff5719" />
                <circle cx="12" cy="22" r="1.5" fill="#ffb59e" />
                <circle cx="4" cy="17" r="1.5" fill="#ff5719" />
                <circle cx="4" cy="7" r="1.5" fill="#ffb59e" />
                <path d="M13 6L9 13H14L11 18" stroke="#ff5719" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-lg tracking-tight" style={{ color: 'var(--color-text-primary)' }}>Quantum Route</span>
          </div>
        </div>

        {/* Center-left Nav Links */}
        <nav className="hidden md:flex items-center gap-6">
          {navLinks.map((link) => {
            const isActive = currentTab === link.id;
            return (
              <button
                key={link.id}
                onClick={() => onSelectTab(link.id)}
                className={`text-sm font-medium transition-colors ${isActive ? 'font-semibold border-b-2 pb-1' : ''}`}
                style={isActive ? { color: 'var(--color-accent-soft)', borderColor: 'var(--color-accent-soft)' } : { color: 'color-mix(in srgb, var(--color-text-muted) 70%, transparent)' }}
              >
                {link.label}
              </button>
            );
          })}
        </nav>

        {/* Right Cluster */}
        <div className="flex items-center gap-3">
          {onOpenReport && (
            <button
              onClick={onOpenReport}
              className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg transition" style={{ border: '1px solid color-mix(in srgb, var(--color-accent) 60%, transparent)', color: 'var(--color-accent-soft)' }}
              title="View & Download Route Audit Report"
            >
              <span>📄 Report</span>
            </button>
          )}

          <ThemeToggle />

          <button
            onClick={onStartOptimization}
            className="btn-ember-gradient px-4 py-2 text-xs uppercase tracking-wider flex items-center gap-1.5"
          >
            <Zap className="w-3.5 h-3.5 fill-white" />
            <span>Start Optimization</span>
          </button>
        </div>

      </div>
    </header>
  );
};
