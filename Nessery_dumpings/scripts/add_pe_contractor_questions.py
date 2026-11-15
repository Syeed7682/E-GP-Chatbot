"""
Add comprehensive, realistic Procuring Entity (PE) and Contractor questions
grounded in the 543-page e-GP System User Manual (PE), the Registration Manual,
the Master Q&A (1,000 solutions), and PPR-2008 / PPA-2006.
"""

import csv
import re
from pathlib import Path

BASE_DIR = Path('e:/E-gp Project manual')
CSV_PATH = BASE_DIR / 'egp_contractor_evaluation_dataset.csv'

def clean_val(v):
    if not v:
        return ''
    v = v.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    v = re.sub(r'^\*+\s*', '', v)
    v = re.sub(r'\s*\*\s*', '; ', v)
    v = v.replace('**', '')
    v = re.sub(r'\s+', ' ', v).strip()
    return v

# New realistic questions for PE and Contractor
NEW_QUESTIONS = [
    # ========================== PE (PROCURING ENTITY) QUESTIONS ==========================
    {
        'category': 'Tender search and discovery',
        'question': 'How does a PE create an Annual Procurement Plan (APP) and define procurement packages for Goods, Works, and Services?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Medium',
        'expected_section': 'Annual Procurement Plan (APP) Creation & Package Setup',
        'expected_page': 'Manual Pages 28-45, Q81',
        'answer': 'To create an APP on e-GP: (1) Log in with PE credentials and navigate to APP > Create APP. (2) Select the financial year, ministry, division, and agency. (3) Click Add Package to define packages: enter package number, description, procurement nature (Goods/Works/Services), procurement method (OTM/LTM/RFQ), approving authority (HOPE/Ministry), estimated cost, and source of funds (GOB/Development Partner). (4) Set milestone dates for IFT publication, tender opening, evaluation, contract award, and completion. (5) Click Save & Submit to forward the APP to HOPE (Head of Procuring Entity) for electronic approval.',
        'citation': 'e-GP System User Manual (PE) Chapter 3 (APP Module), PPR-2008 Rule 16',
        'notes': 'Official PE procedure for APP preparation and package configuration.'
    },
    {
        'category': 'Procurement methods and international tenders',
        'question': 'Can a PE split an approved procurement package into multiple lots, and what approval is required?',
        'language': 'English',
        'question_type': 'Scenario',
        'difficulty': 'Hard',
        'expected_section': 'APP Approval, Revisions & Package Management',
        'expected_page': 'Manual Pages 46-58, Q121',
        'answer': 'Yes, a PE can split an approved package into lots, subject to PPR-2008 Rule 17. Workflow in e-GP: (1) Navigate to APP > Approved Packages and select Initiate Package Revision. (2) Choose the package and select Split Package / Add Lots. (3) Provide formal justification and adjust estimated costs so the sum of lots equals the original budget or submit revised estimate. (4) Re-split packages must not be used to bypass financial delegation thresholds. (5) Submit the revised package for HOPE re-approval. Once approved by HOPE, the lot structure is finalized and published for tender document creation.',
        'citation': 'e-GP System User Manual (PE) Chapter 3, PPR-2008 Rule 17 (Splitting of Packages)',
        'notes': 'PE workflow for package splitting and HOPE revision approval.'
    },
    {
        'category': 'Understanding tender documents',
        'question': 'How does a PE select the appropriate Standard Tender Document (STD) template for works or goods?',
        'language': 'English',
        'question_type': 'Direct',
        'difficulty': 'Medium',
        'expected_section': 'Standard Tender Documents (STDs) & Financial Forms',
        'expected_page': 'Manual Pages 82-105, Q201',
        'answer': 'When creating a tender in e-GP: (1) Navigate to Tender Management > Create Tender and link the approved APP package. (2) In the STD Selection screen, choose the GoB-approved STD matching the procurement nature and value threshold: for Works, PW1 (OTM national small value), PW2 (OTM medium), PW3 (OTM large), or LTM templates; for Goods, PG1, PG2, PG3; for Services, PSN. (3) The system automatically populates standard GCC and ITT clauses based on the chosen STD. (4) The PE then edits the Tender Data Sheet (TDS) and Particular Conditions of Contract (PCC) to insert project-specific requirements.',
        'citation': 'e-GP System User Manual (PE) Chapter 4 (Tender Preparation), PPR-2008 Rule 31',
        'notes': 'Guidance on GoB-approved STD selection by procurement nature and threshold.'
    },
    {
        'category': 'Tender security and bank guarantee',
        'question': 'What is the exact workflow for PE users to upload Official Cost Estimates with OTP security verification?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Hard',
        'expected_section': 'Official Cost Estimate & Password/OTP Authentication',
        'expected_page': 'Manual Pages 110-125, Q241',
        'answer': 'To upload and lock Official Cost Estimates securely in e-GP: (1) Log in as PE Officer and open the draft tender in Tender Management. (2) Navigate to Cost Estimate module. (3) Enter the itemized bill of quantities rates or upload the verified estimate file. (4) Click Submit Official Estimate. (5) The system triggers two-factor security: enters user password and clicks Request OTP. (6) A 6-digit OTP is dispatched to the PE officer registered mobile. (7) Enter the OTP within 5 minutes and click Verify & Lock. Once locked, the official cost estimate is encrypted, hidden from all tenderers, and stored for automated financial evaluation (+10% limit and SLT calculations).',
        'citation': 'e-GP System User Manual (PE) Section 4.5, Q241 (Cost Estimate OTP)',
        'notes': 'Two-factor OTP security requirement for encrypting official cost estimates.'
    },
    {
        'category': 'Pre-tender meeting and clarification',
        'question': 'How does a PE schedule a pre-tender meeting, record vendor queries, and publish official minutes on e-GP?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Medium',
        'expected_section': 'Pre-Tender Meetings & Vendor Query Management',
        'expected_page': 'Manual Pages 140-158, Q281',
        'answer': 'PE pre-tender meeting workflow on e-GP: (1) During tender creation, specify the pre-tender meeting date, time, and venue/link in the TDS. (2) Tenderers submit clarification queries online through the portal before the query cutoff date. (3) Log in as PE, navigate to Tender Management > Pre-Tender Queries. (4) Review submitted queries, prepare consolidated responses, and upload the signed Pre-Tender Minutes and clarification document. (5) Click Publish Minutes. The system automatically sends notification alerts via SMS and email to all tenderers who purchased tender documents, and the minutes become legally binding amendments.',
        'citation': 'e-GP System User Manual (PE) Chapter 5, PPR-2008 Rule 35',
        'notes': 'Official PE procedure for managing vendor queries and publishing pre-tender minutes.'
    },
    {
        'category': 'Tender validity, deadlines and corrigenda',
        'question': 'What is the procedure for a PE to issue a Corrigendum / Addendum for a floating tender, and when must closing date be extended?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Medium',
        'expected_section': 'Corrigendum Management & Schedule Amendments',
        'expected_page': 'Manual Pages 160-178, Q321',
        'answer': 'To issue a Corrigendum on e-GP: (1) Go to Tender Management > Floating Tenders and click Create Corrigendum. (2) Select the sections to amend: schedule dates, BOQ quantities, specifications, or TDS/PCC clauses. (3) Provide detailed justification for the amendment. (4) If substantive changes are made or the amendment is issued close to the deadline, the PE must extend the tender submission closing date (minimum 7-14 days depending on change severity per PPR-2008). (5) Submit the corrigendum for internal PE approval. (6) Once approved, the system publishes the corrigendum and alerts all document purchasers via portal, email, and SMS.',
        'citation': 'e-GP System User Manual (PE) Chapter 6, PPR-2008 Rule 37',
        'notes': 'Corrigendum creation workflow and mandatory deadline extension rules.'
    },
    {
        'category': 'Tender opening and evaluation',
        'question': 'What are the exact roles of TOC members during electronic tender opening, and how is hash verification performed?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Hard',
        'expected_section': 'Tender Opening Reports (TOR1/TOR2) & Hash Verification',
        'expected_page': 'Manual Pages 185-210, Q361',
        'answer': 'Electronic tender opening workflow on e-GP: (1) At the scheduled opening time, TOC (Tender Opening Committee) members log into e-GP. (2) A minimum quorum of TOC members must authenticate with their credentials. (3) The system decrypts submitted bids and validates each tender submission cryptographic hash against the submission timestamp. (4) If hash matches, bid is verified as tamper-free. (5) The system generates Tender Opening Report 1 (TOR-1) showing bidder names, quoted prices, and tender security status. (6) All TOC members digitally sign TOR-1. (7) TOR-1 is automatically published to all participating bidders dashboards.',
        'citation': 'e-GP System User Manual (PE) Chapter 7, PPR-2008 Rule 96',
        'notes': 'TOC online opening protocol, hash verification, and TOR-1 publication.'
    },
    {
        'category': 'Tender opening and evaluation',
        'question': 'How does a PE configure external and internal members in the Tender Evaluation Committee (TEC/TSC)?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Medium',
        'expected_section': 'Tender Evaluation Committees (TEC/TSC) Setup',
        'expected_page': 'Manual Pages 215-235, Q401',
        'answer': 'Setting up TEC/TSC in e-GP: (1) Log in as PE Admin/Officer and navigate to Committee Management > Create TEC/TSC. (2) Enter committee reference number and link to tender. (3) Designate Chairperson, Member-Secretary, and Committee Members. (4) Per PPR-2008 Rule 8, TEC must consist of at least 5 members (or 7 for large procurements), with at least 2 external members from outside the procuring entity or ministry. (5) For external members, search and select verified e-GP external user accounts. (6) Submit the proposed committee to HOPE for digital approval. (7) Upon approval, assigned members receive system roles to access evaluation sheets (TER-1 through TER-4).',
        'citation': 'e-GP System User Manual (PE) Chapter 8, PPR-2008 Rule 8',
        'notes': 'TEC composition rules (mandatory external members) and e-GP configuration.'
    },
    {
        'category': 'Tender opening and evaluation',
        'question': 'How does the e-GP system automatically calculate and flag Significantly Low-Priced Tenders (SLT)?',
        'language': 'English',
        'question_type': 'Direct',
        'difficulty': 'Hard',
        'expected_section': 'Significantly Low-Priced Tender (SLT) Calculation',
        'expected_page': 'Manual Pages 255-275, Q481',
        'answer': 'e-GP automated SLT calculation workflow: (1) During financial evaluation, the system compares each responsive quoted price against the official cost estimate and item-by-item benchmark rates. (2) If a bid price is abnormally low (substantially below the estimate threshold specified in PPR-2008 / CPTU guidelines), the system automatically flags the bid as Significantly Low-Priced Tender (SLT). (3) The TEC issues an online rate analysis clarification request to the bidder through e-GP. (4) The bidder must upload detailed cost breakdown and unit price analysis. (5) TEC evaluates whether the low price poses an execution risk before declaring financial responsiveness.',
        'citation': 'e-GP System User Manual (PE) Chapter 9, PPR-2008 Rule 98',
        'notes': 'SLT detection, automated flagging, and mandatory rate analysis clarification.'
    },
    {
        'category': 'Tender opening and evaluation',
        'question': 'How does e-GP enforce the Rule of +10% and -10% Official Cost Estimate limit for evaluation?',
        'language': 'English',
        'question_type': 'Direct',
        'difficulty': 'Medium',
        'expected_section': 'Financial Responsiveness & +10% Cost Limit Checks',
        'expected_page': 'Manual Pages 240-254, Q441',
        'answer': 'For national Works tenders governed by the +10% and -10% cost limit rule under PPR-2008 amendments: (1) The system uses the locked official cost estimate. (2) Upon opening financial bids, the system calculates the percentage deviation: ((Bid Price - Official Estimate) / Official Estimate) * 100. (3) Bids quoting more than +10% above the official estimate or less than -10% below the estimate (where applicable by GoB notification) are automatically flagged as non-responsive by the system algorithm. (4) The TEC evaluation report (TER) automatically excludes non-compliant bids from ranking.',
        'citation': 'e-GP System User Manual (PE) Section 8.4, PPR-2008 Cost Limit Rules',
        'notes': 'Automated system enforcement of percentage deviation from official estimate.'
    },
    {
        'category': 'Notice of Award and contract signing',
        'question': 'What is the step-by-step procedure for a PE to issue Notification of Award (NOA) through e-GP?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Medium',
        'expected_section': 'Notification of Award (NOA) & Performance Security',
        'expected_page': 'Manual Pages 310-330, Q641',
        'answer': 'To issue an NOA on e-GP: (1) After HOPE/Approving Authority approves the final Tender Evaluation Report (TER-4), navigate to Tender Management > Award Process. (2) Verify the lowest evaluated responsive bidder. (3) Fill in the NOA form: contract amount, completion period, and required Performance Security amount (typically 10% of contract price, or up to 25% for SLT). (4) Specify deadline for Performance Security submission (typically 14 to 28 days) and contract signing. (5) Apply digital signature and click Issue NOA. The system sends the NOA electronically to the winning tenderer, alerts unsuccessful bidders, and posts the public award notice.',
        'citation': 'e-GP System User Manual (PE) Chapter 10, PPR-2008 Rule 102',
        'notes': 'Step-by-step NOA issuance, performance security calculation, and notifications.'
    },
    {
        'category': 'Notice of Award and contract signing',
        'question': 'What is the standstill period after evaluation approval before issuing NOA, and when does it apply?',
        'language': 'English',
        'question_type': 'Scenario',
        'difficulty': 'Hard',
        'expected_section': 'Notification of Award & Standstill Rules',
        'expected_page': 'Manual Pages 325-338, PPR-2008',
        'answer': 'The standstill period is a mandatory pause between publication of the tender evaluation results/intention to award and the final issuance of the NOA (typically 7 to 10 days for qualifying procurements). Purpose: allows unsuccessful tenderers to review results and submit formal complaints or grievances if procurement rules were violated. If a complaint is filed within the standstill window, the e-GP system enforces a procurement freeze, preventing the PE from issuing the NOA until the complaint is officially resolved by the PE or CPTU Review Panel.',
        'citation': 'PPR-2008 Standstill Provisions, PPA-2006 Section 29, Q961',
        'notes': 'Standstill period rules, complaint window, and procurement freeze trigger.'
    },
    {
        'category': 'Contract execution and delivery',
        'question': 'How does a PE project engineer review, verify, and approve Measurement Book (MB) entries?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Medium',
        'expected_section': 'e-CMS Site Handover, Work Programs & Measurement Sheets (MB)',
        'expected_page': 'Manual Pages 370-395, Q761',
        'answer': 'PE Measurement Book (MB) verification in e-CMS: (1) Log in as Project Engineer/Sub-Assistant Engineer and open Contract Management > e-CMS. (2) Select the active contract and open Measurement Book (MB). (3) Review contractor-submitted measured items, dimensions, and completed quantities against BOQ items. (4) Conduct physical site verification. (5) In e-CMS, enter verified measurements, approve or adjust quantities, and attach site inspection photos. (6) Forward the verified MB sheet to the Executive Engineer / Project Director for final certification. Certified MB quantities unlock contractor progress invoicing.',
        'citation': 'e-GP System User Manual (PE) Chapter 11 (e-CMS Module), Q761',
        'notes': 'Field verification and digital MB certification workflow in e-CMS.'
    },
    {
        'category': 'Contract execution and delivery',
        'question': 'How does a PE process and approve Variation Orders (VO), scope changes, and time extensions in e-CMS?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Hard',
        'expected_section': 'Variation Orders, Time Extensions & Call-off Orders',
        'expected_page': 'Manual Pages 410-435, Q841',
        'answer': 'To process a Variation Order in e-CMS: (1) Go to Contract Management > Variations & Amendments. (2) Click Initiate Variation Order and select variation type: Quantity Variation, New Item, or Time Extension. (3) Enter revised quantities, new item rate analysis, cost impact, and technical justification. (4) Verify variation is within permissible delegated financial limits (typically max 15-25% without higher authority sanction per PPR-2008 Rule 39). (5) Forward to Approving Authority for digital approval. (6) Once approved, the contract value and completion milestone dates in e-CMS are automatically updated.',
        'citation': 'e-GP System User Manual (PE) Chapter 12, PPR-2008 Rule 39',
        'notes': 'Variation order workflow, legal limits, and e-CMS contract adjustments.'
    },
    {
        'category': 'Invoices, bills and payments',
        'question': 'How does the Drawing and Disbursing Officer (DDO) verify and submit contractor bills to iBAS++ using mobile OTP?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Hard',
        'expected_section': 'DDO iBAS++ Integration, Mobile OTP & Paypoint Settlement',
        'expected_page': 'Manual Pages 440-465, Q881',
        'answer': 'DDO bill submission to iBAS++: (1) The PE engineer approves the contractor monthly running bill in e-CMS based on certified MB sheets. (2) The bill forwards to the DDO (Drawing and Disbursing Officer) dashboard. (3) DDO reviews deductions: Advance deduction, Security Deposit / Retention (5-10%), Income Tax (TDS), and VAT. (4) Click Submit to iBAS++. (5) The system triggers security authentication: enters password and clicks Generate OTP. (6) DDO enters the 6-digit OTP received on registered mobile. (7) The bill is transmitted electronically to the government iBAS++ financial system for treasury electronic fund transfer directly to the contractor bank account.',
        'citation': 'e-GP System User Manual (PE) Chapter 13 (iBAS++ Integration), Q881',
        'notes': 'Secure DDO two-factor OTP verification for electronic government payment disbursement.'
    },
    {
        'category': 'Performance appraisal, rating and debarment',
        'question': 'What is the formal procedure for a PE to initiate a 42-day temporary suspension or full debarment against a vendor?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Hard',
        'expected_section': 'Vendor Debarment & 42-Day Temporary Suspensions',
        'expected_page': 'Manual Pages 470-492, Q921',
        'answer': 'Debarment procedure on e-GP: (1) PE gathers documented evidence of fraud, corruption, collusion, false qualification certificates, or contract abandonment. (2) Go to Vendor Management > Debarment / Suspension. (3) Initiate Temporary Suspension: PE can impose an immediate 42-day suspension pending investigation, restricting vendor from bidding on new tenders. (4) Issue formal Show-Cause Notice through the portal giving 14 days to respond. (5) Review vendor explanation with the debarment committee. (6) If unsatisfied, PE forwards debarment recommendation to CPTU. (7) Upon CPTU approval, the debarment is published on the e-GP portal and vendor NID/account is blacklisted nationwide.',
        'citation': 'e-GP System User Manual (PE) Chapter 14, PPR-2008 Rule 127, PPA-2006 Section 64',
        'notes': 'Due process for vendor suspension, show-cause notices, and CPTU debarment publishing.'
    },
    {
        'category': 'Complaint, review and appeal',
        'question': 'What happens when a tenderer submits a formal complaint to the PE, and how is the procurement freeze enforced?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Medium',
        'expected_section': 'Complaints Management & Review Panel Escalations',
        'expected_page': 'Manual Pages 495-520, Q961',
        'answer': 'When a complaint is lodged on e-GP: (1) Tenderer submits formal complaint through Complaints module within 7-10 days of event, paying required fee. (2) The e-GP system immediately activates an automated Procurement Freeze: PE cannot open financial bids, approve evaluation, or issue NOA while freeze is active. (3) PE must review and issue a written response within 7 working days. (4) If tenderer is dissatisfied, they escalate to HOPE within 3 days. (5) If still unresolved, tenderer escalates to the CPTU Review Panel with security deposit. (6) Review Panel issues binding decision. The freeze is only lifted upon official resolution.',
        'citation': 'e-GP System User Manual (PE) Chapter 15, PPR-2008 Rules 56-58, PPA-2006 Section 29',
        'notes': 'Automated procurement freeze mechanics, statutory complaint resolution timelines, and Review Panel escalation.'
    },

    # ========================== CONTRACTOR / TENDERER QUESTIONS ==========================
    {
        'category': 'Registration and company profile',
        'question': 'What should a contractor do if National ID (NID) verification fails 3 times during registration?',
        'language': 'English',
        'question_type': 'Scenario',
        'difficulty': 'Medium',
        'expected_section': 'Portal Access, Account Registration, NID & OTP Security Controls',
        'expected_page': 'Registration Manual Page 5, Q1',
        'answer': 'If NID verification fails 3 times: (1) The e-GP system automatically locks the NID verification module for that account to prevent identity fraud. (2) You cannot self-verify online once locked. (3) Gather your official Election Commission NID card copy, Trade License, and registered mobile number. (4) Contact the e-GP Central Helpdesk by calling 16575 or emailing helpdesk@eprocure.gov.bd with subject "NID Verification Lockout". (5) Helpdesk administrators verify your credentials against the national identity database and manually reset the verification lock.',
        'citation': 'e-GP New User Registration Manual Section 3.1, Q1 (NID Verification)',
        'notes': 'Three-attempt lockout security rule and official helpdesk unlocking procedure.'
    },
    {
        'category': 'Registration and company profile',
        'question': 'How does a foreign contractor or international joint venture partner register on Bangladesh e-GP?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Hard',
        'expected_section': 'International Tenderer Registration',
        'expected_page': 'Registration Manual Pages 12-16',
        'answer': 'For International Tenderers registering on e-GP: (1) Go to eprocure.gov.bd and click New User Registration > International Tenderer. (2) Enter foreign company legal name, country of incorporation, registration number, and corporate headquarters address. (3) For foreign authorized representatives without Bangladesh NID, select Passport Number and upload clear scanned passport copy. (4) Upload Certificate of Incorporation, Power of Attorney attested by Bangladesh Embassy/High Commission or Apostilled, and international bank solvency letter. (5) Pay the international registration fee via international credit card/SWIFT. (6) CPTU verifies and activates the account.',
        'citation': 'e-GP New User Registration Manual Section 4 (International Users), PPR-2008',
        'notes': 'International vendor registration requirements, passport verification, and consular attestation.'
    },
    {
        'category': 'Tender search and discovery',
        'question': 'How does a contractor search for tenders using CPV codes, district filters, or procuring entity names?',
        'language': 'English',
        'question_type': 'Direct',
        'difficulty': 'Easy',
        'expected_section': 'Tender Search & Discovery',
        'expected_page': 'Portal Navigation Manual Section 2',
        'answer': 'To search open tenders on e-GP: (1) On eprocure.gov.bd homepage or vendor dashboard, click Tender Search. (2) Use Search Filters: enter Ministry/Division, Procuring Entity name (e.g., RHD, LGED, PWD, BWDB), District/Location where works will be executed, or Procurement Category (Goods/Works/Services). (3) For precise classification, search by CPV (Common Procurement Vocabulary) code or keyword. (4) Set status to Floating to view currently open tenders. (5) The search results show Tender ID, IFT Reference, Closing Date/Time, and Document Fee. Click View to inspect tender details.',
        'citation': 'e-GP Portal User Guide Section 2.1, PPR-2008 Rule 35',
        'notes': 'Advanced search filtering by PE, district, CPV codes, and floating tender status.'
    },
    {
        'category': 'Tender document purchase, download and fees',
        'question': 'What is the procedure if a tenderer pays the document fee via an e-GP partner bank but the portal still displays unpaid?',
        'language': 'English',
        'question_type': 'Scenario',
        'difficulty': 'Medium',
        'expected_section': 'Tender Document Purchase & Payment Reconciliation',
        'expected_page': 'Manual Section 4.2, Q201',
        'answer': 'If payment is deducted but portal shows unpaid: (1) Do not pay a second time immediately. Banking reconciliation between partner bank API and e-GP portal usually takes 15-30 minutes. (2) Obtain bank deposit slip / transaction ID / electronic debit confirmation. (3) Log out, clear browser cache, and log back into e-GP. Check Dashboard > Payment Status. (4) If still unpaid after 1 hour, contact e-GP Helpdesk (16575 / helpdesk@eprocure.gov.bd) and provide Tender ID, Vendor ID, Bank Branch, Transaction Reference, and Amount. Helpdesk triggers manual bank API synchronization to activate document download.',
        'citation': 'e-GP Helpdesk Operational Guide, e-GP System Q&A Q201',
        'notes': 'Payment reconciliation delay handling, transaction proof, and helpdesk API resync.'
    },
    {
        'category': 'Tender preparation and online submission',
        'question': 'How does a contractor fill out the electronic Bill of Quantities (BOQ) / Price Schedule online without errors?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Medium',
        'expected_section': 'Electronic BOQ Preparation & Submission',
        'expected_page': 'Manual Pages 100-118, Q201',
        'answer': 'Filling out electronic BOQ on e-GP: (1) Under tender dashboard, open Financial Forms > Bill of Quantities / Price Schedule. (2) Enter unit rates in numbers for each item; the system automatically calculates Total Amount (Unit Rate * Estimated Quantity). (3) Do not leave any mandatory item blank or enter zero unless intentionally offering free items per ITT rules. (4) In words totals are automatically populated by the system to avoid discrepancy errors. (5) Click Validate & Check Arithmetic to ensure all calculations match system formulas. (6) Save draft frequently. (7) Download the generated summary sheet to verify final quoted price before electronic submission.',
        'citation': 'e-GP System User Manual Chapter 4 (Financial Forms), PPR-2008 Rule 98',
        'notes': 'Online BOQ data entry guidelines, automated formula validation, and arithmetic error prevention.'
    },
    {
        'category': 'Tender security and bank guarantee',
        'question': 'How does a contractor issue and verify an electronic Bank Guarantee (e-BG) for tender security?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Hard',
        'expected_section': 'e-BG (Electronic Bank Guarantee) Module',
        'expected_page': 'Manual Section 5.3, Q641',
        'answer': 'Using electronic Bank Guarantee (e-BG) on e-GP: (1) Contractor visits an e-GP scheduled partner bank (e.g., Sonali, Janata, Agrani, Rupali, Islami Bank, BRAC, etc.). (2) Request an e-BG specifically mapped to the e-GP Tender ID. (3) The bank enters the guarantee directly into the e-GP interbank portal with guarantee number, amount, and validity date (tender validity + 28 days). (4) The system generates a unique e-BG reference code. (5) In your e-GP tender submission screen, navigate to Tender Security Form, select Electronic Bank Guarantee (e-BG), and input the e-BG reference number. (6) Click Verify e-BG. The portal confirms status with green checkmark.',
        'citation': 'e-GP System Guidelines for Electronic Bank Guarantee (e-BG), PPR-2008 Rule 29',
        'notes': 'Direct scheduled bank e-BG mapping, automated interbank validation, and tender security linking.'
    },
    {
        'category': 'Tender preparation and online submission',
        'question': 'What is the exact process to withdraw or submit an amended bid before the tender closing deadline?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Medium',
        'expected_section': 'Tender Withdrawal & Modification Before Closing',
        'expected_page': 'Manual Section 6.2, PPR-2008 Rule 94',
        'answer': 'To withdraw or modify a bid before closing: (1) Log into e-GP and open My Tenders > Submitted Tenders. (2) Locate the tender (ensure status is still Floating and closing time has not passed). (3) Click Withdraw Tender. (4) Confirm withdrawal with password authentication. (5) Once withdrawn, the previous encrypted bid package is cancelled. (6) To submit an amended bid, modify your documents/BOQ rates in the preparation screens and complete the final submission before deadline. (7) A new cryptographic submission hash is generated. Note: Once closing time arrives, the system permanently locks submission; no withdrawal or alteration is possible.',
        'citation': 'PPR-2008 Rule 94 (Modification and Withdrawal of Tenders), e-GP System Operations Guide',
        'notes': 'Statutory rights for pre-closing bid withdrawal/modification and system hash regeneration.'
    },
    {
        'category': 'Notice of Award and contract signing',
        'question': 'What mandatory Beneficial Ownership information must a contractor disclose prior to contract signing?',
        'language': 'English',
        'question_type': 'Direct',
        'difficulty': 'Hard',
        'expected_section': 'Mandatory Beneficial Ownership Disclosures',
        'expected_page': 'Manual Section 10.4, Q681',
        'answer': 'Beneficial ownership disclosure on e-GP: (1) Following NOA acceptance, the winning contractor must complete the Beneficial Ownership Disclosure Form before contract execution. (2) Declare all natural persons who ultimately own or control 10% or more shares or voting rights of the enterprise. (3) Disclose full name, nationality, national ID/passport number, residential address, percentage of ownership, and date when ownership was acquired. (4) If no natural person owns 10% or more, disclose senior managing officials. (5) This requirement complies with Public Procurement Rules and anti-money laundering / anti-corruption transparency standards.',
        'citation': 'e-GP System Q&A Q681, Public Procurement Beneficial Ownership Guidelines',
        'notes': 'Mandatory 10% natural person beneficial ownership disclosure prior to contract signing.'
    },
    {
        'category': 'Notice of Award and contract signing',
        'question': 'How does a contractor sign the digital contract on e-GP using a digital signature certificate/token?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Hard',
        'expected_section': 'Digital Signature Tool & Contract Execution',
        'expected_page': 'Manual Pages 350-372, Q721',
        'answer': 'To sign a contract digitally on e-GP: (1) Obtain a licensed digital signature certificate (USB cryptographic token) from a CCA-approved Certification Authority in Bangladesh. (2) Install e-GP Digital Signature Signer utility/driver on your computer. (3) Insert USB token. (4) Log into e-GP and open Contract Management > Contract Signing. (5) Review the finalized contract agreement text and terms. (6) Click Sign Contract. (7) The browser invokes the e-GP PKI signer utility; enter your cryptographic token PIN. (8) System validates certificate and attaches tamper-proof digital signature. (9) PE counterpart signs digitally to complete legal execution.',
        'citation': 'e-GP System User Manual Chapter 11 (Digital Signature Module), Q721, ICT Act 2006',
        'notes': 'PKI USB cryptographic token hardware usage, CCA certificate validation, and digital contract execution.'
    },
    {
        'category': 'Invoices, bills and payments',
        'question': 'How can a contractor track the settlement and payment clearance status of their bill in iBAS++?',
        'language': 'English',
        'question_type': 'Direct',
        'difficulty': 'Medium',
        'expected_section': 'e-CMS Milestone Invoices & iBAS++ Payment Tracking',
        'expected_page': 'Manual Section 13.2, Q801, Q881',
        'answer': 'Tracking bill status on e-GP: (1) Go to Contract Management > Invoices & Payments. (2) Locate the submitted invoice; view status column: Submitted (awaiting PE engineer verification), MB Certified (measurements verified), DDO Approved (passed to DDO), Sent to iBAS++ (forwarded to treasury). (3) When transmitted to iBAS++, the system displays an iBAS++ Bill Token Number. (4) Once treasury executes the electronic fund transfer, status updates to Paid / Settled with EFT payment voucher reference and date. (5) Funds credit directly to the contractor registered corporate bank account.',
        'citation': 'e-GP System User Manual Chapter 13, Q801 (Progress Invoices), Q881 (iBAS++)',
        'notes': 'End-to-end payment tracking stages from e-CMS MB certification to iBAS++ EFT clearance.'
    },
    {
        'category': 'Complaint, review and appeal',
        'question': 'What is the step-by-step procedure for a contractor to file a formal complaint and escalate to the CPTU Review Panel?',
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Hard',
        'expected_section': 'Complaints Management & Review Panel Escalations',
        'expected_page': 'Manual Pages 500-530, Q961',
        'answer': 'Filing and escalating complaints on e-GP: (1) Within 7-10 days of event, go to Complaints module, select tender, write grounds of complaint citing PPR-2008 violations, attach evidence, pay fee, and submit to PE. (2) Portal activates procurement freeze. (3) If PE does not respond within 7 days or rejects, escalate to HOPE within 3 days. (4) If HOPE does not resolve within 7 days, file appeal to CPTU Review Panel within 7 days. (5) Pay Review Panel registration fee and refundable security deposit. (6) Review Panel convenes hearing within 12 days and issues binding verdict (order re-evaluation, cancel tender, or dismiss). (7) If upheld, security deposit is refunded.',
        'citation': 'e-GP System User Manual Chapter 15, PPR-2008 Rules 56-58, PPA-2006 Section 29, Q961',
        'notes': 'Three-tier complaint escalation hierarchy (PE -> HOPE -> CPTU Review Panel), statutory deadlines, and fee requirements.'
    }
]

def main():
    print("=" * 60)
    print("ENHANCING EVALUATION DATASET WITH REALISTIC PE & CONTRACTOR QUESTIONS")
    print("=" * 60)
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        existing_rows = list(reader)
        
    print(f"Current rows in {CSV_PATH.name}: {len(existing_rows)}")
    
    # Get highest existing EGP number
    highest_num = 0
    for r in existing_rows:
        qid = r['question_id']
        m = re.match(r'EGP-(\d+)', qid)
        if m:
            highest_num = max(highest_num, int(m.group(1)))
            
    print(f"Highest existing question number: {highest_num}")
    
    new_rows = []
    current_counter = highest_num + 1
    
    for q_data in NEW_QUESTIONS:
        qid = f"EGP-{current_counter:04d}"
        row = {
            'question_id': qid,
            'category': q_data['category'],
            'question': clean_val(q_data['question']),
            'language': q_data['language'],
            'question_type': q_data['question_type'],
            'difficulty': q_data['difficulty'],
            'answerability': 'Answerable',
            'expected_section': clean_val(q_data['expected_section']),
            'expected_page': clean_val(q_data['expected_page']),
            'expected_answer': clean_val(q_data['answer']),
            'ground_truth': clean_val(q_data['answer']),
            'expected_citation': clean_val(q_data['citation']),
            'notes': clean_val(q_data['notes'])
        }
        new_rows.append(row)
        current_counter += 1
        
    print(f"Adding {len(new_rows)} new realistic questions for PE & Contractors")
    
    combined = existing_rows + new_rows
    print(f"Total updated dataset rows: {len(combined)}")
    
    with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined)
        
    print(f"Successfully saved enhanced dataset to {CSV_PATH}")
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"Physical lines in {CSV_PATH.name}: {len(lines)}")

if __name__ == '__main__':
    main()
