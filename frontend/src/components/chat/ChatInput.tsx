import React, { useState, useRef } from 'react';
import { Send, Image as ImageIcon, X } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (text: string, imageBase64?: string, imageName?: string) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [text, setText] = useState('');
  const [attachedImage, setAttachedImage] = useState<string | null>(null);
  const [attachedImageName, setAttachedImageName] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAttachedImageName(file.name);
      const reader = new FileReader();
      reader.onload = () => {
        setAttachedImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSend = () => {
    if ((!text.trim() && !attachedImage) || isLoading) return;
    onSendMessage(text.trim(), attachedImage || undefined, attachedImageName || undefined);
    setText('');
    setAttachedImage(null);
    setAttachedImageName('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-3">
      {/* Attached Image Preview */}
      {attachedImage && (
        <div className="mb-2 flex items-center gap-2 p-2 rounded-lg bg-slate-100 dark:bg-slate-800 w-fit">
          <img src={attachedImage} alt="Thumbnail" className="w-10 h-10 object-cover rounded" />
          <span className="text-xs text-slate-700 dark:text-slate-300 max-w-[200px] truncate">
            {attachedImageName}
          </span>
          <button
            onClick={() => {
              setAttachedImage(null);
              setAttachedImageName('');
              if (fileInputRef.current) fileInputRef.current.value = '';
            }}
            className="p-1 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-full"
          >
            <X className="w-3.5 h-3.5 text-slate-500" />
          </button>
        </div>
      )}

      <div className="flex items-end gap-2">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/*"
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          title="Upload e-GP portal screenshot"
          className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <ImageIcon className="w-5 h-5" />
        </button>

        <textarea
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about e-GP guidelines or paste an error screenshot..."
          className="flex-1 max-h-32 min-h-[44px] resize-none rounded-xl border border-slate-200 dark:border-slate-700 px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder:text-slate-400"
        />

        <button
          onClick={handleSend}
          disabled={(!text.trim() && !attachedImage) || isLoading}
          className="p-2.5 rounded-xl bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-40 disabled:hover:bg-emerald-600 transition-all shadow-sm cursor-pointer"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

