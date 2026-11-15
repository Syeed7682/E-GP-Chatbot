import fs from 'fs';
import path from 'path';

const rawChunksPath = path.resolve('data/processed/chunks.json');
const outputPath = path.resolve('frontend/src/data/allManualChunks.json');

console.log('Reading raw chunks from:', rawChunksPath);
const raw = JSON.parse(fs.readFileSync(rawChunksPath, 'utf8'));
console.log(`Loaded ${raw.length} raw chunks.`);

function categorize(text) {
  const lower = text.toLowerCase();
  if (lower.includes('login') || lower.includes('password') || lower.includes('registration') || lower.includes('auth')) return 'authentication';
  if (lower.includes('annual procurement plan') || lower.includes('create app') || lower.includes('package')) return 'app_planning';
  if (lower.includes('tender') || lower.includes('boq') || lower.includes('corrigendum') || lower.includes('cancel')) return 'tender_creation';
  if (lower.includes('workflow') || lower.includes('approv') || lower.includes('sign')) return 'workflow';
  if (lower.includes('evaluation') || lower.includes('tec') || lower.includes('toc') || lower.includes('qualification')) return 'evaluation';
  if (lower.includes('contract') || lower.includes('noa') || lower.includes('performance security') || lower.includes('bill') || lower.includes('ibas')) return 'contract';
  if (lower.includes('debar') || lower.includes('suspen') || lower.includes('blacklist')) return 'procurement_process';
  return 'troubleshooting';
}

function extractScreenReferences(text) {
  const screens = new Set();
  const regex = /Screen\s*[-–—\s]\s*([A-Za-z][0-9]+(?:\.[0-9]+)?)/gi;
  let match;
  while ((match = regex.exec(text)) !== null) {
    screens.add(`Screen - ${match[1].toUpperCase()}`);
  }
  return Array.from(screens);
}

function extractSectionTitle(text, page) {
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
  for (const line of lines) {
    if (/^\d+(\.\d+)*\s+[A-Za-z]/.test(line) && line.length < 80) {
      return line;
    }
    if (/^[A-Z][A-Za-z\s–—\-]{3,50}$/.test(line) && !line.startsWith('Page') && !line.startsWith('Screen')) {
      return line;
    }
  }
  return `e-GP Manual Section (Page ${page})`;
}

function extractKeyTerms(text) {
  const words = text.toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 3 && !['this', 'that', 'with', 'from', 'have', 'were', 'then', 'will', 'your', 'shown'].includes(w));
  return Array.from(new Set(words)).slice(0, 15);
}

// Filter out Table of Contents, Cover pages, and Changelogs (Pages 1 to 5)
// so the search engine only indexes actual procedural chapters (Pages 6 to 543)
const proceduralRaw = raw.filter(c => c.page > 5);
console.log(`Filtered out introductory/TOC pages. Procedural chunks: ${proceduralRaw.length}`);

const fullChunks = proceduralRaw.map((c) => {
  const screens = extractScreenReferences(c.text);
  const title = extractSectionTitle(c.text, c.page);
  const category = categorize(c.text);
  const keyTerms = extractKeyTerms(c.text);

  return {
    chunk_id: c.chunk_id,
    section_title: title,
    category,
    page_number: c.page,
    source: c.source || 'e-GP System User Manual - Procuring Entity User 1 February 2026',
    content: c.text,
    key_terms: keyTerms,
    screen_references: screens,
    image_path: c.image_path || null,
    last_modified: '2026-02-01T10:00:00Z',
    hash: `chunk_${c.chunk_id}_p${c.page}`
  };
});

fs.writeFileSync(outputPath, JSON.stringify(fullChunks, null, 2), 'utf8');
console.log(`Successfully compiled ${fullChunks.length} chunks to: ${outputPath}`);

