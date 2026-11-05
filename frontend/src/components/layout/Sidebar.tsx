import React from 'react';
import {
  FileText,
  Shield,
  Layers,
  HelpCircle,
  AlertTriangle,
  FolderLock,
  ExternalLink
} from 'lucide-react';
import { PORTAL_SCREENS } from '../../data/portalScreens';

interface SidebarProps {
  onSelectTopic: (topic: string) => void;
  onOpenPage: (page: number) => void;
}

const TOPICS = [
  { label: '🔑 Login & PE Account Creation', query: 'How do I log in to the e-GP portal and setup my PE account?' },
  { label: '📋 Annual Procurement Plan (APP)', query: 'What is the step-by-step Annual Procurement Plan (APP) procedure?' },
  { label: '📢 Tender Creation & BOQ Forms', query: 'How do I create and publish a new tender notice?' },
  { label: '🚫 Tender Cancellation Process', query: 'How to delete a tender?' },
  { label: '⚖️ Debarment & Suspension (Rule 127)', query: 'what is debarment?' },
  { label: '🔄 Workflow Approvals & Signing', query: 'How to view Approved Workflow?' },
  { label: '⚠️ Evaluation Discrepancy (Q10.4)', query: 'How to fix evaluation discrepancy error code Q10.4?' }
];

export const Sidebar: React.FC<SidebarProps> = ({ onSelectTopic, onOpenPage }) => {
  return (
    <aside className="w-72 bg-slate-50 dark:bg-slate-950 border-r border-slate-200 dark:border-slate-800 flex flex-col h-full overflow-y-auto p-3.5 space-y-6">
      {/* Quick Topics */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2.5 px-2">
          Core PE Procedures
        </h3>
        <div className="space-y-1">
          {TOPICS.map((t, idx) => (
            <button
              key={idx}
              onClick={() => onSelectTopic(t.query)}
              className="w-full text-left px-2.5 py-2 text-xs font-medium rounded-lg text-slate-700 dark:text-slate-300 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 hover:text-emerald-700 dark:hover:text-emerald-400 transition-colors cursor-pointer truncate"
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Verified Portal Screens */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2.5 px-2 flex items-center justify-between">
          <span>Portal Screen Guides</span>
          <span className="text-[10px] text-emerald-600 font-mono">543 p.</span>
        </h3>
        <div className="space-y-1.5">
          {PORTAL_SCREENS.map((sc) => (
            <div
              key={sc.id}
              onClick={() => onOpenPage(sc.page_number)}
              className="p-2 rounded-lg border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-emerald-500 transition-colors cursor-pointer"
            >
              <div className="flex items-center justify-between text-xs font-semibold text-emerald-800 dark:text-emerald-400">
                <span>{sc.code}</span>
                <span className="text-[10px] text-slate-400">p. {sc.page_number}</span>
              </div>
              <p className="text-[11px] text-slate-600 dark:text-slate-400 truncate mt-0.5">
                {sc.name}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Helpdesk Notice */}
      <div className="mt-auto p-3 rounded-xl bg-slate-200/60 dark:bg-slate-900 border border-slate-300/60 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-400">
        <p className="font-semibold text-slate-800 dark:text-slate-200 mb-1">
          Official Helpdesk
        </p>
        <p className="text-[11px]">📞 +880-960-4224224</p>
        <p className="text-[11px]">📧 helpdesk@eprocure.gov.bd</p>
      </div>
    </aside>
  );
};

