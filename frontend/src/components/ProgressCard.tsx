'use client';

import React from 'react';
import { CheckCircle2, Loader2, Circle } from 'lucide-react';

interface ProgressCardProps {
  steps: string[];
  currentIndex: number;
}

export const ProgressCard: React.FC<ProgressCardProps> = ({ steps, currentIndex }) => {
  // Only display the initial scan/reasoning steps (filtering out step index 6 "Root Cause Found")
  const activeSteps = steps.slice(0, 6);

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl max-w-lg w-full text-left space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="font-semibold text-amber-400 text-sm tracking-wide flex items-center space-x-2">
          <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
          <span>Investigating Kubernetes Cluster...</span>
        </h3>
        <span className="text-xs px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 font-mono animate-pulse">
          Live Scanning
        </span>
      </div>

      <div className="space-y-3 font-mono text-sm">
        {activeSteps.map((step, idx) => {
          const isCompleted = idx < currentIndex;
          const isCurrent = idx === currentIndex;

          return (
            <div
              key={step}
              className={`flex items-center space-x-3 transition-colors duration-300 ${
                isCompleted
                  ? 'text-emerald-400'
                  : isCurrent
                  ? 'text-blue-400 font-semibold'
                  : 'text-slate-600'
              }`}
            >
              {isCompleted ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
              ) : isCurrent ? (
                <Loader2 className="w-5 h-5 text-blue-400 animate-spin flex-shrink-0" />
              ) : (
                <Circle className="w-5 h-5 text-slate-700 flex-shrink-0" />
              )}
              <span>{step}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
