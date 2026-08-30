import React from 'react';
import { Users, FileText, Sparkles } from 'lucide-react';

interface FooterProps {
  onSelectTab?: (tab: string) => void;
  onOpenReport?: () => void;
}

export const Footer: React.FC<FooterProps> = ({ onSelectTab, onOpenReport }) => {
  return (
    <footer className="bg-[var(--color-bg-primary)] border-t border-[var(--color-border)]/30 text-[var(--color-text-muted)] pt-10 pb-8 px-6 mt-16">
      <div className="max-w-[1440px] mx-auto space-y-8">
        
        {/* Simple 2-column layout: Our Team & Documentation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pb-8 border-b border-[var(--color-border)]/20 text-xs">
          
          {/* Column 1: Our Team */}
          <div className="bg-[var(--color-bg-tertiary)]/60 border border-[var(--color-border)]/40 rounded-xl p-5 space-y-3">
            <div className="flex items-center gap-2 font-semibold text-[#ffb59e] uppercase tracking-wider text-xs font-mono">
              <Users className="w-4 h-4 text-[#ff5719]" />
              <span>Our Team</span>
            </div>
            <p className="text-xs text-[var(--color-text-muted)]/80 leading-relaxed font-mono">
              Designed & Developed by the Quantum Route Optimization Engineering Team. Specializing in Delta-Potential Particle Swarm Optimization, Real-Time Telemetry & Traffic Graph Routing.
            </p>
          </div>

          {/* Column 2: Documentation */}
          <div className="bg-[var(--color-bg-tertiary)]/60 border border-[var(--color-border)]/40 rounded-xl p-5 space-y-3">
            <div className="flex items-center gap-2 font-semibold text-[#ffb59e] uppercase tracking-wider text-xs font-mono">
              <FileText className="w-4 h-4 text-[#9dcaff]" />
              <span>Documentation</span>
            </div>
            <div className="flex flex-wrap gap-4 text-xs font-mono pt-1">
              <button
                onClick={() => onSelectTab && onSelectTab('qpso-implementation')}
                className="text-[#9dcaff] hover:underline flex items-center gap-1 cursor-pointer"
              >
                <Sparkles className="w-3.5 h-3.5 text-[#9dcaff]" />
                <span>QPSO Implementation & Mathematical Formulations</span>
              </button>
              {onOpenReport && (
                <button
                  onClick={onOpenReport}
                  className="text-[#ffb59e] hover:underline flex items-center gap-1 cursor-pointer"
                >
                  <span>📄 Download Route Audit Report</span>
                </button>
              )}
            </div>
          </div>

        </div>

        {/* Copyright */}
        <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-[var(--color-text-muted)]/60 font-mono gap-4">
          <p>© 2026 Quantum Route Optimization Platform. All rights reserved.</p>
          <div className="text-[11px] text-[#ffb59e]">
            Powered by Quantum-Behaved Swarm Engine
          </div>
        </div>

      </div>
    </footer>
  );
};
