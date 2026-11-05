import React, { useRef, useEffect, useState } from 'react';
import {
  Send,
  Paperclip,
  X,
  Bot,
  User,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  BookOpen,
  Monitor,
  AlertCircle,
  ExternalLink,
  ShieldCheck,
  RotateCcw,
  Sparkles
} from 'lucide-react';
import { ChatMessage, SyncState, ChatSourceCitation } from '../types/egp';

interface GovtChatAreaProps {
  messages: ChatMessage[];
  syncState: SyncState;
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
  onSelectSuggestedQuestion: (question: string) => void;
}

// Professional Government Response Formatter Component
const FormattedGovtText: React.FC<{ text: string }> = ({ text }) => {
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];
  let currentList: React.ReactNode[] = [];

  const flushList = () => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`list-${elements.length}`} className="space-y-1.5 my-2 pl-1">
          {currentList}
        </ul>
      );
      currentList = [];
    }
  };

  const renderInlineStyles = (str: string) => {
    const parts = str.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="font-semibold text-[#12304A]">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={i} className="px-1.5 py-0.5 rounded bg-slate-100 text-[#0B4F8A] font-mono text-[11px] font-medium border border-slate-200">{part.slice(1, -1)}</code>;
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

    // Markdown Header 3 (### Section Title)
    if (trimmed.startsWith('### ')) {
      flushList();
      const title = trimmed.replace(/^###\s+/, '');
      elements.push(
        <div key={`h3-${idx}`} className="pb-2 mb-2.5 border-b border-[#D5DEE7] flex items-center gap-2">
          <div className="w-1.5 h-4 bg-[#0B4F8A] rounded-full shrink-0" />
          <h4 className="font-bold text-xs md:text-sm text-[#12304A] tracking-tight">{title}</h4>
        </div>
      );
      return;
    }

    // Major sub-status headings like "1. Tender in "Draft" Status:"
    if (/^\d+\.\s+.*(Status|Status:|Guide|Procedure|Guidelines|Examination):/i.test(trimmed)) {
      flushList();
      elements.push(
        <div key={`subhead-${idx}`} className="mt-3 mb-1.5 font-bold text-xs text-[#0B4F8A] flex items-center gap-2">
          <span className="w-4 h-4 rounded-full bg-blue-100 text-[#0B4F8A] text-[10px] font-bold flex items-center justify-center shrink-0">
            {trimmed.charAt(0)}
          </span>
          <span>{renderInlineStyles(trimmed.replace(/^\d+\.\s*/, ''))}</span>
        </div>
      );
      return;
    }

    // Bullet points (- or •)
    if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
      const content = trimmed.substring(2);
      currentList.push(
        <li key={`li-${idx}`} className="flex items-start gap-2 text-xs text-[#334155] leading-relaxed">
          <span className="text-[#0B4F8A] font-bold text-xs mt-0.5">•</span>
          <span>{renderInlineStyles(content)}</span>
        </li>
      );
      return;
    }

    // Numbered procedure steps (1. Step content)
    if (/^\d+[\.\)]\s+/.test(trimmed)) {
      flushList();
      const numMatch = trimmed.match(/^(\d+)[\.\)]\s+(.*)/);
      if (numMatch) {
        const stepNum = numMatch[1];
        const stepContent = numMatch[2];
        elements.push(
          <div key={`step-${idx}`} className="flex items-start gap-2.5 my-1.5 p-2 rounded bg-slate-50/80 border border-slate-100">
            <span className="w-5 h-5 rounded-full bg-[#0B4F8A] text-white text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
              {stepNum}
            </span>
            <span className="text-xs text-[#334155] leading-relaxed">
              {renderInlineStyles(stepContent)}
            </span>
          </div>
        );
        return;
      }
    }

    // Regular paragraph
    flushList();
    elements.push(
      <p key={`p-${idx}`} className="text-xs text-[#334155] leading-relaxed my-1">
        {renderInlineStyles(trimmed)}
      </p>
    );
  });

  flushList();

  return <div className="space-y-1">{elements}</div>;
};

export const GovtChatArea: React.FC<GovtChatAreaProps> = ({
  messages,
  syncState,
  inputQuestion,
  setInputQuestion,
  onSendMessage,
  isLoading,
  uploadedImage,
  onImageSelected,
  onOpenScreenModal,
  language,
  backendError,
  onRetry,
  onSelectSuggestedQuestion
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const toggleSourceExpand = (id: string) => {
    setExpandedSources(prev => ({ ...prev, [id]: !prev[id] }));
  };

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

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex-1 flex flex-col bg-[#F3F6F9] text-[#334155] overflow-hidden relative">
      {/* Top Assistance Banner */}
      <div className="bg-white border-b border-[#D5DEE7] px-6 py-3 flex items-center justify-between shadow-xs">
        <div>
          <h2 className="text-sm font-bold text-[#12304A] flex items-center gap-2">
            <span>{language === 'en' ? 'e-GP Official Manual Assistant' : 'ই-জিপি অফিসিয়াল ম্যানুয়াল সহায়িকা'}</span>
            <span className="text-[10px] bg-blue-100 text-[#0B4F8A] font-semibold px-2 py-0.5 rounded border border-blue-200">
              Procuring Entity (PE) Manual
            </span>
          </h2>
          <p className="text-xs text-slate-500">
            {language === 'en'
              ? 'Answers are grounded in the 543-page official e-GP user manual with precise page citations.'
              : 'অফিসিয়াল ৫৪৩ পৃষ্ঠার ব্যবহারকারী ম্যানুয়াল থেকে যথাযথ পৃষ্ঠা নম্বরসহ উত্তর প্রদান করা হয়।'}
          </p>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-xs">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#F3F6F9] border border-[#D5DEE7] text-slate-600 font-medium">
            <ShieldCheck className="w-3.5 h-3.5 text-[#16834A]" />
            <span>PPR 2025/2026 Rules Grounded</span>
          </span>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
        {/* Welcome Message Card */}
        <div className="bg-white border border-[#D5DEE7] rounded-lg p-5 shadow-xs space-y-3">
          <div className="flex items-start gap-3.5">
            <div className="w-9 h-9 rounded-md bg-[#0B4F8A] text-white flex items-center justify-center shrink-0 shadow-xs">
              <Bot className="w-5 h-5 text-blue-100" />
            </div>
            <div className="space-y-2 text-xs text-[#334155] flex-1">
              <h3 className="font-bold text-sm text-[#12304A]">
                {language === 'en'
                  ? 'Welcome to the e-GP Manual Assistance Chatbot'
                  : 'ই-জিপি ম্যানুয়াল সহায়তা চ্যাটবটে আপনাকে স্বাগতম'}
              </h3>
              <p className="leading-relaxed">
                {language === 'en'
                  ? 'This public-service assistant helps Procuring Entity (PE) officers navigate the official electronic Government Procurement (e-GP) guidelines. Ask any procedural question, seek clarification on PPR rules, or attach an e-GP portal error screenshot for multimodal diagnosis.'
                  : 'এই সরকারি সেবা সহায়িকা ক্রয়কারী সত্তার (PE) কর্মকর্তাদের অফিসিয়াল ই-জিপি নির্দেশিকা অনুসরণে সহায়তা করে। যেকোনো প্রক্রিয়াগত প্রশ্ন করুন বা পোর্টালে কোনো এরর স্ক্রিনশট থাকলে তা সংযুক্ত করুন।'}
              </p>

              <div className="pt-2 border-t border-[#D5DEE7]">
                <span className="font-semibold text-slate-700 block mb-1.5">
                  {language === 'en' ? 'Quick topics you can ask about:' : 'যেসব বিষয়ে প্রশ্ন করতে পারেন:'}
                </span>
                <div className="flex flex-wrap gap-2">
                  {[
                    'How do I log in to the e-GP portal?',
                    'How can I create a Procuring Entity account?',
                    'Annual Procurement Plan (APP) guide',
                    'How to view Approved Workflow?',
                    'How to delete a tender?'
                  ].map((topic, i) => (
                    <button
                      key={i}
                      onClick={() => onSelectSuggestedQuestion(topic)}
                      className="px-2.5 py-1 rounded bg-[#F3F6F9] hover:bg-blue-50 text-[#0B4F8A] hover:text-[#083c6b] border border-[#D5DEE7] hover:border-[#0B4F8A] text-[11px] font-medium transition-colors cursor-pointer"
                    >
                      {topic}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Message History */}
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          const isExpanded = expandedSources[msg.id] ?? false;

          return (
            <div
              key={msg.id}
              className={`flex items-start gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              {!isUser && (
                <div className="w-8 h-8 rounded-md bg-[#0B4F8A] text-white flex items-center justify-center shrink-0 shadow-xs">
                  <Bot className="w-4 h-4 text-blue-100" />
                </div>
              )}

              <div
                className={`max-w-3xl rounded-lg p-4 text-xs space-y-3 shadow-xs border ${
                  isUser
                    ? 'bg-[#EBF3FB] border-blue-200 text-[#12304A]'
                    : 'bg-white border-[#D5DEE7] text-[#334155]'
                }`}
              >
                {/* Uploaded Screenshot if any */}
                {msg.image_url && (
                  <div className="rounded border border-[#D5DEE7] overflow-hidden max-w-sm mb-2 bg-[#F3F6F9]">
                    <img
                      src={msg.image_url}
                      alt={msg.image_name || 'Portal Screenshot'}
                      className="w-full h-auto object-cover max-h-52"
                    />
                    <div className="p-1.5 text-[11px] font-medium text-slate-600 bg-slate-100 border-t border-[#D5DEE7]">
                      📷 {msg.image_name || 'Portal Screenshot'}
                    </div>
                  </div>
                )}

                {/* Main Message Text with Professional Government Typography */}
                <div className="leading-relaxed text-xs">
                  <FormattedGovtText text={msg.text} />
                </div>

                {/* Expandable Source References (Source: Official e-GP User Manual) */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="border border-[#D5DEE7] rounded bg-[#F8FAFC] overflow-hidden mt-2">
                    <button
                      onClick={() => toggleSourceExpand(msg.id)}
                      className="w-full px-3 py-2 flex items-center justify-between text-left text-xs font-semibold text-[#0B4F8A] hover:bg-blue-50/50 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center gap-1.5">
                        <BookOpen className="w-3.5 h-3.5 text-[#16834A]" />
                        <span>Source: Official e-GP User Manual</span>
                        <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.2 rounded font-normal">
                          {msg.sources.length} {msg.sources.length === 1 ? 'citation' : 'citations'}
                        </span>
                      </div>
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-slate-500" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-slate-500" />
                      )}
                    </button>

                    {isExpanded && (
                      <div className="p-3 border-t border-[#D5DEE7] space-y-2.5 bg-white text-[11px]">
                        {msg.sources.map((src, sIdx) => (
                          <div key={sIdx} className="p-2.5 rounded border border-[#E2E8F0] bg-[#F8FAFC] space-y-1">
                            <div className="flex items-center justify-between font-semibold text-slate-800">
                              <span className="truncate pr-2">{src.source}</span>
                              <span className="text-[#0B4F8A] bg-blue-50 px-2 py-0.5 rounded border border-blue-200 shrink-0">
                                Page {src.page}
                              </span>
                            </div>

                            <p className="text-slate-600 leading-relaxed italic">
                              "{src.snippet}"
                            </p>

                            <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-200/60">
                              <span>Chunk ID: #{src.chunk_id}</span>
                              {src.score && (
                                <span className="font-medium text-[#16834A]">
                                  Match Score: {Math.round(src.score * 100)}%
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Bottom Metadata & Copy button */}
                <div className="flex items-center justify-between pt-1 border-t border-slate-100 text-[10px] text-slate-500">
                  <span className="flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3 text-[#16834A]" />
                    <span>e-GP PE Manual Grounded</span>
                  </span>

                  {!isUser && (
                    <button
                      onClick={() => handleCopy(msg.text, msg.id)}
                      className="flex items-center gap-1 px-1.5 py-0.5 rounded hover:bg-slate-100 text-slate-500 hover:text-slate-800 transition-colors cursor-pointer"
                      title="Copy response text"
                    >
                      {copiedId === msg.id ? (
                        <>
                          <Check className="w-3 h-3 text-[#16834A]" />
                          <span className="text-[#16834A]">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>

              {isUser && (
                <div className="w-8 h-8 rounded-md bg-[#12304A] text-white flex items-center justify-center shrink-0 shadow-xs">
                  <User className="w-4 h-4 text-slate-200" />
                </div>
              )}
            </div>
          );
        })}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex items-start gap-3.5">
            <div className="w-8 h-8 rounded-md bg-[#0B4F8A] text-white flex items-center justify-center shrink-0 shadow-xs">
              <Bot className="w-4 h-4 text-blue-100" />
            </div>
            <div className="bg-white border border-[#D5DEE7] rounded-lg p-4 shadow-xs flex items-center gap-3 text-xs text-slate-600">
              <div className="w-4 h-4 border-2 border-[#0B4F8A] border-t-transparent rounded-full animate-spin" />
              <span>Retrieving official procedural guidelines from 543-page e-GP PE manual...</span>
            </div>
          </div>
        )}

        {/* Backend Error Banner if any */}
        {backendError && (
          <div className="bg-red-50 border border-red-300 rounded-lg p-3 text-xs text-red-800 flex items-start justify-between gap-3 shadow-xs">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold block">Backend Service Notice</span>
                <p>{backendError}</p>
                <p className="text-[11px] text-red-700 mt-1">
                  Offline fallback is active: Queries continue to be resolved locally using the in-browser vector index.
                </p>
              </div>
            </div>
            <button
              onClick={onRetry}
              className="px-2.5 py-1 bg-white hover:bg-red-100 text-red-700 border border-red-300 rounded font-semibold text-xs shrink-0 transition-colors"
            >
              Retry Connection
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form Area */}
      <div className="p-4 bg-white border-t border-[#D5DEE7] shadow-sm">
        {/* Uploaded Image Preview Chip */}
        {uploadedImage && (
          <div className="mb-2.5 inline-flex items-center gap-2 p-1.5 px-3 bg-blue-50 border border-blue-200 rounded-md text-xs text-[#0B4F8A]">
            <span className="font-medium truncate max-w-xs">📷 {uploadedImage.name}</span>
            <button
              onClick={() => onImageSelected(null)}
              className="text-slate-500 hover:text-red-600 p-0.5 rounded cursor-pointer"
              title="Remove screenshot"
              aria-label="Remove attached screenshot"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        <form onSubmit={handleFormSubmit} className="space-y-2">
          <div className="relative border border-[#D5DEE7] focus-within:border-[#0B4F8A] focus-within:ring-1 focus-within:ring-[#0B4F8A] rounded-lg bg-white overflow-hidden transition-all">
            <textarea
              ref={textareaRef}
              rows={2}
              value={inputQuestion}
              onChange={(e) => setInputQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                language === 'en'
                  ? "Type your question about e-GP (e.g. login, tender deletion, workflow approval)... Press Enter to send, Shift+Enter for new line"
                  : "ই-জিপি সম্পর্কিত আপনার প্রশ্নটি লিখুন... (পাঠাতে Enter চাপুন, নতুন লাইনের জন্য Shift+Enter)"
              }
              className="w-full p-3 pr-24 text-xs md:text-sm bg-transparent outline-none resize-none text-slate-800 placeholder-slate-400"
            />

            <div className="absolute right-2 bottom-2.5 flex items-center gap-1.5">
              {/* Paperclip / Image Upload Control */}
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
                className="p-1.5 text-slate-500 hover:text-[#0B4F8A] hover:bg-slate-100 rounded transition-colors cursor-pointer"
                title="Attach e-GP portal error screenshot"
                aria-label="Upload portal screenshot"
              >
                <Paperclip className="w-4 h-4" />
              </button>

              {/* Send Button */}
              <button
                type="submit"
                disabled={(!inputQuestion.trim() && !uploadedImage) || isLoading}
                className="px-3.5 py-1.5 bg-[#0B4F8A] hover:bg-[#083c6b] disabled:opacity-40 text-white rounded font-medium text-xs flex items-center gap-1.5 shadow-xs transition-colors cursor-pointer"
                aria-label="Send question"
              >
                <span>Send</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-500 px-1">
            <span>
              Keyboard: <kbd className="bg-slate-100 px-1 py-0.5 rounded border border-slate-300 font-mono text-[10px]">Enter</kbd> to send • <kbd className="bg-slate-100 px-1 py-0.5 rounded border border-slate-300 font-mono text-[10px]">Shift + Enter</kbd> for new line
            </span>
            <span className="font-medium text-[#16834A]">
              PPR 2025/2026 Procurement Rules Compliant
            </span>
          </div>
        </form>
      </div>
    </div>
  );
};
