import React from 'react';
import { Plus, Trash2, Download, Clock3, X } from 'lucide-react';
import { ChatMessage, SyncState } from '../types/egp';
import { API_BASE } from '../services/api';

interface GovtOfficialSidebarProps { syncState: SyncState; isMobileOpen: boolean; onCloseMobile: () => void; history: ChatMessage[]; onDeleteHistoryItem: (id: string) => void; onSelectHistoryItem: (message: ChatMessage) => void; onNewChat: () => void; onClearConversation: () => void; language: 'en' | 'bn'; onOpenSyncModal: () => void; }

export const GovtOfficialSidebar: React.FC<GovtOfficialSidebarProps> = ({ isMobileOpen, onCloseMobile, history, onDeleteHistoryItem, onSelectHistoryItem, onNewChat, onClearConversation, language }) => {
  const historyItems = history.filter((m) => m.sender === 'user' && m.text.trim()).slice().reverse().slice(0, 20);
  const formatDate = (timestamp: number) => new Intl.DateTimeFormat(language === 'bn' ? 'bn-BD' : 'en-BD', { dateStyle: 'medium', timeStyle: 'short' }).format(timestamp);
  return <>
    {isMobileOpen && <button type="button" className="fixed inset-0 z-40 bg-slate-950/45 md:hidden" onClick={onCloseMobile} aria-label="Dismiss manual topics menu backdrop" />}
    <aside aria-label="Manual topics and actions" className={`glass-sidebar fixed inset-y-0 left-0 z-50 flex w-[min(20rem,88vw)] flex-col gap-4 overflow-y-auto border-r border-[#DCE5E0] bg-[#EAF1EC] p-4 text-xs shadow-2xl transition-transform md:static md:w-80 md:translate-x-0 md:shadow-none ${isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
      <div className="flex items-center justify-between border-b border-slate-200 pb-2 md:hidden"><span className="font-semibold text-slate-800">Manual topics</span><button type="button" onClick={onCloseMobile} aria-label="Close manual topics menu"><X className="h-5 w-5" /></button></div>
      <button onClick={() => { onNewChat(); onCloseMobile(); }} className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#176B3A] to-[#183153] px-3 py-3 font-semibold !text-white"><Plus className="h-4 w-4" />New Consultation</button>
      <div className="glass-panel space-y-2 rounded-2xl border border-[#DCE5E0] bg-white p-3.5 shadow-sm"><div className="flex items-center gap-1.5 border-b border-slate-100 pb-2 font-bold text-[#183153]"><Clock3 className="h-3.5 w-3.5 text-[#176B3A]" />Chat History</div><div className="max-h-64 space-y-1.5 overflow-y-auto pr-1">{historyItems.length === 0 && <p className="p-2 text-[11px] text-slate-500">No chat history yet.</p>}{historyItems.map((m) => <div key={m.id} className="flex items-start gap-1 rounded-xl border border-slate-100 bg-slate-50/80 p-2.5"><button type="button" className="min-w-0 flex-1 text-left" onClick={() => { onSelectHistoryItem(m); onCloseMobile(); }} title="Open this conversation"><p className="truncate text-[11.5px] text-slate-700">{m.text}</p><time className="mt-1 block text-[10px] text-slate-400" dateTime={new Date(m.timestamp).toISOString()}>{formatDate(m.timestamp)}</time></button><button type="button" className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-700" onClick={() => onDeleteHistoryItem(m.id)} aria-label={`Delete chat: ${m.text}`} title="Delete this chat"><Trash2 className="h-3.5 w-3.5" /></button></div>)}</div></div>
      <a href={`${API_BASE}/api/manual/download`} download className="flex w-full items-center justify-center gap-2 rounded-lg border border-[#176B3A]/20 bg-white/70 px-3 py-2.5 font-semibold text-[#176B3A]"><Download className="h-4 w-4" />Download Full Manual</a>
      <div className="mt-auto border-t border-slate-200 pt-2"><button onClick={onClearConversation} className="flex w-full items-center justify-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 font-medium text-slate-600"><Trash2 className="h-3.5 w-3.5" />Clear Conversation</button></div>
    </aside>
  </>;
};
