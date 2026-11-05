import React from 'react';
import { User, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { ChatMessage as ChatMessageType } from '../../types/egp';
import { SourceCitation } from './SourceCitation';

interface ChatMessageProps {
  message: ChatMessageType;
  onOpenPage?: (page: number) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, onOpenPage }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5">
          <ShieldCheck className="w-4 h-4" />
        </div>
      )}

      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-sm ${
          isUser
            ? 'bg-emerald-600 text-white rounded-tr-none'
            : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-100 rounded-tl-none'
        }`}
      >
        {/* Attached image preview if user uploaded */}
        {message.image_url && (
          <div className="mb-2.5 overflow-hidden rounded-lg border border-white/20">
            <img src={message.image_url} alt="Attached screenshot" className="max-h-48 rounded object-contain" />
          </div>
        )}

        {/* Message Content */}
        <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap leading-relaxed text-sm">
          {message.content}
        </div>

        {/* Citations */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <SourceCitation sources={message.sources} onOpenPage={onOpenPage} />
        )}

        {/* Meta badges */}
        {!isUser && (
          <div className="mt-2.5 flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-100 dark:border-slate-800/60 pt-1.5">
            <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
              <CheckCircle2 className="w-3 h-3" />
              {message.model_used || 'e-GP PE Manual Grounded'}
            </span>
            <span>{new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-slate-700 text-white flex items-center justify-center shrink-0 shadow-sm mt-0.5">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
};

