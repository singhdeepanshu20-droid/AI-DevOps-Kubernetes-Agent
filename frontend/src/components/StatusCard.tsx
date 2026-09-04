import React from 'react';

interface StatusCardProps {
  status: string;
}

export const StatusCard: React.FC<StatusCardProps> = ({ status }) => {
  return (
    <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium">
      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
      <span>System Status: {status}</span>
    </div>
  );
};
