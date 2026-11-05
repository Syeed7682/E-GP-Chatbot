import { ChatApiResponse, ChatSourceCitation, ManualChunk } from '../types/egp';
import { generateOfflineAnswer, retrieveTopKChunks } from '../utils/offlineVectorEngine';
import { getLocalChunks } from '../utils/indexedDBStorage';

// Base API URL from environment variable, falling back to window location origin or relative path
const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export interface BackendHealthResponse {
  status: string;
  total_chunks?: number;
  vector_store?: string;
  verified_chunks?: number;
  system?: string;
}

export interface SendChatParams {
  question: string;
  image_base64?: string | null;
  image_name?: string;
  top_k?: number;
}

/**
 * Checks the FastAPI backend health status
 */
export async function checkBackendHealth(): Promise<{ isHealthy: boolean; details?: BackendHealthResponse }> {
  try {
    const url = `${API_BASE}/api/chat/health`;
    const res = await fetch(url, { method: 'GET' });
    if (res.ok) {
      const data: BackendHealthResponse = await res.json();
      return { isHealthy: true, details: data };
    }
    // Try fallback endpoint
    const fallbackRes = await fetch(`${API_BASE}/api/health`);
    if (fallbackRes.ok) {
      const data = await fallbackRes.json();
      return { isHealthy: true, details: data };
    }
    return { isHealthy: false };
  } catch {
    return { isHealthy: false };
  }
}

/**
 * Retrieves loaded chunks from the backend
 */
export async function fetchBackendChunks(): Promise<ManualChunk[]> {
  try {
    const url = `${API_BASE}/api/chat/chunks`;
    const res = await fetch(url);
    if (res.ok) {
      const data = await res.json();
      return data.chunks || data;
    }
  } catch (err) {
    console.warn('Could not fetch backend chunks, using local IndexedDB chunks', err);
  }
  return await getLocalChunks();
}

/**
 * Sends chat query to the FastAPI backend with offline-first fallback
 */
export async function sendChatQuery(params: SendChatParams): Promise<ChatApiResponse> {
  const { question, image_base64, image_name, top_k = 3 } = params;

  try {
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question,
        top_k,
        image: image_base64 || null,
        image_base64: image_base64 || null,
        image_name: image_name || null
      })
    });

    if (response.ok) {
      const data = await response.json();
      return {
        question: data.question || question,
        answer: data.answer,
        sources: data.sources || [],
        portal_screens: data.portal_screens || [],
        model_used: data.model_used || 'FastAPI Multimodal RAG Backend',
        was_offline: false
      };
    }
  } catch (err) {
    console.warn('Backend unavailable, falling back to local offline RAG engine:', err);
  }

  // Graceful offline fallback
  const localChunks = await getLocalChunks();
  const offlineResult = generateOfflineAnswer(question, localChunks, image_name);
  return offlineResult;
}
