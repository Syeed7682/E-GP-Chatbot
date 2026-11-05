import React from 'react';
import {
  Plus,
  HelpCircle,
  BookOpen,
  AlertTriangle,
  Info,
  Trash2,
  CheckCircle2,
  Search,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { SyncState } from '../types/egp';

interface GovtOfficialSidebarProps {
  syncState: SyncState;
  onSelectSuggestedQuestion: (question: string) => void;
  onNewChat: () => void;
  onClearConversation: () => void;
  language: 'en' | 'bn';
  onOpenSyncModal: () => void;
}

export const GovtOfficialSidebar: React.FC<GovtOfficialSidebarProps> = ({
  syncState,
  onSelectSuggestedQuestion,
  onNewChat,
  onClearConversation,
  language,
  onOpenSyncModal
}) => {
  const suggestedQuestions = [
    {
      en: 'How do I log in to the e-GP portal?',
      bn: 'কীভাবে ই-জিপি পোর্টালে লগইন করবেন?'
    },
    {
      en: 'How can I create a Procuring Entity account?',
      bn: 'কীভাবে ক্রয়কারী সত্তা (PE) অ্যাকাউন্ট তৈরি করবেন?'
    },
    {
      en: 'How do I find an e-GP procedure in the manual?',
      bn: 'ম্যানুয়ালে ই-জিপি পদ্ধতি কীভাবে খুঁজে পাবেন?'
    },
    {
      en: 'What should I do if I encounter a portal error?',
      bn: 'পোর্টালে ত্রুটি (Error) দেখা দিলে কী করণীয়?'
    },
    {
      en: 'How to delete a tender?',
      bn: 'ড্রাফট টেন্ডার কীভাবে বাতিল বা মুছে ফেলবেন?'
    }
  ];

  return (
    <aside className="w-full md:w-80 bg-white border-r border-[#D5DEE7] p-4 flex flex-col gap-4 text-xs select-none shrink-0 overflow-y-auto">
      {/* 1. New Chat Action */}
      <button
        onClick={onNewChat}
        className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-[#0B4F8A] hover:bg-[#083c6b] text-white rounded-md font-semibold text-xs shadow-xs transition-colors cursor-pointer"
        aria-label="Start a new chat session"
      >
        <Plus className="w-4 h-4" />
        <span>{language === 'en' ? 'New Chat' : 'নতুন কথোপকথন'}</span>
      </button>

      {/* 2. Suggested Questions */}
      <div className="border border-[#D5DEE7] rounded-md bg-[#F3F6F9] p-3 space-y-2">
        <div className="flex items-center gap-1.5 font-bold text-[#12304A] border-b border-[#D5DEE7] pb-1.5">
          <Search className="w-3.5 h-3.5 text-[#0B4F8A]" />
          <span>{language === 'en' ? 'Suggested Questions' : 'প্রস্তাবিত প্রশ্নাবলী'}</span>
        </div>

        <div className="space-y-1.5 pt-0.5">
          {suggestedQuestions.map((q, idx) => {
            const label = language === 'en' ? q.en : q.bn;
            return (
              <button
                key={idx}
                onClick={() => onSelectSuggestedQuestion(q.en)}
                className="w-full text-left p-2 rounded bg-white hover:bg-blue-50 border border-[#D5DEE7] hover:border-[#0B4F8A] text-[#334155] hover:text-[#0B4F8A] font-medium transition-all flex items-start gap-1.5 cursor-pointer leading-snug"
              >
                <ChevronRight className="w-3.5 h-3.5 text-[#0B4F8A] shrink-0 mt-0.5" />
                <span>{label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Supported Manual Card */}
      <div className="border border-[#D5DEE7] rounded-md bg-white p-3 space-y-1.5">
        <div className="flex items-center gap-1.5 font-bold text-[#12304A] border-b border-[#D5DEE7] pb-1.5">
          <BookOpen className="w-3.5 h-3.5 text-[#16834A]" />
          <span>{language === 'en' ? 'Supported Manual' : 'অনুমোদিত ম্যানুয়াল'}</span>
        </div>

        <p className="text-[11px] text-[#334155] font-semibold leading-snug">
          e-GP System User Manual - Procuring Entity User
        </p>
        <div className="text-[11px] text-slate-500 space-y-0.5 pt-1">
          <div className="flex items-center justify-between">
            <span>Edition:</span>
            <span className="font-medium text-slate-800">1 February 2026</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Total Pages:</span>
            <span className="font-medium text-slate-800">543 Pages</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Status:</span>
            <span className="font-semibold text-[#16834A]">Fully Verified ✓</span>
          </div>
        </div>
      </div>

      {/* 4. About This Assistant */}
      <div className="border border-[#D5DEE7] rounded-md bg-white p-3 space-y-1.5">
        <div className="flex items-center gap-1.5 font-bold text-[#12304A]">
          <Info className="w-3.5 h-3.5 text-[#0B4F8A]" />
          <span>{language === 'en' ? 'About This Assistant' : 'সহায়িকা সম্পর্কে'}</span>
        </div>
        <p className="text-[11px] text-[#334155] leading-relaxed">
          {language === 'en'
            ? 'Designed for Procuring Entity (PE) officers to rapidly look up statutory procedures, workflow routing rules, and portal diagnostic resolutions under PPR.'
            : 'পিপিআর বিধিমালার আওতায় ক্রয়কারী সত্তার (PE) কর্মকর্তাদের প্রশাসনিক প্রক্রিয়া ও পোর্টালে কাজের নির্দেশিকা সহজে খুঁজে পেতে প্রস্তুতকৃত।'}
        </p>
      </div>

      {/* 5. Important Notice (Exact Requirement) */}
      <div className="border border-amber-300 bg-amber-50 rounded-md p-3 space-y-1">
        <div className="flex items-center gap-1.5 font-bold text-amber-900 text-xs">
          <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0" />
          <span>{language === 'en' ? 'Important Notice' : 'জরুরি বিজ্ঞপ্তি'}</span>
        </div>
        <p className="text-[11px] text-amber-900 leading-relaxed">
          “This assistant provides informational guidance based on the available e-GP manual. It does not submit tenders, make payments, or perform actions on the e-GP portal.”
        </p>
      </div>

      {/* 6. Clear Conversation Action */}
      <div className="mt-auto pt-2 border-t border-[#D5DEE7]">
        <button
          onClick={onClearConversation}
          className="w-full flex items-center justify-center gap-1.5 py-1.5 px-3 rounded bg-gray-100 hover:bg-red-50 text-slate-600 hover:text-red-700 border border-[#D5DEE7] hover:border-red-300 font-medium text-xs transition-colors cursor-pointer"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>{language === 'en' ? 'Clear Conversation' : 'কথোপকথন মুছুন'}</span>
        </button>
      </div>
    </aside>
  );
};
