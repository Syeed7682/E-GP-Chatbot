import React from 'react';
import { ShieldCheck, Wifi, WifiOff, RefreshCw, Layers, ExternalLink, HelpCircle } from 'lucide-react';
import { SyncState } from '../types/egp';

interface GovernmentHeaderProps {
  syncState: SyncState;
  onOpenSyncModal: () => void;
  onToggleSimulatedOffline: () => void;
  onSyncNow: () => void;
}

export const GovernmentHeader: React.FC<GovernmentHeaderProps> = ({
  syncState,
  onOpenSyncModal,
  onToggleSimulatedOffline,
  onSyncNow
}) => {
  return (
    <header className="border-b border-emerald-950/40 bg-[#07130f] text-slate-100 sticky top-0 z-40 select-none shadow-md">
      {/* Top Govt Identity Bar */}
      <div className="bg-[#003822] text-xs py-1.5 px-4 border-b border-emerald-800/40 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2.5">
          {/* Bangladesh Govt Crest / Seal simulation */}
          <div className="w-5 h-5 rounded-full bg-[#006a4e] border border-amber-400 flex items-center justify-center text-[10px] text-amber-300 font-bold shadow-inner">
            ★
          </div>
          <span className="font-semibold text-emerald-100 tracking-wide">
            Government of the People's Republic of Bangladesh
          </span>
          <span className="hidden md:inline text-emerald-400/60">•</span>
          <span className="hidden md:inline text-emerald-200/90 font-medium">
            Central Procurement Technical Unit (CPTU) / IMED
          </span>
        </div>

        <div className="flex items-center gap-3 text-[11px] text-emerald-200/80">
          <span className="hidden sm:inline-flex items-center gap-1 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/50">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            Official e-GP Portal Manual (PE User 2026)
          </span>
          <span className="text-emerald-400 font-mono">PPR-2026 Comp.</span>
          <div className="border-l border-emerald-700/60 pl-2 flex items-center gap-1">
            <span className="text-amber-400 font-medium">EN</span>
            <span className="text-slate-500">|</span>
            <span className="text-emerald-300/70 hover:text-white cursor-pointer">বাং</span>
          </div>
        </div>
      </div>

      {/* Main Portal Bar */}
      <div className="px-4 py-2.5 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-emerald-900/60 border border-emerald-600/50 text-emerald-300 shadow-sm">
            <Layers className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-1.5">
                National e-Government Procurement System (e-GP)
                <span className="text-[10px] uppercase font-bold px-1.5 py-0.2 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded">
                  Official Assistant
                </span>
              </h1>
            </div>
            <p className="text-[11px] text-emerald-200/70">
              Procuring Entity Automated Guidance &amp; Offline-First Manual Sync
            </p>
          </div>
        </div>

        {/* Sync Controls & Status */}
        <div className="flex items-center gap-2">
          {/* Quick Simulated Offline Toggle */}
          <button
            onClick={onToggleSimulatedOffline}
            title={syncState.is_simulated_offline ? "Click to reconnect to server" : "Click to simulate offline mode"}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium border transition-colors ${
              syncState.is_simulated_offline
                ? 'bg-amber-950/60 text-amber-300 border-amber-600/60 hover:bg-amber-900/60'
                : 'bg-emerald-950/50 text-emerald-200 border-emerald-700/50 hover:bg-emerald-900/50'
            }`}
          >
            {syncState.is_simulated_offline ? (
              <>
                <WifiOff className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
                <span>Simulated Offline</span>
              </>
            ) : (
              <>
                <Wifi className="w-3.5 h-3.5 text-emerald-400" />
                <span>Online</span>
              </>
            )}
          </button>

          {/* Sync Status Button */}
          <button
            onClick={onOpenSyncModal}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium border transition-all ${
              syncState.pending_count > 0
                ? 'bg-amber-950/50 text-amber-200 border-amber-600/70'
                : 'bg-emerald-950/40 text-emerald-200 border-emerald-800/60 hover:border-emerald-600'
            }`}
          >
            {syncState.is_syncing ? (
              <RefreshCw className="w-3.5 h-3.5 text-emerald-300 animate-spin" />
            ) : (
              <div className={`w-2 h-2 rounded-full ${syncState.is_online ? (syncState.pending_count > 0 ? 'bg-amber-400' : 'bg-emerald-400') : 'bg-red-400'}`} />
            )}
            <span className="hidden sm:inline">
              {syncState.is_syncing ? 'Syncing...' : syncState.pending_count > 0 ? `${syncState.pending_count} Pending Sync` : 'Synced'}
            </span>
          </button>

          {/* Force Sync Button */}
          <button
            onClick={onSyncNow}
            disabled={!syncState.is_online || syncState.is_syncing}
            title="Trigger Immediate Sync with Server"
            className="p-1.5 text-emerald-300 hover:text-white bg-emerald-950/60 border border-emerald-800/60 rounded hover:bg-emerald-900/60 disabled:opacity-40 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncState.is_syncing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Marquee Banner */}
      <div className="bg-[#0b1c16] text-[11px] py-0.5 px-4 text-emerald-300/80 border-t border-emerald-950 flex items-center justify-between">
        <div className="flex items-center gap-2 overflow-hidden text-ellipsis whitespace-nowrap">
          <span className="font-bold text-amber-400 shrink-0">PORTAL NOTICE:</span>
          <span className="truncate">
            Official Procuring Entity User Manual (543 pages) indexed • Offline-First vector caching active • Checksum verification SHA-256 compliant.
          </span>
        </div>
        <div className="hidden lg:flex items-center gap-3 shrink-0 text-emerald-400/70 text-[10px]">
          <span>Server Ver: {syncState.server_version}</span>
          <span>•</span>
          <span>Indexed Chunks: 1,188</span>
        </div>
      </div>
    </header>
  );
};
