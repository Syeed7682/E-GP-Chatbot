import React, { useEffect, useMemo, useState } from 'react';
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
import { API_BASE, fetchQuestionSuggestions, QuestionSuggestion } from '../services/api';
import {
  deduplicateQuestionSuggestions,
  searchQuestionSuggestions,
} from '../utils/qaQuestionSuggestions';

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
  const [questions, setQuestions] = useState<QuestionSuggestion[]>([]);
  const [questionsLoading, setQuestionsLoading] = useState(true);
  const [questionsError, setQuestionsError] = useState(false);
  const hasQuery = suggestionQuery.trim().length > 0;

  useEffect(() => {
    let active = true;
    fetchQuestionSuggestions()
      .then((loadedQuestions) => {
        if (active) setQuestions(loadedQuestions);
      })
      .catch((error: unknown) => {
        console.error('Failed to load e-GP Q&A suggestions:', error);
        if (active) setQuestionsError(true);
      })
      .finally(() => {
        if (active) setQuestionsLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const deduplicatedQuestions = useMemo(
    () => deduplicateQuestionSuggestions(questions),
    [questions],
  );

  const matchingSuggestions = useMemo(
    () => searchQuestionSuggestions(suggestionQuery, questions),
    [suggestionQuery, questions],
  );
  const visibleSuggestions = hasQuery
    ? matchingSuggestions.slice(0, 30)
    : deduplicatedQuestions;
  const totalVisibleCount = hasQuery
    ? matchingSuggestions.length
    : deduplicatedQuestions.length;

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
      className={`fixed inset-y-0 left-0 z-50 flex w-[min(20rem,88vw)] shrink-0 select-none flex-col gap-4 overflow-y-auto border-r border-[#183153]/10 bg-[#F4F8F3] p-4 pt-[max(1rem,env(safe-area-inset-top))] text-xs shadow-2xl backdrop-blur-xl transition-transform duration-200 md:static md:z-auto md:h-auto md:min-h-0 md:w-80 md:translate-x-0 md:bg-[#F4F8F3]/95 md:pt-5 md:shadow-none ${
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
        className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#176B3A] to-[#183153] px-3 py-3 text-xs font-semibold text-white shadow-md shadow-[#183153]/10 transition-all hover:from-[#12552e] hover:to-[#12253e] hover:-translate-y-0.5 active:translate-y-0"
        aria-label="Start a new chat session"
      >
        <Plus className="w-4 h-4" />
        <span>{language === 'en' ? 'New Consultation' : 'নতুন কথোপকথন'}</span>
      </button>

      {/* 2. Suggested Questions */}
      <div className="space-y-2.5 rounded-2xl border border-[#183153]/10 bg-white/90 p-3.5 shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 pb-2">
          <div className="flex items-center gap-1.5 font-bold text-[#183153]">
            <Search className="w-3.5 h-3.5 text-[#176B3A]" />
            <span>{language === 'en' ? 'Questions from e-GP Q&A' : 'e-GP প্রশ্নোত্তর থেকে প্রশ্ন'}</span>
          </div>
          <span className="text-[10px] font-mono font-bold text-[#183153] bg-[#8BC34A]/20 px-1.5 py-0.2 rounded">
            {language === 'en' ? `${deduplicatedQuestions.length} questions` : `${deduplicatedQuestions.length}টি প্রশ্ন`}
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
            className="min-w-0 flex-1 rounded-xl border border-[#183153]/15 bg-[#F4F8F3] px-2.5 py-2 text-[11px] text-[#183153] outline-none placeholder:text-slate-500 focus:border-[#176B3A] focus:bg-white focus:ring-2 focus:ring-[#8BC34A]/40"
          />
          <button
            type="submit"
            className="inline-flex shrink-0 items-center gap-1 rounded-lg bg-[#176B3A] px-2.5 py-2 text-[11px] font-semibold text-white transition-colors hover:bg-[#183153]"
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
              ? `Browse ${deduplicatedQuestions.length} questions from the Q&A file`
              : `প্রশ্নোত্তর ফাইলের ${deduplicatedQuestions.length}টি প্রশ্ন দেখুন`}
        </p>

        <div className="max-h-64 space-y-1.5 overflow-y-auto pt-0.5 pr-1">
          {visibleSuggestions.map((suggestion) => {
            return (
              <button
                key={suggestion.question_number}
                onClick={() => {
                  onSelectSuggestedQuestion(suggestion.question);
                  onCloseMobile();
                }}
                className="w-full text-left rounded-xl border border-slate-100 bg-slate-50/80 p-2.5 text-slate-700 transition-all flex items-start gap-2 cursor-pointer leading-snug hover:-translate-y-0.5 hover:border-[#8BC34A] hover:bg-[#F4F8F3] hover:text-[#176B3A] hover:shadow-sm"
              >
                <ChevronRight className="w-3.5 h-3.5 text-[#176B3A] shrink-0 mt-0.5" />
                <span className="text-[11.5px]">
                  {suggestion.question}
                  <span className="ml-1 block pt-0.5 text-[10px] font-normal text-slate-400">
                    {suggestion.module} · Q{suggestion.question_number}
                  </span>
                </span>
              </button>
            );
          })}
          {questionsLoading && (
            <p className="rounded-lg bg-white/70 p-3 text-[11px] leading-relaxed text-slate-500">
              {language === 'en' ? 'Loading e-GP questions...' : 'e-GP প্রশ্ন লোড হচ্ছে...'}
            </p>
          )}
          {!questionsLoading && questionsError && (
            <p role="alert" className="rounded-lg bg-amber-50 p-3 text-[11px] leading-relaxed text-amber-800">
              {language === 'en'
                ? 'Could not load Q&A questions. Check the backend connection and try again.'
                : 'প্রশ্নোত্তর লোড করা যায়নি। ব্যাকএন্ড সংযোগ পরীক্ষা করে আবার চেষ্টা করুন।'}
            </p>
          )}
          {hasQuery && matchingSuggestions.length === 0 && (
            <p className="rounded-lg bg-white/70 p-3 text-[11px] leading-relaxed text-slate-500">
              {language === 'en'
                ? 'No matching Q&A questions. Try a shorter keyword or a different phrase.'
                : 'প্রশ্নোত্তরে মেলেনি। ছোট শব্দ বা অন্য বাক্যাংশ দিয়ে খুঁজুন।'}
            </p>
          )}
        </div>
      </div>

      <a
        href={`${API_BASE}/api/manual/download`}
        className="flex w-full items-center justify-center gap-2 rounded-lg border border-[#176B3A]/20 bg-white/70 px-3 py-2.5 text-xs font-semibold text-[#176B3A] shadow-2xs transition-colors hover:border-[#176B3A] hover:bg-[#F4F8F3]"
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
