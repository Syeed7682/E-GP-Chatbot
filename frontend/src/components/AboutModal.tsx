import React from 'react';
import { X, Info, ShieldCheck, Database, Server, ExternalLink } from 'lucide-react';

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
  language: 'en' | 'bn';
}

export const AboutModal: React.FC<AboutModalProps> = ({
  isOpen,
  onClose,
  language
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-xs flex items-center justify-center p-4 select-none">
      <div className="bg-white border border-[#D5DEE7] rounded-xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col max-h-[85vh] text-[#334155]">
        {/* Header */}
        <div className="bg-[#12304A] px-6 py-4 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-[#0B4F8A] flex items-center justify-center text-blue-200">
              <Info className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold tracking-tight">
                {language === 'en' ? 'About e-GP Manual Assistance' : 'ই-জিপি ম্যানুয়াল সহায়তা সম্পর্কে'}
              </h3>
              <p className="text-[11px] text-blue-200">
                Government e-Procurement Guidance Architecture
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-blue-200 hover:text-white p-1 rounded hover:bg-blue-900 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-4 text-xs leading-relaxed">
          <div>
            <h4 className="font-bold text-sm text-[#12304A] mb-1">
              Project Overview
            </h4>
            <p className="text-slate-600">
              The <strong>e-GP Manual Assistance Chatbot</strong> is an official guidance assistant developed to help Procuring Entity (PE) officers and authorized users easily reference statutory procedural instructions, approval workflows, and system guidelines from the official 543-page e-GP System User Manual.
            </p>
          </div>

          <div className="border border-[#D5DEE7] rounded-lg p-3.5 bg-[#F8FAFC] space-y-2">
            <h5 className="font-bold text-[#0B4F8A] flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-[#16834A]" />
              Official Specifications &amp; Features
            </h5>
            <ul className="space-y-1.5 text-[11px] text-slate-700">
              <li>
                <strong>Official Manual Grounding:</strong> Complete coverage of the e-GP System User Manual (Procuring Entity User, 543 pages).
              </li>
              <li>
                <strong>Statutory Compliance:</strong> Guidelines aligned with Public Procurement Rules (PPR) and standard operating procedures.
              </li>
              <li>
                <strong>Offline Accessibility:</strong> Built-in local caching allows officers to access procedures even during intermittent connectivity.
              </li>
              <li>
                <strong>Public Procurement Security:</strong> Read-only informational guidance with strict adherence to procurement transparency.
              </li>
            </ul>
          </div>

          <div className="border border-amber-300 bg-amber-50 rounded-lg p-3 text-amber-900 text-[11px] leading-relaxed">
            <strong>Public Service Disclaimer:</strong><br />
            This assistant provides informational guidance based on the available e-GP manual. It does not submit tenders, make payments, or perform actions on the official e-GP portal (eprocure.gov.bd).
          </div>
        </div>

        {/* Footer */}
        <div className="bg-[#F3F6F9] px-6 py-3 border-t border-[#D5DEE7] flex items-center justify-between text-xs">
          <span className="text-[11px] text-slate-500">
            e-GP Assistant • Public Service Edition 2026
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-[#0B4F8A] hover:bg-[#083c6b] text-white font-medium text-xs transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
