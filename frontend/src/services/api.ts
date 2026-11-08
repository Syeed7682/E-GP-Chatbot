import { ChatApiResponse, ChatSourceCitation, ManualChunk } from '../types/egp';
import { generateOfflineAnswer, retrieveTopKChunks } from '../utils/offlineVectorEngine';
import { getLocalChunks } from '../utils/indexedDBStorage';

// Production deployments need the separately hosted API; local development may use Vite's proxy.
export const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/+$/, '');

export interface BackendHealthResponse {
  status: string;
  total_chunks?: number;
  vector_store?: string;
  verified_chunks?: number;
  system?: string;
}

export interface SendChatParams {
  question: string;
  previous_question?: string;
  image_base64?: string | null;
  image_mime?: string;
  image_name?: string;
  top_k?: number;
  use_alt_model?: boolean;
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
 * Sends chat queries to FastAPI; offline fallback is limited to development.
 */
export async function sendChatQuery(params: SendChatParams): Promise<ChatApiResponse> {
  const { question, previous_question, image_base64, image_mime, image_name, top_k = 3, use_alt_model = false } = params;

  if (import.meta.env.PROD && !API_BASE) {
    throw new Error('The assistant backend is not configured for this site. Set VITE_API_BASE_URL in Netlify to your public FastAPI backend URL, then redeploy.');
  }

  try {
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question,
        previous_question,
        top_k,
        image: image_base64 || null,
        image_base64: image_base64 || null,
        image_mime: image_mime || 'image/png',
        image_name: image_name || null,
        use_alt_model
      })
    });

    if (!response.ok) {
      throw new Error(`The assistant backend returned HTTP ${response.status}. Check the backend URL and service logs.`);
    }

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.toLowerCase().includes('application/json')) {
      throw new Error('The configured API URL did not return JSON. Set VITE_API_BASE_URL to the FastAPI backend origin, not the Netlify site URL, then redeploy.');
    }

    const data = await response.json();
    return {
      question: data.question || question,
      answer: data.answer,
      sources: data.sources || [],
      portal_screens: data.portal_screens || [],
      model_used: data.model_used || 'FastAPI Multimodal RAG Backend',
      was_offline: false
    };
  } catch (err) {
    if (import.meta.env.PROD) {
      if (err instanceof Error && (err.message.startsWith('The assistant backend') || err.message.startsWith('The configured API URL'))) {
        throw err;
      }
      throw new Error('Could not reach the assistant backend. Check that VITE_API_BASE_URL is the public FastAPI URL, the backend is running, and its CORS_ORIGINS includes this Netlify site.');
    }
    console.warn('Backend unavailable, falling back to local offline RAG engine:', err);
  }

  // Graceful offline fallback
  const localChunks = await getLocalChunks();
  const offlineResult = generateOfflineAnswer(question, localChunks, image_name, previous_question);
  return offlineResult;
}
