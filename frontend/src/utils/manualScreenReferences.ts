import { OFFICIAL_PORTAL_SCREENS, INITIAL_MANUAL_CHUNKS } from '../data/manualChunks';
import { PortalScreen } from '../types/egp';

function normalizeScreenId(value: string): string {
  return value
    .replace(/^screen\s*/i, '')
    .trim()
    .replace(/[\s.,;:!?]+$/g, '')
    .replace(/[^a-z0-9.]/gi, '')
    .toLowerCase();
}

export function findPortalScreen(screenId: string): PortalScreen | undefined {
  const normalizedScreenId = normalizeScreenId(screenId);
  return Object.values(OFFICIAL_PORTAL_SCREENS)
    .find((item) => normalizeScreenId(item.screen_id) === normalizedScreenId);
}

export function findManualPageForScreen(screenId: string): number | undefined {
  const screen = findPortalScreen(screenId);
  const normalizedScreenId = normalizeScreenId(screenId);
  const referencedChunk = INITIAL_MANUAL_CHUNKS.find((chunk) =>
    chunk.screen_references.some((reference) => normalizeScreenId(reference) === normalizedScreenId)
  );

  return referencedChunk?.page_number ?? screen?.page;
}
