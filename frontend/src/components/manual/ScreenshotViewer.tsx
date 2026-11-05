import React from 'react';
import { X, ZoomIn, Download } from 'lucide-react';

interface ScreenshotViewerProps {
  isOpen: boolean;
  imageUrl: string;
  title?: string;
  onClose: () => void;
}

export const ScreenshotViewer: React.FC<ScreenshotViewerProps> = ({
  isOpen,
  imageUrl,
  title = 'Portal Screenshot',
  onClose
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
      <div className="relative max-w-4xl w-full bg-white dark:bg-slate-900 rounded-2xl overflow-hidden shadow-2xl border border-slate-200 dark:border-slate-800">
        <div className="flex items-center justify-between p-3.5 border-b border-slate-200 dark:border-slate-800">
          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2">
            <ZoomIn className="w-4 h-4 text-emerald-600" />
            {title}
          </h3>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-4 max-h-[75vh] overflow-auto flex items-center justify-center bg-slate-100 dark:bg-slate-950">
          <img src={imageUrl} alt={title} className="max-w-full max-h-[70vh] object-contain rounded-lg shadow-sm" />
        </div>

        <div className="p-3 bg-slate-50 dark:bg-slate-900/60 border-t border-slate-200 dark:border-slate-800 flex justify-end">
          <a
            href={imageUrl}
            download="egp-portal-screen.jpg"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            Download Image
          </a>
        </div>
      </div>
    </div>
  );
};

