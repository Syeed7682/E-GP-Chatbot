/**
 * Sync Queue Manager (frontend/src/utils/syncQueue.ts).
 * Queues user queries and mutations while offline and dispatches them when network returns.
 */
import { SyncMutation } from '../types/egp';
import { getOutboxMutations, removeOutboxMutation } from './indexedDBStorage';

export class SyncQueue {
  private isProcessing: boolean = false;

  async processQueue(pushEndpoint: (mutations: SyncMutation[]) => Promise<boolean>): Promise<number> {
    if (this.isProcessing) return 0;
    this.isProcessing = true;

    try {
      const pending = await getOutboxMutations();
      if (pending.length === 0) {
        this.isProcessing = false;
        return 0;
      }

      const success = await pushEndpoint(pending);
      if (success) {
        for (const m of pending) {
          await removeOutboxMutation(m.id);
        }
        this.isProcessing = false;
        return pending.length;
      }
    } catch (err) {
      console.warn('[SyncQueue] Processing warning:', err);
    }

    this.isProcessing = false;
    return 0;
  }
}

export const syncQueue = new SyncQueue();

