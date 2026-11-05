import React from 'react';
import { X, ExternalLink, ShieldAlert, Monitor, CheckCircle, ArrowRight } from 'lucide-react';
import { OFFICIAL_PORTAL_SCREENS } from '../data/manualChunks';
import { PortalScreen } from '../types/egp';

interface PortalScreenModalProps {
  screenId: string | null;
  onClose: () => void;
}

export const PortalScreenModal: React.FC<PortalScreenModalProps> = ({
  screenId,
  onClose
}) => {
  if (!screenId) return null;
  const screen: PortalScreen | undefined = OFFICIAL_PORTAL_SCREENS[screenId];

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 select-none">
      <div className="bg-[#0f171e] border border-slate-700 rounded-2xl w-full max-w-3xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh] animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="bg-[#091016] px-5 py-3.5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/40 text-blue-400 flex items-center justify-center">
              <Monitor className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
                  {screenId}
                </span>
                <h3 className="text-sm font-bold text-white">
                  {screen ? screen.title : 'Official e-GP Portal Screen Reference'}
                </h3>
              </div>
              <p className="text-[11px] text-slate-400">
                Official e-GP Procuring Entity Manual • Page {screen?.page || '56'}
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
        <div className="p-6 overflow-y-auto space-y-4 text-xs">
          {screen ? (
            <>
              {/* Description */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 text-slate-300">
                <p className="leading-relaxed">{screen.description}</p>
                <div className="mt-2 flex items-center gap-4 text-[11px] text-slate-400 border-t border-slate-800 pt-2">
                  <span>Module: <strong className="text-slate-200">{screen.module}</strong></span>
                  <span>Source: <strong className="text-slate-200">PE User Manual 2026</strong></span>
                </div>
              </div>

              {/* Realistic Portal UI Mockup Container */}
              <div className="border border-emerald-900/60 rounded-xl bg-[#08120d] p-4 text-slate-200 shadow-inner">
                {/* Simulated Portal Top Nav */}
                <div className="border-b border-emerald-950 pb-2 mb-3 flex items-center justify-between text-[11px]">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                    <span className="font-bold text-emerald-400">eprocure.gov.bd</span>
                    <span className="text-slate-500">/</span>
                    <span className="text-slate-300 font-mono text-[10px]">{screen.screen_id}</span>
                  </div>
                  <span className="text-emerald-500/80 text-[10px] font-mono">Secured SSL • PKI Token Active</span>
                </div>

                {/* Simulated Form Fields */}
                <div className="space-y-2 bg-[#050c08] p-3 rounded-lg border border-emerald-950">
                  <span className="text-[10px] uppercase font-bold text-emerald-400 tracking-wider">
                    Interface Data Parameters
                  </span>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-1">
                    {screen.fields.map((f, i) => (
                      <div key={i} className="bg-[#0b1710] p-2 rounded border border-emerald-900/50 flex items-center justify-between">
                        <span className="text-slate-300 font-mono text-[11px]">{f}</span>
                        <CheckCircle className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                      </div>
                    ))}
                  </div>
                </div>

                {/* Simulated Action Buttons */}
                <div className="mt-4 flex flex-wrap items-center justify-end gap-2 pt-2 border-t border-emerald-950">
                  {screen.action_buttons.map((btn, i) => (
                    <button
                      key={i}
                      className={`px-3 py-1.5 rounded text-xs font-semibold shadow-sm transition-all ${
                        btn.toLowerCase().includes('delete') || btn.toLowerCase().includes('reject')
                          ? 'bg-red-900/60 hover:bg-red-800 text-red-200 border border-red-700/60'
                          : btn.toLowerCase().includes('approve') || btn.toLowerCase().includes('login')
                          ? 'bg-emerald-700 hover:bg-emerald-600 text-white border border-emerald-500'
                          : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                      }`}
                    >
                      {btn}
                    </button>
                  ))}
                </div>
              </div>

              {/* Warning or Statutory Note */}
              {screen.warning_text && (
                <div className="bg-amber-950/40 border border-amber-800/60 rounded-xl p-3 flex items-start gap-2.5 text-amber-200/90 text-xs">
                  <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-amber-300 block mb-0.5">Statutory Procurement Warning:</span>
                    <p>{screen.warning_text}</p>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="py-8 text-center text-slate-400">
              <p>Portal screen reference details: {screenId}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-[#091016] px-5 py-3 border-t border-slate-800 flex items-center justify-between">
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
