/**
 * Chat Service (frontend/src/services/chatService.ts).
 * High-level orchestration for user messages, history, and offline dispatch.
 */
import { sendChatQuery, SendChatParams } from './api';
import { ChatApiResponse, ChatMessage } from '../types/egp';
import { saveLocalMessage } from '../utils/indexedDBStorage';

export async function submitChatMessage(
  params: SendChatParams,
  onAssistantMessage?: (msg: ChatMessage) => void
): Promise<ChatApiResponse> {
  // 1. Dispatch chat query (routes to backend with offline fallback)
  const response = await sendChatQuery(params);

  // 2. Persist assistant message to offline cache
  const assistantMsg: ChatMessage = {
    id: `asst-${Date.now()}`,
    role: 'assistant',
    content: response.answer,
    sources: response.sources,
    portal_screens: response.portal_screens,
    model_used: response.model_used,
    was_offline: response.was_offline,
    timestamp: Date.now()
  };

  try {
    await saveLocalMessage(assistantMsg);
  } catch (err) {
    console.warn('Could not persist message locally:', err);
  }

  if (onAssistantMessage) {
    onAssistantMessage(assistantMsg);
  }

  return response;
}

