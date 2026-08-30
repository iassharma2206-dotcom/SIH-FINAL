import React from 'react';

interface HyperparameterSliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  description: string;
  onChange: (val: number) => void;
}

export const HyperparameterSlider: React.FC<HyperparameterSliderProps> = ({
  label,
  value,
  min,
  max,
  step = 1,
  description,
  onChange
}) => {
  return (
    <div className="mb-5 bg-[var(--color-bg-primary)] border border-[var(--color-border)]/50 p-4 rounded-xl">
      <div className="flex items-center justify-between mb-2">
        <label className="text-xs font-mono font-semibold uppercase text-[#ffb59e] tracking-wider">
          {label}
        </label>
        <span className="text-xs font-mono font-bold text-[var(--color-text-primary)] bg-[var(--color-bg-quaternary)] px-2.5 py-1 rounded-md border border-[var(--color-border)]">
          {value}
        </span>
      </div>

      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full accent-[#ffb59e] bg-[var(--color-bg-quaternary)] h-2 rounded-lg cursor-pointer my-2"
      />

      <p className="text-[11px] text-[var(--color-text-muted)]/70 mt-1">{description}</p>
    </div>
  );
};
