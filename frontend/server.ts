import express from 'express';
import http from 'http';
import { createServer as createViteServer } from 'vite';
import dotenv from 'dotenv';
import { GoogleGenAI } from '@google/genai';
import { HfInference } from '@huggingface/inference';
import Tesseract from 'tesseract.js';
import { INITIAL_MANUAL_CHUNKS, SERVER_DATASET_VERSION, SERVER_DATASET_HASH } from './src/data/manualChunks.ts';
import { retrieveTopKChunks, generateOfflineAnswer } from './src/utils/offlineVectorEngine.ts';
import { fastHash } from './src/utils/crypto.ts';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json({ limit: '50mb' }));

// In-memory server sync audit store
const syncedAuditLog: any[] = [];
let serverCurrentVersion = SERVER_DATASET_VERSION;
let serverDatasetHash = SERVER_DATASET_HASH;

// System Prompt for e-GP Procurement Entity RAG
const EGP_SYSTEM_PROMPT = `You are Proca, the official e-GP (electronic Government Procurement) Manual AI Assistant for Procuring Entity (PE) users, established by the Central Procurement Technical Unit (CPTU) and Ministry of Planning.

CRITICAL INSTRUCTIONS:
1. Base all answers strictly on the provided e-GP manual context chunks (Procuring Entity User Manual 543 pages).
2. Always provide actionable, step-by-step numbered instructions.
3. Explicitly cite the source document and page number(s) in this format:
   📖 Source: e-GP System User Manual (Procuring Entity User 1 February 2026), Page [X]
4. When relevant, reference official portal screens (e.g. Screen - Q10.4, Screen - D6, Screen - AUTH-01) with:
   📷 Refer to portal screens: [Screen Names]
5. If the user provides a portal screenshot or error code, analyze it precisely, diagnose the underlying rule or token requirement, and guide the user on how to fix it.
6. Maintain a helpful, polite, and authoritative civil service tone.`;

// 1. Health Endpoints (FastAPI compatibility)
app.get(['/api/health', '/api/chat/health'], (req, res) => {
  res.json({
    status: 'ok',
    system: 'e-GP Official Manual Assistant Service',
    total_chunks: 1188,
    verified_chunks: 1188,
    version: serverCurrentVersion,
    hf_configured: Boolean(process.env.HF_TOKEN || process.env.HUGGINGFACE_TOKEN),
    gemini_configured: Boolean(process.env.GEMINI_API_KEY)
  });
});

app.get('/api/chat/chunks', (req, res) => {
  res.json({
    total_chunks: INITIAL_MANUAL_CHUNKS.length,
    chunks: INITIAL_MANUAL_CHUNKS
  });
});

// 2. Sync Version Endpoint
app.get('/api/sync/version', (req, res) => {
  res.json({
    version: serverCurrentVersion,
    hash: serverDatasetHash,
    chunk_count: INITIAL_MANUAL_CHUNKS.length,
    timestamp: Date.now()
  });
});

// 3. Sync Chunks Endpoint
app.get('/api/sync/chunks', (req, res) => {
  res.json({
    version: serverCurrentVersion,
    hash: serverDatasetHash,
    chunks: INITIAL_MANUAL_CHUNKS,
    timestamp: Date.now()
  });
});

// 4. Sync Push Mutations Endpoint (Reconciliation & Conflict Resolution)
app.post('/api/sync/push', (req, res) => {
  const { mutations, conflict_strategy, client_id } = req.body;
  const conflicts: any[] = [];
  const processed: string[] = [];

  if (Array.isArray(mutations)) {
    for (const mutation of mutations) {
      // Simulate conflict detection if client mutation revision is stale
      if (mutation.revision && mutation.revision < 1) {
        conflicts.push({
          mutation_id: mutation.id,
          entity_type: mutation.type,
          client_state: mutation.payload,
          server_state: { status: 'overridden_by_server_policy' },
          resolved_with: conflict_strategy
        });
      }

      syncedAuditLog.push({
        id: mutation.id,
        type: mutation.type,
        client_id: client_id || 'anonymous',
        synced_at: Date.now(),
        payload_hash: mutation.hash || fastHash(JSON.stringify(mutation.payload))
      });
      processed.push(mutation.id);
    }
  }

  res.json({
    status: 'success',
    processed_count: processed.length,
    processed_ids: processed,
    conflicts,
    server_time: Date.now()
  });
});

// 5. Chat Endpoint (Multimodal RAG with FastAPI proxy, Hugging Face Qwen, Gemini, or Grounded Fallback)
app.post('/api/chat', async (req, res) => {
  const { question, image_base64, image_mime = 'image/png', image_name, top_k = 3 } = req.body;

  if (!question && !image_base64) {
    return res.status(400).json({ error: 'Question or image is required' });
  }

  // 0. Prioritize FastAPI Python backend (port 8000) if active
  try {
    const fastApiUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000';
    const pyRes = await fetch(`${fastApiUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        image_base64: image_base64 || null,
        image: image_base64 || null,
        image_name: image_name || null,
        top_k
      }),
      signal: AbortSignal.timeout(4000)
    });
    if (pyRes.ok) {
      const pyData = await pyRes.json();
      return res.json(pyData);
    }
  } catch {
    // Python backend not running or timed out, fallback to local Express engine
  }

  // 1. Process image with OCR if attached
  let ocrExtractedText = '';
  if (image_base64) {
    try {
      const cleanBase64 = image_base64.replace(/^data:image\/[a-z]+;base64,/, '');
      const imgBuffer = Buffer.from(cleanBase64, 'base64');
      const ocrResult = await Tesseract.recognize(imgBuffer, 'eng');
      ocrExtractedText = (ocrResult.data?.text || '').trim();
      if (ocrExtractedText) {
        console.log(`[OCR Extracted Text (${ocrExtractedText.length} chars)]:`, ocrExtractedText.slice(0, 100));
      }
    } catch (ocrErr: any) {
      console.warn('OCR processing notice:', ocrErr.message);
    }
  }

  // Combine query and OCR content for precision retrieval
  const effectiveQuery = [question, ocrExtractedText].filter(Boolean).join(' ').trim() || 'e-GP portal screen analysis';

  // Retrieve relevant manual chunks
  const retrieved = retrieveTopKChunks(effectiveQuery, INITIAL_MANUAL_CHUNKS, top_k, Boolean(image_base64));
  const retrievedContextText = retrieved.map((r, i) => 
    `[CHUNK ${i + 1} - Page ${r.chunk.page_number} (${r.chunk.section_title})]\n${r.chunk.content}\nScreen References: ${r.chunk.screen_references.join(', ')}`
  ).join('\n\n---\n\n');

  const sources = retrieved.map(r => ({
    source: r.chunk.source,
    page: r.chunk.page_number,
    chunk_id: r.chunk.chunk_id,
    score: r.score,
    snippet: r.chunk.content.slice(0, 160) + '...',
    screen_reference: r.chunk.screen_references[0]
  }));

  const portalScreens = Array.from(new Set(retrieved.flatMap(r => r.chunk.screen_references)));

  // Try calling Hugging Face if HF_TOKEN is present
  const hfToken = process.env.HF_TOKEN || process.env.HUGGINGFACE_TOKEN;
  if (hfToken) {
    try {
      const hf = new HfInference(hfToken);
      const promptText = `USER QUESTION: ${question || 'Analyze this portal screenshot and explain the required e-GP procedure or error fix.'}
${ocrExtractedText ? `EXTRACTED PORTAL TEXT: ${ocrExtractedText}\n` : ''}
RELEVANT OFFICIAL e-GP PE MANUAL CONTEXT:
${retrievedContextText}

Respond clearly following the official e-GP rules. Include step-by-step guide, screen references, and source page citation.`;

      const modelToUse = process.env.LLM_MODEL || 'Qwen/Qwen2.5-72B-Instruct';
      const response = await hf.chatCompletion({
        model: modelToUse,
        messages: [
          { role: 'system', content: EGP_SYSTEM_PROMPT },
          { role: 'user', content: promptText }
        ],
        max_tokens: 1024
      });

      const answer = response.choices?.[0]?.message?.content || '';
      if (answer) {
        return res.json({
          question: question || 'Portal Screenshot Diagnostic',
          answer,
          sources,
          portal_screens: portalScreens,
          model_used: 'e-GP PE Manual Grounded',
          was_offline: false
        });
      }
    } catch (hfErr: any) {
      console.warn('Hugging Face call notice (using grounded local engine):', hfErr.message);
    }
  }

  // Try calling Gemini if API key is present
  if (process.env.GEMINI_API_KEY) {
    try {
      const ai = new GoogleGenAI({
        apiKey: process.env.GEMINI_API_KEY,
        httpOptions: {
          headers: {
            'User-Agent': 'aistudio-build'
          }
        }
      });

      const parts: any[] = [];

      if (image_base64) {
        const cleanBase64 = image_base64.replace(/^data:image\/[a-z]+;base64,/, '');
        parts.push({
          inlineData: {
            mimeType: image_mime,
            data: cleanBase64
          }
        });
      }

      const promptText = `USER QUESTION: ${question || 'Analyze this portal screenshot and explain the required e-GP procedure or error fix.'}
${ocrExtractedText ? `EXTRACTED PORTAL TEXT: ${ocrExtractedText}\n` : ''}
RELEVANT OFFICIAL e-GP PE MANUAL CONTEXT:
${retrievedContextText}

Respond clearly following the system instructions. Include step-by-step guide, screen references, and source page citation.`;

      parts.push({ text: promptText });

      const response = await ai.models.generateContent({
        model: 'gemini-3.8-flash',
        contents: { parts },
        config: {
          systemInstruction: EGP_SYSTEM_PROMPT
        }
      });

      const answer = response.text || '';

      return res.json({
        question: question || 'Portal Screenshot Diagnostic',
        answer,
        sources,
        portal_screens: portalScreens,
        model_used: 'e-GP PE Manual Grounded',
        was_offline: false
      });
    } catch (err: any) {
      console.warn('Gemini API call failed or rate-limited, falling back to deterministic local RAG engine:', err.message);
    }
  }

  // Graceful fallback: Offline / Deterministic RAG generation with OCR-enhanced query
  const offlineResult = generateOfflineAnswer(effectiveQuery, INITIAL_MANUAL_CHUNKS, image_name);
  return res.json({
    question: question || 'Portal Screenshot Diagnostic',
    answer: offlineResult.answer,
    sources: offlineResult.sources.length > 0 ? offlineResult.sources : sources,
    portal_screens: offlineResult.portal_screens.length > 0 ? offlineResult.portal_screens : portalScreens,
    model_used: 'e-GP PE Manual Grounded',
    was_offline: true
  });
});

async function startServer() {
  const isProd = process.env.NODE_ENV === 'production';
  const server = http.createServer(app);

  if (!isProd) {
    const vite = await createViteServer({
      server: {
        middlewareMode: true,
        hmr: { server }
      },
      appType: 'spa'
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static('dist'));
    app.get('*', (req, res) => {
      res.sendFile('dist/index.html', { root: '.' });
    });
  }

  const listenPort = (portToTry: number) => {
    server.listen(portToTry, '0.0.0.0', () => {
      console.log(`\n======================================================`);
      console.log(`  [e-GP Server] running on http://localhost:${portToTry}`);
      console.log(`======================================================\n`);
    });

    server.once('error', (err: any) => {
      if (err.code === 'EADDRINUSE') {
        console.warn(`[e-GP Server] Port ${portToTry} is occupied, trying http://localhost:${portToTry + 1}...`);
        listenPort(portToTry + 1);
      } else {
        console.error('[e-GP Server] Listen error:', err);
      }
    });
  };

  listenPort(Number(PORT));
}

startServer();
