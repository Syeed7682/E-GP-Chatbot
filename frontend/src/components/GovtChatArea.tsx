import React, { useRef, useEffect, useState } from 'react';
import {
  Send,
  Paperclip,
  X,
  Monitor,
  AlertCircle,
  Image as ImageIcon,
  ChevronDown,
  ChevronUp,
  BookOpen,
  Phone,
  ShieldCheck,
  Sparkles,
  MessageCircle,
  ArrowUpRight
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
        <h4 key={`h3-${idx}`} className="font-semibold text-sm text-slate-800">
          {renderInlineStyles(title)}
        </h4>
      );
      return;
    }

    if (trimmed.startsWith('#### ')) {
      flushList();
      const title = trimmed.replace(/^####\s+/, '');
      elements.push(
        <h5 key={`h4-${idx}`} className="font-semibold text-slate-800">
          {renderInlineStyles(title)}
        </h5>
      );
      return;
    }

    if (trimmed.length <= 100 && /^[^:]+:\s*$/.test(trimmed)) {
      flushList();
      elements.push(
        <p key={`label-${idx}`} className="font-semibold text-slate-800">
          {renderInlineStyles(trimmed.replace(/\s+:/, ':'))}
        </p>
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
  const [isOpen, setIsOpen] = useState(false);
  const source = imageSources[pageIndex];

  if (imageSources.length === 0) return null;

  if (!source || source.page == null) {
    return (
      <p role="status" className="mt-2 text-xs text-amber-700">
        Manual page image unavailable. Check the public backend URL and ensure the manual PDF is installed on the backend.
      </p>
    );
  }

  const screenLabel = source.screen_reference
    ? `View Scenario — ${source.screen_reference}`
    : `View Scenario — Page ${source.page}`;

  return (
    <div className="mt-2">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 rounded-lg border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-700 transition-colors hover:bg-blue-100 hover:text-blue-900"
      >
        <ImageIcon className="h-3 w-3" />
        <span>{screenLabel}</span>
        {isOpen ? (
          <ChevronUp className="h-3 w-3" />
        ) : (
          <ChevronDown className="h-3 w-3" />
        )}
      </button>

      {isOpen && (
        <div className="mt-2 rounded-lg border border-blue-200 bg-blue-50/50 p-2">
          <img
            src={
              source.image_path
                ? /^https?:\/\//i.test(source.image_path)
                  ? source.image_path
                  : `${API_BASE}${source.image_path.startsWith('/') ? '' : '/'}${source.image_path}`
                : `${API_BASE}/api/manual/page/${source.page}/image`
            }
            alt={`Official e-GP Manual, page ${source.page}`}
            className="max-h-96 max-w-full rounded-lg object-contain"
            onError={() => setPageIndex((index) => Math.min(index + 1, imageSources.length))}
          />
          {imageSources.length > 1 && (
            <div className="mt-1.5 flex items-center justify-center gap-2">
              <button
                onClick={() => setPageIndex((i) => Math.max(0, i - 1))}
                disabled={pageIndex === 0}
                className="rounded border border-blue-200 bg-white px-2 py-0.5 text-xs text-blue-700 disabled:opacity-40"
              >
                ← Prev
              </button>
              <span className="text-xs text-slate-500">
                {pageIndex + 1} / {imageSources.length}
              </span>
              <button
                onClick={() => setPageIndex((i) => Math.min(imageSources.length - 1, i + 1))}
                disabled={pageIndex === imageSources.length - 1}
                className="rounded border border-blue-200 bg-white px-2 py-0.5 text-xs text-blue-700 disabled:opacity-40"
              >
                Next →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const ManualReferences: React.FC<{ sources: ChatSourceCitation[] }> = ({ sources }) => {
  const pages = Array.from(new Set(sources.flatMap((source) => source.page == null ? [] : [source.page]))).slice(0, 4);
  const qaReferences = Array.from(new Set(
    sources
      .filter((source) => source.source_type === 'qa' && source.question_number != null)
      .map((source) => `${source.source}${source.module ? ` · ${source.module}` : ''} · Question ${source.question_number}`)
  ));
  const [isOpen, setIsOpen] = useState(false);

  if (pages.length === 0 && qaReferences.length === 0) return null;

  const refText = [
    ...(pages.length ? [`Official e-GP Manual · ${pages.map((page) => `p. ${page}`).join(', ')}`] : []),
    ...qaReferences,
  ].join('; ');

  return (
    <div className="mt-2">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 rounded-lg border border-amber-200 bg-amber-50 px-3 py-1.5 text-xs font-medium text-amber-700 transition-colors hover:bg-amber-100 hover:text-amber-900"
      >
        <BookOpen className="h-3 w-3" />
        <span>Source Reference</span>
        {isOpen ? (
          <ChevronUp className="h-3 w-3" />
        ) : (
          <ChevronDown className="h-3 w-3" />
        )}
      </button>

      {isOpen && (
        <div className="mt-2 rounded-lg border border-amber-200 bg-amber-50/70 px-3 py-2 text-xs leading-5 text-slate-700">
          <p>📖 <strong>Reference:</strong> {refText}</p>
        </div>
      )}
    </div>
  );
};

const MessageActionButtons: React.FC<{
  sources?: ChatSourceCitation[];
  msgId: string;
}> = ({ sources, msgId }) => {
  const [openPanel, setOpenPanel] = useState<'scenario' | 'reference' | 'helpdesk' | null>(null);

  const toggle = (panel: 'scenario' | 'reference' | 'helpdesk') =>
    setOpenPanel((prev) => (prev === panel ? null : panel));

  // Compute image sources
  const imageSources = sources
    ? Array.from(
        new Map(
          [
            ...sources.filter((s) => s.page != null && s.screen_reference),
            ...sources.filter((s) => s.page != null),
          ].map((s) => [s.page, s])
        ).values()
      )
    : [];

  const [pageIndex, setPageIndex] = useState(0);
  const imgSource = imageSources[pageIndex];

  // Compute reference text
  const pages = sources
    ? Array.from(new Set(sources.flatMap((s) => (s.page == null ? [] : [s.page])))).slice(0, 4)
    : [];
  const qaRefs = sources
    ? Array.from(
        new Set(
          sources
            .filter((s) => s.source_type === 'qa' && s.question_number != null)
            .map((s) => `${s.source}${s.module ? ` · ${s.module}` : ''} · Question ${s.question_number}`)
        )
      )
    : [];
  const hasRef = pages.length > 0 || qaRefs.length > 0;
  const refText = [
    ...(pages.length ? [`Official e-GP Manual · ${pages.map((p) => `p. ${p}`).join(', ')}`] : []),
    ...qaRefs,
  ].join('; ');

  const hasScenario = imageSources.length > 0 && imgSource && imgSource.page != null;

  const scenarioLabel = hasScenario
    ? imgSource.screen_reference
      ? `View Scenario — ${imgSource.screen_reference}`
      : `View Scenario — Page ${imgSource.page}`
    : '';

  return (
    <div className="mt-2.5 space-y-2">
      {/* Horizontal button row */}
      <div className="flex flex-wrap items-center gap-1.5">
        {hasScenario && (
          <button
            onClick={() => toggle('scenario')}
            className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[11px] font-medium transition-colors ${
              openPanel === 'scenario'
                ? 'border-blue-400 bg-blue-100 text-blue-800'
                : 'border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100'
            }`}
          >
            <ImageIcon className="h-3 w-3" />
            <span>{scenarioLabel}</span>
            {openPanel === 'scenario' ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
          </button>
        )}

        {hasRef && (
          <button
            onClick={() => toggle('reference')}
            className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[11px] font-medium transition-colors ${
              openPanel === 'reference'
                ? 'border-amber-400 bg-amber-100 text-amber-800'
                : 'border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100'
            }`}
          >
            <BookOpen className="h-3 w-3" />
            <span>Source Reference</span>
            {openPanel === 'reference' ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
          </button>
        )}

        <button
          onClick={() => toggle('helpdesk')}
          className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[11px] font-medium transition-colors ${
            openPanel === 'helpdesk'
              ? 'border-slate-400 bg-slate-100 text-slate-800'
              : 'border-slate-200 bg-slate-50 text-slate-600 hover:bg-slate-100'
          }`}
        >
          <Phone className="h-3 w-3" />
          <span>Contact Helpdesk</span>
          {openPanel === 'helpdesk' ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
        </button>
      </div>

      {/* Expanded panels */}
      {openPanel === 'scenario' && hasScenario && (
        <div className="rounded-lg border border-blue-200 bg-blue-50/50 p-2">
          <img
            src={
              imgSource.image_path
                ? /^https?:\/\//i.test(imgSource.image_path)
                  ? imgSource.image_path
                  : `${API_BASE}${imgSource.image_path.startsWith('/') ? '' : '/'}${imgSource.image_path}`
                : `${API_BASE}/api/manual/page/${imgSource.page}/image`
            }
            alt={`Official e-GP Manual, page ${imgSource.page}`}
            className="max-h-96 max-w-full rounded-lg object-contain"
            onError={() => setPageIndex((i) => Math.min(i + 1, imageSources.length))}
          />
          {imageSources.length > 1 && (
            <div className="mt-1.5 flex items-center justify-center gap-2">
              <button
                onClick={() => setPageIndex((i) => Math.max(0, i - 1))}
                disabled={pageIndex === 0}
                className="rounded border border-blue-200 bg-white px-2 py-0.5 text-xs text-blue-700 disabled:opacity-40"
              >
                ← Prev
              </button>
              <span className="text-xs text-slate-500">{pageIndex + 1} / {imageSources.length}</span>
              <button
                onClick={() => setPageIndex((i) => Math.min(imageSources.length - 1, i + 1))}
                disabled={pageIndex === imageSources.length - 1}
                className="rounded border border-blue-200 bg-white px-2 py-0.5 text-xs text-blue-700 disabled:opacity-40"
              >
                Next →
              </button>
            </div>
          )}
        </div>
      )}

      {openPanel === 'reference' && hasRef && (
        <div className="rounded-lg border border-amber-200 bg-amber-50/70 px-3 py-2 text-xs leading-5 text-slate-700">
          <p>📖 <strong>Reference:</strong> {refText}</p>
        </div>
      )}

      {openPanel === 'helpdesk' && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50/70 px-3 py-2.5 text-xs leading-5 text-slate-700 space-y-0.5">
          <p>📞 <strong>e-GP Helpdesk Hotline:</strong> 16575 (from any mobile network in Bangladesh)</p>
          <p>☎️ <strong>Telephone Support:</strong> +880 9609112233 / +880 1762625528–31</p>
          <p>✉️ <strong>Email Support:</strong>{' '}
            <a href="mailto:helpdesk@eprocure.gov.bd" className="text-blue-600 underline">helpdesk@eprocure.gov.bd</a>
            {' / '}
            <a href="mailto:e-gphelpdesk@cptu.gov.bd" className="text-blue-600 underline">e-gphelpdesk@cptu.gov.bd</a>
          </p>
          <p>🌐 <strong>Official Portal:</strong>{' '}
            <a href="https://www.eprocure.gov.bd" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">
              https://www.eprocure.gov.bd
            </a>
          </p>
          <p>🏢 <strong>Authority:</strong> Bangladesh Public Procurement Authority (BPPA) / CPTU, IMED, Ministry of Planning</p>
        </div>
      )}
    </div>
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
    <div className="relative flex min-h-0 flex-1 flex-col overflow-hidden bg-[#f7faff] text-slate-800">
      {/* Messages Stream */}
      <div className="min-h-0 flex-1 overflow-y-auto bg-[radial-gradient(circle_at_top,_rgba(219,234,254,0.62),_transparent_42%)] px-3 py-5 sm:px-5 sm:py-6 md:px-8">
        {messages.length === 0 && (
          <div className="mx-auto flex min-h-full w-full max-w-3xl items-center justify-center py-4">
            <div className="w-full max-w-2xl rounded-[1.75rem] border border-white bg-white/85 p-6 text-center shadow-[0_20px_70px_-35px_rgba(15,34,54,0.45)] backdrop-blur-xl sm:p-10">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-[#0B4F8A] to-[#12304A] text-white shadow-lg shadow-blue-900/20">
                <ShieldCheck className="h-8 w-8" />
              </div>
              <div className="mt-5 flex items-center justify-center gap-2 text-[11px] font-bold uppercase tracking-[0.18em] text-[#0B4F8A]">
                <Sparkles className="h-3.5 w-3.5" />
                <span>Official manual assistant</span>
              </div>
              <h2 className="mt-3 text-2xl font-bold tracking-tight text-[#12304A] sm:text-3xl">
                How can we help today?
              </h2>
              <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-500 sm:text-[15px]">
                Ask about e-GP procedures, tender workflows, or upload a portal screenshot. Answers are grounded in the official Procuring Entity manual.
              </p>
              <div className="mt-7 grid gap-2 text-left sm:grid-cols-2">
                {[
                  ['Start a tender', 'How do I create and publish a new tender notice?'],
                  ['Find a procedure', 'How do I log in to the e-GP portal?'],
                  ['Resolve an issue', 'How do I fix evaluation discrepancy error code Q10.4?'],
                  ['Understand a term', 'What is debarment?']
                ].map(([label, prompt]) => (
                  <button
                    key={prompt}
                    type="button"
                    onClick={() => onSendMessage(prompt)}
                    className="group rounded-xl border border-slate-200 bg-slate-50/80 p-3 text-left transition-all hover:-translate-y-0.5 hover:border-blue-300 hover:bg-blue-50/70 hover:shadow-sm"
                  >
                    <span className="flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-[#0B4F8A]">
                      {label}
                      <ArrowUpRight className="h-3.5 w-3.5 opacity-0 transition-opacity group-hover:opacity-100" />
                    </span>
                    <span className="mt-1 block text-xs leading-5 text-slate-600">{prompt}</span>
                  </button>
                ))}
              </div>
              <div className="mt-6 flex items-center justify-center gap-2 text-[11px] text-slate-400">
                <MessageCircle className="h-3.5 w-3.5" />
                <span>Press Enter to send · Shift + Enter for a new line</span>
              </div>
            </div>
          </div>
        )}

        {messages.length > 0 && (
          <div className="mx-auto w-full max-w-3xl space-y-5">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';

          return (
            <div
              key={msg.id}
              className={`flex w-full min-w-0 ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              {!isUser && (
                <div className="mr-3 mt-1 hidden h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-[#0B4F8A] text-white shadow-sm sm:flex">
                  <ShieldCheck className="h-4 w-4" />
                </div>
              )}
              <div
                className={`min-w-0 max-w-[94%] space-y-2 rounded-2xl px-4 py-3.5 shadow-sm sm:max-w-[85%] sm:px-5 ${
                  isUser
                    ? 'rounded-tr-md bg-[#3568D4] text-white shadow-blue-900/10'
                    : 'rounded-tl-md border border-slate-200/80 bg-white text-slate-800'
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

                {!isUser && (
                  <>
                    <div className="flex items-center gap-2 border-t border-slate-100 pt-2 text-[10px] font-semibold uppercase tracking-wide text-emerald-700">
                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                      Grounded in official manual
                    </div>
                    <MessageActionButtons sources={msg.sources} msgId={msg.id} />
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
        )}
      </div>

      {/* Input Form Area */}
      <div className="border-t border-slate-200/80 bg-white/90 p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] shadow-[0_-12px_30px_-24px_rgba(15,34,54,0.5)] backdrop-blur-xl sm:p-4 sm:pb-[max(1rem,env(safe-area-inset-bottom))]">
        <div className="mx-auto max-w-3xl">
          {uploadedImage && (
            <div className="mb-2.5 inline-flex items-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs text-slate-700">
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
            <div className="relative overflow-hidden rounded-2xl border border-slate-300 bg-white transition-all focus-within:border-[#0B4F8A] focus-within:ring-4 focus-within:ring-blue-500/10">
              <textarea
                ref={textareaRef}
                rows={1}
                value={inputQuestion}
                onChange={(e) => setInputQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={language === 'en' ? 'Ask a question...' : 'প্রশ্ন লিখুন...'}
                className="w-full resize-none bg-transparent p-4 pr-28 text-sm text-slate-800 outline-none placeholder:text-slate-400"
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
                  className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-blue-50 hover:text-[#0B4F8A]"
                  title="Attach e-GP portal screenshot"
                  aria-label="Upload portal screenshot"
                >
                  <Paperclip className="h-4 w-4" />
                </button>
                <button
                  type="submit"
                  disabled={(!inputQuestion.trim() && !uploadedImage) || isLoading}
                  className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#0B4F8A] text-white transition-all hover:bg-[#083c6b] hover:shadow-md disabled:cursor-not-allowed disabled:opacity-40"
                  aria-label="Send question"
                >
                  <Send className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </form>
          <p className="mt-2 text-center text-[10px] text-slate-400">AI guidance can be reviewed against the cited manual pages before official action.</p>
        </div>
      </div>
    </div>
  );
};
