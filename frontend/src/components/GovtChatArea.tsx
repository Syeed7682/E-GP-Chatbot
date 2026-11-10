import React, { useRef, useEffect, useState } from 'react';
import {
  Send,
  Paperclip,
  X,
  Monitor,
  AlertCircle
} from 'lucide-react';
import { ChatMessage, ChatSourceCitation } from '../types/egp';
import { API_BASE } from '../services/api';
import { formatAssistantAnswer } from '../utils/answerFormatting';

interface GovtChatAreaProps {
  messages: ChatMessage[];
  inputQuestion: string;
  setInputQuestion: (q: string) => void;
  onSendMessage: (question: string) => void;
  isLoading: boolean;
  uploadedImage: { base64: string; name: string; mime: string } | null;
  onImageSelected: (image: { base64: string; name: string; mime: string } | null) => void;
  onOpenScreenModal: (screenId: string) => void;
  language: 'en' | 'bn';
  backendError: string | null;
  onRetry: () => void;
}

const FormattedGovtText: React.FC<{ text: string; onOpenScreenModal?: (screenId: string) => void }> = ({ text, onOpenScreenModal }) => {
  const lines = formatAssistantAnswer(text)
    .split('\n')
    .filter((line) => line.trim());
  const elements: React.ReactNode[] = [];
  let currentList: React.ReactNode[] = [];

  const flushList = () => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`list-${elements.length}`} className="space-y-1 my-1 pl-1">
          {currentList}
        </ul>
      );
      currentList = [];
    }
  };

  const renderInlineStyles = (str: string) => {
    const parts = str.split(/(\*\*[^*]+\*\*|\*[^*\n]+\*|`[^`]+`|Screen\s*[-–—:]\s*[A-Za-z0-9_.]+)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="font-semibold text-[#0F172A]">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('*') && part.endsWith('*')) {
        return <em key={i}>{part.slice(1, -1)}</em>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={i} className="px-1.5 py-0.5 rounded bg-slate-100 text-[#0B4F8A] font-mono text-[11px] font-medium border border-slate-200">{part.slice(1, -1)}</code>;
      }
      if (/^Screen\s*[-–—:]\s*[A-Za-z0-9_.]+/i.test(part)) {
        return (
          <button
            key={i}
            type="button"
            onClick={() => onOpenScreenModal && onOpenScreenModal(part)}
            className="inline-flex items-center gap-1 mx-1 text-[#0B4F8A] underline underline-offset-2 cursor-pointer"
            title={`View ${part}`}
          >
            <Monitor className="w-3 h-3 text-[#0B4F8A]" />
            <span>{part}</span>
          </button>
        );
      }
      return part;
    });
  };

  lines.forEach((line, idx) => {
    const trimmed = line.trim();
    if (!trimmed) {
      flushList();
      return;
    }

    if (trimmed.startsWith('### ')) {
      flushList();
      const title = trimmed.replace(/^###\s+/, '');
      elements.push(
        <h4 key={`h3-${idx}`} className="font-semibold text-sm text-slate-800">{title}</h4>
      );
      return;
    }

    if (trimmed.startsWith('#### ')) {
      flushList();
      const title = trimmed.replace(/^####\s+/, '');
      elements.push(
        <h5 key={`h4-${idx}`} className="font-semibold text-slate-800">{title}</h5>
      );
      return;
    }

    if (/^\d+\.\s+.*(Status|Status:|Guide|Procedure|Guidelines|Examination):/i.test(trimmed)) {
      flushList();
      elements.push(
        <p key={`subhead-${idx}`} className="font-semibold text-slate-800">
          {renderInlineStyles(trimmed.replace(/^\d+\.\s*/, ''))}
        </p>
      );
      return;
    }

    if (/^Step\s+\d+\s*[—–-]\s*/i.test(trimmed)) {
      flushList();
      elements.push(
        <p key={`step-heading-${idx}`} className="font-semibold text-slate-800">
          {renderInlineStyles(trimmed)}
        </p>
      );
      return;
    }

    if (trimmed.startsWith('- ') || trimmed.startsWith('* ') || trimmed.startsWith('• ')) {
      const content = trimmed.substring(2);
      currentList.push(
        <li key={`li-${idx}`} className="flex items-start gap-2 text-sm text-slate-700 leading-relaxed">
          <span className="text-slate-500 shrink-0">•</span>
          <span>{renderInlineStyles(content)}</span>
        </li>
      );
      return;
    }

    const numMatch = trimmed.match(/^(?:\*\*)?(\d+)[\.\)](?:\*\*)?\s+(.*)/);
    if (numMatch) {
      flushList();
      const stepNum = numMatch[1];
      const stepContent = numMatch[2];
      elements.push(
        <p key={`step-${idx}`} className="text-sm text-slate-700 leading-relaxed">
          <span className="font-medium text-slate-800">{stepNum}. </span>
          <span>
            {renderInlineStyles(stepContent)}
          </span>
        </p>
      );
      return;
    }

    if (trimmed === '---') {
      flushList();
      elements.push(<hr key={`hr-${idx}`} className="my-2 border-slate-200" />);
      return;
    }

    flushList();
    elements.push(
      <p key={`p-${idx}`} className="text-sm text-slate-700 leading-relaxed my-1">
        {renderInlineStyles(trimmed)}
      </p>
    );
  });

  flushList();

  return <div className="min-w-0 space-y-1 break-words [overflow-wrap:anywhere]">{elements}</div>;
};

const ManualAnswerImage: React.FC<{ sources: ChatSourceCitation[] }> = ({ sources }) => {
  const imageSources = Array.from(
    new Map(
      [
        ...sources.filter((source) => source.page != null && source.screen_reference),
        ...sources.filter((source) => source.page != null)
      ].map((source) => [source.page, source])
    ).values()
  );
  const [pageIndex, setPageIndex] = useState(0);
  const source = imageSources[pageIndex];

  if (imageSources.length === 0) return null;

  if (!source || source.page == null) {
    return (
      <p role="status" className="mt-2 text-xs text-amber-700">
        Manual page image unavailable. Check the public backend URL and ensure the manual PDF is installed on the backend.
      </p>
    );
  }

  return (
    <img
      src={
        source.image_path
          ? /^https?:\/\//i.test(source.image_path)
            ? source.image_path
            : `${API_BASE}${source.image_path.startsWith('/') ? '' : '/'}${source.image_path}`
          : `${API_BASE}/api/manual/page/${source.page}/image`
      }
      alt={`Official e-GP Manual, page ${source.page}`}
      className="mt-2 max-h-80 max-w-full rounded-lg object-contain"
      onError={() => setPageIndex((index) => Math.min(index + 1, imageSources.length))}
    />
  );
};

const ManualReferences: React.FC<{ sources: ChatSourceCitation[] }> = ({ sources }) => {
  const pages = Array.from(new Set(sources.flatMap((source) => source.page == null ? [] : [source.page]))).slice(0, 4);
  const qaReferences = Array.from(new Set(
    sources
      .filter((source) => source.source_type === 'qa' && source.question_number != null)
      .map((source) => `${source.source}${source.module ? ` · ${source.module}` : ''} · Question ${source.question_number}`)
  ));
  if (pages.length === 0 && qaReferences.length === 0) return null;

  return (
    <p className="mt-2 text-xs text-slate-500">
      Reference: {[
        ...(pages.length ? [`Official e-GP Manual · ${pages.map((page) => `p. ${page}`).join(', ')}`] : []),
        ...qaReferences,
      ].join('; ')}
    </p>
  );
};

export const GovtChatArea: React.FC<GovtChatAreaProps> = ({
  messages,
  inputQuestion,
  setInputQuestion,
  onSendMessage,
  isLoading,
  uploadedImage,
  onImageSelected,
  onOpenScreenModal,
  language,
  backendError,
  onRetry
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if ((inputQuestion.trim() || uploadedImage) && !isLoading) {
        onSendMessage(inputQuestion);
      }
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if ((inputQuestion.trim() || uploadedImage) && !isLoading) {
      onSendMessage(inputQuestion);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('Please upload a valid image file (PNG, JPG, or WEBP)');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const base64 = event.target?.result as string;
      onImageSelected({
        base64,
        name: file.name,
        mime: file.type
      });
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  return (
    <div className="relative flex min-h-0 flex-1 flex-col overflow-hidden bg-white/25 text-slate-800">
      {/* Messages Stream */}
      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto bg-transparent p-3 sm:p-4 md:p-6">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';

          return (
            <div
              key={msg.id}
              className={`mx-auto flex w-full min-w-0 max-w-3xl ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`min-w-0 max-w-[94%] space-y-2 rounded-2xl px-3 py-3 sm:max-w-[85%] sm:px-4 ${
                  isUser
                    ? 'rounded-tr-md bg-[#3568D4] text-white'
                    : 'rounded-tl-md border border-white/70 bg-white/55 text-slate-800 shadow-sm backdrop-blur-lg'
                }`}
              >
                {/* Uploaded Screenshot if any */}
                {msg.image_url && (
                  <div className="mb-2 max-w-sm overflow-hidden rounded-lg">
                    <img
                      src={msg.image_url}
                      alt={msg.image_name || 'Portal Screenshot'}
                      className="max-h-64 w-full rounded-lg object-contain"
                    />
                  </div>
                )}

                {/* Main Message Text with Professional Government Typography */}
                <div className={isUser ? 'text-sm leading-6' : 'chat-answer'}>
                  {isUser ? (
                    <p className="whitespace-pre-wrap text-sm">{msg.text}</p>
                  ) : (
                    <FormattedGovtText text={msg.text} onOpenScreenModal={onOpenScreenModal} />
                  )}
                </div>

                {!isUser && msg.sources && msg.sources.length > 0 && (
                  <>
                    <ManualAnswerImage key={`${msg.id}-manual-image`} sources={msg.sources} />
                    <ManualReferences sources={msg.sources} />
                  </>
                )}
              </div>
            </div>
          );
        })}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="mx-auto flex w-full max-w-3xl">
            <div className="flex items-center gap-3 rounded-2xl bg-[#F3F4F6] px-4 py-3 text-sm text-slate-600">
              <div className="w-4 h-4 border-2 border-[#0B4F8A] border-t-transparent rounded-full animate-spin" />
              <span>{language === 'en' ? 'Thinking…' : 'ভাবছি…'}</span>
            </div>
          </div>
        )}

        {/* Backend Error Banner if any */}
        {backendError && (
          <div className="mx-auto flex w-full max-w-3xl items-center justify-between gap-3 rounded-xl border border-amber-300 bg-amber-50 p-3 text-xs text-amber-900">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <p>{backendError}</p>
            </div>
            <button
              onClick={onRetry}
              className="shrink-0 rounded border border-amber-300 bg-white px-2.5 py-1 font-semibold text-xs text-amber-800 hover:bg-amber-100"
            >
              Retry Connection
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form Area */}
      <div className="border-t border-white/70 bg-white/45 p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] backdrop-blur-xl sm:p-4 sm:pb-[max(1rem,env(safe-area-inset-bottom))]">
        <div className="mx-auto max-w-3xl">
          {uploadedImage && (
            <div className="mb-2.5 inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-700">
              <span className="max-w-xs truncate">{uploadedImage.name}</span>
              <button
                onClick={() => onImageSelected(null)}
                className="rounded p-0.5 text-slate-500 transition-colors hover:text-red-600"
                title="Remove screenshot"
                aria-label="Remove attached screenshot"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          )}

          <form onSubmit={handleFormSubmit}>
            <div className="relative overflow-hidden rounded-xl border border-slate-300 bg-white transition-all focus-within:border-[#0B4F8A] focus-within:ring-2 focus-within:ring-blue-500/20">
              <textarea
                ref={textareaRef}
                rows={1}
                value={inputQuestion}
                onChange={(e) => setInputQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={language === 'en' ? 'Ask a question...' : 'প্রশ্ন লিখুন...'}
                className="w-full resize-none bg-transparent p-3.5 pr-28 text-sm text-slate-800 outline-none placeholder-slate-400"
              />

              <div className="absolute bottom-2.5 right-2.5 flex items-center gap-1.5">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept="image/png,image/jpeg,image/webp"
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-[#0B4F8A]"
                  title="Attach e-GP portal screenshot"
                  aria-label="Upload portal screenshot"
                >
                  <Paperclip className="h-4 w-4" />
                </button>
                <button
                  type="submit"
                  disabled={(!inputQuestion.trim() && !uploadedImage) || isLoading}
                  className="flex h-9 w-9 items-center justify-center rounded-full bg-[#3568D4] text-white transition-colors hover:bg-blue-700 disabled:opacity-40"
                  aria-label="Send question"
                >
                  <Send className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
