import React from 'react';
import {
  MessageSquare,
  HelpCircle,
  BookOpen,
  Globe,
  Wifi,
  WifiOff,
  RefreshCw,
  Layers,
  ChevronDown,
  Cpu,
  Menu
} from 'lucide-react';
import { SyncState } from '../types/egp';

interface GovtOfficialHeaderProps {
  syncState: SyncState;
  onOpenMobileMenu: () => void;
  activeTab: 'chat' | 'guide';
  setActiveTab: (tab: 'chat' | 'guide') => void;
  language: 'en' | 'bn';
  onToggleLanguage: () => void;
  onOpenSyncModal: () => void;
  onNewChat: () => void;
  useAltModel: boolean;
  onToggleAltModel: () => void;
}

export const GovtOfficialHeader: React.FC<GovtOfficialHeaderProps> = ({
  syncState,
  onOpenMobileMenu,
  activeTab,
  setActiveTab,
  language,
  onToggleLanguage,
  onOpenSyncModal,
  onNewChat,
  useAltModel,
  onToggleAltModel
}) => {
  return (
    <header className="relative z-40 w-full shrink-0 bg-[#193653] text-white border-b border-[#D8E3D8]/20 shadow-sm backdrop-blur-xl select-none font-sans">
      {/* Top Government-Style Strip */}
      <div className="hidden">
        <div className="flex min-w-0 items-center gap-2.5">
          {/* Bangladesh National Circular Emblem */}
          <div className="w-4.5 h-4.5 rounded-full bg-[#006A4E] flex items-center justify-center p-0.5 shadow-xs">
            <div className="w-2.5 h-2.5 rounded-full bg-[#F42A41]" />
          </div>
          <div className="flex items-center gap-2">
            <span className="truncate font-semibold text-white tracking-wide">
              {language === 'en'
                ? "Government Public Service Portal • e-Procurement Guidance"
                : "সরকারি সেবা পোর্টাল • ই-জিপি প্রকিউরমেন্ট সহায়িকা"}
            </span>
            <span className="hidden lg:inline text-[#8BC34A]/60">•</span>
            <span className="hidden lg:inline text-[10.5px] text-[#F4F8F3]/75">
              Procuring Entity User Manual Edition 1 Feb 2026
            </span>
          </div>
        </div>

        {/* System Status Sign & Language Controls */}
        <div className="ml-auto flex max-w-full flex-wrap items-center justify-end gap-1.5 sm:gap-2.5">
          {/* Live Online / Offline Network Badge */}
          <div
            className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10.5px] font-semibold tracking-wide ${
              syncState.is_online
                ? 'bg-[#176B3A] text-[#D8F3A8] border border-[#8BC34A]/60 shadow-2xs'
                : 'bg-amber-950/80 text-amber-300 border border-amber-500/50 shadow-2xs'
            }`}
            title={syncState.is_online ? 'Connected to e-GP Central Manual Index' : 'Operating in In-Browser Offline Index Mode'}
          >
            <span className={`w-2 h-2 rounded-full ${syncState.is_online ? 'bg-[#8BC34A] animate-pulse' : 'bg-amber-400'}`} />
            <span>{syncState.is_online ? (language === 'en' ? 'Online Index' : 'অনলাইন') : (language === 'en' ? 'Offline Cache' : 'অফলাইন')}</span>
          </div>

          {/* Language Toggle */}
          <button
            onClick={onToggleLanguage}
            className="flex h-7 items-center gap-1 px-2 py-1 rounded-md bg-[#193653] hover:bg-[#24466A] text-[#F4F8F3] text-[10px] font-medium border border-[#8BC34A]/35 transition-all cursor-pointer hover:border-[#8BC34A]"
            aria-label="Toggle language between English and Bangla"
          >
            <Globe className="w-3 h-3 text-[#8BC34A]" />
            <span className={language === 'en' ? 'font-bold text-white' : 'text-[#F4F8F3]/70'}>EN</span>
            <span className="text-[#8BC34A]/80">/</span>
            <span className={language === 'bn' ? 'font-bold text-white' : 'text-[#F4F8F3]/70'}>বাংলা</span>
          </button>

          {/* E1 / E2 Model Toggle */}
          <div className="flex items-center gap-0.5 bg-[#10243D] p-0.5 rounded-md border border-[#8BC34A]/30" title={useAltModel ? 'E2: Groq Qwen multimodal vision model (Active)' : 'E1: Groq GPT-OSS grounded text model'}>
            <button
              onClick={!useAltModel ? undefined : onToggleAltModel}
              className={`flex h-7 items-center gap-1 px-2 py-1 rounded text-[10px] font-semibold transition-all cursor-pointer ${
                !useAltModel
                  ? 'bg-[#176B3A] text-white shadow-2xs font-bold'
                  : 'text-[#F4F8F3]/70 hover:text-white hover:bg-white/10'
              }`}
              aria-label="Use default grounded engine (E1)"
            >
              <Cpu className="w-3 h-3" />
              <span>E1 Text</span>
            </button>
            <button
              onClick={useAltModel ? undefined : onToggleAltModel}
              className={`flex h-7 items-center gap-1 px-2 py-1 rounded text-[10px] font-semibold transition-all cursor-pointer ${
                useAltModel
                  ? 'bg-[#8BC34A] text-[#183153] shadow-2xs font-bold'
                  : 'text-[#F4F8F3]/70 hover:text-white hover:bg-white/10'
              }`}
              aria-label="Use multimodal vision engine (E2)"
            >
              <Cpu className="w-3 h-3" />
              <span>E2 Vision</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Branding & Navigation Row */}
      <div className="max-w-[1500px] mx-2 sm:mx-4 lg:mx-auto w-auto px-3 sm:px-5 py-2.5 flex flex-wrap items-center justify-between gap-x-4 gap-y-2 rounded-2xl border border-white/20 bg-[#163f55]/55 shadow-xl shadow-black/20 backdrop-blur-2xl supports-[backdrop-filter]:bg-white/[0.10]">
        {/* Project Branding */}
        <div className="flex min-w-0 flex-1 items-center gap-2 sm:gap-3">
          <button
            type="button"
            onClick={onOpenMobileMenu}
            className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-[#8BC34A]/35 text-[#F4F8F3] hover:bg-white/10 md:hidden"
            aria-label="Open manual topics menu"
          >
            <Menu className="h-5 w-5" />
          </button>
          <img
            src="/govt-seal.png"
            alt="Government of Bangladesh seal"
            className="hidden h-11 w-11 shrink-0 rounded-full border border-white/40 bg-white p-0.5 object-contain shadow-sm sm:block"
          />
          <div className="min-w-0">
            <div className="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1">
              <h1 className="truncate whitespace-nowrap text-sm sm:text-base md:text-[17px] font-bold tracking-tight text-white leading-tight">
                {language === 'en' ? 'e-GP Official Manual Assistant' : 'ই-জিপি অফিসিয়াল ম্যানুয়াল সহায়িকা'}
              </h1>
              <span className="hidden sm:inline-flex text-[10px] font-semibold px-2 py-0.5 bg-[#176B3A] text-white rounded-full tracking-wide border border-[#8BC34A]/50 shadow-2xs">
                {language === 'en' ? 'CPTU Verified' : 'সরকারি'}
              </span>
            </div>
            <p className="hidden sm:block text-xs text-[#F4F8F3]/75 leading-tight">
              {language === 'en'
                ? 'Statutory procedural intelligence for Procuring Entity (PE) officers • PPR 2025/2026'
                : 'অফিসিয়াল ই-জিপি ব্যবহারকারী ম্যানুয়ালের তথ্যের ওপর ভিত্তি করে এআই সহায়তা'}
            </p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex w-full shrink-0 items-center justify-end gap-1.5 text-xs font-medium sm:ml-auto sm:w-auto sm:gap-2">
          <div className="hidden lg:inline-flex h-9 items-center gap-1.5 rounded-full border border-[#8BC34A]/60 bg-[#176B3A]/60 px-3 text-[10px] font-semibold text-[#D8F3A8] shadow-sm">
            <span className="h-2 w-2 rounded-full bg-[#8BC34A] animate-pulse" />
            <span>{language === 'en' ? 'Online Index' : 'অনলাইন'}</span>
          </div>

          <button
            onClick={onToggleLanguage}
            className="hidden md:inline-flex h-9 items-center gap-1 rounded-full border border-white/25 bg-white/10 px-3 text-[10px] font-semibold text-white/90 transition hover:bg-white/20"
            aria-label="Toggle language between English and Bangla"
          >
            <Globe className="h-3.5 w-3.5 text-[#8BC34A]" />
            <span>EN / {language === 'en' ? 'বাংলা' : 'English'}</span>
            <ChevronDown className="h-3 w-3 text-white/70" />
          </button>

          <button
            onClick={onToggleAltModel}
            className="hidden lg:inline-flex h-9 items-center gap-1.5 rounded-full border border-white/25 bg-white/10 px-3 text-[10px] font-semibold text-white/90 transition hover:bg-white/20"
          >
            <Cpu className="h-3.5 w-3.5" />
            <span>{useAltModel ? 'E2 Vision' : 'E1 Text'}</span>
          </button>

          <button
            onClick={() => { setActiveTab('chat'); onNewChat(); }}
            className={`h-9 px-3 sm:px-4 py-1 rounded-full transition-all flex items-center gap-1.5 cursor-pointer ${
              activeTab === 'chat'
                ? 'bg-[#176B3A] text-white shadow-sm font-semibold border border-[#8BC34A]/50'
                : 'text-[#F4F8F3]/75 hover:text-white hover:bg-white/10'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>{language === 'en' ? 'Consultation Chat' : 'প্রশ্ন করুন'}</span>
          </button>

          <button
            onClick={() => setActiveTab('guide')}
            className={`h-9 px-3 sm:px-4 py-1 rounded-full transition-all flex items-center gap-1.5 cursor-pointer ${
              activeTab === 'guide'
                ? 'bg-[#176B3A] text-white shadow-sm font-semibold border border-[#8BC34A]/50'
                : 'text-[#F4F8F3]/75 hover:text-white hover:bg-white/10'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>{language === 'en' ? 'User Guide' : 'ব্যবহার নির্দেশিকা'}</span>
          </button>

        </nav>
      </div>
    </header>
  );
};
