import React from 'react';
import { ShieldCheck, BookOpen, Layers } from 'lucide-react';
import { OfflineIndicator } from '../offline/OfflineIndicator';
import { SyncManager } from '../offline/SyncManager';

interface HeaderProps {
  activeTab: 'chat' | 'manual' | 'screens';
  onTabChange: (tab: 'chat' | 'manual' | 'screens') => void;
  onOpenInspector?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onTabChange,
  onOpenInspector
}) => {
  return (
    <header className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 sticky top-0 z-30 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Left: Official Emblem & Title */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-700 text-white flex items-center justify-center font-bold shadow-sm">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold text-slate-900 dark:text-white leading-tight">
                e-GP Official Manual Assistant
              </h1>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300">
                PE Grounded
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Procuring Entity User Guidelines • 543 Pages • PPR-2008
            </p>
          </div>
        </div>

        {/* Center: Navigation Tabs */}
        <div className="hidden md:flex items-center gap-1 bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl">
          <button
            onClick={() => onTabChange('chat')}
            className={`px-3.5 py-1.5 text-xs font-medium rounded-lg transition-colors cursor-pointer ${
              activeTab === 'chat'
                ? 'bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 shadow-2xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            Chat Assistant
          </button>
          <button
            onClick={() => onTabChange('manual')}
            className={`px-3.5 py-1.5 text-xs font-medium rounded-lg transition-colors cursor-pointer ${
              activeTab === 'manual'
                ? 'bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 shadow-2xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            Manual Viewer (543 Pages)
          </button>
          <button
            onClick={() => onTabChange('screens')}
            className={`px-3.5 py-1.5 text-xs font-medium rounded-lg transition-colors cursor-pointer ${
              activeTab === 'screens'
                ? 'bg-white dark:bg-slate-900 text-emerald-700 dark:text-emerald-400 shadow-2xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            Portal Screens
          </button>
        </div>

        {/* Right: Offline Status & Sync */}
        <div className="flex items-center gap-3">
          <OfflineIndicator />
          <SyncManager onOpenInspector={onOpenInspector} />
        </div>
      </div>
    </header>
  );
};

