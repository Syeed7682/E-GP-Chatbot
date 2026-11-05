import React, { useRef } from 'react';
import {
  ShoppingCart,
  Clock,
  Search,
  FileText,
  FileSpreadsheet,
  Workflow,
  BarChart3,
  Trash2,
  Upload,
  X,
  HelpCircle,
  Database,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { SyncState } from '../types/egp';

interface SidebarProps {
  syncState: SyncState;
  onSelectQuickQuestion: (question: string) => void;
  onClearConversation: () => void;
  uploadedImage: { base64: string; name: string; mime: string } | null;
  onImageSelected: (image: { base64: string; name: string; mime: string } | null) => void;
  onOpenSyncModal: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  syncState,
  onSelectQuickQuestion,
  onClearConversation,
  uploadedImage,
  onImageSelected,
  onOpenSyncModal
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const quickQuestions = [
    {
      icon: Search,
      label: 'How to open / create a PE account?',
      query: 'How to open / create a PE account?'
    },
    {
      icon: FileSpreadsheet,
      label: 'How does a user log in to e-GP?',
      query: 'How does a user log in to e-GP?'
    },
    {
      icon: FileText,
      label: 'Annual Procurement Plan (APP) guide',
      query: 'Annual Procurement Plan (APP) guide'
    },
    {
      icon: Workflow,
      label: 'How to view Approved Workflow?',
      query: 'How to view Approved Workflow?'
    },
    {
      icon: BarChart3,
      label: 'Proposal evaluation procedure',
      query: 'Proposal evaluation procedure'
    },
    {
      icon: Trash2,
      label: 'How to delete a tender?',
      query: 'How to delete a tender?'
    }
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please upload a valid image file (PNG, JPG, or WEBP)');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const base64 = event.target?.result as string;
      onImageSelected({
        base64,
        name: file.name,
        mime: file.type
      });
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  return (
    <aside className="w-72 md:w-80 bg-[#0d151c] text-slate-200 border-r border-slate-800 flex flex-col h-full shrink-0 select-none overflow-y-auto">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-blue-600/20 border border-blue-500/40 text-blue-400 shadow-md">
            <ShoppingCart className="w-6 h-6 text-blue-400" />
            <div className="absolute -bottom-1 -right-1 bg-amber-400 text-slate-900 rounded-full p-0.5">
              <Clock className="w-3 h-3" />
            </div>
          </div>
          <div>
            <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
              e-GP Guide
            </h2>
            <p className="text-xs text-slate-400">
              Procuring Entity System Manual
            </p>
          </div>
        </div>
      </div>

      <div className="p-3.5 space-y-4 flex-1">
        {/* System Status Card */}
        <div className="bg-[#12221e] border border-emerald-800/40 rounded-xl p-3 text-xs space-y-1.5 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-medium">
              <span className={`w-2.5 h-2.5 rounded-full ${syncState.is_online ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
              <span className={syncState.is_online ? 'text-emerald-300' : 'text-amber-300 font-semibold'}>
                {syncState.is_online ? 'System Ready' : 'Offline Mode (Local Vector)'}
              </span>
            </div>
            <span className="text-[10px] text-emerald-400/80 bg-emerald-950 px-1.5 py-0.5 rounded border border-emerald-800/60 font-mono">
              v2026.2
            </span>
          </div>

          <div className="text-slate-300 flex items-center gap-1.5 pt-0.5">
            <span className="text-slate-400">📑</span>
            <span className="text-slate-200 font-medium">Manual:</span>
            <span className="text-emerald-300 truncate">Procuring Entity User</span>
          </div>

          <div className="text-slate-300 flex items-center justify-between pt-0.5">
            <div className="flex items-center gap-1.5">
              <span className="text-slate-400">📂</span>
              <span className="text-slate-200 font-medium">Verified Chunks:</span>
              <span className="text-emerald-300 font-bold">{syncState.total_synced_count}</span>
            </div>
            {syncState.pending_count > 0 && (
              <span className="text-[10px] text-amber-300 bg-amber-950/80 px-1.5 py-0.5 rounded border border-amber-800/50">
                {syncState.pending_count} to sync
              </span>
            )}
          </div>
        </div>

        {/* Quick Questions Section */}
        <div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-300 uppercase tracking-wider mb-2 px-1">
            <span>💡</span>
            <span>Quick Questions</span>
          </div>
          <div className="space-y-1.5">
            {quickQuestions.map((q, idx) => {
              const Icon = q.icon;
              return (
                <button
                  key={idx}
                  onClick={() => onSelectQuickQuestion(q.query)}
                  className="w-full text-left p-2.5 rounded-lg text-xs font-medium text-slate-300 bg-slate-900/60 hover:bg-slate-800/90 border border-slate-800 hover:border-slate-700 transition-all flex items-center justify-between group cursor-pointer"
                >
                  <div className="flex items-center gap-2 truncate pr-2">
                    <Icon className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-400 shrink-0" />
                    <span className="truncate group-hover:text-white">{q.label}</span>
                  </div>
                  <ArrowRight className="w-3 h-3 text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                </button>
              );
            })}
          </div>
        </div>

        {/* Upload Screenshot (Optional) */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3 text-xs space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 font-semibold text-slate-200">
              <span>📷</span>
              <span>Upload Screenshot</span>
              <span className="text-[10px] font-normal text-slate-400">(Optional)</span>
            </div>
            <button
              title="Upload portal error screen for multimodal diagnostic"
              className="text-slate-500 hover:text-slate-300"
            >
              <HelpCircle className="w-3.5 h-3.5" />
            </button>
          </div>

          <p className="text-[11px] text-slate-400">
            Have an e-GP portal screenshot or error?
          </p>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="image/png,image/jpeg,image/webp"
            className="hidden"
          />

          {!uploadedImage ? (
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border border-dashed border-slate-700 hover:border-blue-500/60 rounded-lg p-3 text-center cursor-pointer transition-colors bg-slate-950/40 hover:bg-blue-950/20"
            >
              <button
                type="button"
                className="w-full flex items-center justify-center gap-2 py-1.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-medium border border-slate-700 transition-colors pointer-events-none"
              >
                <Upload className="w-3.5 h-3.5 text-blue-400" />
                <span>Upload</span>
              </button>
              <span className="text-[10px] text-slate-500 block mt-1.5">
                200MB per file • PNG, JPG
              </span>
            </div>
          ) : (
            <div className="bg-slate-950 border border-blue-500/40 rounded-lg p-2 space-y-2">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs text-blue-300 font-medium truncate">
                  {uploadedImage.name}
                </span>
                <button
                  onClick={() => onImageSelected(null)}
                  className="text-slate-400 hover:text-red-400 p-0.5 rounded"
                  title="Remove image"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="relative rounded overflow-hidden max-h-28 border border-slate-800">
                <img
                  src={uploadedImage.base64}
                  alt="Uploaded Portal Screen"
                  className="w-full h-auto object-cover"
                />
              </div>
              <div className="flex items-center justify-between text-[10px] text-slate-400">
                <span className="text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Attached for multimodal analysis
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Clear Conversation */}
        <button
          onClick={onClearConversation}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-medium text-slate-400 hover:text-red-300 bg-slate-900/40 hover:bg-red-950/30 border border-slate-800/80 hover:border-red-900/50 transition-colors cursor-pointer"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Clear Conversation</span>
        </button>
      </div>

      {/* Offline Data Sync Status Footer */}
      <div className="p-3 border-t border-slate-800/90 bg-[#0a1015] text-[11px]">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <div className="flex items-center gap-1.5">
            <Database className="w-3 h-3 text-emerald-400" />
            <span className="font-semibold text-slate-300">Offline-First Store:</span>
          </div>
          <span className="text-emerald-400 font-mono text-[10px]">IndexedDB</span>
        </div>

        <div className="flex items-center justify-between text-slate-400 text-[10px]">
          <span>Sync Outbox Queue:</span>
          <span className={syncState.pending_count > 0 ? 'text-amber-400 font-bold' : 'text-slate-300'}>
            {syncState.pending_count} pending
          </span>
        </div>

        <button
          onClick={onOpenSyncModal}
          className="mt-2 w-full py-1 px-2 rounded bg-slate-800/80 hover:bg-emerald-950 text-emerald-300 hover:text-emerald-200 border border-slate-700 hover:border-emerald-700/60 text-[11px] font-medium text-center transition-colors"
        >
          Open Sync Inspector &amp; Hash Logs →
        </button>
      </div>
    </aside>
  );
};
