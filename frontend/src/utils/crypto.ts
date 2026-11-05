/**
 * Cryptographic and Integrity Utilities for Offline-First Data Structures
 */

/**
 * Computes a fast deterministic 32-bit FNV-1a hash formatted as hex
 */
export function fastHash(str: string): string {
  let hash = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    hash ^= str.charCodeAt(i);
    hash += (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
  }
  return ('0000000' + (hash >>> 0).toString(16)).slice(-8);
}

/**
 * Computes SHA-256 hash using browser crypto if available, falling back to deterministic multiround hash
 */
export async function computeSha256(data: string): Promise<string> {
  if (typeof crypto !== 'undefined' && crypto.subtle) {
    try {
      const msgUint8 = new TextEncoder().encode(data);
      const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    } catch {
      // Fallback below
    }
  }

  // Pure JS fallback
  let h1 = 0xdeadbeef, h2 = 0x41c6ce57;
  for (let i = 0; i < data.length; i++) {
    const ch = data.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return (4294967296 * (2097151 & h2) + (h1 >>> 0)).toString(16).padStart(16, '0');
}

/**
 * Validates data structure integrity by checking whether current hash matches expected hash
 */
export async function verifyDataIntegrity(data: unknown, expectedHash: string): Promise<boolean> {
  const serialized = typeof data === 'string' ? data : JSON.stringify(data);
  const calculated = await computeSha256(serialized);
  return calculated.toLowerCase() === expectedHash.toLowerCase() ||
         fastHash(serialized).toLowerCase() === expectedHash.toLowerCase();
}
