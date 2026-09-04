'use client';

import React from 'react';
import { InvestigationHistoryItem } from '@/types';
import { History, ShieldAlert, CheckCircle2 } from 'lucide-react';

interface HistoryTableProps {
  items: InvestigationHistoryItem[];
  onSelectItem?: (item: InvestigationHistoryItem) => void;
}

export const HistoryTable: React.FC<HistoryTableProps> = ({ items }) => {
  if (!items || items.length === 0) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 text-center text-slate-400 max-w-3xl w-full">
        <History className="w-8 h-8 mx-auto text-slate-600 mb-2" />
        <p className="text-sm">No previous investigations found in AWS DynamoDB.</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 max-w-3xl w-full text-left space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <History className="w-5 h-5 text-amber-400" />
          <h3 className="font-semibold text-slate-200 text-sm tracking-wide uppercase">
            Previous Investigations (AWS DynamoDB)
          </h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">{items.length} records</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="text-slate-400 border-b border-slate-800/80">
              <th className="pb-3 px-2 font-medium">TIME</th>
              <th className="pb-3 px-2 font-medium">NAMESPACE</th>
              <th className="pb-3 px-2 font-medium">ROOT CAUSE</th>
              <th className="pb-3 px-2 font-medium text-right">CONFIDENCE</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {items.map((item, idx) => (
              <tr key={item.id || idx} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3 px-2 text-slate-400 whitespace-nowrap">{item.timestamp}</td>
                <td className="py-3 px-2 text-amber-400 whitespace-nowrap">{item.namespace}</td>
                <td className="py-3 px-2 text-slate-200 font-sans font-medium">
                  <div className="flex items-center space-x-2">
                    {item.root_cause.toLowerCase().includes('healthy') || item.root_cause.toLowerCase().includes('no issue') ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                    ) : (
                      <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0" />
                    )}
                    <span className="truncate max-w-xs">{item.root_cause}</span>
                  </div>
                </td>
                <td className="py-3 px-2 text-right font-bold text-slate-300">{item.confidence}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
