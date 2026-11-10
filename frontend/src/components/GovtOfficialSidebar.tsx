import React, { useMemo, useState } from 'react';
import {
  Plus,
  HelpCircle,
  Trash2,
  Search,
  ChevronRight,
  Download,
  X,
} from 'lucide-react';
import { SyncState } from '../types/egp';
import { API_BASE } from '../services/api';
import {
  MANUAL_QUESTION_SUGGESTIONS,
  searchManualQuestionSuggestions,
} from '../utils/manualQuestionSuggestions';

interface GovtOfficialSidebarProps {
  syncState: SyncState;
  isMobileOpen: boolean;
  onCloseMobile: () => void;
  onSelectSuggestedQuestion: (question: string) => void;
  onNewChat: () => void;
  onClearConversation: () => void;
  language: 'en' | 'bn';
  onOpenSyncModal: () => void;
}

export const GovtOfficialSidebar: React.FC<GovtOfficialSidebarProps> = ({
  syncState,
  isMobileOpen,
  onCloseMobile,
  onSelectSuggestedQuestion,
  onNewChat,
  onClearConversation,
  language,
  onOpenSyncModal
}) => {
  const [suggestionQuery, setSuggestionQuery] = useState('');
  const hasQuery = suggestionQuery.trim().length > 0;
  const matchingSuggestions = useMemo(
    () => searchManualQuestionSuggestions(suggestionQuery),
    [suggestionQuery],
  );
  const visibleSuggestions = hasQuery
    ? matchingSuggestions.slice(0, 30)
    : MANUAL_QUESTION_SUGGESTIONS.slice(0, 12);
  const totalVisibleCount = hasQuery
    ? matchingSuggestions.length
    : MANUAL_QUESTION_SUGGESTIONS.length;

  return (
    <>
    {isMobileOpen && (
      <button
        type="button"
        className="fixed inset-0 z-40 bg-slate-950/45 backdrop-blur-[2px] md:hidden"
        onClick={onCloseMobile}
        aria-label="Dismiss manual topics menu backdrop"
      />
    )}
    <aside
      aria-label="Manual topics and actions"
      className={`fixed inset-y-0 left-0 z-50 flex w-[min(20rem,88vw)] shrink-0 select-none flex-col gap-4 overflow-y-auto border-r border-white/60 bg-white/95 p-4 pt-[max(1rem,env(safe-area-inset-top))] text-xs shadow-2xl backdrop-blur-xl transition-transform duration-200 md:static md:z-auto md:h-auto md:min-h-0 md:w-80 md:translate-x-0 md:bg-white/30 md:pt-4 md:shadow-none ${
      isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
    }`}>
      <div className="flex items-center justify-between border-b border-slate-200 pb-2 md:hidden">
        <span className="font-semibold text-slate-800">Manual topics</span>
        <button
          type="button"
          onClick={onCloseMobile}
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-600 hover:bg-slate-100"
          aria-label="Close manual topics menu"
        >
          <X className="h-5 w-5" />
        </button>
      </div>
      {/* 1. New Chat Action */}
      <button
        onClick={() => {
          onNewChat();
          onCloseMobile();
        }}
        className="w-full flex items-center justify-center gap-2 py-2.5 px-3 bg-gradient-to-r from-[#0B4F8A] to-[#12304A] hover:from-[#083c6b] hover:to-[#0f2438] text-white rounded-lg font-semibold text-xs shadow-sm transition-all cursor-pointer hover:scale-101 active:scale-99"
        aria-label="Start a new chat session"
      >
        <Plus className="w-4 h-4" />
        <span>{language === 'en' ? 'New Consultation' : 'নতুন কথোপকথন'}</span>
      </button>

      {/* 2. Suggested Questions */}
      <div className="border border-white/70 rounded-xl bg-white/40 backdrop-blur-md p-3.5 space-y-2.5 shadow-2xs">
        <div className="flex items-center justify-between border-b border-slate-200 pb-2">
          <div className="flex items-center gap-1.5 font-bold text-[#0F172A]">
            <Search className="w-3.5 h-3.5 text-[#0B4F8A]" />
            <span>{language === 'en' ? 'Questions from the Manual' : 'ম্যানুয়াল থেকে প্রশ্ন'}</span>
          </div>
          <span className="text-[10px] font-mono font-bold text-slate-500 bg-slate-200/60 px-1.5 py-0.2 rounded">
            {language === 'en' ? `${MANUAL_QUESTION_SUGGESTIONS.length} questions` : `${MANUAL_QUESTION_SUGGESTIONS.length}টি প্রশ্ন`}
          </span>
        </div>

        <form
          className="flex gap-1.5"
          onSubmit={(event) => {
            event.preventDefault();
            setSuggestionQuery(suggestionQuery.trim());
          }}
        >
          <input
            type="search"
            value={suggestionQuery}
            onChange={(event) => setSuggestionQuery(event.target.value)}
            placeholder={language === 'en' ? 'Search by word or question...' : 'শব্দ বা প্রশ্ন দিয়ে খুঁজুন...'}
            aria-label="Search suggested manual questions"
            className="min-w-0 flex-1 rounded-lg border border-slate-300 bg-white/80 px-2.5 py-2 text-[11px] text-slate-800 outline-none placeholder:text-slate-400 focus:border-[#0B4F8A] focus:ring-2 focus:ring-blue-500/20"
          />
          <button
            type="submit"
            className="inline-flex shrink-0 items-center gap-1 rounded-lg bg-[#0B4F8A] px-2.5 py-2 text-[11px] font-semibold text-white transition-colors hover:bg-[#083c6b]"
          >
            <Search className="h-3.5 w-3.5" />
            <span>{language === 'en' ? 'Search' : 'খুঁজুন'}</span>
          </button>
        </form>

        <p className="text-[10px] text-slate-500" aria-live="polite">
          {hasQuery
            ? language === 'en'
              ? `${totalVisibleCount} matching suggestions${totalVisibleCount > 30 ? ' · showing first 30' : ''}`
              : `${totalVisibleCount}টি মিলেছে${totalVisibleCount > 30 ? ' · প্রথম ৩০টি দেখানো হচ্ছে' : ''}`
            : language === 'en'
              ? `Browse ${MANUAL_QUESTION_SUGGESTIONS.length} topics from the manual`
              : `ম্যানুয়ালের ${MANUAL_QUESTION_SUGGESTIONS.length}টি বিষয় দেখুন`}
        </p>

        <div className="max-h-64 space-y-1.5 overflow-y-auto pt-0.5 pr-1">
          {visibleSuggestions.map((suggestion) => {
            return (
              <button
                key={`${suggestion.page}-${suggestion.question}`}
                onClick={() => {
                  onSelectSuggestedQuestion(suggestion.question);
                  onCloseMobile();
                }}
                className="w-full text-left p-2.5 rounded-lg bg-white hover:bg-blue-50/70 border border-slate-200 hover:border-[#0B4F8A] text-slate-700 hover:text-[#0B4F8A] font-medium transition-all flex items-start gap-2 cursor-pointer leading-snug shadow-2xs hover:scale-101"
              >
                <ChevronRight className="w-3.5 h-3.5 text-[#0B4F8A] shrink-0 mt-0.5" />
                <span className="text-[11.5px]">
                  {suggestion.question}
                  <span className="ml-1 block pt-0.5 text-[10px] font-normal text-slate-400">
                    Manual page {suggestion.page}
                  </span>
                </span>
              </button>
            );
          })}
          {hasQuery && matchingSuggestions.length === 0 && (
            <p className="rounded-lg bg-white/70 p-3 text-[11px] leading-relaxed text-slate-500">
              {language === 'en'
                ? 'No matching manual topics. Try a shorter keyword or a different phrase.'
                : 'ম্যানুয়ালে মেলেনি। ছোট শব্দ বা অন্য বাক্যাংশ দিয়ে খুঁজুন।'}
            </p>
          )}
        </div>
      </div>

      <a
        href={`${API_BASE}/api/manual/download`}
        className="flex w-full items-center justify-center gap-2 rounded-lg border border-[#0B4F8A]/20 bg-white/70 px-3 py-2.5 text-xs font-semibold text-[#0B4F8A] shadow-2xs transition-colors hover:border-[#0B4F8A] hover:bg-blue-50"
      >
        <Download className="h-4 w-4" />
        <span>{language === 'en' ? 'Download Full Manual' : 'সম্পূর্ণ ম্যানুয়াল ডাউনলোড'}</span>
      </a>

      {/* Clear Conversation Action */}
      <div className="mt-auto pt-2 border-t border-slate-200">
        <button
          onClick={onClearConversation}
          className="w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-slate-50 hover:bg-red-50 text-slate-600 hover:text-red-700 border border-slate-200 hover:border-red-300 font-medium text-xs transition-colors cursor-pointer"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>{language === 'en' ? 'Clear Conversation' : 'কথোপকথন মুছুন'}</span>
        </button>
      </div>
    </aside>
    </>
  );
};
