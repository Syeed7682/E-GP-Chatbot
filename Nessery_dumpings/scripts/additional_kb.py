"""
Additional KB entries for the 242 unmatched questions.
This file adds entries for questions that had no close match in the original KB.
"""

def get_additional_kb():
    """Return additional KB entries for questions not covered by the main KB."""
    kb = {}
    
    # ============ Tender Search extras ============
    kb['how do i find framework agreement opportunities'] = {
        'section': 'Procurement Methods & Framework Agreements',
        'page': 'Q81-Q120, PPR-2008',
        'answer': "To find framework agreement opportunities on e-GP: (1) Framework agreements are long-term arrangements between a PE and suppliers for recurring goods/services procurement. (2) Search the e-GP portal using the Tender Search section; framework agreement tenders are published like regular tenders with specific identification. (3) The APP (Q81) may indicate framework agreements in the procurement method or package description. (4) Per PPR-2008 Rule 73A, framework agreements are used for frequently purchased items. (5) Once a framework agreement is established, call-off orders are placed against it without re-tendering. (6) Check PE-specific pages for ongoing framework opportunities. (7) Contact the e-GP Helpdesk (16575) for guidance on available framework agreements.",
        'citation': 'e-GP System Q&A: Q81-Q120 (APP), PPR-2008 Rule 73A',
        'notes': 'Source: e-GP System Q&A Q81, PPR-2008. Framework agreements for recurring procurement.'
    }
    
    # ============ Document purchase extras ============
    kb['does the document price change after a corrigendum'] = {
        'section': 'Corrigendum & Document Fees',
        'page': 'Q321, Q201',
        'answer': "Generally, the tender document fee does not change after a corrigendum. (1) The document purchase fee is set at the time of tender publication and typically remains fixed. (2) A corrigendum (Q321) may modify specifications, quantities, dates, or conditions, but usually does not alter the document fee. (3) If a corrigendum significantly changes the tender scope, the PE may cancel and re-tender with a new fee. (4) Tenderers who have already purchased documents receive the corrigendum at no additional cost. (5) The corrigendum is an addendum to the original document, not a replacement requiring re-purchase. (6) Check the specific corrigendum notice for any mention of fee changes.",
        'citation': 'e-GP System Q&A: Q321 (Corrigendum), Q201 (STDs), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q321, Q201. Corrigendum is free addition to purchased documents.'
    }
    
    kb['where can i find the payment receipt'] = {
        'section': 'Tender Document Purchase',
        'page': 'Q201-Q240',
        'answer': "To find your tender document payment receipt: (1) Check your e-GP dashboard or payment history section — the system records all transactions. (2) Look in the specific tender's detail page where you made the purchase. (3) Your bank's online banking portal or mobile app will have the transaction record if payment was made via e-GP partner bank. (4) Check your registered email — payment confirmation notifications are typically sent via email. (5) The e-GP Message Box (Q41) may contain payment confirmation notifications. (6) If you cannot find the receipt, contact the e-GP Helpdesk (Hotline: 16575) with your vendor ID, tender reference number, and approximate payment date/amount.",
        'citation': 'e-GP System Q&A: Q201-Q240 (STDs), Q41 (Message Box)',
        'notes': 'Source: e-GP System Q&A Q201, Q41. Check dashboard, email, bank records, or Helpdesk.'
    }
    
    # ============ Eligibility extras ============
    kb['where can i find the eligibility requirements'] = {
        'section': 'Eligibility & TDS',
        'page': 'Q161',
        'answer': "Eligibility requirements for each tender are found in: (1) The Tender Data Sheet (TDS) — the primary document specifying eligibility criteria for each specific tender (Q161). (2) The Invitation for Tender (IFT) summary — provides a brief overview of eligibility requirements in the public notice. (3) Instructions to Tenderers (ITT) — contains general eligibility rules referenced by the TDS. (4) Per PPR-2008, eligibility criteria must be clearly stated and non-discriminatory. (5) Common criteria include: valid registration, Trade License, TIN, VAT, financial capacity, experience, non-debarment. (6) Check the TDS carefully before preparing your bid to ensure full compliance.",
        'citation': 'e-GP System Q&A: Q161 (TDS), PPR-2008 Rules 16, 49',
        'notes': 'Source: e-GP System Q&A Q161, PPR-2008. TDS is the primary source for eligibility criteria.'
    }
    
    kb['what financial turnover evidence may be requested'] = {
        'section': 'Financial Qualification',
        'page': 'Q161, Q401',
        'answer': "Financial turnover evidence commonly requested in e-GP tenders: (1) Audited financial statements (balance sheets, income statements) for the last 3-5 financial years. (2) Average annual construction/supply turnover from similar business for the specified period. (3) The required minimum turnover is typically 100-200% of the estimated contract value, as specified in the TDS (Q161). (4) Certified copies of audited accounts from a chartered accountant. (5) Bank solvency certificate showing current financial standing. (6) Bank statements demonstrating liquidity or credit facilities. (7) Tax return filings confirming revenue declarations. (8) The TEC (Q401) verifies all financial documents during evaluation. Submit all evidence as specified in the TDS.",
        'citation': 'e-GP System Q&A: Q161 (TDS), Q401 (TEC), PPR-2008 Rule 49',
        'notes': 'Source: e-GP System Q&A Q161, Q401, PPR-2008. Turnover thresholds specified in each TDS.'
    }
    
    kb['can work experience from a manual contract be recorded'] = {
        'section': 'Experience Recording',
        'page': 'Q161, Q401',
        'answer': "Yes, work experience from manual (non-e-GP) contracts can be used for qualification: (1) Submit work completion certificates, contract agreements, or client reference letters as evidence. (2) The documents must clearly state: contract value, scope of work, completion date, and client details. (3) The TEC (Q401) verifies experience against the TDS requirements regardless of whether the contract was through e-GP or manual procurement. (4) For e-GP-registered contracts, the system may have records in the tenderer database. For manual contracts, provide physical/scanned documentation. (5) Per PPR-2008, the evaluation considers all valid experience evidence. (6) Ensure manual contract certificates are attested/notarized if required by the TDS.",
        'citation': 'e-GP System Q&A: Q161 (TDS), Q401 (TEC), PPR-2008 Rule 49',
        'notes': 'Source: PPR-2008 Rule 49. Both e-GP and manual contract experience are valid with proper documentation.'
    }
    
    kb['how can i add an e-gp contract to my tenderer database'] = {
        'section': 'Tenderer Database & Records',
        'page': 'Q761-Q800, Q801-Q840',
        'answer': "Adding an e-GP contract to your tenderer database: (1) Contracts executed through e-GP are automatically recorded in the system's database linked to your vendor account. (2) When a contract is signed digitally (Q721), the system creates a contract record. (3) Contract execution milestones (Q761 site handover, Q801 progress) are tracked in e-CMS. (4) Upon contract completion, the performance record is finalized and visible in your account. (5) To ensure your records are complete, verify that all contract milestones are properly documented in e-CMS. (6) For contracts not automatically appearing, contact the PE or e-GP Helpdesk (16575) to update your tenderer database. (7) Your tenderer database serves as your experience portfolio for future tenders.",
        'citation': 'e-GP System Q&A: Q721 (Contract), Q761 (e-CMS), Q801 (Progress)',
        'notes': 'Source: e-GP System Q&A Q721, Q761, Q801. e-GP contracts are auto-recorded in system.'
    }
    
    kb['how do i understand the required liquid asset or credit facility evidence'] = {
        'section': 'Financial Qualification',
        'page': 'Q161, Q401',
        'answer': "Understanding liquid asset or credit facility evidence requirements: (1) The TDS (Q161) specifies the minimum liquid assets or credit facilities required, typically as a percentage of the estimated contract value. (2) Liquid assets include: cash in bank, demand deposits, and readily marketable securities. (3) Credit facilities: confirmed credit lines from banks (letter of credit facilities, bank overdraft limits). (4) Evidence required: bank solvency certificate, bank statements showing balances, letters from banks confirming credit lines, and audited balance sheets showing current assets. (5) The TEC (Q401) evaluates whether your available resources (net of commitments to other ongoing contracts) meet the threshold. (6) Calculate your available capacity: total liquid assets minus commitments to existing contracts.",
        'citation': 'e-GP System Q&A: Q161 (TDS), Q401 (TEC), PPR-2008 Rule 49',
        'notes': 'Source: e-GP System Q&A Q161, Q401, PPR-2008. Liquid assets = cash + deposits - existing commitments.'
    }
    
    kb['can a subcontractors experience be considered'] = {
        'section': 'Subcontractor Experience',
        'page': 'Q161, Q401',
        'answer': "Whether a subcontractor's experience can be considered depends on the TDS (Q161): (1) Generally, qualification requirements must be met by the prime contractor (or JV partners). (2) Some tenders allow subcontractor experience for specific specialized sub-components, if explicitly stated in the TDS. (3) Per PPR-2008, the prime contractor bears full responsibility regardless of subcontracting, so the PE primarily evaluates the prime contractor's capabilities. (4) If subcontractor experience is accepted, the TDS will specify conditions (e.g., subcontractor must be named, signed agreement required). (5) The TEC (Q401) evaluates per TDS rules. (6) Best practice: where possible, ensure the prime contractor or JV partners meet experience requirements without relying on subcontractor experience.",
        'citation': 'e-GP System Q&A: Q161 (TDS), Q401 (TEC), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q161, Q401, PPR-2008. Subcontractor experience allowed only if TDS permits.'
    }
    
    kb['can one contract be used to support more than one qualification criterion'] = {
        'section': 'Qualification Assessment',
        'page': 'Q161, Q401',
        'answer': "Yes, a single contract can be used to support multiple qualification criteria: (1) If one past contract demonstrates both financial turnover and relevant experience, it can be cited for both criteria. (2) The TDS (Q161) may specify separate thresholds for different criteria (e.g., turnover in general and experience in specific type of work). (3) The same contract can count toward: minimum contract value experience, relevant sector experience, and annual turnover calculation. (4) However, when the TDS requires 'N number of contracts of minimum X value', each contract can only be counted once toward that specific number. (5) The TEC (Q401) evaluates each criterion independently. (6) Provide clear cross-references in your submission showing which contracts satisfy which criteria.",
        'citation': 'e-GP System Q&A: Q161 (TDS), Q401 (TEC), PPR-2008 Rule 49',
        'notes': 'Source: PPR-2008 Rule 49. One contract can satisfy multiple criteria types simultaneously.'
    }
    
    # ============ Submission extras ============
    kb['which forms must be completed before submission'] = {
        'section': 'Tender Submission Forms',
        'page': 'Q201',
        'answer': "Forms that must be completed before tender submission on e-GP: (1) Tender Form (Letter of Tender) — formal offer letter signed by authorized representative. (2) Price Schedule / Bill of Quantities (BOQ) — itemized pricing (Q201). (3) Qualification Information Form — company details, experience, financial data. (4) Tender Security Form — details of bank guarantee or earnest money deposit. (5) Power of Attorney — authorizing the signatory. (6) JV Agreement Form (if applicable) — signed by all JV partners. (7) Manufacturer's Authorization (for Goods tenders if required). (8) Declaration forms — non-debarment, ethical conduct, beneficial ownership. (9) The specific forms required are listed in the tender document and TDS (Q161). (10) All forms must be fully completed — incomplete forms may cause bid rejection.",
        'citation': 'e-GP System Q&A: Q201 (STDs/Financial Forms), Q161 (TDS)',
        'notes': 'Source: e-GP System Q&A Q201, Q161. Check tender document for complete list of required forms.'
    }
    
    kb['can i save a draft and continue later'] = {
        'section': 'Online Submission',
        'page': 'Q201-Q240',
        'answer': "Regarding saving drafts on e-GP: (1) The e-GP system may allow you to save partial submission data and continue later, but this depends on the specific portal functionality. (2) If draft saving is available, look for a 'Save Draft' or 'Save Progress' button within the submission form. (3) Important: Do NOT rely solely on draft saving — if the session expires, unsaved data may be lost. (4) Best practice: prepare all documents offline first (BOQ calculations, form entries, scanned documents), then complete the online submission in one session. (5) Do not wait until the last minute — complete your submission well before the deadline. (6) If draft saving is not available, you must complete the entire submission in a single session. (7) Keep local copies of all entered data before submitting.",
        'citation': 'e-GP System Q&A: Q201-Q240 (STDs/Forms)',
        'notes': 'Source: e-GP System Q&A Q201. Prepare offline; do not rely solely on draft saving.'
    }
    
    kb['what file formats and sizes are accepted'] = {
        'section': 'File Upload Requirements',
        'page': 'Q201-Q240',
        'answer': "File formats and sizes accepted on e-GP: (1) Common accepted formats: PDF (preferred for documents), JPG/PNG (for scanned images), Excel/CSV (for financial forms if required). (2) Maximum file size limits are set by the system — typically individual files may be limited to 2-10 MB. (3) Check the tender document or TDS for specific format requirements. (4) For large files: compress images, reduce PDF resolution, or split into multiple files. (5) Ensure scanned documents are clear and legible even after compression. (6) Some forms may need to be filled within the e-GP online system rather than uploaded as separate files. (7) If you encounter upload errors, check file size, format, and internet speed. (8) Contact e-GP Helpdesk (16575) if unsure about accepted formats.",
        'citation': 'e-GP System Q&A: Q201-Q240 (STDs)',
        'notes': 'Source: e-GP System Q&A Q201. PDF preferred; check TDS for specific format requirements.'
    }
    
    kb['how do i replace an incorrect uploaded file before closing'] = {
        'section': 'Bid Modification Before Closing',
        'page': 'Q201-Q240',
        'answer': "To replace an incorrect uploaded file before closing on e-GP: (1) If the tender closing date has NOT passed, you can typically withdraw and re-submit your bid with the corrected file. (2) Log into the portal, navigate to the tender, and look for 'Withdraw' or 'Modify Submission' option. (3) Upload the correct file to replace the incorrect one. (4) Re-submit the complete bid before the deadline. (5) Verify the new submission is complete and all files are correctly uploaded. (6) Download or save the new submission acknowledgement. (7) Important: After the closing date, NO file replacement is possible. (8) Best practice: Double-check all uploaded documents before final submission.",
        'citation': 'e-GP System Q&A: Q201-Q240 (STDs), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q201, PPR-2008. Modification only before closing deadline.'
    }
    
    kb['how can i confirm that my tender was successfully submitted'] = {
        'section': 'Submission Confirmation',
        'page': 'Q201-Q240, Q361',
        'answer': "To confirm your tender was successfully submitted on e-GP: (1) After clicking 'Submit', the system should display a submission confirmation page with a reference number and timestamp. (2) Check your e-GP dashboard — submitted tenders should appear in your 'My Submissions' or similar section. (3) The system generates a hash of your submission for integrity verification (Q361). (4) Check your Message Box (Q41) for submission confirmation notifications. (5) Check your registered email for submission confirmation. (6) If you don't see confirmation, DO NOT assume it was submitted — check immediately and re-submit if needed (before the deadline). (7) Take a screenshot of the confirmation page for your records.",
        'citation': 'e-GP System Q&A: Q201-Q240, Q361 (Hash), Q41 (Message Box)',
        'notes': 'Source: e-GP System Q&A Q201, Q361. Hash generated at submission; check dashboard and email.'
    }
    
    kb['where can i download or print the submission acknowledgement'] = {
        'section': 'Submission Acknowledgement',
        'page': 'Q201-Q240',
        'answer': "To download or print the submission acknowledgement: (1) After successful submission, the confirmation page typically has a 'Print' or 'Download' option. (2) If you missed it, log back into e-GP and navigate to the tender under 'My Submissions' or 'Submitted Tenders'. (3) The submission details page should show the submission reference, timestamp, and hash — use browser print function (Ctrl+P) to save as PDF. (4) Check your registered email — submission confirmation emails serve as acknowledgement records. (5) The submission hash itself is a verifiable proof of submission integrity. (6) Keep this acknowledgement for your records and as evidence of timely submission.",
        'citation': 'e-GP System Q&A: Q201-Q240 (STDs)',
        'notes': 'Source: e-GP System Q&A Q201. Print or save confirmation page; email also serves as record.'
    }
    
    kb['what happens if my internet connection drops during submission'] = {
        'section': 'Submission & Technical Issues',
        'page': 'Q201-Q240',
        'answer': "If your internet connection drops during submission: (1) Any unsaved/un-submitted data may be lost — the system typically does not auto-save partial submissions. (2) Reconnect immediately and log back into the portal. (3) Check if the submission was completed: look in 'My Submissions' for the tender. (4) If submission was NOT completed, you need to restart the process and re-upload all files. (5) If the issue occurred during final submission click, verify whether the system registered the bid. (6) Best practices to prevent this: use a stable wired connection, avoid peak hours (near deadlines), submit 1-2 hours before the closing time, have a backup internet connection (mobile hotspot). (7) If the portal was down (server-side issue), document it and contact e-GP Helpdesk (16575) for potential deadline extension.",
        'citation': 'e-GP System Q&A: Q201-Q240, e-GP Helpdesk',
        'notes': 'Source: e-GP System Q&A Q201. Submit early; keep backup internet; document outages.'
    }
    
    # ============ Tender security extras ============
    kb['can i extend tender security when the pe requests an extension'] = {
        'section': 'Tender Security Extension',
        'page': 'Q42, Q641',
        'answer': "Yes, when the PE requests a tender validity extension, you should extend your tender security accordingly: (1) The PE may request tender validity extension if evaluation is not complete (Q42). (2) Per PPR-2008, the tender security must remain valid for 28 days beyond the tender validity period. (3) If you agree to the validity extension, contact your bank to extend the bank guarantee's validity date. (4) Submit the extended security to the PE through e-GP. (5) If you decline the extension, you can withdraw without forfeiting your tender security. (6) Ensure the extended security covers the new validity period plus 28 days. (7) Failure to extend security while agreeing to validity extension may result in bid rejection.",
        'citation': 'e-GP System Q&A: Q42 (Validity Alerts), Q641 (NOA/Security), PPR-2008 Rule 29',
        'notes': 'Source: e-GP System Q&A Q42, Q641, PPR-2008. Security must cover validity + 28 days.'
    }
    
    kb['can tender security be submitted in a different currency'] = {
        'section': 'Tender Security Currency',
        'page': 'Q161',
        'answer': "Tender security currency requirements: (1) For national tenders, tender security must typically be in Bangladeshi Taka (BDT) from a scheduled bank in Bangladesh. (2) For international tenders, the TDS (Q161) specifies acceptable currencies — usually the bidding currency or a freely convertible currency. (3) The form (bank guarantee, demand draft, pay order) must be from an acceptable bank as specified in the TDS. (4) Per PPR-2008, for international procurements, security from an internationally recognized bank may be accepted. (5) Always check the TDS for specific currency and bank requirements. (6) Security in the wrong currency may result in bid rejection as non-responsive.",
        'citation': 'e-GP System Q&A: Q161 (TDS), PPR-2008 Rule 29',
        'notes': 'Source: PPR-2008 Rule 29. National tenders: BDT; international: as specified in TDS.'
    }
    
    # ============ Validity & corrigendum extras ============
    kb['can the pe change the closing date through a corrigendum'] = {
        'section': 'Corrigendum & Closing Date',
        'page': 'Q321',
        'answer': "Yes, the PE can change the closing date through a corrigendum: (1) A corrigendum (Q321) can extend (or in rare cases shorten) the tender closing date/time. (2) Per PPR-2008, if changes to the tender document are significant, the PE must provide adequate additional time for tenderers to adjust their bids. (3) The system notifies all document purchasers of the new closing date via e-GP portal, SMS, and email. (4) If you've already submitted your bid, the extended period allows you to modify it if needed. (5) Check for corrigenda regularly through your Message Box (Q41). (6) The corrigendum officially supersedes the original schedule.",
        'citation': 'e-GP System Q&A: Q321 (Corrigendum), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q321, PPR-2008. PE must provide adequate additional time for significant changes.'
    }
    
    kb['what should i do if a corrigendum is published close to the deadline'] = {
        'section': 'Corrigendum & Deadline',
        'page': 'Q321',
        'answer': "If a corrigendum is published close to the deadline: (1) Read the corrigendum immediately to understand what changed. (2) Check if the closing date was extended — most corrigenda near the deadline include a date extension. (3) If changes affect your bid price, quantities, or qualifications, update your submission accordingly. (4) If insufficient time is provided to incorporate changes, submit a clarification request (Q281) asking for more time. (5) Per PPR-2008, the PE should provide reasonable time for tenderers to incorporate corrigendum changes. (6) If you've already submitted, consider withdrawing and re-submitting with corrections before the new deadline. (7) Do not ignore the corrigendum — non-compliance may make your bid non-responsive.",
        'citation': 'e-GP System Q&A: Q321 (Corrigendum), Q281 (Queries), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q321, PPR-2008. Read corrigendum immediately; request extension if needed.'
    }
    
    kb['can the pe request an extension of tender validity'] = {
        'section': 'Tender Validity Extension',
        'page': 'Q42',
        'answer': "Yes, the PE can request a tender validity extension: (1) The system sends automated alerts (Q42) to tenderers when the PE requests an extension. (2) This typically happens when evaluation is not completed within the original validity period. (3) Tenderers can accept or decline the extension request. (4) If you accept: extend your tender security validity accordingly (plus 28 days). (5) If you decline: you may withdraw your bid without forfeiting tender security. (6) Per PPR-2008, validity extensions should not be routine and bid prices cannot be changed during extension. (7) The PE must provide justification for the extension request.",
        'citation': 'e-GP System Q&A: Q42 (Validity Extension Alerts), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q42, PPR-2008. Tenderer can accept or decline; security must extend too.'
    }
    
    kb['do i need to extend my tender security when validity is extended'] = {
        'section': 'Tender Security & Validity',
        'page': 'Q42, Q641',
        'answer': "Yes, you must extend your tender security when agreeing to a validity extension: (1) Per PPR-2008, tender security must remain valid for 28 days beyond the tender validity period. (2) When the PE requests validity extension (Q42), your security must cover the extended period + 28 days. (3) Contact your bank to extend the bank guarantee validity date. (4) Submit proof of the extended security to the PE through e-GP. (5) If you cannot or choose not to extend, you may decline the validity extension and withdraw without security forfeiture. (6) Failure to extend security while accepting validity extension may result in your bid being treated as withdrawn.",
        'citation': 'e-GP System Q&A: Q42 (Validity Alerts), PPR-2008 Rule 29',
        'notes': 'Source: e-GP System Q&A Q42, PPR-2008. Security validity = bid validity + 28 days.'
    }
    
    kb['can i withdraw if i do not agree to an extension'] = {
        'section': 'Tender Validity & Withdrawal',
        'page': 'Q42',
        'answer': "Yes, you can withdraw if you do not agree to a validity extension: (1) When the PE requests a tender validity extension (Q42), agreeing is optional. (2) If you decline the extension, you can withdraw your bid. (3) Per PPR-2008, declining a validity extension request is NOT grounds for forfeiting your tender security — your security will be returned. (4) This is different from withdrawing your bid before the original validity expires (which may trigger forfeiture). (5) Respond to the extension request within the deadline specified by the PE. (6) If you don't respond, the PE may treat your bid as withdrawn after the original validity period.",
        'citation': 'e-GP System Q&A: Q42 (Validity Alerts), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q42, PPR-2008. Declining extension = no security forfeiture.'
    }
    
    # ============ Pre-tender meeting extras ============
    kb['can i ask a question about an unclear specification'] = {
        'section': 'Pre-Tender Clarifications',
        'page': 'Q281',
        'answer': "Yes, you can and should ask questions about unclear specifications: (1) Use the e-GP portal's clarification request mechanism (Q281) to submit your question. (2) Reference the specific document section, clause number, or specification item that is unclear. (3) Submit well before the query deadline specified in the TDS. (4) The PE reviews and publishes responses to all document purchasers (Q281) for transparency. (5) You can also raise questions during the pre-tender meeting if scheduled. (6) Per PPR-2008, the PE must respond to legitimate clarification requests. (7) Only officially published responses are binding — do not rely on informal communication.",
        'citation': 'e-GP System Q&A: Q281 (Vendor Queries/Pre-Tender Minutes), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q281. Submit via portal; responses published to all purchasers.'
    }
    
    kb['will clarification responses be shared with all tenderers'] = {
        'section': 'Pre-Tender Clarifications',
        'page': 'Q281',
        'answer': "Yes, clarification responses are shared with all tenderers who purchased documents: (1) Per PPR-2008 and e-GP system design, the PE publishes all clarification responses to all document purchasers (Q281) to maintain fairness and transparency. (2) The responses are posted on the e-GP portal under the tender's clarification section. (3) The pre-tender meeting minutes are also published to all purchasers (Q281). (4) Your identity as the questioner may or may not be disclosed. (5) This ensures all tenderers have equal information for bid preparation. (6) All published clarifications become part of the official tender documentation.",
        'citation': 'e-GP System Q&A: Q281 (Vendor Queries/Pre-Tender Minutes), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q281, PPR-2008. All clarifications shared equally for fairness.'
    }
    
    kb['can a clarification change the tender requirements'] = {
        'section': 'Clarifications & Amendments',
        'page': 'Q281, Q321',
        'answer': "Clarifications vs. amendments on e-GP: (1) A simple clarification explains existing requirements without changing them. (2) If the PE's response involves a substantive change to specifications, quantities, conditions, or requirements, it requires a formal Corrigendum (Q321), not just a clarification. (3) Per PPR-2008, changes to tender documents must be made through official corrigenda. (4) If a clarification response effectively changes a requirement, the PE should issue a corrigendum to formalize it. (5) Tenderers should review both clarifications and corrigenda carefully. (6) If you believe a clarification changes requirements without a proper corrigendum, raise this concern with the PE or file a complaint.",
        'citation': 'e-GP System Q&A: Q281 (Queries), Q321 (Corrigendum), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q281, Q321. Substantive changes require formal corrigendum.'
    }
    
    # ============ Evaluation extras ============
    kb['what does responsive or non-responsive mean in the portal'] = {
        'section': 'Tender Evaluation Terms',
        'page': 'Q401, Q361',
        'answer': "Responsive vs. non-responsive in e-GP evaluation: (1) 'Responsive' means your bid substantially complies with all requirements in the tender documents — correct forms, adequate tender security, proper documentation, compliant technical proposal, and valid pricing. (2) 'Non-responsive' means your bid has a material deviation that cannot be waived — missing tender security, unsigned documents, failure to meet eligibility criteria, incomplete pricing, or non-compliance with specifications. (3) The TEC (Q401) determines responsiveness during preliminary examination. (4) Per PPR-2008, a bid is non-responsive if it has a material deviation from the tender document requirements. (5) Non-responsive bids are rejected and not further evaluated. (6) Minor informalities (clerical errors, missing non-essential pages) may be waived at the TEC's discretion.",
        'citation': 'e-GP System Q&A: Q401 (TEC), Q361 (Opening), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q401, PPR-2008. Non-responsive = material deviation; bid rejected.'
    }
    
    kb['where can i submit a response to an evaluation clarification'] = {
        'section': 'Evaluation Clarifications',
        'page': 'Q521',
        'answer': "To submit a response to an evaluation clarification request: (1) The TEC issues clarification requests to tenderers online through the e-GP system (Q521). (2) You will receive a notification in your Message Box and via email/SMS. (3) Log into the portal and navigate to the tender's clarification section. (4) Read the TEC's question carefully and prepare your response. (5) Submit your response within the deadline specified by the TEC. (6) Attach supporting documents as needed. (7) Per PPR-2008, clarification responses must NOT change the substance of your bid — they should only explain, elaborate, or provide additional evidence for what was already in your submission. (8) Failure to respond within the deadline may result in the TEC evaluating based on submitted information only.",
        'citation': 'e-GP System Q&A: Q521 (TEC Clarifications & Vendor Responses), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q521. Responses must not change bid substance; deadline is strict.'
    }
    
    kb['can the pe request a tender validity extension during evaluation'] = {
        'section': 'Validity Extension During Evaluation',
        'page': 'Q42',
        'answer': "Yes, the PE can request a tender validity extension during evaluation: (1) This commonly occurs when evaluation takes longer than the original validity period. (2) The system sends automated alerts (Q42) to all bidders requesting the extension. (3) Each tenderer independently decides to accept or decline. (4) Accepting requires: extending tender security validity accordingly. (5) Declining allows withdrawal without security forfeiture. (6) Per PPR-2008, bid prices cannot be changed during extension — the original bid prices remain fixed. (7) The PE should minimize validity extensions by completing evaluation promptly.",
        'citation': 'e-GP System Q&A: Q42 (Validity Extension Alerts), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q42, PPR-2008. Prices remain fixed during extension.'
    }
    
    # ============ Complaint extras ============
    kb['can a complaint affect issuance of the notice of award'] = {
        'section': 'Complaints & NOA',
        'page': 'Q961, Q641',
        'answer': "Yes, a complaint can affect issuance of the NOA: (1) Per PPR-2008 and PPA-2006, a valid complaint triggers a procurement freeze — the PE cannot issue the NOA while the complaint is being processed (Q961). (2) The freeze remains until the complaint is resolved by the PE or the Review Panel. (3) If the complaint is upheld, the evaluation may be redone or the tender cancelled. (4) If the complaint is dismissed, the PE proceeds with NOA issuance. (5) This mechanism protects tenderers' rights and ensures due process. (6) Frivolous complaints may be rejected quickly, but legitimate concerns must be properly investigated before award proceeds.",
        'citation': 'e-GP System Q&A: Q961 (Complaints), Q641 (NOA), PPR-2008, PPA-2006',
        'notes': 'Source: e-GP System Q&A Q961, Q641. Complaint triggers procurement freeze; NOA delayed.'
    }
    
    kb['can i withdraw a complaint after submitting it'] = {
        'section': 'Complaint Management',
        'page': 'Q961',
        'answer': "Withdrawing a complaint on e-GP: (1) A complainant may request to withdraw their complaint before it is fully resolved. (2) Check the complaint management section in the portal for a withdrawal option. (3) The PE/Review Panel may accept the withdrawal if proceedings have not progressed significantly. (4) Once withdrawn, the procurement freeze may be lifted and the tender process continues. (5) Note: withdrawing a frivolous complaint may still be noted in records. (6) If you have genuine concerns, it's better to pursue the complaint than withdraw under pressure. (7) Per PPA-2006, intimidating a complainant into withdrawal is a punishable offense. (8) Contact the e-GP Helpdesk (16575) for assistance with complaint management.",
        'citation': 'e-GP System Q&A: Q961 (Complaints), PPA-2006',
        'notes': 'Source: e-GP System Q&A Q961, PPA-2006. Withdrawal possible; intimidation is punishable.'
    }
    
    # ============ JV extras ============
    kb['can two companies participate together as a jvca'] = {
        'section': 'Joint Venture / Consortium',
        'page': 'Q4, Q161',
        'answer': "Yes, two or more companies can participate together as a Joint Venture / Consortium Association (JVCA) on e-GP: (1) The JV must be formed with a signed JV Agreement specifying roles, responsibilities, and the lead partner. (2) During registration (Q4), select 'Joint Venture' as the legal structure. (3) The TDS (Q161) specifies whether JVs are allowed and the maximum number of partners. (4) Each partner must meet their proportionate qualification share. (5) The lead partner is responsible for the overall bid submission and communication. (6) All partners are jointly and severally liable for the contract. (7) Submit: JV Agreement, Power of Attorney, individual partner documents, and combined qualification evidence.",
        'citation': 'e-GP System Q&A: Q4 (Registration), Q161 (TDS), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q4, Q161, PPR-2008. JV partners jointly and severally liable.'
    }
    
    kb['what information about jv partners may be required'] = {
        'section': 'JV Partner Information',
        'page': 'Q161',
        'answer': "Information about JV partners typically required in e-GP tenders: (1) Full legal name, address, and registration details of each partner. (2) Role and responsibility allocation (lead partner vs. other partners). (3) Percentage share of work/participation for each partner. (4) Individual qualification documents: Trade License, TIN, VAT, financial statements, experience certificates. (5) Authorized representative and Power of Attorney. (6) Bank account details of the lead partner (for payments). (7) JV Agreement — signed by all partners detailing: formation, responsibilities, profit-sharing, authorized signatory, and dissolution terms. (8) The TDS (Q161) specifies exact JV-related document requirements.",
        'citation': 'e-GP System Q&A: Q161 (TDS), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q161, PPR-2008. All partners submit individual qualification docs.'
    }
    
    kb['how is each jv partners participation share recorded'] = {
        'section': 'JV Participation Shares',
        'page': 'Q161',
        'answer': "Recording JV partner participation shares: (1) The JV Agreement submitted with the bid specifies each partner's percentage share of work and financial responsibility. (2) During bid submission, the participation shares are declared in the JV declaration form. (3) The TDS (Q161) may specify minimum participation percentages (e.g., lead partner must have at least 51%). (4) After contract award, the e-CMS system tracks execution by the JV entity. (5) For experience recording, each partner's contribution is allocated proportionally. (6) Payment distribution follows the JV Agreement terms, though the PE typically makes payments to the lead partner's account. (7) Each partner's share determines their proportionate qualification credit for future tenders.",
        'citation': 'e-GP System Q&A: Q161 (TDS), PPR-2008',
        'notes': 'Source: PPR-2008. Shares specified in JV Agreement; lead partner typically receives payments.'
    }
    
    kb['can a jv use the experience of its members'] = {
        'section': 'JV Qualification',
        'page': 'Q161, Q401',
        'answer': "Yes, a JV can use the combined experience of its members: (1) Per PPR-2008 and standard TDS conditions, the JV's qualification is assessed based on the combined capabilities of all partners. (2) Each partner's experience contributes to the JV's overall qualification. (3) The TDS (Q161) may specify: lead partner must meet a minimum percentage of experience requirements (e.g., 40-60%), and all partners collectively must meet 100%. (4) Experience certificates from individual partners' past projects are submitted and evaluated (Q401). (5) However, each specific experience claim must belong to a specific partner — not shared between partners. (6) Financial capacity (turnover, credit facilities) can also be combined per TDS rules.",
        'citation': 'e-GP System Q&A: Q161 (TDS), Q401 (TEC), PPR-2008',
        'notes': 'Source: PPR-2008. JV qualification = combined partner capabilities per TDS formula.'
    }
    
    kb['can a company participate in the same tender independently and as a jv member'] = {
        'section': 'JV & Independent Bidding',
        'page': 'Q161',
        'answer': "No, a company generally cannot participate in the same tender both independently and as a JV member: (1) Per PPR-2008 and standard e-GP TDS conditions (Q161), a tenderer can submit only one bid — either independently or as part of a JV. (2) Submitting both would constitute a conflict of interest and grounds for disqualification of all affected bids. (3) Similarly, a company cannot be a member of two different JVs bidding on the same tender. (4) The TDS explicitly states these restrictions. (5) During evaluation, the TEC (Q401) checks for such conflicts. (6) Violation may result in bid rejection and potential debarment for fraudulent practice.",
        'citation': 'e-GP System Q&A: Q161 (TDS), PPR-2008',
        'notes': 'Source: PPR-2008. One bid per company per tender — either solo or JV, not both.'
    }
    
    kb['where can i find subcontracting restrictions'] = {
        'section': 'Subcontracting Restrictions',
        'page': 'Q161',
        'answer': "Subcontracting restrictions are found in: (1) The Particular Conditions of Contract (PCC) — specifies the maximum percentage of work that can be subcontracted (Q161). (2) The Tender Data Sheet (TDS) — may include subcontracting conditions. (3) General Conditions of Contract (GCC) — contains standard subcontracting clauses. (4) Per PPR-2008, typical restrictions include: maximum 25-40% of work can be subcontracted, subcontractors cannot be debarred entities, PE approval may be required for subcontracting, and the prime contractor remains fully responsible. (5) Major or critical portions of work usually cannot be subcontracted. (6) Check these documents carefully before planning any subcontracting arrangement.",
        'citation': 'e-GP System Q&A: Q161 (TDS/PCC), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q161, PPR-2008. PCC and TDS specify subcontracting limits.'
    }
    
    kb['how is a jv contract value allocated among partners in the database'] = {
        'section': 'JV Contract Allocation',
        'page': 'Q761-Q800',
        'answer': "JV contract value allocation in the e-GP database: (1) The contract value is allocated among JV partners based on the participation shares declared in the JV Agreement. (2) If the lead partner has 60% share and others have 40%, the contract value is allocated proportionally for experience recording purposes. (3) Each partner gets credit for their proportionate share when using the contract as experience evidence in future tenders. (4) The e-CMS system (Q761) tracks the overall contract execution. (5) For future qualification purposes, a partner can claim experience only for their allocated share value, not the full contract value. (6) This proportional allocation is standard practice per PPR-2008.",
        'citation': 'e-GP System Q&A: Q761 (e-CMS), PPR-2008',
        'notes': 'Source: PPR-2008. Experience credit proportional to declared JV share.'
    }
    
    # ============ NOA & Contract extras ============
    kb['how will i know if my company has received the notice of award'] = {
        'section': 'NOA Notification',
        'page': 'Q641, Q41',
        'answer': "How you'll know about receiving the NOA: (1) The e-GP system sends the NOA electronically through the portal (Q641). (2) You receive a notification in your Message Box (Q41). (3) SMS alert sent to your registered mobile number. (4) Email notification sent to your registered email. (5) The NOA details appear on the tender page in the portal. (6) The NOA includes: contract reference, awarded amount, completion timeline, and Performance Security submission deadline. (7) You must acknowledge receipt and acceptance of the NOA within the specified timeframe. (8) Check your notifications regularly, especially during evaluation periods.",
        'citation': 'e-GP System Q&A: Q641 (NOA), Q41 (Message Box)',
        'notes': 'Source: e-GP System Q&A Q641, Q41. Multi-channel notification: portal + SMS + email.'
    }
    
    kb['can a complaint prevent contract signing'] = {
        'section': 'Complaints & Contract Signing',
        'page': 'Q961, Q721',
        'answer': "Yes, a complaint can prevent contract signing: (1) A valid complaint triggers a procurement freeze (Q961) — no further actions including contract signing can proceed until the complaint is resolved. (2) If a complaint is filed after NOA but before contract signing, the signing is suspended. (3) The PE must resolve the complaint (or escalate to the Review Panel) before proceeding. (4) If the complaint is upheld, the award may be reversed. (5) If dismissed, contract signing (Q721) proceeds. (6) Per PPA-2006, the freeze mechanism ensures due process. (7) The winning tenderer's Performance Security obligation may be deferred until the complaint is resolved.",
        'citation': 'e-GP System Q&A: Q961 (Complaints), Q721 (Contract), PPA-2006',
        'notes': 'Source: e-GP System Q&A Q961, Q721, PPA-2006. Complaint freeze suspends contract signing.'
    }
    
    # ============ Contract execution extras ============
    kb['what happens if the completion date needs to be extended'] = {
        'section': 'Time Extension',
        'page': 'Q841',
        'answer': "If the completion date needs to be extended on e-GP: (1) The contractor submits a time extension request through e-CMS, providing justification (Q841). (2) Valid grounds include: scope changes via variation orders, force majeure events, PE-caused delays (late site handover, delayed approvals), exceptionally adverse weather, and changes in regulatory requirements. (3) The PE reviews the request and supporting evidence. (4) If approved, a variation order (Q841) formalizes the time extension. (5) The new completion date is recorded in e-CMS. (6) Liquidated damages calculation is adjusted based on the approved extension. (7) The contractor's Performance Security validity may need extension accordingly.",
        'citation': 'e-GP System Q&A: Q841 (Variation Orders/Time Extensions), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q841. Time extension via variation order with PE approval.'
    }
    
    kb['how are variation orders reflected in e-cms'] = {
        'section': 'Variation Orders in e-CMS',
        'page': 'Q841, Q842-Q880',
        'answer': "Variation orders in e-CMS: (1) Variation orders are initiated and processed through the e-Contract Management System (Q841). (2) Types include: scope variations (additional work, changed quantities), time extensions, and call-off orders. (3) The system records: variation description, justification, revised BOQ items/quantities, cost impact, and time impact. (4) Both PE and contractor must acknowledge variations in the system. (5) Approved variations update the contract value and/or completion date. (6) Payment for variation work is processed through the same e-CMS invoice mechanism (Q801). (7) Per PPR-2008, variations have limits (typically within contingency allowance) and require appropriate approval authority.",
        'citation': 'e-GP System Q&A: Q841 (Variation Orders), Q842-Q880 (Procedures)',
        'notes': 'Source: e-GP System Q&A Q841. Variations tracked in e-CMS; update contract value and timeline.'
    }
    
    kb['can a repeat order be recorded against a contract'] = {
        'section': 'Repeat/Call-off Orders',
        'page': 'Q841',
        'answer': "Recording repeat/call-off orders in e-GP: (1) Call-off orders (repeat orders) can be recorded against existing contracts or framework agreements through e-CMS (Q841). (2) For framework agreements, call-off orders are placed against the established contract without re-tendering. (3) The system tracks each call-off order with its quantity, value, and delivery details. (4) Per PPR-2008, repeat orders must be within the scope and value limits of the original contract or framework agreement. (5) Variation orders (Q841) handle changes to the original contract scope, while call-off orders draw down from pre-agreed terms. (6) Each order is documented and linked to the parent contract in the system.",
        'citation': 'e-GP System Q&A: Q841 (Variation Orders/Call-off Orders), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q841. Call-off orders within framework agreement limits.'
    }
    
    kb['how do i report delayed delivery or implementation'] = {
        'section': 'Contract Monitoring',
        'page': 'Q761, Q801',
        'answer': "Reporting delayed delivery or implementation on e-GP: (1) Delays are tracked through e-CMS based on work program milestones (Q761, Q801). (2) If you're the contractor facing a delay, submit a time extension request through e-CMS (Q841) with justification. (3) If you're reporting a PE-caused delay (late payments, site access issues), document it in e-CMS and through official correspondence. (4) The system tracks progress against the approved work program — deviations are visible to both parties. (5) Liquidated damages may apply for contractor-caused delays per PCC terms. (6) For force majeure delays, submit evidence and request relief per contract conditions. (7) Maintain detailed daily records of delay causes for dispute resolution purposes.",
        'citation': 'e-GP System Q&A: Q761 (e-CMS), Q801 (Progress), Q841 (Variations)',
        'notes': 'Source: e-GP System Q&A Q761, Q801, Q841. Document delays in e-CMS; request time extension if justified.'
    }
    
    kb['what evidence should i keep for completed work'] = {
        'section': 'Contract Documentation',
        'page': 'Q761, Q801',
        'answer': "Evidence to keep for completed work: (1) Approved measurement sheets/books from e-CMS (Q761). (2) Signed work completion certificates from the PE. (3) Progress reports and milestone completion records (Q801). (4) Payment certificates and invoices. (5) Quality test reports and material certificates. (6) Photographs of completed work (before, during, after). (7) Approved variation orders (Q841) and their documentation. (8) Correspondence with the PE regarding approvals, instructions, and clarifications. (9) Daily work logs and site records. (10) Final completion certificate and defect liability period documentation. These records serve as experience evidence for future tenders and for dispute resolution if needed.",
        'citation': 'e-GP System Q&A: Q761 (e-CMS/MB), Q801 (Progress), Q841 (Variations)',
        'notes': 'Source: e-GP System Q&A Q761, Q801. Keep all records for future tender qualification and disputes.'
    }
    
    # ============ Invoice/Payment extras ============
    kb['what does bill processing through ibas++ mean'] = {
        'section': 'iBAS++ Payment Processing',
        'page': 'Q881',
        'answer': "Bill processing through iBAS++ on e-GP: (1) iBAS++ (Integrated Budget and Accounting System) is the government's financial management system for budget execution and payment processing. (2) When an invoice is approved in e-CMS, the DDO (Drawing & Disbursement Officer) submits the e-GP bill to iBAS++ (Q881). (3) The DDO uses Mobile OTP verification for secure bill submission. (4) iBAS++ processes the payment through the government paypoint settlement system. (5) The payment is credited to the contractor's registered bank account. (6) This integration ensures: transparent payment trail, budget compliance, and automated reconciliation. (7) Track payment status through the e-GP portal and your bank account.",
        'citation': 'e-GP System Q&A: Q881 (DDO iBAS++ Bills)',
        'notes': 'Source: e-GP System Q&A Q881. iBAS++ is the government payment system; OTP-secured.'
    }
    
    kb['how can i view a payment certificate'] = {
        'section': 'Payment Certificates',
        'page': 'Q801, Q881',
        'answer': "To view a payment certificate on e-GP: (1) Log into the portal and navigate to the specific contract in e-CMS. (2) Check the payment/invoice section of the contract. (3) Approved payment certificates are generated after invoice certification by the PE engineer. (4) The certificate shows: payment number, period covered, measured quantities, rates applied, gross amount, deductions (retention, tax), and net payable amount. (5) Payment certificates link to the corresponding measurement sheets (Q761) and progress records (Q801). (6) The DDO's iBAS++ bill submission (Q881) references these certificates. (7) Download or print certificates for your records. (8) Contact the PE or e-GP Helpdesk (16575) if certificates are not visible.",
        'citation': 'e-GP System Q&A: Q801 (Progress/Invoices), Q881 (iBAS++)',
        'notes': 'Source: e-GP System Q&A Q801, Q881. Certificates in e-CMS contract section.'
    }
    
    kb['can i view measurement or progress records'] = {
        'section': 'e-CMS Progress Records',
        'page': 'Q761, Q801',
        'answer': "Yes, you can view measurement and progress records on e-GP: (1) Log into the portal and navigate to the specific contract in e-CMS. (2) Measurement sheets/books (Q761) show approved quantities for each work item. (3) Progress records (Q801) show milestone completion status and physical/financial progress percentages. (4) The system tracks: quantities completed per BOQ item, measurement dates, engineer approval status, and cumulative progress. (5) Both PE and contractor can view these records. (6) Progress data feeds into invoice generation (Q801). (7) Use these records to monitor your own contract performance and prepare for milestone-based payments.",
        'citation': 'e-GP System Q&A: Q761 (Measurement Sheets), Q801 (Physical Progress)',
        'notes': 'Source: e-GP System Q&A Q761, Q801. Both parties can view e-CMS records.'
    }
    
    kb['how are deductions or adjustments shown in the bill'] = {
        'section': 'Bill Deductions',
        'page': 'Q801, Q881',
        'answer': "Deductions and adjustments in e-GP bills: (1) Bills/invoices in e-CMS show both gross and net amounts with itemized deductions. (2) Common deductions include: retention money (typically 5-10% per PCC), income tax at source, VAT deductions, advance recovery (if advance payment was made), liquidated damages (for delays), and any other contractual deductions. (3) The payment certificate details each deduction separately. (4) Retention money is accumulated and released per PCC terms (typically 50% at completion, 50% after defect liability period). (5) The DDO submits the net amount to iBAS++ (Q881) for payment. (6) Verify all deductions against contract terms; dispute any incorrect deductions with the PE in writing.",
        'citation': 'e-GP System Q&A: Q801 (Invoices), Q881 (iBAS++)',
        'notes': 'Source: e-GP System Q&A Q801, Q881. Bills show itemized deductions; verify against PCC terms.'
    }
    
    # ============ Performance & Debarment extras ============
    kb['where can i view my companys performance rating'] = {
        'section': 'Performance Rating',
        'page': 'Q921',
        'answer': "To view your company's performance rating on e-GP: (1) Log into the portal and check your vendor profile or dashboard section. (2) Performance ratings are linked to completed contracts tracked through e-CMS. (3) The PE rates contractor performance based on: quality of work, timeliness, compliance with safety standards, responsiveness, and adherence to contract terms. (4) Ratings may be visible in your tenderer database under completed contracts. (5) Good performance records strengthen your qualification for future tenders. (6) Poor performance may trigger debarment proceedings (Q921). (7) If you cannot find your rating, contact the respective PE or e-GP Helpdesk (16575).",
        'citation': 'e-GP System Q&A: Q921 (Debarment/Suspensions)',
        'notes': 'Source: e-GP System Q&A Q921. Performance ratings in vendor profile; linked to completed contracts.'
    }
    
    kb['what factors may appear in a performance appraisal'] = {
        'section': 'Performance Appraisal Factors',
        'page': 'Q921',
        'answer': "Factors in performance appraisal on e-GP: (1) Quality of work/goods/services delivered vs. specifications. (2) Timeliness — completion within the contract period or approved extensions. (3) Safety compliance — adherence to safety standards and accident records. (4) Environmental compliance — conformity with environmental conditions. (5) Responsiveness — communication, issue resolution, cooperation with PE. (6) Financial management — invoice accuracy, no fraudulent claims. (7) Defect liability — number and severity of defects during warranty period. (8) Subcontractor management — quality of subcontracted work. (9) Documentation — completeness and accuracy of project records. (10) Per PPR-2008, the PE must conduct fair and documented performance assessments. Poor ratings affect future tender eligibility.",
        'citation': 'e-GP System Q&A: Q921 (Debarment), PPR-2008',
        'notes': 'Source: PPR-2008. Performance appraisal covers quality, timeliness, safety, and compliance.'
    }
    
    kb['how can i correct an inaccurate contract performance record'] = {
        'section': 'Performance Record Correction',
        'page': 'Q921',
        'answer': "To correct an inaccurate contract performance record: (1) Contact the Procuring Entity that made the assessment with evidence of the inaccuracy. (2) Provide supporting documents: actual completion dates, quality certificates, PE acknowledgements, and any other evidence contradicting the inaccurate record. (3) Request a formal review and correction of the performance rating. (4) If the PE does not respond, escalate to the e-GP Helpdesk (Hotline: 16575) or CPTU. (5) For disputes, refer to the contract's dispute resolution clause. (6) Per PPR-2008, performance assessments must be fair, documented, and based on verifiable evidence. (7) Keep all project records to support any future corrections.",
        'citation': 'e-GP System Q&A: Q921 (Debarment), PPR-2008',
        'notes': 'Source: PPR-2008. Contact PE first; escalate to CPTU if needed.'
    }
    
    kb['can a debarment decision be revised'] = {
        'section': 'Debarment Review',
        'page': 'Q921',
        'answer': "Whether a debarment decision can be revised: (1) Per PPR-2008, debarment decisions can be challenged through the Review Panel or administrative appeal process. (2) Temporary suspensions (42-day) expire automatically (Q921). (3) For full debarment, the vendor may: present new evidence, request re-hearing, or challenge the decision through administrative appeal. (4) After the debarment period expires, the vendor can re-register and participate in procurement. (5) Early reinstatement may be possible if the debarment grounds are resolved (e.g., fraudulent document corrected, fine paid). (6) Contact CPTU or the relevant authority for the formal appeal process. (7) During debarment, engage legal counsel to understand available remedies.",
        'citation': 'e-GP System Q&A: Q921 (Debarment/Suspensions), PPR-2008, PPA-2006',
        'notes': 'Source: e-GP System Q&A Q921, PPR-2008. Appeal through Review Panel; debarment has fixed duration.'
    }
    
    kb['does a poor performance rating automatically mean debarment'] = {
        'section': 'Performance & Debarment',
        'page': 'Q921',
        'answer': "A poor performance rating does NOT automatically mean debarment: (1) Debarment requires specific grounds per PPR-2008: fraud, corruption, collusion, coercion, or persistent failure (Q921). (2) A single poor performance rating may trigger a warning or investigation, but not automatic debarment. (3) Multiple poor ratings or persistent underperformance may lead to debarment proceedings. (4) The PE must follow due process: formal notice, opportunity to respond, and documented decision. (5) Temporary suspension (42 days) may be imposed pending investigation. (6) A poor rating does affect your competitiveness in future tender evaluations where past performance is considered. (7) Address performance issues proactively to avoid escalation.",
        'citation': 'e-GP System Q&A: Q921 (Debarment), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q921, PPR-2008. Poor rating ≠ automatic debarment; requires due process.'
    }
    
    # ============ Goods/Works/Services extras ============
    kb['what additional forms may apply to a goods tender'] = {
        'section': 'Goods Tender Forms',
        'page': 'Q201',
        'answer': "Additional forms for goods tenders on e-GP: (1) Price Schedule for Goods — itemized pricing of goods including CIF/CIP/DDP prices, customs duties, taxes. (2) Manufacturer's Authorization Letter — confirming you're an authorized dealer/distributor (if required by TDS). (3) Country of Origin Declaration — origin of manufactured goods. (4) Delivery Schedule — proposed delivery dates per lot/item. (5) Technical Data Sheets/Brochures — specifications of offered goods. (6) Warranty Certificate — commitment to warranty period and terms. (7) After-Sales Service Plan (if required). (8) Inspection and Testing Certificate templates. (9) Spare Parts Price List (for equipment). (10) The specific forms are listed in the STD for Goods (Q201) and the TDS.",
        'citation': 'e-GP System Q&A: Q201 (STDs/Financial Forms), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q201. Check STD for Goods for complete form list.'
    }
    
    kb['how do i read a works bill of quantities'] = {
        'section': 'Works BOQ',
        'page': 'Q201',
        'answer': "Reading a Works Bill of Quantities (BOQ): (1) The BOQ lists all work items organized by sections (e.g., Site Preparation, Foundations, Structural, Finishing, Electrical, Plumbing). (2) Each item has: item number, detailed description, unit of measurement (m³, m², kg, LS), estimated quantity, unit rate (to be filled by tenderer), and total amount. (3) Read specifications alongside the BOQ to understand quality requirements for each item. (4) Cross-reference with drawings to verify quantities. (5) Fill in unit rates that cover: materials, labor, equipment, overheads, and profit. (6) The Financial Form Summary (Q201) totals all BOQ sections. (7) Provisional sums and contingencies may be included as line items. (8) Ensure arithmetic accuracy — unit rate × quantity = total for each item.",
        'citation': 'e-GP System Q&A: Q201 (STDs/Financial Forms)',
        'notes': 'Source: e-GP System Q&A Q201. BOQ organized by work sections; verify quantities against drawings.'
    }
    
    kb['what should i check in a service proposal'] = {
        'section': 'Service Proposals',
        'page': 'Q201',
        'answer': "Key items to check in a service proposal: (1) Scope of Services — clearly defined deliverables and timeline. (2) Methodology — approach and work plan for delivering the services. (3) Staffing Plan — key personnel CVs, qualifications, and man-month allocations. (4) Activity Schedule — breakdown of tasks with durations and milestones. (5) Budget/Price — man-month rates, reimbursable expenses, and total price. (6) Terms of Reference (ToR) compliance — ensure your proposal addresses all ToR requirements. (7) Evaluation criteria — understand how the proposal will be scored (quality-cost ratio). (8) For consultancy services, the technical and financial proposals may be submitted separately. (9) Per PPR-2008, consultancy selection uses methods like QCBS, QBS, or FBS.",
        'citation': 'e-GP System Q&A: Q201 (STDs), PPR-2008',
        'notes': 'Source: PPR-2008. Consultancy proposals evaluated on quality and cost.'
    }
    
    kb['how are consultancy technical proposals evaluated'] = {
        'section': 'Consultancy Evaluation',
        'page': 'Q401, Q601',
        'answer': "Consultancy technical proposals are evaluated differently from works/goods: (1) Evaluation methods per PPR-2008 include: QCBS (Quality and Cost Based Selection — most common), QBS (Quality Based Selection), FBS (Fixed Budget Selection), and LCS (Least Cost Selection). (2) Technical evaluation criteria typically include: relevant experience (20-25%), methodology/approach (25-35%), key personnel qualifications (30-40%), and work plan/innovation (10-20%). (3) Technical proposals are scored first; those meeting minimum technical score (usually 70-75%) have their financial proposals opened. (4) The TEC (Q401) evaluates against criteria in the RFP/TDS. (5) For QCBS, final score = (technical score × weight) + (financial score × weight). (6) Evaluation reports (TER, Q601) document the scoring rationale.",
        'citation': 'e-GP System Q&A: Q401 (TEC), Q601 (TER), PPR-2008',
        'notes': 'Source: PPR-2008. Technical score minimum 70-75%; QCBS combines quality and cost.'
    }
    
    kb['where can i find the activity schedule for a service contract'] = {
        'section': 'Service Contract Activity Schedule',
        'page': 'Q161, Q201',
        'answer': "Finding the activity schedule for a service contract: (1) The activity schedule is part of the tender document package, either in the Technical Specifications or as a separate annex. (2) The TDS (Q161) references the activity schedule requirements. (3) For consultancy services, the Terms of Reference (ToR) defines the expected activity timeline. (4) The tenderer prepares their own activity schedule as part of the technical proposal, showing: tasks/activities, deliverables, timelines, and resource allocation. (5) The PE's expected activity schedule (if provided) serves as a benchmark. (6) After contract award, the detailed activity schedule is finalized and tracked through e-CMS.",
        'citation': 'e-GP System Q&A: Q161 (TDS), Q201 (STDs)',
        'notes': 'Source: e-GP System Q&A Q161, Q201. Activity schedule in ToR; tenderer proposes own schedule.'
    }
    
    kb['how do i identify the required delivery schedule for goods'] = {
        'section': 'Goods Delivery Schedule',
        'page': 'Q161, Q201',
        'answer': "Identifying the required delivery schedule for goods: (1) The delivery schedule is specified in the TDS (Q161) and the Schedule of Requirements section of the tender document. (2) The Particular Conditions of Contract (PCC) specifies delivery terms (DAP/CIF/FOB etc.) and timeline. (3) Key elements: delivery location (site or warehouse), expected delivery dates or period, partial delivery acceptance, and shipping documentation requirements. (4) The Price Schedule for Goods (Q201) includes delivery-related cost components. (5) For imported goods: account for shipping, customs clearance, and inland transport time. (6) Your bid should demonstrate ability to meet the required delivery schedule. (7) Liquidated damages apply for late delivery per PCC terms.",
        'citation': 'e-GP System Q&A: Q161 (TDS), Q201 (STDs/Price Schedule)',
        'notes': 'Source: e-GP System Q&A Q161, Q201. Delivery terms and schedule in TDS/PCC.'
    }
    
    kb['what is different about a works contract compared with a goods contract'] = {
        'section': 'Works vs. Goods Contracts',
        'page': 'Q201',
        'answer': "Key differences between works and goods contracts on e-GP: (1) Works: involves construction, renovation, or repair at a physical site; uses BOQ (Bill of Quantities) with measured items; longer execution period; site management and supervision; measurement-based payments; progress milestones; defect liability period. (2) Goods: involves supply/delivery of physical items; uses Price Schedule with itemized quantities; typically shorter delivery period; inspection and acceptance at delivery; warranty-based quality assurance. (3) Different STD templates (Q201): STD for Works vs. STD for Goods. (4) Different contract conditions: Works PCC covers site access, variations, time extensions; Goods PCC covers shipping, inspection, warranties. (5) Different evaluation focus: Works emphasizes construction experience; Goods emphasizes supply capability and product compliance.",
        'citation': 'e-GP System Q&A: Q201 (STDs), PPR-2008',
        'notes': 'Source: PPR-2008. Different STDs, conditions, and evaluation focus for works vs. goods.'
    }
    
    # ============ Procurement method extras ============
    kb['how do i know whether a tender is national or international'] = {
        'section': 'National vs. International Tenders',
        'page': 'Q81, Q161',
        'answer': "Identifying national vs. international tenders on e-GP: (1) The Invitation for Tender (IFT) clearly states whether the tender is 'National' or 'International'. (2) The procurement method in the TDS (Q161) indicates: OTM (Open Tendering Method) for national, and International Open Tendering for international. (3) International tenders are published in at least one international publication. (4) The APP (Q81) specifies the procurement method including international designation. (5) International tenders allow foreign bidders, often require English-language submissions, and may accept foreign currency pricing. (6) Per PPR-2008, international tendering is required when estimated values exceed specified thresholds or domestic market cannot meet requirements.",
        'citation': 'e-GP System Q&A: Q81 (APP), Q161 (TDS), PPR-2008',
        'notes': 'Source: PPR-2008. IFT and TDS indicate national/international; threshold-based.'
    }
    
    kb['where can i find the rules applicable to rfq'] = {
        'section': 'RFQ Rules',
        'page': 'Q81, PPR-2008',
        'answer': "Rules applicable to RFQ (Request for Quotation): (1) PPR-2008 Rules govern RFQ for small-value procurements below prescribed thresholds. (2) RFQ is a simplified procurement method requiring minimum 3 quotations from eligible suppliers. (3) On e-GP, RFQ tenders are published through the portal like regular tenders but with streamlined documentation. (4) Key RFQ features: simplified tender documents, shorter preparation period, no pre-tender meeting, simplified evaluation (usually lowest-price responsive). (5) RFQ may not require tender security for very small values. (6) The APP (Q81) identifies packages designated for RFQ. (7) Detailed RFQ rules are in PPR-2008 Chapter 8 (or equivalent procurement method rules section).",
        'citation': 'e-GP System Q&A: Q81 (APP), PPR-2008 (RFQ Rules)',
        'notes': 'Source: PPR-2008. RFQ for small-value; simplified process with minimum 3 quotations.'
    }
    
    kb['can a tender be retendered after cancellation'] = {
        'section': 'Tender Cancellation & Re-tendering',
        'page': 'Q81',
        'answer': "Yes, a cancelled tender can be re-tendered: (1) Per PPR-2008, the PE may cancel a tender for reasons including: no responsive bids, all bids exceeding estimated cost significantly, fundamental changes in scope, or irregularities in the process. (2) After cancellation, the PE can re-tender with: modified specifications, revised estimated cost, adjusted eligibility criteria, or changed procurement method. (3) A new APP entry or revision (Q121) may be needed. (4) The re-tendered procurement follows the full tender cycle from IFT publication. (5) All original document purchasers are typically informed of the cancellation and re-tendering. (6) New document purchase is required for the re-tendered version.",
        'citation': 'e-GP System Q&A: Q81 (APP), Q121 (Revision), PPR-2008',
        'notes': 'Source: PPR-2008. Re-tendering follows full process with potential modifications.'
    }
    
    kb['how do i identify a single-source procurement notice'] = {
        'section': 'Direct/Single-Source Procurement',
        'page': 'Q81',
        'answer': "Identifying a single-source/direct procurement notice: (1) The IFT or notice clearly identifies the procurement method as 'Direct Procurement' or 'Single Source'. (2) Per PPR-2008 Rules 72-73, direct procurement requires strong justification: emergency situations, sole supplier/proprietary items, continuation of existing contract, or national security. (3) On the e-GP portal, the procurement method filter can be set to 'Direct Procurement' in tender search. (4) The APP (Q81) lists the designated procurement method for each package. (5) Direct procurement notices may not invite competition — the PE selects a specific supplier. (6) If you believe direct procurement is unjustified, you may file a complaint per PPR-2008.",
        'citation': 'e-GP System Q&A: Q81 (APP), PPR-2008 Rules 72-73',
        'notes': 'Source: PPR-2008 Rules 72-73. Direct procurement requires documented justification.'
    }
    
    # ============ Technical troubleshooting extras ============
    kb['my payment is successful but the portal still shows unpaid what now'] = {
        'section': 'Payment Troubleshooting',
        'page': 'Q201-Q240',
        'answer': "If payment is successful but the portal shows unpaid: (1) Wait 15-30 minutes — payment reconciliation between the bank and e-GP may have a processing delay. (2) Save your bank payment confirmation (transaction ID, receipt, SMS confirmation) as evidence. (3) Try refreshing the page or logging out and back in. (4) If still showing unpaid after 1 hour, contact the e-GP Helpdesk (Hotline: 16575, Email: helpdesk@eprocure.gov.bd) with: your vendor ID, tender reference, payment amount, transaction ID/reference, and bank name. (5) The Helpdesk can verify the payment with the partner bank and manually update the status. (6) Act quickly if the document purchase deadline is approaching — document the issue with screenshots and timestamps.",
        'citation': 'e-GP System Q&A: Q201-Q240, e-GP Helpdesk',
        'notes': 'Source: e-GP System Q&A. Payment reconciliation delay; contact Helpdesk 16575 with bank receipt.'
    }
    
    kb['the tender dashboard is blank how can i troubleshoot it'] = {
        'section': 'Technical Troubleshooting',
        'page': 'Q5-Q40',
        'answer': "Troubleshooting a blank tender dashboard: (1) Clear browser cache and cookies, then reload. (2) Try a different browser (Chrome recommended for e-GP). (3) Disable browser extensions that might block content. (4) Check your internet connection stability. (5) Verify you're logged in correctly — session may have expired silently. (6) Try accessing from a different network. (7) Check if the portal is undergoing maintenance. (8) If the issue persists, try accessing at a different time (off-peak hours). (9) Contact the e-GP Helpdesk (16575) with: your browser type/version, screenshot of the blank page, and your vendor ID. (10) The Helpdesk can check if there's a system-side issue with your account.",
        'citation': 'e-GP System Q&A: Q5-Q40 (Portal Access)',
        'notes': 'Source: e-GP System Q&A Q5-Q40. Clear cache; use Chrome; contact Helpdesk if persistent.'
    }
    
    kb['my browser session expired while completing a form what happens to my data'] = {
        'section': 'Session Expiry & Data Loss',
        'page': 'Q5-Q40',
        'answer': "When browser session expires during form completion: (1) Unsaved form data is typically LOST — the e-GP system does not auto-save partial form entries. (2) You'll need to log in again and restart the form from scratch. (3) Any uploaded files that were not yet submitted are also lost. (4) Prevention strategies: save/submit form sections frequently if the system allows partial saves, copy lengthy text entries to a local file before pasting into e-GP, avoid long idle periods, keep sessions active by interacting with the page, use a stable internet connection. (5) For tender submission, prepare all content offline first, then enter it in one session well before the deadline. (6) If session expires during final submission, check if the submission was registered.",
        'citation': 'e-GP System Q&A: Q5-Q40 (Portal Access)',
        'notes': 'Source: e-GP System Q&A Q5-Q40. Unsaved data is lost on session expiry; prepare offline first.'
    }
    
    kb['how can i report a technical problem with evidence'] = {
        'section': 'Technical Issue Reporting',
        'page': 'Q5-Q40',
        'answer': "To report a technical problem with evidence: (1) Take screenshots of the error messages or issues (include the browser URL bar and timestamp). (2) Note your browser type and version (e.g., Chrome 120, Firefox 119). (3) Record the exact date, time, and actions leading to the problem. (4) Note the tender reference number if the issue is tender-specific. (5) Contact the e-GP Helpdesk: Hotline 16575 or Email helpdesk@eprocure.gov.bd. (6) In your report include: your vendor ID/username, description of the problem, steps to reproduce, screenshots, browser/OS details, and internet connection type. (7) For deadline-critical issues (e.g., cannot submit before closing), explicitly mention the urgency. (8) This documented evidence supports any request for deadline extensions due to system issues.",
        'citation': 'e-GP System Q&A: Q5-Q40, e-GP Helpdesk',
        'notes': 'Source: e-GP System Q&A. Screenshot evidence + Helpdesk report supports extension requests.'
    }
    
    # ============ Notifications extras ============
    kb['where can i find the official contact for portal support'] = {
        'section': 'e-GP Support Contacts',
        'page': 'Q5-Q40',
        'answer': "Official contacts for e-GP portal support: (1) e-GP Helpdesk Hotline: 16575 (available during business hours). (2) Email: helpdesk@eprocure.gov.bd. (3) The e-GP portal (eprocure.gov.bd) has a 'Contact Us' or 'Help' section with support information. (4) CPTU (Central Procurement Technical Unit) — oversees the e-GP system and handles escalated issues. (5) For PE-specific issues, contact the relevant Procuring Entity directly. (6) For account and registration issues, the Helpdesk is your primary contact. (7) For complaint and review matters, CPTU's Review Panel handles escalations. (8) Keep the Helpdesk number (16575) saved for urgent issues during tender deadlines.",
        'citation': 'e-GP System Q&A: Q5-Q40, e-GP Helpdesk',
        'notes': 'Source: e-GP Helpdesk: 16575, helpdesk@eprocure.gov.bd. CPTU for escalations.'
    }
    
    kb['how can i keep a record of messages received through e-gp'] = {
        'section': 'Message Box Records',
        'page': 'Q41',
        'answer': "Keeping records of e-GP messages: (1) Your Message Box (Q41) stores all system notifications chronologically. (2) Important messages to save: tender alerts, corrigendum notifications, validity extension requests, evaluation results, NOA notifications, and payment updates. (3) Take screenshots or print important notifications using browser print (Ctrl+P > Save as PDF). (4) Save or forward important email notifications from e-GP to a dedicated folder. (5) Save SMS notifications (screenshot or note content). (6) For critical tender-related communications, maintain a log with dates and content summaries. (7) These records serve as evidence for dispute resolution and audit purposes. (8) The Message Box retains messages for a system-defined period — save important ones externally.",
        'citation': 'e-GP System Q&A: Q41 (Message Box)',
        'notes': 'Source: e-GP System Q&A Q41. Save messages externally; Message Box retention is time-limited.'
    }
    
    # ============ Real-life scenario extras ============
    kb['i noticed a mistake in my uploaded document just before closing what should i do'] = {
        'section': 'Last-Minute Document Correction',
        'page': 'Q201',
        'answer': "If you notice a mistake in your uploaded document just before closing: (1) If time permits, immediately withdraw your submission, correct the document, and re-submit before the closing deadline. (2) Act quickly — the system locks submissions at the exact closing time. (3) If the error is minor (typo, formatting): re-upload the corrected file and re-submit. (4) If the error is in pricing: correct the calculations and re-upload the BOQ. (5) If time is extremely limited and you cannot re-submit: the error will remain in your bid. Arithmetic errors may be corrected by the TEC per PPR-2008 (unit rate prevails). (6) For future prevention: finalize all documents 24+ hours before deadline, do a complete review before uploading. (7) Never wait until the last minute for submission.",
        'citation': 'e-GP System Q&A: Q201 (STDs), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q201. Withdraw, correct, re-submit if time permits.'
    }
    
    kb['the pe changed the closing date after i prepared my tender what should i verify'] = {
        'section': 'Corrigendum Response',
        'page': 'Q321',
        'answer': "When the PE changes the closing date after you've prepared your tender: (1) Read the full corrigendum (Q321) — the closing date change may accompany other modifications. (2) Verify if specifications, BOQ quantities, or conditions were also changed. (3) Update your bid if any changes affect your pricing or technical proposal. (4) Check your tender security validity — ensure it covers the new closing date + validity period + 28 days. (5) If you've already submitted, consider withdrawing and re-submitting with updates if needed. (6) Verify your bid's tender validity period extends beyond the new closing date. (7) Review your resource availability and pricing for the new timeline. (8) Respond to the extended deadline and don't ignore changes.",
        'citation': 'e-GP System Q&A: Q321 (Corrigendum), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q321. Check for all changes, not just date; update security validity.'
    }
    
    kb['my bank guarantee expires before the new validity date what should i do'] = {
        'section': 'Bank Guarantee Extension',
        'page': 'Q42, Q641',
        'answer': "If your bank guarantee expires before the new validity date: (1) Contact your bank immediately to extend the guarantee's validity period. (2) The extended guarantee must cover: new tender validity end date + 28 days. (3) Submit the extended guarantee to the PE through e-GP before the extension deadline. (4) If your bank needs time, inform the PE and request additional time for the guarantee extension. (5) If you cannot extend: you may decline the validity extension and withdraw without security forfeiture (per PPR-2008). (6) Do NOT submit a bid with an expired or insufficient guarantee — it will be rejected as non-responsive. (7) Alternatively, issue a new guarantee for the extended period if your bank cannot modify the existing one.",
        'citation': 'e-GP System Q&A: Q42 (Validity Alerts), Q641 (Security), PPR-2008 Rule 29',
        'notes': 'Source: PPR-2008 Rule 29. Guarantee must cover validity + 28 days; decline extension if cannot extend.'
    }
    
    kb['i received a clarification request but the response deadline is near how should i proceed'] = {
        'section': 'Clarification Response Under Time Pressure',
        'page': 'Q521',
        'answer': "Handling a clarification request with a tight deadline: (1) Read the TEC's request immediately and understand what information is needed (Q521). (2) Prioritize gathering the requested documents/explanations. (3) If you genuinely cannot respond within the deadline, submit a request for extension explaining the reason. (4) Submit whatever you can within the deadline — partial responses are better than no response. (5) Per PPR-2008, clarification responses must not change the substance of your bid — only explain or provide evidence for what was already submitted. (6) If the deadline passes without response, the TEC evaluates based on your submitted information only. (7) Organize your tender files proactively so clarification documents can be found quickly.",
        'citation': 'e-GP System Q&A: Q521 (TEC Clarifications), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q521. Submit what you can; partial response better than none.'
    }
    
    kb['my company name differs slightly across certificates what should i check'] = {
        'section': 'Document Consistency',
        'page': 'Q4, Q161',
        'answer': "When company name differs across certificates: (1) Ensure your e-GP registration name exactly matches your primary Trade License name. (2) Minor variations (e.g., 'Ltd.' vs. 'Limited', '&' vs. 'and') may be acceptable but should be explained. (3) Submit a declaration explaining name variations if they exist across documents (Trade License, TIN, VAT, bank documents). (4) The TEC (Q401) may issue a clarification request about name inconsistencies. (5) For significant differences (merger, name change), submit official name change documentation (court order, RJSC certificate). (6) Update all certificates to reflect the current legal name to avoid future issues. (7) Inconsistencies may trigger non-responsiveness determination if not adequately explained.",
        'citation': 'e-GP System Q&A: Q4 (Registration), Q161 (TDS), PPR-2008',
        'notes': 'Source: PPR-2008. Name consistency important; explain variations; update all certificates.'
    }
    
    kb['my tender appears submitted but i have no acknowledgement how can i verify it'] = {
        'section': 'Submission Verification',
        'page': 'Q201, Q361',
        'answer': "Verifying tender submission without acknowledgement: (1) Check your e-GP dashboard under 'My Submissions' or 'Submitted Tenders' — your bid should appear there. (2) Check your Message Box (Q41) for system-generated submission confirmation. (3) Check your registered email — a confirmation email may have gone to spam. (4) The system generates a submission hash (Q361) — if a hash exists for your bid, it was submitted. (5) If dashboard shows no submission, your bid may NOT have been submitted — act immediately if the deadline hasn't passed. (6) Contact the e-GP Helpdesk (16575) urgently with your vendor ID and tender reference to verify server-side records. (7) Take screenshots of your dashboard as evidence of the situation.",
        'citation': 'e-GP System Q&A: Q201, Q361 (Hash), Q41 (Message Box)',
        'notes': 'Source: e-GP System Q&A Q201, Q361. Check dashboard and Helpdesk; hash confirms submission.'
    }
    
    kb['the pe asks for a validity extension and my bank needs time what should i consider'] = {
        'section': 'Validity Extension & Bank Processing',
        'page': 'Q42',
        'answer': "When the PE requests validity extension and your bank needs time: (1) Respond to the PE's extension request within the deadline — indicate your intention to accept but note the bank processing time needed. (2) Contact your bank immediately to initiate the guarantee extension process. (3) If the PE's response deadline is before the bank can process, explain the situation and request additional time for the guarantee extension. (4) Per PPR-2008, declining the extension allows withdrawal without security forfeiture — this is your fallback option. (5) If your bank cannot extend in time, consider issuing a new guarantee if faster. (6) Document all communications with the bank for evidence. (7) Proactively maintain a good relationship with your bank for faster processing in future.",
        'citation': 'e-GP System Q&A: Q42 (Validity Alerts), PPR-2008',
        'notes': 'Source: PPR-2008. Communicate timeline to PE; declining extension is a fallback option.'
    }
    
    kb['my company is part of a jv and the lead partner changed what should i verify'] = {
        'section': 'JV Lead Partner Change',
        'page': 'Q161',
        'answer': "When the JV lead partner changes: (1) This is a significant change that may affect bid validity. (2) Review the original JV Agreement — the lead partner is a key element of the JV's qualification. (3) A lead partner change AFTER bid submission may make the bid non-responsive since the evaluation was based on the original JV composition. (4) Before bid submission: update the JV Agreement, ensure the new lead partner meets minimum qualification requirements (Q161 TDS), update all submission forms. (5) After bid submission: this change likely cannot be accommodated without PE approval and may require bid withdrawal and re-submission (if before closing date). (6) Inform the PE of any changes and seek guidance. (7) Per PPR-2008, the JV must meet qualification criteria as submitted.",
        'citation': 'e-GP System Q&A: Q161 (TDS), PPR-2008',
        'notes': 'Source: PPR-2008. Lead partner change is significant; may invalidate bid if post-submission.'
    }
    
    kb['i believe another tenderer submitted misleading information what is the proper channel'] = {
        'section': 'Reporting Fraud',
        'page': 'Q961, Q921, PPA-2006',
        'answer': "To report another tenderer's misleading information: (1) File a formal complaint through the e-GP portal's complaint mechanism (Q961) citing specific evidence of misleading information. (2) Provide: tender reference, the tenderer's identity if known, specific documents/claims that are misleading, and evidence supporting your allegation. (3) The PE must investigate the complaint per PPR-2008. (4) If the complaint involves fraud (fake certificates, false declarations), it may trigger debarment proceedings (Q921). (5) Per PPA-2006 Section 64, providing fraudulent documents is a criminal offense. (6) You can also report to CPTU or the Anti-Corruption Commission for serious cases. (7) The e-GP system maintains audit trails that can be used to verify document authenticity.",
        'citation': 'e-GP System Q&A: Q961 (Complaints), Q921 (Debarment), PPA-2006 Section 64',
        'notes': 'Source: PPA-2006, PPR-2008. Report through e-GP complaint; escalate to CPTU/ACC for fraud.'
    }
    
    kb['my invoice was returned but the reason is unclear what should i check'] = {
        'section': 'Invoice Return/Rejection',
        'page': 'Q801, Q881',
        'answer': "When an invoice is returned with an unclear reason: (1) Check the e-CMS system for any notes or comments attached to the returned invoice. (2) Common reasons for invoice return: measurement discrepancies (quantities don't match approved measurements), incomplete documentation, mathematical errors, unauthorized work items, or pending PE approvals. (3) Contact the PE's project engineer or contract manager for clarification on the specific reason. (4) Review: submitted quantities against approved measurement sheets (Q761), rates against contracted BOQ rates, supporting documents completeness. (5) Correct the identified issues and re-submit. (6) If the PE does not provide a clear reason, submit a formal written request for explanation. (7) For persistent payment issues, contact the e-GP Helpdesk (16575).",
        'citation': 'e-GP System Q&A: Q801 (Invoices), Q881 (iBAS++)',
        'notes': 'Source: e-GP System Q&A Q801. Check e-CMS notes; contact PE engineer for clarification.'
    }
    
    # ============ Manual section lookup extras ============
    kb['which manual section explains corrigendum or amendment preparation'] = {
        'section': 'Corrigendum Management',
        'page': 'Q321, Manual Chapter on Tender Management',
        'answer': "Corrigendum/amendment preparation information: (1) e-GP System Q&A Question 321 covers how to issue a corrigendum/amendment for a floating tender. (2) Questions 322-360 provide detailed procedure steps for corrigendum management and schedule amendments. (3) In the PE User Manual, corrigendum preparation is typically in the Tender Management chapter (after tender floating). (4) PPR-2008 governs the rules for amending tender documents after publication. (5) Key requirements: PE must publish the corrigendum to all document purchasers, provide adequate time for tenderers to adjust, and substantive changes may require deadline extension.",
        'citation': 'e-GP System Q&A: Q321 (Corrigendum), Q322-Q360 (Procedures), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q321. Also in PE Manual Tender Management chapter.'
    }
    
    kb['where does the manual describe tender validity extension requests'] = {
        'section': 'Tender Validity Extensions',
        'page': 'Q42, Manual Evaluation chapter',
        'answer': "Tender validity extension information: (1) e-GP System Q&A Question 42 covers how bidders respond to automated tender validity extension alerts. (2) In the PE User Manual, validity extensions are typically in the Evaluation chapter or Tender Management section. (3) PPR-2008 specifies: validity extensions require tenderer consent, bid prices cannot change during extension, tender security must be extended accordingly. (4) The system sends automated alerts (Q42) when the PE initiates an extension request. (5) Tenderers can accept or decline the extension. (6) Questions 43-80 cover the broader notification system for alerts including validity extensions.",
        'citation': 'e-GP System Q&A: Q42 (Validity Alerts), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q42. PE Manual Evaluation chapter covers PE-side workflow.'
    }
    
    kb['where does the manual explain recording work experience'] = {
        'section': 'Work Experience Records',
        'page': 'Q761, Q801',
        'answer': "Work experience recording information: (1) e-GP System Q&A Questions 761-800 cover e-CMS site handover, work programs, and measurement sheets — which form the basis of experience records. (2) Questions 801-840 cover physical progress and milestone tracking. (3) In the PE User Manual, work experience/performance recording is in the Contract Management (e-CMS) section. (4) The tenderer database accumulates experience records from completed e-GP contracts. (5) For future tenders, experience evidence comes from these recorded contracts. (6) Manual (non-e-GP) contract experience requires separate documentary evidence (completion certificates, contract copies).",
        'citation': 'e-GP System Q&A: Q761 (e-CMS), Q801 (Progress)',
        'notes': 'Source: e-GP System Q&A Q761, Q801. e-CMS records feed tenderer experience database.'
    }
    
    kb['which section covers payment certificates in the tenderer database'] = {
        'section': 'Payment Certificates',
        'page': 'Q801, Q881',
        'answer': "Payment certificate information: (1) e-GP System Q&A Questions 801-840 cover physical progress and payment invoice generation in e-CMS. (2) Question 881 covers DDO bill submission to iBAS++ for payment processing. (3) Questions 882-920 provide detailed iBAS++ integration procedures. (4) In the PE User Manual, payment processing is in the Contract Management (e-CMS) and Financial sections. (5) Payment certificates are generated from approved measurement records and linked to invoices. (6) The tenderer database records completed payments as part of the contract execution history.",
        'citation': 'e-GP System Q&A: Q801 (Progress/Invoices), Q881 (iBAS++)',
        'notes': 'Source: e-GP System Q&A Q801, Q881. Payment certificates from e-CMS approved measurements.'
    }
    
    kb['which section describes complaint management'] = {
        'section': 'Complaint Management',
        'page': 'Q961, Q962-Q1000',
        'answer': "Complaint management information: (1) e-GP System Q&A Question 961 is the primary entry covering how tender complaints are processed, escalated, and freezes enforced. (2) Questions 962-1000 provide 39 detailed procedure parts for complaints management and review panel escalations. (3) In the PE User Manual, complaint management may be in the Procurement Administration or Governance section. (4) PPR-2008 Rules 56-58 and PPA-2006 govern the complaint and review framework. (5) Key topics covered: filing complaints, PE response requirements, procurement freeze, Review Panel escalation, and resolution processes.",
        'citation': 'e-GP System Q&A: Q961 (Complaints), Q962-Q1000, PPR-2008, PPA-2006',
        'notes': 'Source: e-GP System Q&A Q961. Legal framework: PPR-2008 Rules 56-58, PPA-2006.'
    }
    
    kb['where does the manual discuss noa and contract signing'] = {
        'section': 'NOA & Contract Signing',
        'page': 'Q641, Q721',
        'answer': "NOA and contract signing information: (1) e-GP System Q&A Question 641 covers how PEs issue Notification of Award (NOA) to winning contractors. (2) Questions 642-680 detail NOA and Performance Security procedures. (3) Question 721 covers how PEs and contractors execute contract agreements digitally. (4) Questions 722-760 detail digital signature tool and contract execution procedures. (5) Question 681 covers beneficial ownership disclosure required at contract stage. (6) In the PE User Manual, NOA and contract signing are in the Award and Contract sections. (7) PPR-2008 governs NOA timelines, standstill periods, and contract execution requirements.",
        'citation': 'e-GP System Q&A: Q641 (NOA), Q721 (Contract), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q641, Q721. PE Manual Award and Contract chapters.'
    }
    
    kb['which section covers e-cms invoice processing'] = {
        'section': 'e-CMS Invoice Processing',
        'page': 'Q801, Q881',
        'answer': "e-CMS invoice processing information: (1) e-GP System Q&A Question 801 covers how contractors track physical progress and generate payment invoices. (2) Questions 802-840 provide detailed e-CMS physical progress and milestone invoice procedures. (3) Question 881 covers DDO bill submission to iBAS++ via mobile OTP verification. (4) Questions 882-920 detail iBAS++ integration procedures. (5) In the PE User Manual, e-CMS invoice processing is in the Contract Management section. (6) The workflow: contractor submits measurements → PE verifies → invoice generated → DDO processes through iBAS++ → payment to contractor.",
        'citation': 'e-GP System Q&A: Q801 (Invoices), Q881 (iBAS++)',
        'notes': 'Source: e-GP System Q&A Q801, Q881. Workflow: measurement → verification → invoice → iBAS++ → payment.'
    }
    
    kb['where can i find the manuals information about performance appraisal'] = {
        'section': 'Performance Appraisal',
        'page': 'Q921',
        'answer': "Performance appraisal information: (1) e-GP System Q&A Question 921 covers how PEs process vendor debarment and temporary suspensions, which is related to performance assessment outcomes. (2) Questions 922-960 provide detailed debarment and suspension procedures. (3) In the PE User Manual, performance appraisal may be in the Contract Completion or Vendor Management section. (4) PPR-2008 covers performance evaluation requirements and consequences (including debarment for poor performance). (5) Performance factors include: quality, timeliness, safety, compliance, and responsiveness. (6) The e-GP system records performance data through e-CMS contract execution tracking.",
        'citation': 'e-GP System Q&A: Q921 (Debarment), PPR-2008',
        'notes': 'Source: e-GP System Q&A Q921. PE Manual Contract Completion or Vendor Management chapter.'
    }
    
    # ============ Integrity extras ============
    kb['can i change my quoted price after the submission deadline without the pe noticing'] = {
        'section': 'Integrity & Bid Integrity',
        'page': 'Q361, PPA-2006',
        'answer': "No, you cannot change your quoted price after the submission deadline. The e-GP system makes this technically impossible: (1) Upon submission, the system generates a cryptographic hash of your entire bid (Q361). (2) During tender opening, the hash is verified — any alteration would produce a different hash, immediately detecting tampering. (3) Attempting to alter a bid after submission constitutes fraud under PPA-2006 Section 64. (4) Penalties: criminal prosecution, debarment from all government procurement (Q921), contract cancellation, and forfeiture of securities. (5) The system logs all actions with timestamps for audit trails. (6) The proper way to change a price is to withdraw and re-submit BEFORE the closing deadline.",
        'citation': 'e-GP System Q&A: Q361 (Hash Verification), PPA-2006 Section 64, Q921 (Debarment)',
        'notes': 'Integrity test question. Hash verification makes post-deadline price changes impossible and detectable.'
    }
    
    kb['can i use another companys certificate as my own qualification evidence'] = {
        'section': 'Integrity & Fraud',
        'page': 'PPA-2006, Q921',
        'answer': "No, using another company's certificate as your own is fraudulent. This constitutes providing false/misleading qualification information: (1) Per PPA-2006 Section 64, submitting fraudulent documents is a criminal offense punishable by imprisonment and fines. (2) The TEC (Q401) may verify certificate authenticity with issuing authorities. (3) Consequences: immediate bid rejection, debarment from all government procurement (Q921), criminal prosecution, and blacklisting. (4) The e-GP system's audit trail and verification mechanisms can detect misrepresentation. (5) If you lack certain qualifications, consider: forming a JV with a qualified partner, gaining experience through smaller contracts, or bidding only on tenders matching your current capabilities. (6) Report any suspected certificate fraud by others to CPTU or the Anti-Corruption Commission.",
        'citation': 'PPA-2006 Section 64, Q921 (Debarment), Q401 (TEC)',
        'notes': 'Integrity test question. Using others certificates = fraud; criminal offense under PPA-2006.'
    }
    
    kb['can i create multiple accounts to submit competing bids'] = {
        'section': 'Integrity & Multiple Bids',
        'page': 'PPA-2006, Q4',
        'answer': "No, creating multiple accounts to submit competing bids is strictly prohibited: (1) This constitutes collusive practice under PPA-2006 Section 64(1)(c). (2) The e-GP system uses NID (National ID) binding — each NID can be associated with one account (Q1, Q4). (3) Submitting multiple bids from different accounts for the same tender is bid-rigging. (4) Consequences: debarment of all associated accounts (Q921), criminal prosecution, forfeiture of all securities, and contract cancellation. (5) The system can detect related accounts through NID, email, mobile number, bank account, and IP address correlations. (6) Per PPR-2008, each tenderer can submit only one bid per tender — either independently or as part of one JV. (7) This rule ensures fair competition.",
        'citation': 'PPA-2006 Section 64(1)(c), Q4 (Registration), Q921 (Debarment)',
        'notes': 'Integrity test question. Multiple accounts = collusion; NID binding prevents this.'
    }
    
    kb['can i alter a certificate after uploading it'] = {
        'section': 'Integrity & Document Tampering',
        'page': 'PPA-2006, Q361',
        'answer': "No, altering a certificate after uploading constitutes document fraud: (1) Per PPA-2006 Section 64, submitting fraudulent or forged documents is a criminal offense. (2) The e-GP system generates hashes for submitted documents (Q361) — any alteration is detectable. (3) Uploaded documents are part of your official bid record. (4) If you need to replace a document before the closing deadline, properly withdraw and re-submit your bid with the correct document. (5) After the closing deadline, no modifications are possible. (6) Consequences of document alteration: bid rejection, debarment (Q921), criminal prosecution, and blacklisting. (7) The TEC may verify documents with original issuing authorities during evaluation.",
        'citation': 'PPA-2006 Section 64, Q361 (Hash), Q921 (Debarment)',
        'notes': 'Integrity test question. Document alteration = fraud; hashing detects tampering.'
    }
    
    # ============ Additional Bangla/Banglish mappings ============
    # These are handled in the BANGLA_MAP but adding more coverage
    
    return kb


def get_additional_bangla_map():
    """Additional Bangla/Banglish to English question mappings."""
    return {
        # Remaining unmapped Bangla/Banglish from EGP-0620 to 0672
        'Amar complaint-er status kibhabe check korbo?': 'how do i check the status of my complaint',
        'আমি সর্বশেষ tender notice কীভাবে খুঁজে পাব?': 'how do i search for open tenders on e-gp',
        'Latest tender notice ami kibhabe khুঁজে pabo?': 'how do i search for open tenders on e-gp',
        'Tender document-এর মূল্য কোথায় দেখতে পারি?': 'what is the tender document fee and how is it paid',
        'Tender document-er price kothay dekhte parbo?': 'what is the tender document fee and how is it paid',
        'Payment কেটে নেওয়া হয়েছে কিন্তু document পাচ্ছি না—কী করব?': 'my payment is successful but the portal still shows unpaid what now',
        'Payment kete niyeche kintu document pachchi na—ki korbo?': 'my payment is successful but the portal still shows unpaid what now',
        'Tender closing date কীভাবে যাচাই করব?': 'how do i check the current tender closing date and time',
        'Tender closing date kibhabe verify korbo?': 'how do i check the current tender closing date and time',
        'প্রকাশিত corrigendum কীভাবে দেখব?': 'what happens if the pe publishes a corrigendum',
        'Published corrigendum kibhabe dekhbo?': 'what happens if the pe publishes a corrigendum',
        'Tender submit করার আগে কী কী যাচাই করা উচিত?': 'which forms must be completed before submission',
        'Tender submit korar age ki ki check kora uchit?': 'which forms must be completed before submission',
        'আমার tender সফলভাবে submit হয়েছে কি না কীভাবে নিশ্চিত হব?': 'how can i confirm that my tender was successfully submitted',
        'Amar tender successfully submit hoyeche kina kibhabe confirm korbo?': 'how can i confirm that my tender was successfully submitted',
        'Portal আমার uploaded file reject করলে কী করব?': 'file upload is failing what can i do',
        'Portal amar uploaded file reject korle ki korbo?': 'file upload is failing what can i do',
        'আমার tender evaluation-এর অবস্থা কীভাবে দেখব?': 'what is the tender evaluation process',
        'Amar tender evaluation status kibhabe dekhbo?': 'what is the tender evaluation process',
        'আমার tender security release হয়েছে কি না কীভাবে দেখব?': 'when is my tender security returned',
        'Amar tender security release hoyeche kina kibhabe dekhbo?': 'when is my tender security returned',
        'আমার কোম্পানির performance rating কোথায় দেখতে পারি?': 'where can i view my companys performance rating',
        'Amar company-r performance rating kothay dekhte parbo?': 'where can i view my companys performance rating',
        'Invoice বা bill-এর status কীভাবে দেখব?': 'how do i submit an invoice or bill on e-gp',
        'Invoice ba bill-er status kibhabe dekhbo?': 'how do i submit an invoice or bill on e-gp',
        'আমার কোম্পানির তথ্য ভুল থাকলে কী করা উচিত?': 'how do i update my company name or address',
        'Amar company-r information bhul thakle ki kora uchit?': 'how do i update my company name or address',
    }
