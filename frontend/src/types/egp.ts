/**
 * e-GP Manual Chatbot - Types & Data Contracts
 * Supports Multimodal RAG, FAISS-style Local Vectors, and Offline-First Synchronization
 */

export interface ManualChunk {
  chunk_id: number;
  section_title: string;
  category: 'authentication' | 'app_planning' | 'tender_creation' | 'workflow' | 'evaluation' | 'contract' | 'troubleshooting';
  page_number: number;
  source: string;
  content: string;
  key_terms: string[];
  screen_references: string[]; // e.g. ["Screen - Q10.4", "Screen - D6"]
  vector: number[]; // 64-dimensional normalized vector for client-side FAISS cosine similarity
  last_modified: string; // ISO string
  hash: string; // SHA-256 or CRC32 hash for integrity verification
}

export interface PortalScreen {
  screen_id: string; // "Screen - Q10.4"
  title: string;
  page: number;
  description: string;
  module: string;
  fields: string[];
  action_buttons: string[];
  warning_text?: string;
  screenshot_svg_type: 'login' | 'workflow' | 'tender_edit' | 'app_form' | 'evaluation_grid' | 'error_dialog' | 'contract_view';
}

export interface ChatSourceCitation {
  source: string;
  page?: number | null;
  chunk_id?: number | null;
  score: number;
  snippet: string;
  source_type?: 'manual' | 'qa';
  source_files?: string[];
  question_number?: number | null;
  module?: string | null;
  screen_reference?: string;
  image_path?: string | null;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: number;
  sources?: ChatSourceCitation[];
  portal_screens?: string[];
  image_url?: string;
  image_name?: string;
  // Offline sync metadata
  sync_status: 'synced' | 'pending' | 'syncing' | 'failed';
  local_revision: number;
  hash?: string;
  answered_offline?: boolean;
}

export type SyncMutationType = 'create_message' | 'bookmark_chunk' | 'feedback_vote' | 'update_note';

export interface SyncMutation {
  id: string;
  type: SyncMutationType;
  payload: any;
  client_timestamp: number;
  revision: number;
  status: 'pending' | 'syncing' | 'synced' | 'conflict';
  hash: string;
}

export interface SyncConflict {
  id: string;
  mutation_id: string;
  entity_type: string;
  client_state: any;
  server_state: any;
  resolution_strategy: 'server_wins' | 'client_wins' | 'merged';
  resolved_at?: number;
  notes: string;
}

export interface SyncState {
  is_online: boolean;
  is_simulated_offline: boolean;
  is_syncing: boolean;
  last_synced_at: number | null;
  server_version: string;
  local_version: string;
  pending_count: number;
  total_synced_count: number;
  conflict_count: number;
  checksum_verified: boolean;
  server_hash: string;
  local_hash: string;
  conflict_strategy: 'server_wins' | 'client_wins' | 'last_write_wins';
}

export interface ChatApiResponse {
  question: string;
  answer: string;
  sources: ChatSourceCitation[];
  portal_screens: string[];
  model_used: string;
  was_offline: boolean;
}
