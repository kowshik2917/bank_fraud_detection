import React from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle, AlertOctagon } from 'lucide-react';

export const RiskBadge = ({ level = 'LOW', score = null, size = 'md' }) => {
  const lvl = level ? level.toUpperCase() : 'LOW';

  const configs = {
    CRITICAL: {
      bg: 'bg-red-950/80 border-red-800/80 text-red-400',
      dot: 'bg-red-500',
      icon: AlertOctagon,
      label: 'CRITICAL',
    },
    HIGH: {
      bg: 'bg-orange-950/80 border-orange-800/80 text-orange-400',
      dot: 'bg-orange-500',
      icon: ShieldAlert,
      label: 'HIGH',
    },
    MEDIUM: {
      bg: 'bg-yellow-950/80 border-yellow-800/80 text-yellow-400',
      dot: 'bg-yellow-500',
      icon: AlertTriangle,
      label: 'MEDIUM',
    },
    LOW: {
      bg: 'bg-emerald-950/80 border-emerald-800/80 text-emerald-400',
      dot: 'bg-emerald-500',
      icon: ShieldCheck,
      label: 'LOW',
    },
  };

  const config = configs[lvl] || configs.LOW;
  const Icon = config.icon;

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-medium',
    lg: 'text-sm px-3 py-1.5 gap-2 font-semibold',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border ${config.bg} ${
        sizeClasses[size] || sizeClasses.md
      }`}
    >
      <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
      <span>{config.label}</span>
      {score !== null && (
        <span className="ml-1 px-1.5 py-0.2 rounded bg-black/40 text-[10px] font-mono">
          {score}
        </span>
      )}
    </span>
  );
};

export default RiskBadge;
