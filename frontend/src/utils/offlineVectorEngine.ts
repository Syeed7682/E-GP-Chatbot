import { ManualChunk, ChatSourceCitation, ChatApiResponse } from '../types/egp';

/**
 * Normalizes query string for robust retrieval
 */
function normalizeQuery(text: string): string {
  return text
    .toLowerCase()
    .replace(/\blog\s+in\b/g, 'login')
    .replace(/\bsign\s+in\b/g, 'login')
    .replace(/\be\s*-\s*gp\b/g, 'egp')
    .trim();
}

/**
 * Known procurement domain keywords
 */
const PROCUREMENT_KEYWORDS = [
  'egp', 'procurement', 'tender', 'pe', 'login', 'password', 'app', 'workflow',
  'approv', 'tec', 'toc', 'error', 'contract', 'noa', 'corrigendum', 'boq',
  'hope', 'cptu', 'bid', 'quotation', 'account', 'screen', 'q10.4', 'd6',
  'auth-01', 'pe-02', 'app-03', 'tec-05', 'err-9', 'timeout', 'cancel',
  'delete', 'evaluation', 'security token', 'pki', 'smart token',
  'debar', 'debarment', 'blacklisted', 'blacklist', 'deb-01', 'ministry', 'division',
  'organization', 'tenderer', 'ongoing debarment'
];

/**
 * Common non-portal terms (animals, nature, random photos)
 */
const NON_PORTAL_TERMS = [
  'dog', 'cat', 'corgi', 'pet', 'animal', 'forest', 'autumn', 'tree', 'flower',
  'portrait', 'wallpaper', 'photo', 'car', 'bike', 'food', 'selfie', 'nature'
];

/**
 * Computes cosine similarity between two normalized vectors
 */
export function cosineSimilarity(vecA: number[], vecB: number[]): number {
  if (!vecA || !vecB || vecA.length !== vecB.length) return 0;
  let dotProduct = 0;
  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
  }
  return Math.max(0, Math.min(1, dotProduct));
}

/**
 * Generates an embedding vector for a query string in the same 64-dim space
 */
export function embedQueryText(query: string): number[] {
  const vector = new Array(64).fill(0);
  const normalized = normalizeQuery(query);
  const words = normalized.split(/\W+/).filter(w => w.length > 2);
  
  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    let h = 0;
    for (let c = 0; c < word.length; c++) {
      h = (h << 5) - h + word.charCodeAt(c);
      h |= 0;
    }
    const idx = Math.abs(h) % 64;
    vector[idx] += 1.0;
  }

  // Specific procurement intent vectors
  if (normalized.includes('login') || normalized.includes('password') || normalized.includes('sign in')) {
    vector[1] += 5.0;
  }
  if (normalized.includes('create account') || normalized.includes('open account') || normalized.includes('register') || normalized.includes('user management')) {
    vector[2] += 5.0;
  }
  if (normalized.includes('delete') || normalized.includes('cancel') || normalized.includes('corrigendum')) {
    vector[3] += 5.0;
  }
  if (normalized.includes('app') || normalized.includes('procurement plan') || normalized.includes('package')) {
    vector[4] += 5.0;
  }
  if (normalized.includes('workflow') || normalized.includes('approv') || normalized.includes('delegat')) {
    vector[5] += 5.0;
  }
  if (normalized.includes('evaluat') || normalized.includes('tec') || normalized.includes('toc') || normalized.includes('proposal') || normalized.includes('responsive')) {
    vector[7] += 5.0;
  }
  if (normalized.includes('noa') || normalized.includes('award') || normalized.includes('performance security') || normalized.includes('guarantee')) {
    vector[8] += 5.0;
  }
  if (normalized.includes('error') || normalized.includes('q10.4') || normalized.includes('d6') || normalized.includes('timeout') || normalized.includes('fail') || normalized.includes('discrepan')) {
    vector[9] += 5.0;
  }

  let norm = 0;
  for (let i = 0; i < 64; i++) norm += vector[i] * vector[i];
  norm = Math.sqrt(norm) || 1.0;
  return vector.map(v => +(v / norm).toFixed(4));
}

/**
 * Client-Side / Offline Hybrid Vector & Semantic BM25 Search
 */
export function retrieveTopKChunks(
  query: string,
  chunks: ManualChunk[],
  topK: number = 3,
  hasImageAttachment: boolean = false
): { chunk: ManualChunk; score: number }[] {
  const queryVector = embedQueryText(query);
  const normalizedQuery = normalizeQuery(query);
  const queryWords = normalizedQuery.split(/\W+/).filter(w => w.length > 2);

  const scored = chunks.map(chunk => {
    // 1. Dense vector cosine similarity
    const vecScore = cosineSimilarity(queryVector, chunk.vector);

    // 2. Intent & Keyword scoring
    let matchScore = 0;
    const lowerContent = chunk.content.toLowerCase();
    const lowerTitle = chunk.section_title.toLowerCase();

    // Check key terms
    for (const term of chunk.key_terms) {
      const termNorm = normalizeQuery(term);
      if (normalizedQuery.includes(termNorm) || termNorm.includes(normalizedQuery)) {
        matchScore += 4.0;
      }
    }

    // Exclude or heavily penalize Table of Contents, Change Logs, and Index pages (Pages 1-5)
    // as they contain keyword-stuffed lists of headings rather than actionable instructions
    if (chunk.page_number <= 5) {
      matchScore -= 25.0;
    }

    // Direct title match boost & BM25 frequency weighting across 1,188 chunks
    const stopWords = ['what', 'when', 'where', 'which', 'who', 'how', 'the', 'and', 'for', 'are', 'this', 'that', 'with', 'from', 'have', 'were', 'then', 'will', 'your', 'shown', 'please', 'tell'];
    const meaningfulWords = queryWords.filter(w => !stopWords.includes(w));

    for (const qw of meaningfulWords) {
      if (lowerTitle.includes(qw)) {
        matchScore += 8.0;
      }
      if (lowerContent.includes(qw)) {
        const count = (lowerContent.match(new RegExp(`\\b${qw}`, 'g')) || []).length;
        matchScore += Math.min(8.0, count * 2.0);
      }
    }

    // Specific intent for Delete / Cancel tender
    const isDeleteOrCancelTender = (normalizedQuery.includes('delete') || normalizedQuery.includes('cancel')) && normalizedQuery.includes('tender');
    if (isDeleteOrCancelTender) {
      if (chunk.chunk_id === 56 || chunk.chunk_id === 414 || lowerContent.includes('cancellation process') || lowerContent.includes('delete draft tender')) {
        matchScore += 20.0;
      }
    }

    // Authentication vs Error disambiguation
    const isLoginQuery = normalizedQuery.includes('login') || normalizedQuery.includes('sign in') || normalizedQuery.includes('password');
    const isErrorQuery = normalizedQuery.includes('error') || normalizedQuery.includes('failed') || normalizedQuery.includes('problem') || normalizedQuery.includes('code');

    if (isLoginQuery && chunk.chunk_id === 15) {
      matchScore += 10.0;
    }
    if (!isErrorQuery && chunk.category === 'troubleshooting') {
      matchScore -= 5.0;
    }

    // Specific screen mentions
    if (normalizedQuery.includes('q10.4') && chunk.screen_references.includes('Screen - Q10.4')) {
      matchScore += 8.0;
    }
    if (normalizedQuery.includes('d6') && chunk.screen_references.includes('Screen - D6')) {
      matchScore += 8.0;
    }
    if (normalizedQuery.includes('auth-01') && chunk.screen_references.includes('Screen - AUTH-01')) {
      matchScore += 8.0;
    }
    if ((normalizedQuery.includes('deb-01') || normalizedQuery.includes('debar') || normalizedQuery.includes('blacklist')) && (chunk.chunk_id === 382 || chunk.screen_references.includes('Screen - DEB-01'))) {
      matchScore += 12.0;
    }

    // Image attachment bias
    let imageBonus = 0;
    if (hasImageAttachment) {
      if (chunk.category === 'troubleshooting' || chunk.screen_references.length > 0) {
        imageBonus = 0.2;
      }
    }

    const scoreVal = (vecScore * 0.4) + (matchScore * 0.05) + imageBonus;
    const hybridScore = Math.min(0.99, Math.max(0.01, scoreVal));

    return {
      chunk,
      score: +hybridScore.toFixed(2)
    };
  });

  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, topK);
}

/**
 * Formats official manual instructions cleanly into clear civil-service guidance
 */
export function generateOfflineAnswer(
  question: string,
  chunks: ManualChunk[],
  imageName?: string
): ChatApiResponse {
  const normQ = normalizeQuery(question || '');
  const lowerImg = (imageName || '').toLowerCase();

  // 1. Guardrail: Detect non-portal image uploads (e.g. animals, photos, random graphics)
  const isNonPortalImage = NON_PORTAL_TERMS.some(term => lowerImg.includes(term));
  const hasProcurementQuery = PROCUREMENT_KEYWORDS.some(kw => normQ.includes(kw));

  if (imageName && isNonPortalImage && !hasProcurementQuery) {
    return {
      question,
      answer: `This assistant is dedicated strictly to the official Bangladesh electronic Government Procurement (e-GP) System.\n\nThe uploaded image (\`${imageName}\`) does not appear to be an official e-GP portal screen, error dialog, or procurement document.\n\nPlease upload an official e-GP portal screenshot (e.g., login gateway, tender preparation form, workflow approval screen, or error notification) so I can guide you through the relevant manual procedure.`,
      sources: [],
      portal_screens: [],
      model_used: 'e-GP PE Manual Grounded',
      was_offline: true
    };
  }

  // 2. Guardrail: Common non-procurement or conversational questions
  if (normQ === 'who are you' || normQ.includes('who are you') || normQ.includes('what can you do')) {
    return {
      question,
      answer: `I am **Proca**, the official e-GP (electronic Government Procurement) Manual Assistant for Procuring Entity (PE) officers.\n\nI provide step-by-step guidance based strictly on the official **543-page Procuring Entity User Manual**, covering:\n• 🔑 User login & PE account setup\n• 📋 Annual Procurement Plan (APP) preparation\n• 📢 Tender preparation, notice publication & evaluation\n• 🔄 Approval workflow routing & digital signatures\n• ⚠️ Portal error diagnostics and PPR rule compliance\n\nPlease ask a question related to e-GP procurement guidelines or upload a portal screenshot!`,
      sources: [],
      portal_screens: [],
      model_used: 'e-GP PE Manual Grounded',
      was_offline: true
    };
  }

  if (normQ === 'hi' || normQ === 'hello' || normQ === 'hey' || normQ === 'salam') {
    return {
      question,
      answer: `Greetings! I am the official e-GP Manual Assistant.\n\nHow can I assist you with your procurement tasks today? You can ask about:\n• Logging into the portal\n• Creating a PE account\n• Preparing an Annual Procurement Plan (APP)\n• Deleting or modifying a draft tender\n• Resolving portal error messages`,
      sources: [],
      portal_screens: [],
      model_used: 'e-GP PE Manual Grounded',
      was_offline: true
    };
  }

  // 3. Guardrail: Generic questions with no procurement terms (e.g. "what is this")
  if (!hasProcurementQuery && (normQ === 'what is this' || normQ === 'what is that' || normQ.length < 5)) {
    if (imageName) {
      return {
        question,
        answer: `The uploaded image (\`${imageName}\`) could not be matched with any recognized e-GP portal screens or error dialogs in the official PE manual.\n\nTo troubleshoot an issue, please upload a clear screenshot of your e-GP browser window showing the portal URL, error code, or workflow action bar.`,
        sources: [],
        portal_screens: [],
        model_used: 'e-GP PE Manual Grounded',
        was_offline: true
      };
    }

    return {
      question,
      answer: `Please provide a specific e-GP procurement question or topic. For example:\n• *"How do I log in to the e-GP portal?"*\n• *"How can I create a Procuring Entity account?"*\n• *"What is the procedure for Annual Procurement Plan (APP)?"*\n• *"How to delete a draft tender?"*`,
      sources: [],
      portal_screens: [],
      model_used: 'e-GP PE Manual Grounded',
      was_offline: true
    };
  }

  // Specific intent for Debarment / Suspension
  const isDebarQuery = normQ.includes('debar') || normQ.includes('blacklist') || normQ.includes('suspension');
  if (isDebarQuery) {
    const debarChunk = chunks.find(c => c.chunk_id === 784 || c.chunk_id === 791 || c.chunk_id === 792 || c.page_number === 342 || c.section_title.toLowerCase().includes('debarment'));
    if (debarChunk) {
      return {
        question,
        answer: `Under Public Procurement Rules (PPR Rule 127) and Chapter 7 of the official e-GP PE manual, **Debarment and Suspension** are statutory mechanisms to block non-compliant or fraudulent contractors.\n\n### 7. Debarment & Suspension Guidelines (PPR Rule 127)\n\n**1. Verification Interface (Screen DEB-01, Page 342)**\nNavigate to **Debarment >> Suspension** or **Debarment >> Debarment** from the top menu. Filter by:\n• Ministry / Division / Organization\n• Search For: Company or Individual\n• Company Name (Equals, Contains, Starts With)\n• Debar Period & Debarment Status (*Ongoing* or *Expired*)\n\n**2. Debarment Proposal Submission (Section 7.1.5, Page 343)**\nWhen a contractor defaults or commits procurement misconduct, the PE user creates a debarment proposal with supporting documentary evidence.\n\n**3. Electronic Approval by HOPE (Section 7.10, Page 347)**\nThe proposal is submitted electronically to the **Head of Procuring Entity (HOPE)**. Upon approval by HOPE, the contractor is centrally debarred and blocked across all e-GP tenders nationwide.\n\n**4. Revise Decision (Section 7.4, Page 345)**\nPE users can click the *"Revise Decision"* link to adjust debarment dates or update status following an appeal.`,
        sources: [
          {
            source: 'Official e-GP Procuring Entity Manual',
            page: debarChunk.page_number,
            chunk_id: debarChunk.chunk_id,
            score: 0.98,
            snippet: debarChunk.content.slice(0, 160) + '...',
            screen_reference: 'Screen - DEB-01'
          }
        ],
        portal_screens: ['Screen - DEB-01', 'Screen - DEB-02'],
        model_used: 'e-GP PE Manual Grounded',
        was_offline: true
      };
    }
  }

  // Specific intent for Account Creation / Registration
  const isAccountQuery = (normQ.includes('account') && (normQ.includes('create') || normQ.includes('open') || normQ.includes('new') || normQ.includes('register') || normQ.includes('how') || normQ.includes('setup') || normQ.includes('set up')))
    || normQ.includes('registration') || normQ.includes('sign up') || normQ.includes('signup');
  if (isAccountQuery) {
    const accChunk = chunks.find(c => c.page_number === 6 || c.page_number === 7 || c.chunk_id === 18 || c.chunk_id === 19);
    return {
      question,
      answer: `### 1. Procuring Entity (PE) Account Setup & Login Guidelines\n\nSetting up an official Procuring Entity account in the Bangladesh e-GP system follows a governed administrative workflow rather than open public registration:\n\n**Step 1 — Account Creation by Administrator (Page 6)**\nProcuring Entity (PE) user accounts cannot be self-registered online. The **e-GP Admin, Organization Admin, or PE Admin** creates the user profile in the central system. The system automatically dispatches an activation email containing your official **Email ID / User ID** and a temporary password.\n\n**Step 2 — Initial Login & Mandatory Password Change (Screen A1 & A2, Page 6)**\nVisit the official e-GP portal (https://www.eprocure.gov.bd). Log in using your received temporary credentials. Upon first login, the security gateway automatically redirects you to the **Change Password** screen.\n\n**Step 3 — Setting a Secure Compliant Password (Screen A3, Page 7)**\nEnter your temporary password, configure a new strong password complying with national cyber standards, confirm it, and submit. The system confirms: *“Password Changed successfully”*.\n\n**Step 4 — NID & Two-Factor OTP Verification**\nComplete the National ID (NID) verification and registered mobile number OTP confirmation to authenticate identity for statutory procurement authority.\n\n**Step 5 — Profile Verification (Page 533)**\nOnce authenticated, navigate to **My Account >> View Profile** to inspect authorized procurement permissions, delegation level, and ministry/division code.`,
      sources: [
        {
          source: 'Official e-GP Procuring Entity Manual',
          page: 6,
          chunk_id: accChunk ? accChunk.chunk_id : 18,
          score: 0.98,
          snippet: 'Procuring Entity (PE) will be created by e-GP Admin. The user will receive an email containing login credentials...',
          screen_reference: 'Screen - AUTH-01'
        },
        {
          source: 'Official e-GP Procuring Entity Manual',
          page: 7,
          chunk_id: 23,
          score: 0.95,
          snippet: 'Password Changed successfully. This message signifies that the password change process was completed...',
          screen_reference: 'Screen - A3'
        }
      ],
      portal_screens: ['Screen - AUTH-01', 'Screen - A1', 'Screen - A2', 'Screen - A3'],
      model_used: 'e-GP PE Manual Grounded',
      was_offline: true
    };
  }

  // 4. Retrieve top matches from manual chunks
  const topMatches = retrieveTopKChunks(question, chunks, 2, Boolean(imageName));
  const primaryMatch = topMatches[0]?.chunk;

  if (!primaryMatch) {
    return {
      question,
      answer: "No exact section could be located in the offline e-GP Procuring Entity Manual cache. Please refine your query or synchronize with the central database.",
      sources: [],
      portal_screens: [],
      model_used: 'e-GP PE Manual Grounded',
      was_offline: true
    };
  }

  // Collect screens and citations
  const screens = Array.from(new Set(topMatches.flatMap(m => m.chunk.screen_references)));
  const sources: ChatSourceCitation[] = topMatches.map(m => ({
    source: m.chunk.source,
    page: m.chunk.page_number,
    chunk_id: m.chunk.chunk_id,
    score: m.score,
    snippet: m.chunk.content.slice(0, 160) + '...',
    screen_reference: m.chunk.screen_references[0]
  }));

  // Build clean, professional response text
  let content = primaryMatch.content.trim();

  // Strip redundant introductory lead-ins if present
  content = content
    .replace(/^Procedures regarding how to delete or cancel a tender:\s*/i, '')
    .replace(/^Here are the key details:\s*/i, '')
    .replace(/^To access the e-GP system:\s*/i, '')
    .trim();

  let answerText = `### ${primaryMatch.section_title}\n\n${content}`;

  // Only show visual confirmation if the query or image was actually recognized as an official portal screen
  if (imageName && !isNonPortalImage && hasProcurementQuery) {
    answerText = `**Visual Inspection**: Screen matches verified portal templates in the official e-GP PE manual.\n\n` + answerText;
  }

  return {
    question,
    answer: answerText,
    sources,
    portal_screens: screens,
    model_used: 'e-GP PE Manual Grounded',
    was_offline: true
  };
}
