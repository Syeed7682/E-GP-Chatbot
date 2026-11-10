import React, { useState } from 'react';
import { BookOpen, ExternalLink, ChevronDown, ChevronUp, Image as ImageIcon } from 'lucide-react';
import { ChatSourceCitation } from '../../types/egp';

interface SourceCitationProps {
  sources: ChatSourceCitation[];
  onOpenPage?: (page: number) => void;
}

export const SourceCitation: React.FC<SourceCitationProps> = ({ sources, onOpenPage }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 border-t border-slate-200/80 dark:border-slate-800/80 pt-2.5">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full text-xs font-medium text-emerald-800 dark:text-emerald-400 hover:text-emerald-900 transition-colors"
      >
        <div className="flex items-center gap-1.5">
          <BookOpen className="w-3.5 h-3.5 text-emerald-600" />
          <span>Official Manual Source Citations ({sources.length})</span>
        </div>
        {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
      </button>

      {isExpanded && (
        <div className="mt-2 space-y-2">
          {sources.map((src, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded-lg bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200/60 dark:border-emerald-800/40 text-xs"
            >
              <div className="flex items-center justify-between font-semibold text-emerald-900 dark:text-emerald-300">
                <span className="flex items-center gap-1">
                  {src.page != null
                    ? `📖 Page ${src.page} — ${src.source}`
                    : `📚 ${src.source}${src.module ? ` · ${src.module}` : ''}${src.question_number ? ` · Question ${src.question_number}` : ''}`}
                </span>
                {src.page != null && onOpenPage && (
                  <button
                    onClick={() => {
                      const page = src.page;
                      if (page != null) onOpenPage(page);
                    }}
                    className="flex items-center gap-1 text-[11px] text-emerald-700 hover:underline cursor-pointer"
                  >
                    View Page <ExternalLink className="w-3 h-3" />
                  </button>
                )}
              </div>
              <p className="mt-1 text-slate-700 dark:text-slate-300 italic line-clamp-2">
                "{src.snippet}"
              </p>
              {src.screen_reference && (
                <div className="mt-1.5 flex items-center gap-1 text-[11px] font-medium text-emerald-700 dark:text-emerald-400">
                  <ImageIcon className="w-3 h-3" />
                  <span>{src.screen_reference}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
