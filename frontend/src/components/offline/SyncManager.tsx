import React, { useState } from 'react';
import { RefreshCw, CheckCircle, Database } from 'lucide-react';
import { triggerBackgroundSync } from '../../services/syncService';

interface SyncManagerProps {
  onOpenInspector?: () => void;
}

export const SyncManager: React.FC<SyncManagerProps> = ({ onOpenInspector }) => {
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<string>('Just now');

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      await triggerBackgroundSync();
      setLastSyncTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    } catch (err) {
      console.warn('Sync notice:', err);
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <div className="flex items-center gap-2 text-xs">
      <button
        onClick={handleSync}
        disabled={isSyncing}
        title="Sync manual index with central server"
        className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors cursor-pointer"
      >
        <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin text-emerald-600' : ''}`} />
        <span>{isSyncing ? 'Syncing...' : 'Sync Data'}</span>
      </button>

      {onOpenInspector && (
        <button
          onClick={onOpenInspector}
          title="Inspect IndexedDB offline cache"
          className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
        >
          <Database className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};

