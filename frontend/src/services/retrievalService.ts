/**
 * Retrieval Service (frontend/src/services/retrievalService.ts).
 * Client-side retrieval adapter connecting to IndexedDB and offline vector engine.
 */
import { ManualChunk } from '../types/egp';
import { getLocalChunks } from '../utils/indexedDBStorage';
import { retrieveTopKChunks } from '../utils/offlineVectorEngine';

export async function searchLocalManual(query: string, topK: number = 5): Promise<{ chunk: ManualChunk; score: number }[]> {
  const chunks = await getLocalChunks();
  return retrieveTopKChunks(query, chunks, topK);
}

