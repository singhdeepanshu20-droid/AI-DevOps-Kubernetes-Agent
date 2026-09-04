'use client';

import React from 'react';
import { UserSession } from '@/types';
import { ShieldCheck, LogIn, LogOut, Cpu } from 'lucide-react';

interface HeaderProps {
  user: UserSession | null;
  onOpenAuth: () => void;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({ user, onOpenAuth, onLogout }) => {
  return (
    <header className="glass-header px-6 py-3.5 sticky top-0 z-40">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-amber-500 via-orange-500 to-amber-600 flex items-center justify-center font-black text-white shadow-lg shadow-amber-500/20 text-sm tracking-tight border border-amber-400/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-extrabold text-base tracking-tight text-white block">
              AI Kubernetes Agent
            </span>
            <span className="text-[11px] text-amber-400/90 block font-mono font-medium">
              AWS Bedrock • AWS Cognito • AWS DynamoDB
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {user ? (
            <div className="flex items-center space-x-3 bg-slate-900/90 border border-slate-700/80 px-3.5 py-1.5 rounded-full text-sm shadow-sm backdrop-blur-md">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span className="text-slate-200 font-medium text-xs font-mono">{user.email}</span>
              <button
                onClick={onLogout}
                className="text-slate-400 hover:text-red-400 transition-colors ml-1 p-1"
                title="Sign out (Cognito)"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white rounded-full text-xs font-semibold transition-all shadow-md shadow-amber-600/20 active:scale-95"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Sign In (AWS Cognito)</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
