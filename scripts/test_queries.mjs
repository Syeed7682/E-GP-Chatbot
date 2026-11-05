import fs from 'fs';

const chunks = JSON.parse(fs.readFileSync('./frontend/src/data/allManualChunks.json', 'utf8'));

function testQ(q) {
  const qWords = q.toLowerCase().split(/\W+/).filter(w => w.length > 2);
  const scored = chunks.map(c => {
    const text = c.content.toLowerCase();
    const title = c.section_title.toLowerCase();
    let score = 0;
    for (const w of qWords) {
      if (title.includes(w)) score += 8.0;
      if (text.includes(w)) score += 2.0;
    }
    return { chunk: c, score };
  });
  scored.sort((a, b) => b.score - a.score);
  console.log(`[Query: "${q}"] -> Page ${scored[0].chunk.page_number} (Chunk ${scored[0].chunk.chunk_id}): ${scored[0].chunk.section_title}`);
  console.log(`  Snippet: ${scored[0].chunk.content.replace(/\s+/g, ' ').slice(0, 100)}...\n`);
}

testQ('post qualification procedure');
testQ('how to issue notification of award');
testQ('what is tender corrigendum');
testQ('how to pay bill in ibas');
testQ('annual procurement plan creation');
testQ('what is debarment');
testQ('how to login to egp portal');

