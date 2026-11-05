import React from 'react';
import {
  MessageSquare,
  HelpCircle,
  BookOpen,
  Info,
  Globe,
  Wifi,
  WifiOff,
  RefreshCw,
  Layers,
  ChevronDown
} from 'lucide-react';
import { SyncState } from '../types/egp';

interface GovtOfficialHeaderProps {
  syncState: SyncState;
  activeTab: 'chat' | 'guide' | 'about';
  setActiveTab: (tab: 'chat' | 'guide' | 'about') => void;
  language: 'en' | 'bn';
  onToggleLanguage: () => void;
  onOpenSyncModal: () => void;
  onNewChat: () => void;
}

export const GovtOfficialHeader: React.FC<GovtOfficialHeaderProps> = ({
  syncState,
  activeTab,
  setActiveTab,
  language,
  onToggleLanguage,
  onOpenSyncModal,
  onNewChat
}) => {
  return (
    <header className="w-full bg-[#12304A] text-white border-b border-[#0B4F8A] shadow-sm select-none">
      {/* Top Government-Style Strip */}
      <div className="bg-[#0B4F8A] text-[11px] px-4 py-1 flex items-center justify-between text-blue-100 border-b border-blue-900/50">
        <div className="flex items-center gap-2">
          {/* Bangladesh-inspired circular emblem icon */}
          <div className="w-4 h-4 rounded-full bg-[#16834A] flex items-center justify-center p-0.5 shadow-xs">
            <div className="w-2.5 h-2.5 rounded-full bg-[#E11D48]" />
          </div>
          <span className="font-semibold text-white tracking-wide">
            {language === 'en'
              ? "Government Public Service Portal • e-Procurement Guidance"
              : "সরকারি সেবা পোর্টাল • ই-জিপি প্রকিউরমেন্ট সহায়িকা"}
          </span>
        </div>

        {/* System Status Sign & Language Controls */}
        <div className="flex items-center gap-3">
          <div
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium ${
              syncState.is_online
                ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-500/40'
                : 'bg-amber-950/60 text-amber-300 border border-amber-500/40'
            }`}
            title={syncState.is_online ? 'Connected to e-GP Knowledge Base' : 'Running in Offline Mode'}
          >
            <span className={`w-2 h-2 rounded-full ${syncState.is_online ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
            <span>{syncState.is_online ? (language === 'en' ? 'Online' : 'অনলাইন') : (language === 'en' ? 'Offline' : 'অফলাইন')}</span>
          </div>

          {/* Language Toggle */}
          <button
            onClick={onToggleLanguage}
            className="flex items-center gap-1 px-2 py-0.5 rounded bg-[#12304A] hover:bg-blue-900 text-blue-100 text-[11px] font-medium border border-blue-400/30 transition-colors cursor-pointer"
            aria-label="Toggle language between English and Bangla"
          >
            <Globe className="w-3 h-3 text-emerald-400" />
            <span className={language === 'en' ? 'font-bold text-white' : 'text-blue-300'}>EN</span>
            <span className="text-blue-400">/</span>
            <span className={language === 'bn' ? 'font-bold text-white' : 'text-blue-300'}>বাংলা</span>
          </button>
        </div>
      </div>

      {/* Main Branding & Navigation Row */}
      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-4">
        {/* Project Branding */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#0B4F8A] border border-blue-400/40 flex items-center justify-center text-white shadow-sm shrink-0">
            <BookOpen className="w-5 h-5 text-blue-200" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg md:text-xl font-bold tracking-tight text-white leading-tight">
                {language === 'en' ? 'e-GP Manual Assistance' : 'ই-জিপি ম্যানুয়াল সহায়িকা'}
              </h1>
              <span className="text-[10px] font-semibold px-2 py-0.5 bg-[#16834A] text-white rounded-sm tracking-wide">
                {language === 'en' ? 'Official' : 'সরকারি'}
              </span>
            </div>
            <p className="text-xs text-blue-200/90 leading-tight">
              {language === 'en'
                ? 'AI-powered assistance based on the official e-GP user manual'
                : 'অফিসিয়াল ই-জিপি ব্যবহারকারী ম্যানুয়ালের তথ্যের ওপর ভিত্তি করে এআই সহায়তা'}
            </p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex items-center gap-1 text-xs font-medium">
          <button
            onClick={() => { setActiveTab('chat'); onNewChat(); }}
            className={`px-3 py-1.5 rounded transition-colors flex items-center gap-1.5 cursor-pointer ${
              activeTab === 'chat'
                ? 'bg-[#0B4F8A] text-white shadow-xs font-semibold'
                : 'text-blue-200 hover:text-white hover:bg-blue-900/50'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>{language === 'en' ? 'Ask a Question' : 'প্রশ্ন করুন'}</span>
          </button>

          <button
            onClick={() => setActiveTab('guide')}
            className={`px-3 py-1.5 rounded transition-colors flex items-center gap-1.5 cursor-pointer ${
              activeTab === 'guide'
                ? 'bg-[#0B4F8A] text-white shadow-xs font-semibold'
                : 'text-blue-200 hover:text-white hover:bg-blue-900/50'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>{language === 'en' ? 'User Guide' : 'ব্যবহার নির্দেশিকা'}</span>
          </button>

          <button
            onClick={() => setActiveTab('about')}
            className={`px-3 py-1.5 rounded transition-colors flex items-center gap-1.5 cursor-pointer ${
              activeTab === 'about'
                ? 'bg-[#0B4F8A] text-white shadow-xs font-semibold'
                : 'text-blue-200 hover:text-white hover:bg-blue-900/50'
            }`}
          >
            <Info className="w-3.5 h-3.5" />
            <span>{language === 'en' ? 'About' : 'সম্পর্কে'}</span>
          </button>
        </nav>
      </div>
    </header>
  );
};
