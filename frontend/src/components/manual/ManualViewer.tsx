import React, { useState, useEffect } from 'react';
import { BookOpen, Search, Image as ImageIcon } from 'lucide-react';
import { PageNavigator } from './PageNavigator';
import { ScreenshotViewer } from './ScreenshotViewer';
import { ManualChunk } from '../../types/egp';
import { INITIAL_MANUAL_CHUNKS } from '../../data/manualChunks';

interface ManualViewerProps {
  initialPage?: number;
}

export const ManualViewer: React.FC<ManualViewerProps> = ({ initialPage = 6 }) => {
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeModalImage, setActiveModalImage] = useState<string | null>(null);

  useEffect(() => {
    if (initialPage) setCurrentPage(initialPage);
  }, [initialPage]);

  // Filter chunks for current page
  const pageChunks = INITIAL_MANUAL_CHUNKS.filter(c => c.page_number === currentPage);

  // Filter chunks for search
  const searchedChunks = searchQuery.trim()
    ? INITIAL_MANUAL_CHUNKS.filter(
        c =>
          c.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
          c.section_title.toLowerCase().includes(searchQuery.toLowerCase())
      ).slice(0, 10)
    : [];

  return (
    <div className="flex flex-col h-full bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800">
      {/* Header & Page Navigator */}
      <PageNavigator
        currentPage={currentPage}
        totalPages={543}
        onPageChange={(p) => {
          setCurrentPage(p);
          setSearchQuery('');
        }}
      />

      {/* Quick Search */}
      <div className="p-3 border-b border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-900/50">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search within 543 manual pages..."
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-emerald-500"
          />
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {searchQuery.trim() ? (
          <div>
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
              Search Results ({searchedChunks.length})
            </h4>
            <div className="space-y-3">
              {searchedChunks.map((chunk) => (
                <div
                  key={chunk.chunk_id}
                  onClick={() => {
                    setCurrentPage(chunk.page_number);
                    setSearchQuery('');
                  }}
                  className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-emerald-500 hover:bg-emerald-50/30 dark:hover:bg-emerald-950/20 cursor-pointer transition-colors"
                >
                  <div className="flex items-center justify-between text-xs font-semibold text-emerald-800 dark:text-emerald-400 mb-1">
                    <span>Page {chunk.page_number}</span>
                    <span className="text-slate-400 font-normal">Chunk #{chunk.chunk_id}</span>
                  </div>
                  <h5 className="text-sm font-medium text-slate-800 dark:text-slate-200 mb-1">
                    {chunk.section_title}
                  </h5>
                  <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-3">
                    {chunk.content}
                  </p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                <BookOpen className="w-4 h-4" />
                e-GP PE User Manual (Page {currentPage})
              </span>
            </div>

            {pageChunks.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-sm">
                No indexed text blocks on Page {currentPage}.
              </div>
            ) : (
              <div className="space-y-4">
                {pageChunks.map((chunk) => (
                  <div
                    key={chunk.chunk_id}
                    className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-950/40"
                  >
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-2">
                      {chunk.section_title}
                    </h4>
                    <p className="text-xs text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed">
                      {chunk.content}
                    </p>

                    {chunk.screen_references && chunk.screen_references.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2 pt-2 border-t border-slate-200/60 dark:border-slate-800/60">
                        {chunk.screen_references.map((screen, idx) => (
                          <button
                            key={idx}
                            onClick={() => setActiveModalImage(`/api/manual/page/${currentPage}/image`)}
                            className="flex items-center gap-1 text-[11px] px-2 py-1 rounded bg-emerald-100/70 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 font-medium hover:bg-emerald-200 cursor-pointer"
                          >
                            <ImageIcon className="w-3 h-3" />
                            <span>{screen}</span>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Screenshot Viewer Modal */}
      <ScreenshotViewer
        isOpen={Boolean(activeModalImage)}
        imageUrl={activeModalImage || ''}
        title={`Portal Screen — Page ${currentPage}`}
        onClose={() => setActiveModalImage(null)}
      />
    </div>
  );
};

