'use client';

import React, { useState } from 'react';
import { Diagnosis } from '@/types';
import { Check, Copy, Terminal, ShieldAlert, CheckCircle2 } from 'lucide-react';

interface RootCauseCardProps {
  diagnosis: Diagnosis;
}

export const RootCauseCard: React.FC<RootCauseCardProps> = ({ diagnosis }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (diagnosis.kubectl_command) {
      navigator.clipboard.writeText(diagnosis.kubectl_command);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const rootCauseLower = diagnosis.root_cause.toLowerCase();
  const isHealthy =
    !rootCauseLower.includes('unhealthy') &&
    !rootCauseLower.includes('error') &&
    !rootCauseLower.includes('failed') &&
    !rootCauseLower.includes('crash') &&
    (rootCauseLower.includes('no issue') ||
     rootCauseLower.includes('no major issues') ||
     rootCauseLower.includes('healthy') ||
     rootCauseLower.includes('normal'));

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl max-w-3xl w-full text-left space-y-6">
      {/* Header Banner */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2.5 rounded-xl ${isHealthy ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}`}>
            {isHealthy ? <CheckCircle2 className="w-6 h-6" /> : <ShieldAlert className="w-6 h-6" />}
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">AI Diagnosis Result</h3>
            <p className="text-xs text-slate-400">Senior Kubernetes SRE Reasoning Engine</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 bg-slate-800/80 px-3.5 py-1.5 rounded-full border border-slate-700">
          <span className="text-xs text-slate-400">Confidence:</span>
          <span className="text-sm font-bold text-blue-400 font-mono">{diagnosis.confidence}%</span>
        </div>
      </div>

      {/* Healthy Cluster State Banner */}
      {isHealthy && (
        <div className="p-4 bg-emerald-950/40 border border-emerald-800/60 rounded-xl space-y-1">
          <h4 className="text-sm font-bold text-emerald-300">No critical Kubernetes issues detected.</h4>
          <p className="text-xs text-emerald-400/90">Cluster appears healthy. Workloads, services, and endpoints are running normally.</p>
        </div>
      )}

      {/* Root Cause Section */}
      <div className="space-y-1.5">
        <span className={`text-xs font-bold uppercase tracking-wider ${isHealthy ? 'text-emerald-400' : 'text-amber-400'}`}>Root Cause</span>
        <div className="text-base font-semibold text-slate-100 bg-slate-950/60 border border-slate-800 p-3.5 rounded-xl">
          {diagnosis.root_cause}
        </div>
      </div>

      {/* Explanation Section */}
      <div className="space-y-1.5">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Explanation</span>
        <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/30 p-3.5 rounded-xl border border-slate-800/60">
          {diagnosis.explanation}
        </p>
      </div>

      {/* Suggested Fix Section */}
      <div className="space-y-1.5">
        <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">Suggested Fix</span>
        <p className="text-sm text-slate-200 leading-relaxed bg-slate-950/30 p-3.5 rounded-xl border border-slate-800/60">
          {diagnosis.fix}
        </p>
      </div>

      {/* kubectl Command Section */}
      {diagnosis.kubectl_command && (
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center space-x-1.5">
              <Terminal className="w-3.5 h-3.5 inline" />
              <span>Recommended Command</span>
            </span>
            <button
              onClick={handleCopy}
              className="text-xs text-slate-400 hover:text-white flex items-center space-x-1 transition-colors px-2 py-1 bg-slate-800 rounded-md"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied!' : 'Copy'}</span>
            </button>
          </div>
          <pre className="bg-slate-950 border border-slate-800 p-4 rounded-xl font-mono text-sm text-emerald-300 overflow-x-auto">
            <code>{diagnosis.kubectl_command}</code>
          </pre>
        </div>
      )}

      {/* Prevention Note if present */}
      {diagnosis.prevention && (
        <div className="text-xs text-slate-400 border-t border-slate-800/80 pt-3">
          <span className="font-semibold text-slate-300">Prevention Tip: </span>
          {diagnosis.prevention}
        </div>
      )}
    </div>
  );
};
