import React, { useRef, useEffect } from 'react';
import { ChatMessage as ChatMessageType } from '../../types/egp';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { Shield, Sparkles } from 'lucide-react';

interface ChatWindowProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  onSendMessage: (text: string, imageBase64?: string, imageName?: string) => void;
  onOpenPage?: (page: number) => void;
  onSelectPrompt?: (prompt: string) => void;
}

const QUICK_PROMPTS = [
  'How do I log in to the e-GP portal?',
  'How to delete a tender?',
  'what is debarment?',
  'Annual Procurement Plan (APP) guide',
  'How to view Approved Workflow?'
];

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  onSendMessage,
  onOpenPage,
  onSelectPrompt
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex flex-col h-full bg-slate-50 dark:bg-slate-950">
      {/* Scrollable Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 max-w-lg mx-auto">
            <div className="w-16 h-16 rounded-2xl bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-400 flex items-center justify-center mb-4 shadow-inner">
              <Shield className="w-8 h-8" />
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">
              Official e-GP Manual Assistant
            </h2>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
              Procuring Entity (PE) guidance grounded strictly in the 543-page official Bangladesh e-GP User Manual. Ask procedural questions or attach portal screenshots.
            </p>

            {/* Quick Prompts */}
            <div className="mt-6 flex flex-wrap gap-2 justify-center">
              {QUICK_PROMPTS.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => onSelectPrompt ? onSelectPrompt(prompt) : onSendMessage(prompt)}
                  className="text-xs px-3 py-1.5 rounded-full border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:border-emerald-500 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors shadow-2xs cursor-pointer"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} onOpenPage={onOpenPage} />
          ))
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex gap-3 justify-start mb-4">
            <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center shrink-0 animate-pulse">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm">
              <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                <span>Searching 543 manual pages and synthesizing grounded answer...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input Area */}
      <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
    </div>
  );
};

