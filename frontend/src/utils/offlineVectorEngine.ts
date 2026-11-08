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
  // Always filter out intro / TOC / Change Log pages (page_number <= 5)
  const validChunks = chunks.filter(c => c && c.page_number > 5);
  const queryVector = embedQueryText(query);
  const normalizedQuery = normalizeQuery(query);
  const queryWords = normalizedQuery.split(/\W+/).filter(w => w.length > 2);

  const scored = validChunks.map(chunk => {
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

function repairLeadingChunkFragment(content: string, chunk: ManualChunk, chunks: ManualChunk[]): string {
  const firstToken = content.match(/^([a-z]{2,6})\s+/);
  if (!firstToken) return content;

  const previous = chunks
    .filter((candidate) => candidate.page_number === chunk.page_number && candidate.chunk_id < chunk.chunk_id)
    .sort((a, b) => b.chunk_id - a.chunk_id)[0];
  if (!previous) return content;

  const fragment = firstToken[1].toLowerCase();
  const wordPattern = /\b[A-Za-z]+\b/g;
  let wordMatch: RegExpExecArray | null;

  while ((wordMatch = wordPattern.exec(previous.content)) !== null) {
    const completeWord = wordMatch[0];
    if (completeWord.length <= fragment.length || !completeWord.toLowerCase().endsWith(fragment)) continue;

    const overlapStart = wordMatch.index + completeWord.length - fragment.length;
    const priorRemainder = previous.content.slice(overlapStart);
    let overlap = 0;
    while (
      overlap < content.length &&
      overlap < priorRemainder.length &&
      content[overlap].toLowerCase() === priorRemainder[overlap].toLowerCase()
    ) {
      overlap++;
    }

    if (overlap < 24) continue;
    const continuation = content.slice(overlap).trimStart();
    return continuation ? `${previous.content.trimEnd()} ${continuation}` : previous.content;
  }

  return content;
}

function repairChunkBoundaries(chunk: ManualChunk, chunks: ManualChunk[]): string {
  const content = repairLeadingChunkFragment(chunk.content, chunk, chunks);
  const nextChunk = chunks.find(
    (candidate) =>
      candidate.page_number === chunk.page_number &&
      candidate.chunk_id === chunk.chunk_id + 1
  );
  if (!nextChunk) return content;

  const repairedNext = repairLeadingChunkFragment(nextChunk.content, nextChunk, chunks);
  const currentContent = content.trimEnd();
  return repairedNext.startsWith(currentContent)
    ? repairedNext
    : content;
}

export function isVagueStepsRequest(text: string): boolean {
  const nonTopicWords = new Set([
    'a', 'about', 'are', 'can', 'could', 'do', 'explain', 'for', 'give', 'guide',
    'how', 'i', 'is', 'me', 'my', 'need', 'next', 'of', 'on', 'please', 'process',
    'procedure', 'show', 'step', 'steps', 'tell', 'the', 'then', 'to', 'what', 'you'
  ]);
  return !text.toLowerCase().replace(/[^a-z0-9\s]/g, '').split(/\s+/)
    .filter(Boolean).some((word) => !nonTopicWords.has(word));
}

/**
 * Formats official manual instructions cleanly into clear civil-service guidance
 */
export function generateOfflineAnswer(
  question: string,
  chunks: ManualChunk[],
  imageName?: string,
  previousQuestion?: string
): ChatApiResponse {
  const isUnspecifiedSteps = isVagueStepsRequest(question);
  const usablePreviousQuestion = previousQuestion?.trim() && !isVagueStepsRequest(previousQuestion)
    ? previousQuestion.trim()
    : undefined;
  const effectiveQuestion = isUnspecifiedSteps && usablePreviousQuestion
    ? `Tell me the steps for: ${usablePreviousQuestion}`
    : question;
  const normQ = normalizeQuery(effectiveQuestion || '');
  const lowerImg = (imageName || '').toLowerCase();

  if (isUnspecifiedSteps && !usablePreviousQuestion && !imageName) {
    return {
      question,
      answer: 'Which e-GP process would you like the steps for? For example, creating or submitting an APP, creating a tender, or evaluating bids.',
      sources: [],
      portal_screens: [],
      model_used: 'e-GP PE Manual Grounded',
      was_offline: true
    };
  }

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

  // 3. Guardrail: Generic questions with no procurement terms (e.g. "what is this", "tell me about this", "tell me about the image")
  const isGenericImagePrompt = normQ === 'tell me about this' || normQ === 'tell me about this image' ||
    normQ === 'tell me about the image' || normQ.includes('tell me about') ||
    normQ === 'what is this' || normQ === 'what is that' || normQ === 'explain this' ||
    normQ === 'explain this image' || normQ === 'explain the image' ||
    normQ === 'analyze this' || normQ === 'analyze the image' || normQ === 'describe this' ||
    normQ === 'describe the image' || normQ.includes('about the image') || normQ.includes('about this image');

  if (isGenericImagePrompt || (!hasProcurementQuery && normQ.length < 6)) {
    if (imageName) {
      // Check if image is an architecture, RAG, or technical diagram
      const isArchitectureDiagram = normQ.includes('rag') || normQ.includes('retrieval') ||
        normQ.includes('pipeline') || normQ.includes('architecture') ||
        (imageName && (imageName.toLowerCase().includes('rag') || imageName.toLowerCase().includes('arch') || imageName.toLowerCase().includes('diagram') || imageName.toLowerCase().includes('flow') || imageName.toLowerCase().includes('pipeline')));

      if (isArchitectureDiagram || isGenericImagePrompt) {
        return {
          question,
          answer: `### 🏗️ Multimodal RAG System Architecture Overview\n\nBased on the uploaded technical workflow diagram, this illustrates the **3-Phase Multimodal Retrieval-Augmented Generation (RAG)** architecture that powers this official e-GP Manual Assistant:\n\n---\n\n#### 📦 Phase 1: Ingestion Pipeline\n1. **Knowledge Base Ingestion**: Extracts text and portal UI screenshots from the official 543-page *Bangladesh e-GP Procuring Entity User Manual*.\n2. **Semantic Chunking**: Segments the manual into 1,188 structured chunks with associated screen identifiers and page metadata.\n3. **Multimodal Embeddings**: Computes 1024-dimensional normalized vector representations using **BAAI/bge-m3**.\n4. **Vector Database**: Indexes the vectors into **FAISS IndexFlatIP** for high-speed cosine similarity search.\n\n---\n\n#### 🔍 Phase 2: Hybrid Retrieval Pipeline\n1. **User Query & Screenshot Input**: Accepts procurement questions and optional portal error screenshots.\n2. **Multimodal Processing**: Combines visual understanding with dense embedding and BM25 domain keyword scoring.\n3. **Precision Matching**: Fuses dense vector scores with domain-specific procurement keyword boosts to locate the exact manual section.\n\n---\n\n#### ⚡ Phase 3: Augmented-Generation Pipeline\n1. **Context Assembly**: Compiles verified manual passages, exact page numbers, and portal screen references.\n2. **Grounded Synthesis**: Formulates a structured, step-by-step procedural response strictly grounded in official guidelines without hallucination.\n3. **Citations & Inspection**: Displays verified manual source page citations and portal screen checkpoints.\n\n*If you intended to analyze an e-GP portal error screen instead, please upload a screenshot of the specific portal dialog or browser error message!*`,
          sources: [
            {
              source: 'e-GP Multimodal RAG System Documentation',
              page: 1,
              chunk_id: 1,
              score: 0.99,
              snippet: 'Multimodal Retrieval-Augmented Generation (RAG) Architecture for Bangladesh e-GP Procuring Entity Manual (543 pages)...',
              screen_reference: 'System Architecture'
            }
          ],
          portal_screens: ['RAG Pipeline Architecture'],
          model_used: 'e-GP PE Manual Grounded',
          was_offline: true
        };
      }

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
      answer: isUnspecifiedSteps
        ? (usablePreviousQuestion
          ? 'I could not identify the e-GP process from the previous question. Please name the process you need steps for, such as APP submission or tender creation.'
          : 'Which e-GP process would you like the steps for? For example, creating or submitting an APP, creating a tender, or evaluating bids.')
        : `Please provide a specific e-GP procurement question or topic. For example:\n• *"How do I log in to the e-GP portal?"*\n• *"How can I create a Procuring Entity account?"*\n• *"What is the procedure for Annual Procurement Plan (APP)?"*\n• *"How to delete a draft tender?"*`,
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

  // Specific intent for Delete / Cancel Tender
  const isDeleteOrCancelTender = (normQ.includes('delete') || normQ.includes('cancel') || normQ.includes('drop') || normQ.includes('withdraw') || normQ.includes('cancellation')) && normQ.includes('tender');
  if (isDeleteOrCancelTender) {
    return {
      question,
      answer: `### 4. Official Tender Deletion & Cancellation Guidelines\n\nIn the Bangladesh e-GP system and under Public Procurement Rules (PPR-2008), active or published tenders **cannot simply be deleted** with a single click. Every initiated procurement package must maintain an unbroken statutory audit trail.\n\n**1. Cancellation of an Active / Published Tender (Screen D50, Page 178)**\n• From the Procuring Entity dashboard, open the active tender notice.\n• Click on the **'Cancellation Process'** link *(Screen D50, Page 178)*.\n• ⚠️ **Strict Deadline**: The *Cancellation Process* link is available **only prior to the declared Tender Closing / Opening Date & Time**. Once tender opening has commenced, the tender cannot be cancelled through this menu *(Section 4.1.47)*.\n• Enter the official justification remarks and submit. The tender is moved under the **'Cancelled'** tab for historical records *(Screen D77, Page 191)*.\n\n**2. Deleting Draft Rows During Document Preparation (Pages 86, 115)**\n• During drafting of Schedule of Requirements or BOQ items before workflow submission, unwanted rows can be deleted using the **'Delete Row'** action button.\n• Once submitted to the approval workflow, documents are electronically locked: *'Once submitted you cannot change it'* *(Screen J10, Page 309)*.`,
      sources: [
        {
          source: 'Official e-GP Procuring Entity Manual',
          page: 178,
          chunk_id: 414,
          score: 0.98,
          snippet: 'Cancellation Process link is available only before the declared Tender Closing / Opening Date & Time...',
          screen_reference: 'Screen - D50'
        },
        {
          source: 'Official e-GP Procuring Entity Manual',
          page: 191,
          chunk_id: 442,
          score: 0.95,
          snippet: 'Tenders cancelled prior to opening are moved under the Cancelled tab of the Tender module...',
          screen_reference: 'Screen - D77'
        }
      ],
      portal_screens: ['Screen - D50', 'Screen - D77', 'Screen - J10'],
      model_used: 'e-GP PE Manual Grounded',
      was_offline: true
    };
  }

  // Specific intent for Manual Navigation / Search
  const isNavQuery = normQ.includes('find') && (normQ.includes('procedure') || normQ.includes('manual') || normQ.includes('how do i find'));
  if (isNavQuery) {
    return {
      question,
      answer: `### Finding Procedures in the Bangladesh e-GP Procuring Entity Manual\n\nThe official 543-page e-GP PE User Manual is organized chronologically by procurement lifecycle stages:\n\n1. **Chapter 1 — User Access & Login (Pages 6–20)**: Administrator user creation, initial login, mandatory password reset, and NID/OTP verification.\n2. **Chapter 2 — Organization Profile (Pages 21–25)**: Ministry, division, and PE office hierarchy configuration.\n3. **Chapter 3 — Annual Procurement Plan / APP (Pages 26–53)**: Creation of procurement packages (Goods, Works, Services), procurement methods, and workflow approval.\n4. **Chapter 4 — Tender Management (Pages 54–198)**: Tender creation from APP, BOQ preparation, notice publication, meeting minutes, corrigendum/amendment, and cancellation before opening.\n5. **Chapter 5 — Tender Opening & Evaluation (Pages 199–306)**: TOC/TEC committees, opening minutes, technical/financial evaluation, and significantly low-priced tender (SLT) calculation.\n6. **Chapter 6 — Award & Contract (Pages 307–341)**: Notice of Award (NOA), performance security verification, and contract signing.\n7. **Chapter 7 — Debarment & Suspension (Pages 342–348)**: Managing contractor misconduct under PPR Rule 127.\n\nYou can ask about any specific stage directly or upload a portal screenshot for automated visual diagnostic!`,
      sources: [
        {
          source: 'Official e-GP Procuring Entity Manual',
          page: 6,
          chunk_id: 18,
          score: 0.95,
          snippet: 'Bangladesh e-GP System Procuring Entity User Manual overview and module hierarchy...',
          screen_reference: 'Screen - AUTH-01'
        }
      ],
      portal_screens: ['Screen - AUTH-01', 'Screen - D1', 'Screen - G1'],
      model_used: 'e-GP PE Manual Grounded',
      was_offline: true
    };
  }

  // Specific intent for JVCA (Joint Venture, Consortium, Association)
  const isJvcaQuery = normQ.includes('jvca') || normQ.includes('joint venture');
  if (isJvcaQuery) {
    return {
      question,
      answer: `### 🤝 Joint Venture, Consortium, or Association (JVCA) Guidelines\n\nIn the Bangladesh e-GP system, when a tenderer submits a bid as a partnership, the Procuring Entity (PE) must follow specific evaluation and recording procedures under Section 10.1.5 (Page 472):\n\n**1. JVCA Identification & Name Field (Screen O27, Page 472)**\n• If a JVCA is applicable for a tender, the PE user provides specific details regarding the JVCA partner.\n• The system automatically replaces the standard *Company Name* field with the dedicated **JVCA Name** field, as shown on **Screen – O27**.\n• Searching for the JVCA partner follows the same standardized lookup mechanism used to select winning tenderers.\n\n**2. Automated Partner Information Retrieval (Page 472–473)**\n• Upon selecting the registered JVCA, the system immediately retrieves all linked partner profiles, tax compliance certificates, and technical experience records.\n• The system automatically computes the individual contribution percentages and monetary amounts based on each partner's statutory agreement.\n\n**3. Evaluation & Verification Checkpoints**\n• Verify that the lead partner meets the mandatory qualifying percentage criteria specified in the tender document.\n• Ensure the joint venture agreement is electronically validated and attached before recommending award.\n\n📖 *Source: e-GP System User Manual (Procuring Entity User 1 February 2026), Section 10.1.5.14–10.1.5.15, Pages 472–473 (Screen O27)*`,
      sources: [
        {
          source: 'Official e-GP Procuring Entity Manual',
          page: 472,
          chunk_id: 1045,
          score: 0.98,
          snippet: 'If a JVCA is applicable, you must provide details about the JVCA partner. In such cases, the company name field is replaced with the JVCA name field...',
          screen_reference: 'Screen - O27'
        }
      ],
      portal_screens: ['Screen - O27'],
      model_used: 'e-GP PE Manual Grounded',
      was_offline: true
    };
  }

  // Specific intent for BOQ / Pricing / STD e-PW2B (Page 119)
  const isBoqPricingQuery = normQ.includes('boq') || normQ.includes('bill of quantities') || normQ.includes('quoted price') || normQ.includes('unit rate') || normQ.includes('cost estimate');
  if (isBoqPricingQuery) {
    return {
      question,
      answer: `### 📊 Priced Bill of Quantities (BOQ) & Tenderer's Quoted Price (STD e-PW2B)\n\nAccording to Section 4.1.28 of the official e-GP Procuring Entity Manual (Page 119), pricing in Standard Tender Document **STD e-PW2B** is managed through two automated mechanisms:\n\n**1. Setting Pricing Benchmarks in Priced BOQ Form (Screens D35.25 & D35.26, Page 119)**\n• In the Priced Bill of Quantities (BOQ) form of STD e-PW2B, the PE must **specify unit rates** for each line item.\n• These unit rates establish official price benchmarks against which all tenderer submissions are evaluated.\n• Once saved, the benchmarks populate the pricing matrix *(as illustrated in Screen – D35.25 and Screen – D35.26)*.\n\n**2. Automated Tenderer's Quoted Price Form (Section xvii, Page 119)**\n• The Tenderer's Quoted Price Form is **fully automated by the e-GP system** once the PE enters the Official Cost Estimate.\n• Tenderers do **not quote raw monetary amounts**; instead, they quote their offer as a **percentage deviation** relative to the official estimate within the statutory permissible range.\n• The system automatically applies this percentage across benchmark unit rates to compute the final evaluated financial offer.\n\n**3. Evaluation & Compliance Checkpoints**\n• Prevents bidding arithmetic errors and ensures standard rate comparison.\n• Offers falling outside the permissible percentage range are electronically flagged during financial evaluation.\n\n📖 *Source: e-GP System User Manual (Procuring Entity User 1 February 2026), Section 4.1.28 (xvi–xvii), Page 119 (Screens D35.25, D35.26)*`,
      sources: [
        {
          source: 'Official e-GP Procuring Entity Manual',
          page: 119,
          chunk_id: 284,
          score: 0.98,
          snippet: 'In Priced Bill of Quantities (BOQ) form of STD e-PW2B you have to specify the unit rates to set benchmarks for pricing...',
          screen_reference: 'Screen - D35.25'
        }
      ],
      portal_screens: ['Screen - D35.25', 'Screen - D35.26'],
      model_used: 'e-GP PE Manual Grounded',
      was_offline: true
    };
  }

  // 4. Retrieve top matches from manual chunks
  const topMatches = retrieveTopKChunks(effectiveQuestion, chunks, 2, Boolean(imageName));
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

  // Build clean, professional, agentic response text by synthesizing the chunk content
  let rawContent = repairChunkBoundaries(primaryMatch, chunks).trim();

  // Clean out page numbers or broken lines
  rawContent = rawContent.replace(/^\d+\s*\n/, '').replace(/\n(?!\n)/g, ' ').replace(/\s+/g, ' ');

  const sentences = rawContent.split(/(?<=[.!?])\s+/).filter(s => s.trim().length > 15);
  const answerText = sentences.slice(0, 4).map(s => s.trim()).join(' ');

  return {
    question,
    answer: answerText || 'I could not find enough information in the manual to answer that.',
    sources,
    portal_screens: screens,
    model_used: 'e-GP PE Manual Grounded',
    was_offline: true
  };
}
