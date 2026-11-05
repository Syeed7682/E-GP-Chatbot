import React from 'react';
import { X, BookOpen, Search, Image as ImageIcon, ShieldCheck, CheckCircle2, ArrowRight } from 'lucide-react';

interface UserGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectQuery: (q: string) => void;
  language: 'en' | 'bn';
}

export const UserGuideModal: React.FC<UserGuideModalProps> = ({
  isOpen,
  onClose,
  onSelectQuery,
  language
}) => {
  if (!isOpen) return null;

  const guideSections = [
    {
      title: '1. User Authentication & Login Procedures',
      page: 'Page 6',
      desc: 'Guidance on navigating to eprocure.gov.bd, password recovery, PE user credentials, and USB PKI security tokens.',
      sampleQuery: 'How does a user log in to e-GP with security token?'
    },
    {
      title: '2. PE Account Opening & Role Delegations',
      page: 'Page 18',
      desc: 'Procedures for establishing Procuring Entity profiles, CPTU authorization, assigning Creator, Reviewer, and Approver roles.',
      sampleQuery: 'How can I create a Procuring Entity account?'
    },
    {
      title: '3. Tender Deletion & Corrigendum Under PPR',
      page: 'Page 56',
      desc: 'Statutory rules distinguishing draft deletion from published cancellation, pre-tender meeting scheduling, and gazetted corrigendum.',
      sampleQuery: 'How to delete a tender?'
    },
    {
      title: '4. Annual Procurement Plan (APP) Preparation',
      page: 'Page 112',
      desc: 'Drafting procurement packages (OTM, RFQ, LTM), assigning budget heads (Development vs Revenue), and obtaining HOPE sign-off.',
      sampleQuery: 'Annual Procurement Plan (APP) guide'
    },
    {
      title: '5. Workflow Sign-Off & Approvals',
      page: 'Page 189',
      desc: 'Routing tender schedules through sequential approval authorities, returning with clarification notes, and digital token verification.',
      sampleQuery: 'How to view Approved Workflow?'
    },
    {
      title: '6. Tender Evaluation (TEC) & Technical Compliance',
      page: 'Page 310',
      desc: 'Evaluation matrix, responsiveness checks, liquid asset confirmation, and recommending the lowest evaluated responsive tenderer (LERT).',
      sampleQuery: 'Proposal evaluation procedure'
    }
  ];

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-xs flex items-center justify-center p-4 select-none">
      <div className="bg-white border border-[#D5DEE7] rounded-xl w-full max-w-3xl overflow-hidden shadow-2xl flex flex-col max-h-[85vh] text-[#334155]">
        {/* Header */}
        <div className="bg-[#12304A] px-6 py-4 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-[#0B4F8A] flex items-center justify-center text-blue-200">
              <BookOpen className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold tracking-tight">
                {language === 'en' ? 'e-GP Manual User Guide' : 'ই-জিপি ম্যানুয়াল ব্যবহার নির্দেশিকা'}
              </h3>
              <p className="text-[11px] text-blue-200">
                Official Procuring Entity User Manual Overview (543 pages)
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
        <div className="p-6 overflow-y-auto space-y-4 text-xs">
          <p className="leading-relaxed text-slate-600">
            {language === 'en'
              ? 'The e-GP Manual Chatbot indexes the complete official Procuring Entity (PE) User Manual. Click any topic below to automatically ask the Assistant:'
              : 'ই-জিপি ম্যানুয়াল চ্যাটবটে ক্রয়কারী সত্তার (PE) ৫৪৩ পৃষ্ঠার পুরো নির্দেশিকা ইন্ডেক্স করা রয়েছে। যেকোনো বিষয়ে ক্লিক করে সরাসরি সহায়তা নিন:'}
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
            {guideSections.map((sec, idx) => (
              <div
                key={idx}
                className="p-3 rounded-lg border border-[#D5DEE7] bg-[#F8FAFC] hover:bg-blue-50/50 hover:border-[#0B4F8A] transition-all space-y-1.5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between font-bold text-[#12304A]">
                    <span className="truncate pr-2">{sec.title}</span>
                    <span className="text-[10px] bg-blue-100 text-[#0B4F8A] px-1.5 py-0.2 rounded font-mono shrink-0">
                      {sec.page}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 leading-snug mt-1">
                    {sec.desc}
                  </p>
                </div>

                <button
                  onClick={() => {
                    onSelectQuery(sec.sampleQuery);
                    onClose();
                  }}
                  className="pt-2 text-[11px] text-[#0B4F8A] font-semibold hover:underline flex items-center gap-1 cursor-pointer"
                >
                  <span>Ask Assistant: "{sec.sampleQuery}"</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="bg-[#F3F6F9] px-6 py-3 border-t border-[#D5DEE7] flex items-center justify-between text-xs">
          <span className="text-[11px] text-slate-500">
            Source: Central Procurement Technical Unit (CPTU) • BPPA
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
