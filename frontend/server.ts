import express from 'express';
import http from 'http';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer as createViteServer } from 'vite';
import dotenv from 'dotenv';
import Tesseract from 'tesseract.js';
import { INITIAL_MANUAL_CHUNKS, SERVER_DATASET_VERSION, SERVER_DATASET_HASH } from './src/data/manualChunks.ts';
import { retrieveTopKChunks, generateOfflineAnswer } from './src/utils/offlineVectorEngine.ts';
import { fastHash } from './src/utils/crypto.ts';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const PROJECT_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const EXTRACTED_IMAGES_DIR = path.join(PROJECT_ROOT, 'data', 'extracted_images');

app.use(express.json({ limit: '50mb' }));

// In-memory server sync audit store
const syncedAuditLog: any[] = [];
let serverCurrentVersion = SERVER_DATASET_VERSION;
let serverDatasetHash = SERVER_DATASET_HASH;

// System Prompt for e-GP Procurement Entity RAG
const EGP_SYSTEM_PROMPT = `You are Proca, the official e-GP (electronic Government Procurement) Manual AI Assistant for Procuring Entity (PE) users, established by the Central Procurement Technical Unit (CPTU) and Ministry of Planning.

Answer using only the provided e-GP manual context and any uploaded screenshot. Never invent procurement procedures, rules, or deadlines. Start with a direct answer in one short, natural paragraph; use a short numbered list only when sequential steps are needed. Keep it concise, correct obvious OCR line-break or split-word errors when clear, and do not copy chunk headings or extraction artifacts. Do not include page numbers, citations, chunk IDs, source labels, or a separate screen-reference list in the answer; the application displays references separately. Mention a screen or menu in the answer only when needed to explain an action. For screenshots, describe only visible details and relevant supported manual guidance. If the context is insufficient, say so briefly.`;

// 1. Health Endpoints (FastAPI compatibility)
app.get(['/api/health', '/api/chat/health'], (req, res) => {
  res.json({
    status: 'ok',
    system: 'e-GP Official Manual Assistant Service',
    total_chunks: 1188,
    verified_chunks: 1188,
    version: serverCurrentVersion,
    hf_configured: Boolean(process.env.HF_TOKEN || process.env.HUGGINGFACE_TOKEN),
    groq_configured: Boolean(process.env.GROQ_API_KEY),
    llm_model: process.env.GROQ_TEXT_MODEL || 'openai/gpt-oss-20b',
    vision_model: process.env.GROQ_VISION_MODEL || 'qwen/qwen3.8-27b',
    gemini_configured: false
  });
});

app.get('/api/chat/chunks', (req, res) => {
  res.json({
    total_chunks: INITIAL_MANUAL_CHUNKS.length,
    chunks: INITIAL_MANUAL_CHUNKS
  });
});

app.get('/api/manual/page/:page_num/image', async (req, res, next) => {
  const page = Number(req.params.page_num);
  if (!Number.isInteger(page) || page < 1 || page > 543) {
    return res.status(404).json({ error: 'Manual page must be between 1 and 543.' });
  }

  const candidates = [
    `page_${page}.jpg`,
    `page_${page}.png`,
    `page_${page}_img_0.jpg`,
    `page_${page}_img_0.png`
  ];

  for (const filename of candidates) {
    try {
      const image = await readFile(path.join(EXTRACTED_IMAGES_DIR, filename));
      const mediaType = image[0] === 0xff && image[1] === 0xd8
        ? 'image/jpeg'
        : image[0] === 0x89 && image[1] === 0x50 && image[2] === 0x4e && image[3] === 0x47
          ? 'image/png'
          : null;

      if (!mediaType) {
        return res.status(415).json({ error: `Unsupported image format for manual page ${page}.` });
      }

      res.type(mediaType);
      res.setHeader('Cache-Control', 'public, max-age=86400');
      return res.send(image);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') {
        return next(error);
      }
    }
  }

  try {
    const fastApiUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8000';
    const response = await fetch(`${fastApiUrl}/api/manual/page/${page}/image`);
    if (!response.ok) {
      return res.status(response.status).json({ error: `Could not retrieve manual page ${page} image.` });
    }

    const mediaType = response.headers.get('content-type')?.split(';')[0];
    if (mediaType !== 'image/jpeg' && mediaType !== 'image/png') {
      return res.status(502).json({ error: `Backend returned an unsupported image format for manual page ${page}.` });
    }

    const image = Buffer.from(await response.arrayBuffer());
    res.type(mediaType);
    res.setHeader('Cache-Control', 'public, max-age=86400');
    return res.send(image);
  } catch (error) {
    console.error(`Could not retrieve rendered manual page ${page} image from FastAPI:`, error);
    return res.status(503).json({ error: 'Manual page rendering is unavailable because the FastAPI backend could not be reached.' });
  }
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
  const { question, image_base64, image_mime = 'image/png', image_name, top_k = 3, use_alt_model = false } = req.body;

  if (!question && !image_base64) {
    return res.status(400).json({ error: 'Question or image is required' });
  }

  const shouldRouteToVision = use_alt_model;

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
        image_mime: image_mime || 'image/png',
        top_k,
        use_alt_model: shouldRouteToVision
      }),
      signal: AbortSignal.timeout(60000)
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

  // Use Groq for both local-server fallback and FastAPI-backed inference.
  const groqApiKey = process.env.GROQ_API_KEY;
  if (groqApiKey) {
    try {
      const promptText = `USER QUESTION: ${question || 'Analyze this portal screenshot and explain the required e-GP procedure or error fix.'}
${ocrExtractedText ? `EXTRACTED PORTAL TEXT: ${ocrExtractedText}\n` : ''}
RELEVANT OFFICIAL e-GP PE MANUAL CONTEXT (use as evidence; do not copy OCR artifacts or metadata):
${retrievedContextText}

Write a concise, direct answer in a natural conversational style. Prefer one short paragraph; use numbered steps only if the user needs a sequence of actions. Do not include page numbers, citations, chunk headings, source labels, or a separate screen list in the answer. Those references are displayed separately.`;

      const modelToUse = use_alt_model || image_base64
        ? process.env.GROQ_VISION_MODEL || 'qwen/qwen3.8-27b'
        : process.env.GROQ_TEXT_MODEL || 'openai/gpt-oss-20b';
      const imageDataUrl = image_base64
        ? image_base64.startsWith('data:')
          ? image_base64
          : `data:${image_mime || 'image/png'};base64,${image_base64}`
        : null;
      const userContent = imageDataUrl
        ? [
            { type: 'text' as const, text: promptText },
            { type: 'image_url' as const, image_url: { url: imageDataUrl } }
          ]
        : promptText;
      const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${groqApiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: modelToUse,
          messages: [
            { role: 'system', content: EGP_SYSTEM_PROMPT },
            { role: 'user', content: userContent }
          ],
          temperature: 0.2,
          max_completion_tokens: 1024
        }),
        signal: AbortSignal.timeout(45000)
      });

      if (!response.ok) {
        throw new Error(`Groq returned ${response.status}: ${(await response.text()).slice(0, 250)}`);
      }
      const payload = await response.json() as {
        choices?: Array<{ message?: { content?: string | null } }>;
      };
      const answer = payload.choices?.[0]?.message?.content || '';
      if (answer) {
        return res.json({
          question: question || 'Portal Screenshot Diagnostic',
          answer,
          sources,
          portal_screens: portalScreens,
          model_used: `${modelToUse} (Groq; e-GP Grounded)`,
          was_offline: false
        });
      }
    } catch (groqErr: any) {
      console.warn('Groq call notice (using grounded local engine):', groqErr.message);
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
