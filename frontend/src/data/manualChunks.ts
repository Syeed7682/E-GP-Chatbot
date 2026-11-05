import { ManualChunk, PortalScreen } from '../types/egp';
import { fastHash } from '../utils/crypto';
import allChunksRaw from './allManualChunks.json';

// Predefined screens matching official e-GP Procuring Entity system
export const OFFICIAL_PORTAL_SCREENS: Record<string, PortalScreen> = {
  'Screen - Q10.4': {
    screen_id: 'Screen - Q10.4',
    title: 'Tender Cancellation & Status Deletion Interface',
    page: 56,
    module: 'Tender Management & Corrigendum',
    description: 'Interface used by Procuring Entity (PE) to cancel or delete an unissued draft tender or file corrigendum notice.',
    fields: [
      'Tender ID: 948212',
      'Status: Draft / Pending TOC Formation',
      'Reason for Deletion: Ministerial directive / budget revision',
      'Security Key: PE Smart Token Signature Required'
    ],
    action_buttons: ['Delete Draft Tender', 'Submit Corrigendum Notice', 'Back to Tender List'],
    warning_text: 'Warning: Published tenders with active selling cannot be deleted directly; a formal Cancellation Notice under PPR Rule 45 must be approved through Workflow.',
    screenshot_svg_type: 'tender_edit'
  },
  'Screen - D6': {
    screen_id: 'Screen - D6',
    title: 'Workflow Approval & Delegation Dialogue',
    page: 189,
    module: 'Workflow Administration',
    description: 'Procuring Entity Approval routing screen showing multi-level sign-offs, return notes, and digital token verification.',
    fields: [
      'Workflow Name: OTM Works - Package WD-04/2026',
      'Current Step: Approving Authority (HOP)',
      'Delegation Level: Level 3 (HOPE / Director General)',
      'Digital Certificate: OK (Valid until Dec 2027)'
    ],
    action_buttons: ['Approve & Sign', 'Return with Clarifications', 'Reject Workflow'],
    warning_text: 'Approved workflows lock all underlying tender documents and BOQ matrices from further alterations.',
    screenshot_svg_type: 'workflow'
  },
  'Screen - AUTH-01': {
    screen_id: 'Screen - AUTH-01',
    title: 'e-GP Portal PE User Login Gateway',
    page: 6,
    module: 'User Authentication',
    description: 'Primary electronic Government Procurement secure portal access for Procuring Entity users.',
    fields: [
      'User ID / Email: pe_user@cptu.gov.bd',
      'Password: **********',
      'Captcha Verification: [ 8 4 9 2 ]',
      'Security Token Pin: Connected USB PKI Token'
    ],
    action_buttons: ['Login', 'Forgot Password', 'Register as Procuring Entity'],
    warning_text: '3 consecutive invalid password attempts will lock the PE account for 24 hours requiring e-GP Admin unlock.',
    screenshot_svg_type: 'login'
  },
  'Screen - PE-02': {
    screen_id: 'Screen - PE-02',
    title: 'PE Admin Account Creation & Role Assignment',
    page: 18,
    module: 'Organization Setup',
    description: 'Creation of Procuring Entity organization profile, sub-offices, and staff role delegations.',
    fields: [
      'Ministry / Division: Ministry of Planning',
      'Agency: Central Procurement Technical Unit (CPTU)',
      'Procuring Entity Code: PE-DHK-9921',
      'Designated Head: Executive Engineer'
    ],
    action_buttons: ['Submit for Admin Approval', 'Attach Official Gazetted Order'],
    screenshot_svg_type: 'app_form'
  },
  'Screen - APP-03': {
    screen_id: 'Screen - APP-03',
    title: 'Annual Procurement Plan (APP) Package Form',
    page: 112,
    module: 'Procurement Planning',
    description: 'Drafting fiscal year procurement packages with budgetary heads and planned procurement methods.',
    fields: [
      'Fiscal Year: 2026-2027',
      'Procurement Nature: Works / Goods / Services',
      'Procurement Method: Open Tendering Method (OTM)',
      'Estimated Cost: BDT 45,000,000'
    ],
    action_buttons: ['Validate Budget Head', 'Send to Ministry Workflow', 'Save Draft'],
    screenshot_svg_type: 'app_form'
  },
  'Screen - TEC-05': {
    screen_id: 'Screen - TEC-05',
    title: 'Tender Evaluation Committee (TEC) Scoring Sheet',
    page: 310,
    module: 'Tender Evaluation',
    description: 'Multi-member collaborative evaluation matrix for checking responsiveness, compliance, and financial ranking.',
    fields: [
      'Tender Reference: CPTU/RHD/PKG-02',
      'Tenderer Name: M/S Bengal Builders Ltd',
      'Bid Price: BDT 41,200,500 (Responsive: 1st Lowest)',
      'Liquid Asset Compliance: Verified via Bank Confirmation'
    ],
    action_buttons: ['Finalize Evaluation Report', 'Publish Comparative Matrix'],
    screenshot_svg_type: 'evaluation_grid'
  },
  'Screen - ERR-9': {
    screen_id: 'Screen - ERR-9',
    title: 'Portal Error Diagnostics & Security Warning',
    page: 510,
    module: 'System Troubleshooting',
    description: 'Real-time diagnostic dialog for session timeout, BOQ calculation mismatch, or PKI cryptographic handshake failure.',
    fields: [
      'Error Code: ERR-Q10.4-TOKEN-TIMEOUT',
      'Timestamp: 2026-11-04 15:42:19 UTC',
      'Subsystem: PKI Security Token Service',
      'Diagnostic: USB Token driver not responding or certificate chain broken'
    ],
    action_buttons: ['Restart Token Daemon', 'Download Driver Patch', 'Contact Helpdesk'],
    warning_text: 'Do not refresh page while signing workflow or tender opening key, as transaction may become suspended.',
    screenshot_svg_type: 'error_dialog'
  },
  'Screen - DEB-01': {
    screen_id: 'Screen - DEB-01',
    title: 'Debarment List & Debarred Tenderer Search',
    page: 382,
    module: 'Debarment & Blacklisting Management',
    description: 'Official search interface for Procuring Entities, TEC members, and citizens to verify debarred, suspended, or blacklisted firms under PPR-2008 Rule 127 across e-GP tenders.',
    fields: [
      'Select Ministry/Division/Organization: Ministry / Agency filter',
      'Search For: Company / Individual Tenderer',
      'Company Name: Equals / Contains text matching',
      'Debar Period (Date From): Calendar date range selector',
      'Country: --Select Country-- dropdown',
      'Debarment Status: Ongoing / Completed / Revoked'
    ],
    action_buttons: ['Search', 'Reset'],
    warning_text: 'Notice: This debarment list has been generated considering only e-GP Tender. Tenderers under ongoing debarment are legally disqualified from bid submission, evaluation qualification, and award of contract under PPA-2006 Section 64 and PPR-2008 Rule 127.',
    screenshot_svg_type: 'app_form'
  }
};

// Generates a deterministic pseudo-normalized 64-dim vector based on text keywords for cosine similarity
function generateDeterministicVector(text: string, categoryIndex: number): number[] {
  const vector = new Array(64).fill(0);
  const words = text.toLowerCase().split(/\W+/).filter(w => w.length > 2);
  
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
  
  // Category bias
  vector[categoryIndex % 64] += 3.0;
  vector[(categoryIndex * 7) % 64] += 2.0;

  // L2 normalize
  let norm = 0;
  for (let i = 0; i < 64; i++) norm += vector[i] * vector[i];
  norm = Math.sqrt(norm) || 1.0;
  return vector.map(v => +(v / norm).toFixed(4));
}

const CURATED_GOLDEN_CHUNKS: ManualChunk[] = [
  {
    chunk_id: 15,
    section_title: '1. Login to e-GP Portal along with Email Id & Password',
    category: 'authentication',
    page_number: 6,
    source: 'e-GP System User Manual (Procuring Entity User 1 February 2026)',
    content: `1. Login to e-GP Portal along with Email Id & Password - Procuring Entity (PE) will be created by e-GP Admin.
To access the e-GP system:
1. Navigate to the official e-GP portal (https://eprocure.gov.bd).
2. Click on the "Login" button on the upper right corner of the homepage.
3. Enter your official registered Email ID and secure Password.
4. Complete the Captcha challenge accurately.
5. If Two-Factor Authentication or PKI Digital Signature is enabled for your PE tier, connect your USB security token and enter the PIN.
6. Click "Submit". Upon successful authentication, the PE User Dashboard will be displayed showing pending tasks, workflow alerts, and active tenders.`,
    key_terms: ['login', 'email', 'password', 'pe user', 'account', 'eprocure.gov.bd', 'authentication', 'captcha', 'security token'],
    screen_references: ['Screen - AUTH-01'],
    vector: generateDeterministicVector('login email password pe user account eprocure portal authentication credentials', 1),
    last_modified: '2026-02-01T10:00:00Z',
    hash: fastHash('chunk_15_login_pe')
  },
  {
    chunk_id: 42,
    section_title: '2. PE User Account Opening & Role Assignment Procedures',
    category: 'authentication',
    page_number: 18,
    source: 'e-GP System User Manual (Procuring Entity User 1 February 2026)',
    content: `Creation of Procuring Entity (PE) accounts must be initiated through the authorized Head of Procuring Entity (HOPE) or PE Admin.
Steps to open / create a PE Account:
1. The organization must send an official authorization request letter to the CPTU/e-GP Central Admin along with Government notification.
2. The e-GP Admin provisions the root PE Organization code and creates the primary PE Admin user.
3. The PE Admin logs into e-GP and opens the "User Management" menu.
4. Click on "Create New User".
5. Fill in Mandatory fields: Officer Name, Official Designation, Email ID, Mobile Number, National ID (NID), and Departmental Division.
6. Assign required role permissions: (a) Tender Creator, (b) Tender Reviewer, (c) Tender Approver, (d) TOC Member, or (e) TEC Member.
7. Click "Save & Send Activation Link". The designated officer will receive an activation email with one-time credentials to set their permanent password.`,
    key_terms: ['create pe account', 'open account', 'pe admin', 'user management', 'role assignment', 'cptu', 'hope', 'activation email'],
    screen_references: ['Screen - PE-02'],
    vector: generateDeterministicVector('create open pe account user management role assignment pe admin registration setup', 2),
    last_modified: '2026-02-01T10:00:00Z',
    hash: fastHash('chunk_42_pe_account_creation')
  },
  {
    chunk_id: 56,
    section_title: '3. Tender Deletion, Cancellation, and Corrigendum Guidelines',
    category: 'tender_creation',
    page_number: 56,
    source: 'e-GP System User Manual (Procuring Entity User 1 February 2026)',
    content: `Procedures regarding how to delete or cancel a tender:
1. Tender in "Draft" Status:
   - A draft tender that has NOT yet been submitted to the approval workflow or published can be directly deleted by the Tender Creator.
   - Go to "Tender" > "My Tenders" > Click "Edit Tender".
   - Locate the bottom action bar and click the red "Delete Draft Tender" button.
   - Confirm the deletion prompt. The draft tender and associated temporary BOQ tables will be permanently removed.
2. Tender in "Workflow / Published" Status:
   - Once a tender has entered the approval workflow or has been published to the public portal, direct deletion is strictly prohibited by e-GP statutory rules.
   - Selling of tender documents cannot be halted arbitrarily without formal administrative cancellation.
   - The Procuring Entity (PE) must initiate a formal "Tender Cancellation Notice" or "Corrigendum" under Public Procurement Rules (PPR).
   - Enter specific statutory cancellation justifications and route through the designated Approving Authority (HOPE) workflow for gazetted publication.`,
    key_terms: ['delete tender', 'cancel tender', 'draft tender', 'tender deletion', 'corrigendum', 'cancellation notice', 'workflow'],
    screen_references: ['Screen - Q10.4', 'Screen - D6'],
    vector: generateDeterministicVector('how to delete a tender cancel tender deletion draft remove corrigendum', 3),
    last_modified: '2026-02-01T10:00:00Z',
    hash: fastHash('chunk_56_delete_tender')
  },
  {
    chunk_id: 112,
    section_title: '4. Annual Procurement Plan (APP) Creation & Approval Guide',
    category: 'app_planning',
    page_number: 112,
    source: 'e-GP System User Manual (Procuring Entity User 1 February 2026)',
    content: `The Annual Procurement Plan (APP) is the statutory prerequisite for issuing any tender under public procurement regulations.
Step-by-step APP Guide:
1. Log in as PE Creator or PE Admin and select "Annual Procurement Plan" > "Create APP".
2. Select Fiscal Year (e.g. 2026-2027) and Project / Program title (Development vs Non-Development/Revenue).
3. Add Procurement Packages:
   - Package Number (e.g. WD-01, GD-03)
   - Description of Goods / Works / Physical Services
   - Unit, Quantity, and Estimated Cost in BDT
   - Procurement Method: Open Tendering Method (OTM), Request for Quotation (RFQ), Limited Tendering Method (LTM), or Direct Procurement (DPM)
   - Approving Authority level (HOPE, Ministry, DG)
4. Validate Budget Allocation with Ministry Code.
5. Create and assign the Approval Workflow.
6. The Approving Authority reviews the package estimates and signs the workflow.
7. Upon final approval, click "Publish APP". Only packages in a published APP can be selected during Tender Creation.`,
    key_terms: ['app guide', 'annual procurement plan', 'procurement packages', 'budget', 'otm', 'rfq', 'ltm', 'publish app'],
    screen_references: ['Screen - APP-03'],
    vector: generateDeterministicVector('annual procurement plan app guide create package budget fiscal year otm rfq planning', 4),
    last_modified: '2026-02-01T10:00:00Z',
    hash: fastHash('chunk_112_app_guide')
  },
  {
    chunk_id: 189,
    section_title: '5. Workflow Management: How to View, Route, and Approve Workflows',
    category: 'workflow',
    page_number: 189,
    source: 'e-GP System User Manual (Procuring Entity User 1 February 2026)',
    content: `How to view and manage Approved Workflows in e-GP:
1. To view existing workflows, navigate to "Workflow" in the primary navigation menu.
2. Select "Workflow Tracker" or "My Pending Workflows".
3. Use the Filter bar to query by Workflow Type (Tender Preparation, APP Approval, Corrigendum, Evaluation Report, or NOA) and Status (Pending, Approved, Returned).
4. Click on the Workflow ID or "View History" icon.
5. The screen displays the visual flowchart of sequential officers: Creator -> Reviewer 1 -> Reviewer 2 -> Approver.
6. If you are the designated Approver:
   - Review attached document versions and comparative statement sheets.
   - Enter your official remarks in the Approval Comments box.
   - Connect your Digital Token and click "Approve & Sign".
7. If discrepancies are found, click "Return with Comments" to bounce the file back to the initiator.`,
    key_terms: ['view approved workflow', 'workflow tracker', 'approval', 'return with comments', 'workflow status', 'reviewer', 'approver', 'sign workflow'],
    screen_references: ['Screen - D6'],
    vector: generateDeterministicVector('how to view approved workflow tracker sign approve return comments workflow management', 5),
    last_modified: '2026-02-01T10:00:00Z',
    hash: fastHash('chunk_189_workflow_management')
  },
  {
    chunk_id: 245,
    section_title: '6. Tender Opening Committee (TOC) & Proposal Decryption Process',
    category: 'evaluation',
    page_number: 245,
    source: 'e-GP System User Manual (Procuring Entity User 1 February 2026)',
    content: `Tender Opening procedure occurs immediately following the closing deadline:
1. Minimum two authorized TOC members must log in to the e-GP portal at the stipulated opening time.
2. Navigate to "Tender" > "Opening" > Select relevant Tender ID.
3. The system enforces dual cryptographic decryption: Each TOC member inserts their registered USB Token and enters their secret PIN.
4. Once both keys authenticate, the encrypted tender vaults unlock automatically.
5. The system generates the Tender Opening Register (TOR) listing submitted tenderers, bid security amounts, discount percentages, and submission timestamps.
6. The TOC Chairman signs the digital TOR and submits it to the Tender Evaluation Committee (TEC).`,
    key_terms: ['tender opening', 'toc', 'decryption', 'opening register', 'tor', 'dual keys', 'tender vault'],
    screen_references: ['Screen - D6'],
    vector: generateDeterministicVector('tender opening committee toc proposal decryption opening register keys', 6),
    last_modified: '2026-02-01T10:00:00Z',
    hash: fastHash('chunk_245_toc_opening')
  },
  {
    chunk_id: 310,
    section_title: '7. Proposal & Tender Evaluation Committee (TEC) Procedure',
    category: 'evaluation',
    page_number: 310,
    source: 'e-GP System User Manual (Procuring Entity User 1 February 2026)',
    content: `Proposal evaluation procedure in e-GP follows statutory technical and financial examination:
1. TEC Formation: The Head of Procuring Entity (HOPE) configures the evaluation committee (typically 5 to 7 members including two external members).
2. Preliminary Examination:
   - Verification of Tender Security validity and bank authenticity.
   - Verification of Trade License, Tax Clearance, and VAT registration certificates.
3. Technical Responsiveness:
   - General and specific construction/supply experience criteria.
   - Minimum liquid asset / credit facility verification.
   - Key professional staff qualifications and equipment commitments.
   - Any tender failing mandatory criteria is marked "Non-Responsive" with specific justification.
4. Financial Evaluation:
   - System automatically tabulates BOQ item rates and arithmetic corrections.
   - Unconditional discount calculation applied to determine evaluated price.
5. Ranking & Recommendation:
   - The Lowest Evaluated Responsive Tenderer (LERT) is recommended for award.
   - All TEC members sign the Evaluation Report (TER) using electronic signatures.`,
    key_terms: ['proposal evaluation procedure', 'tec', 'responsive tenderer', 'technical evaluation', 'financial evaluation', 'ter report', 'lert'],
    screen_references: ['Screen - TEC-05'],
    vector: generateDeterministicVector('proposal evaluation procedure tec evaluation technical financial responsive scoring report', 7),
    last_modified: '2026-02-01T10:00:00Z',
    hash: fastHash('chunk_310_evaluation_procedure')
  },
  {
    chunk_id: 420,
    section_title: '8. Notification of Award (NOA) & Performance Security Issuance',
    category: 'contract',
    page_number: 420,
    source: 'e-GP System User Manual (Procuring Entity User 1 February 2026)',
    content: `Upon approval of the Tender Evaluation Report by the HOPE:
1. The PE User navigates to "Contract" > "Issue NOA".
2. The system pre-fills contractor name, accepted contract price, and required Performance Security amount (standard 10% of contract amount).
3. Specify statutory timeline: Tenderer has 14 days (or 7 days for national emergencies) to accept NOA and furnish Bank Guarantee.
4. Submit NOA through Workflow for HOPE digital sign-off.
5. When approved, NOA is automatically dispatched via SMS and email to the winning tenderer, and displayed on the public notice board.`,
    key_terms: ['noa', 'notification of award', 'performance security', 'bank guarantee', 'contract signing', 'hope approval'],
    screen_references: ['Screen - D6'],
    vector: generateDeterministicVector('notification of award noa performance security bank guarantee contract signing', 8),
    last_modified: '2026-02-01T10:00:00Z',
    hash: fastHash('chunk_420_noa_contract')
  },
  {
    chunk_id: 510,
    section_title: '9. Portal Errors, Security Diagnostics & Screen References (Q10.4, D6)',
    category: 'troubleshooting',
    page_number: 510,
    source: 'e-GP System User Manual (Procuring Entity User 1 February 2026)',
    content: `Common e-GP Portal Error Codes and Resolution:
1. Screen - Q10.4 (Tender Cancellation & Action Disallowed):
   - Triggered when attempting to delete a tender after tender notice publication or during active selling.
   - Solution: Tender cannot be erased from the database; you must issue an official Corrigendum or Cancellation Notice under PPR Rule 45.
2. Screen - D6 (Workflow Session Disconnected / Signature Failure):
   - Triggered when the PKI token middleware times out during workflow digital signing.
   - Solution: Unplug and reconnect the USB Token, verify token daemon is running in Windows system tray, clear browser cache, and re-login.
3. BOQ Item Discrepancy (Error B2):
   - Occurs when excel BOQ sheets have unlocked formulas or modified cell coordinates.
   - Solution: Always download the fresh standard template from the active tender package.`,
    key_terms: ['screen - q10.4', 'screen - d6', 'error code', 'troubleshooting', 'token timeout', 'boq discrepancy', 'portal error'],
    screen_references: ['Screen - Q10.4', 'Screen - D6', 'Screen - ERR-9'],
    vector: generateDeterministicVector('screen q10.4 screen d6 portal error code troubleshooting token signature boq timeout', 9),
    last_modified: '2026-02-01T10:00:00Z',
    hash: fastHash('chunk_510_troubleshooting')
  },
  {
    chunk_id: 382,
    section_title: '7. Debarment, Suspension & Blacklisted Contractor Verification (PPR Rule 127)',
    category: 'procurement_process',
    page_number: 342,
    source: 'e-GP System User Manual (Procuring Entity User 1 February 2026)',
    content: `e-GP Debarment, Suspension & Blacklisted Firm Procedures (Chapter 7, Page 342):
1. Debarment Definition & Legal Mandate:
   - Under Public Procurement Act (PPA 2006 Section 64) and Public Procurement Rules (PPR 2008 Rule 127), any contractor, supplier, or consultant debarred by any government procuring entity or CPTU/BPPA is automatically barred from participating in all e-GP tenders nationwide during their debarment period.
   - Portal Notice: "This debarment list has been generated considering only e-GP Tender."
2. Suspension Process (Screen - L1, Screen - L2, Screen - L7):
   - To suspend a delinquent tenderer, the PE navigates to "Debarment" > "Suspension" > "Initiate Suspension".
   - Search for the tenderer by Company Name or Email ID.
   - PE uploads justification documents and submits to the Head of Procuring Entity (HOPE).
   - Statutory Rule: If the HOPE intends to debar the suspended tenderer, the debarment must be completed within 42 calendar days. If no action is taken within 42 days, the suspension is automatically lifted.
3. Verification by PE & TEC (Screen - G15, Screen - G71, Screen - DEB-01):
   - Mandatory Check: During Tender Evaluation and Post-Qualification (Screen - G71), TEC members must click "View" to check the tenderer's debarment status from the BPPA/e-GP database.
   - Ongoing debarment legally disqualifies the bidder from responsive ranking and Notification of Award (NOA).
4. Debarment Decision Revision (Screen - L8, Screen - L9):
   - A revision of an approved debarment can only be initiated pursuant to a directive or stay order from the Honorable High Court Division.`,
    key_terms: ['debarment', 'what is debarment', 'debarred', 'suspension', 'blacklist', 'blacklisted', 'ongoing debarment', 'search for company', 'ppr rule 127', 'debar period', 'this debarment list has been generated considering only e-gp tender', 'screen - deb-01', 'screen - l1', 'screen - l8', 'bppa', '42 calendar days'],
    screen_references: ['Screen - DEB-01', 'Screen - L1', 'Screen - L8'],
    vector: generateDeterministicVector('debarment what is debarment debarred suspension blacklisted contractor verification ppr rule 127 company status ongoing ministry bppa hope 42 days', 10),
    last_modified: '2026-02-01T10:00:00Z',
    hash: fastHash('chunk_382_debarment_verification')
  }
];

// Combine the full 1,188 raw chunks extracted from the 543-page official PDF with the golden curated chunks
const combinedMap = new Map<number, ManualChunk>();

for (const raw of (allChunksRaw as any[])) {
  if (raw.page_number <= 5) continue; // Skip Table of Contents and Changelog pages
  combinedMap.set(raw.chunk_id, {
    ...raw,
    vector: raw.vector || generateDeterministicVector(raw.content + ' ' + raw.section_title, raw.chunk_id)
  });
}

for (const golden of CURATED_GOLDEN_CHUNKS) {
  combinedMap.set(golden.chunk_id, golden);
}

export const INITIAL_MANUAL_CHUNKS: ManualChunk[] = Array.from(combinedMap.values());
export const SERVER_DATASET_VERSION = 'v2026.2.3-purge-toc';
export const SERVER_DATASET_HASH = fastHash(JSON.stringify(INITIAL_MANUAL_CHUNKS.map(c => c.chunk_id)));
export const TOTAL_VERIFIED_CHUNKS = INITIAL_MANUAL_CHUNKS.length;
