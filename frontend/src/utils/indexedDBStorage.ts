import { ManualChunk, ChatMessage, SyncMutation, SyncConflict } from '../types/egp';
import { INITIAL_MANUAL_CHUNKS, SERVER_DATASET_VERSION, SERVER_DATASET_HASH } from '../data/manualChunks';

const DB_NAME = 'egp_rag_offline_db';
const DB_VERSION = 2;

let dbInstance: IDBDatabase | null = null;

async function openDatabase(): Promise<IDBDatabase> {
  if (dbInstance) return dbInstance;
  return new Promise((resolve, reject) => {
    if (typeof indexedDB === 'undefined') {
      return reject(new Error('IndexedDB not supported'));
    }
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (e) => {
      const db = (e.target as IDBOpenDBRequest).result;

      if (db.objectStoreNames.contains('chunks')) {
        db.deleteObjectStore('chunks');
      }
      db.createObjectStore('chunks', { keyPath: 'chunk_id' });

      if (!db.objectStoreNames.contains('messages')) {
        db.createObjectStore('messages', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('outbox')) {
        db.createObjectStore('outbox', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('conflicts')) {
        db.createObjectStore('conflicts', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('metadata')) {
        db.createObjectStore('metadata', { keyPath: 'key' });
      }
    };

    request.onsuccess = (e) => {
      dbInstance = (e.target as IDBOpenDBRequest).result;
      resolve(dbInstance);
    };

    request.onerror = (e) => {
      reject((e.target as IDBOpenDBRequest).error);
    };
  });
}

// Fallback memory stores if IndexedDB is blocked
const memoryStore = {
  chunks: new Map<number, ManualChunk>(),
  messages: new Map<string, ChatMessage>(),
  outbox: new Map<string, SyncMutation>(),
  conflicts: new Map<string, SyncConflict>(),
  metadata: new Map<string, any>()
};

export async function initOfflineStorage(): Promise<void> {
  try {
    const db = await openDatabase();
    const localVersion = await getMetadata('local_version');
    if (localVersion !== SERVER_DATASET_VERSION) {
      console.log(`[IndexedDB] Refreshing chunks store from ${localVersion} to ${SERVER_DATASET_VERSION}`);
      const tx = db.transaction(['chunks', 'metadata'], 'readwrite');
      const store = tx.objectStore('chunks');
      store.clear(); // Purge old cached chunks completely!
      for (const chunk of INITIAL_MANUAL_CHUNKS) {
        if (chunk.page_number > 5) {
          store.put(chunk);
        }
      }
      const metaStore = tx.objectStore('metadata');
      metaStore.put({ key: 'server_version', value: SERVER_DATASET_VERSION });
      metaStore.put({ key: 'local_version', value: SERVER_DATASET_VERSION });
      metaStore.put({ key: 'dataset_hash', value: SERVER_DATASET_HASH });
      metaStore.put({ key: 'last_synced_at', value: Date.now() });
    } else {
      await saveChunksLocally(INITIAL_MANUAL_CHUNKS);
    }
  } catch (err) {
    console.warn('IndexedDB unavailable, using in-memory/localStorage fallback', err);
    // Seed memory store
    INITIAL_MANUAL_CHUNKS.filter(c => c.page_number > 5).forEach(c => memoryStore.chunks.set(c.chunk_id, c));
    memoryStore.metadata.set('server_version', SERVER_DATASET_VERSION);
    memoryStore.metadata.set('local_version', SERVER_DATASET_VERSION);
    memoryStore.metadata.set('dataset_hash', SERVER_DATASET_HASH);
    memoryStore.metadata.set('last_synced_at', Date.now());
  }
}

export async function getLocalChunks(): Promise<ManualChunk[]> {
  try {
    const db = await openDatabase();
    return new Promise((resolve) => {
      const tx = db.transaction('chunks', 'readonly');
      const store = tx.objectStore('chunks');
      const req = store.getAll();
      req.onsuccess = () => {
        // ALWAYS filter out introductory/TOC/Changelog pages (page_number <= 5)
        const validChunks = ((req.result || []) as ManualChunk[]).filter(c => c.page_number > 5);
        if (validChunks.length > 50) {
          resolve(validChunks);
        } else {
          resolve(INITIAL_MANUAL_CHUNKS.filter(c => c.page_number > 5));
        }
      };
      req.onerror = () => resolve(INITIAL_MANUAL_CHUNKS.filter(c => c.page_number > 5));
    });
  } catch {
    return memoryStore.chunks.size > 0 
      ? Array.from(memoryStore.chunks.values()).filter(c => c.page_number > 5)
      : INITIAL_MANUAL_CHUNKS.filter(c => c.page_number > 5);
  }
}

export async function saveChunksLocally(chunks: ManualChunk[]): Promise<void> {
  try {
    const db = await openDatabase();
    const tx = db.transaction('chunks', 'readwrite');
    const store = tx.objectStore('chunks');
    for (const chunk of chunks) {
      if (chunk.page_number > 5) {
        store.put(chunk);
      }
    }
  } catch {
    chunks.filter(c => c.page_number > 5).forEach(c => memoryStore.chunks.set(c.chunk_id, c));
  }
}

export async function getLocalMessages(): Promise<ChatMessage[]> {
  try {
    const db = await openDatabase();
    return new Promise((resolve) => {
      const tx = db.transaction('messages', 'readonly');
      const store = tx.objectStore('messages');
      const req = store.getAll();
      req.onsuccess = () => {
        const msgs = (req.result || []) as ChatMessage[];
        msgs.sort((a, b) => a.timestamp - b.timestamp);
        resolve(msgs);
      };
      req.onerror = () => resolve([]);
    });
  } catch {
    const msgs = Array.from(memoryStore.messages.values());
    msgs.sort((a, b) => a.timestamp - b.timestamp);
    return msgs;
  }
}

export async function saveMessageLocally(message: ChatMessage): Promise<void> {
  try {
    const db = await openDatabase();
    const tx = db.transaction('messages', 'readwrite');
    tx.objectStore('messages').put(message);
  } catch {
    memoryStore.messages.set(message.id, message);
  }
}

export async function updateMessageLocally(message: Partial<ChatMessage> & { id: string }): Promise<void> {
  try {
    const db = await openDatabase();
    const tx = db.transaction('messages', 'readwrite');
    const store = tx.objectStore('messages');
    const req = store.get(message.id);
    req.onsuccess = () => {
      if (req.result) {
        store.put({ ...req.result, ...message });
      }
    };
  } catch {
    const existing = memoryStore.messages.get(message.id);
    if (existing) {
      memoryStore.messages.set(message.id, { ...existing, ...message });
    }
  }
}

export async function clearAllLocalMessages(): Promise<void> {
  try {
    const db = await openDatabase();
    const tx = db.transaction('messages', 'readwrite');
    tx.objectStore('messages').clear();
  } catch {
    memoryStore.messages.clear();
  }
}

// Outbox mutations for offline synchronization
export async function queueMutation(mutation: SyncMutation): Promise<void> {
  try {
    const db = await openDatabase();
    const tx = db.transaction('outbox', 'readwrite');
    tx.objectStore('outbox').put(mutation);
  } catch {
    memoryStore.outbox.set(mutation.id, mutation);
  }
}

export async function getPendingMutations(): Promise<SyncMutation[]> {
  try {
    const db = await openDatabase();
    return new Promise((resolve) => {
      const tx = db.transaction('outbox', 'readonly');
      const req = tx.objectStore('outbox').getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => resolve([]);
    });
  } catch {
    return Array.from(memoryStore.outbox.values());
  }
}

export async function removeMutation(id: string): Promise<void> {
  try {
    const db = await openDatabase();
    const tx = db.transaction('outbox', 'readwrite');
    tx.objectStore('outbox').delete(id);
  } catch {
    memoryStore.outbox.delete(id);
  }
}

export async function recordConflict(conflict: SyncConflict): Promise<void> {
  try {
    const db = await openDatabase();
    const tx = db.transaction('conflicts', 'readwrite');
    tx.objectStore('conflicts').put(conflict);
  } catch {
    memoryStore.conflicts.set(conflict.id, conflict);
  }
}

export async function getConflicts(): Promise<SyncConflict[]> {
  try {
    const db = await openDatabase();
    return new Promise((resolve) => {
      const tx = db.transaction('conflicts', 'readonly');
      const req = tx.objectStore('conflicts').getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => resolve([]);
    });
  } catch {
    return Array.from(memoryStore.conflicts.values());
  }
}

export async function setMetadata(key: string, value: any): Promise<void> {
  try {
    const db = await openDatabase();
    const tx = db.transaction('metadata', 'readwrite');
    tx.objectStore('metadata').put({ key, value });
  } catch {
    memoryStore.metadata.set(key, value);
  }
}

export async function getMetadata<T = any>(key: string, defaultValue?: T): Promise<T | undefined> {
  try {
    const db = await openDatabase();
    return new Promise((resolve) => {
      const tx = db.transaction('metadata', 'readonly');
      const req = tx.objectStore('metadata').get(key);
      req.onsuccess = () => resolve(req.result ? req.result.value : defaultValue);
      req.onerror = () => resolve(defaultValue);
    });
  } catch {
    return memoryStore.metadata.has(key) ? memoryStore.metadata.get(key) : defaultValue;
  }
}
