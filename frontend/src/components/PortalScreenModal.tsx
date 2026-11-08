import React, { useEffect, useState } from 'react';
import { X, Monitor, ImageOff } from 'lucide-react';
import { API_BASE } from '../services/api';
import { findManualPageForScreen, findPortalScreen } from '../utils/manualScreenReferences';

interface PortalScreenModalProps {
  screenId: string | null;
  onClose: () => void;
}

export const PortalScreenModal: React.FC<PortalScreenModalProps> = ({
  screenId,
  onClose
}) => {
  const page = screenId ? findManualPageForScreen(screenId) : undefined;
  const screen = screenId ? findPortalScreen(screenId) : undefined;
  const imageUrl = page ? `${API_BASE}/api/manual/page/${page}/image` : null;
  const [imageStatus, setImageStatus] = useState<'loading' | 'loaded' | 'error'>('loading');

  useEffect(() => {
    setImageStatus('loading');
  }, [imageUrl]);

  const imageTitle = screen?.title ?? `Manual screenshot for ${screenId}`;

  if (!screenId) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/35 backdrop-blur-md flex items-center justify-center p-4 select-none">
      <div className="bg-[#0f171e]/75 backdrop-blur-2xl border border-white/20 rounded-2xl w-full max-w-3xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh] animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="bg-white/[0.04] px-5 py-3.5 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/40 text-blue-400 flex items-center justify-center">
              <Monitor className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                  {screenId}
                </span>
                <h3 className="text-sm font-bold text-white">{imageTitle}</h3>
              </div>
              <p className="text-[11px] text-slate-400">
                Official e-GP Procuring Entity Manual • Page {page ?? 'not found'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 overflow-y-auto min-h-64 flex items-center justify-center bg-slate-950/25">
          {imageUrl ? (
            <>
              {imageStatus === 'loading' && (
                <p className="text-sm text-slate-400">Loading the original manual page image…</p>
              )}
              {imageStatus === 'error' && (
                <div className="flex flex-col items-center gap-2 text-center text-slate-400">
                  <ImageOff className="w-8 h-8" />
                  <p>The original screenshot for page {page} is not available from the image service.</p>
                </div>
              )}
              <img
                src={imageUrl}
                alt={`${screenId} from e-GP manual, page ${page}`}
                className={`max-h-[65vh] max-w-full object-contain ${imageStatus === 'loaded' ? 'block' : 'hidden'}`}
                onLoad={() => setImageStatus('loaded')}
                onError={() => setImageStatus('error')}
              />
            </>
          ) : (
            <div className="flex flex-col items-center gap-2 text-center text-slate-400">
              <ImageOff className="w-8 h-8" />
              <p>This screen reference could not be matched to a page in the manual.</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-white/[0.04] px-5 py-3 border-t border-white/10 flex items-center justify-between">
          <span className="text-[11px] text-slate-400">
            Referenced in e-GP System User Manual (Procuring Entity User)
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-medium text-xs transition-colors"
          >
            Close Preview
          </button>
        </div>
      </div>
    </div>
  );
};
