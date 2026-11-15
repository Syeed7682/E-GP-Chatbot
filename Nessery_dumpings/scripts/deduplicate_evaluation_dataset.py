"""
Deduplicate the evaluation dataset:
1. Contractor questions: Deduplicate prefix variants ('Please explain:', 'As a tenderer,', 'I am a contractor.')
   Keep distinct questions across English, Bangla, and Banglish.
2. Q&A questions: Deduplicate the 946 repetitive 'Procedure Part 1..39' template slices.
   Keep the 54 unique operational workflow topics, each with its comprehensive procedural ground truth.
3. Strict 1-row-per-line formatting (no raw line breaks or asterisks).
"""

import csv
import re
import sys
from pathlib import Path

BASE_DIR = Path('e:/E-gp Project manual')
sys.path.insert(0, str(BASE_DIR / 'scripts'))

import populate_contractor_dataset
import additional_kb

CSV_OUT = BASE_DIR / 'egp_contractor_evaluation_dataset.csv'

def clean_val(v):
    if not v:
        return ''
    v = v.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    v = re.sub(r'^\*+\s*', '', v)
    v = re.sub(r'\s*\*\s*', '; ', v)
    v = v.replace('**', '')
    v = re.sub(r'\s+', ' ', v).strip()
    return v

def normalize_key(q: str) -> str:
    s = q.strip().lower()
    s = re.sub(r'^(please explain:\s*|as a tenderer,\s*|i am a contractor\.\s*)', '', s)
    s = re.sub(r'\s*-\s*procedure part\s*\d+\s*', '', s)
    s = re.sub(r'[?.,!;:"]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

# 1. Build Contractor Unique Questions
qa_entries = populate_contractor_dataset.parse_qa_file()
kb = populate_contractor_dataset.build_answer_kb(qa_entries)
extra_kb = additional_kb.get_additional_kb()
kb.update(extra_kb)
bangla_map = dict(populate_contractor_dataset.BANGLA_MAP)
bangla_map.update(additional_kb.get_additional_bangla_map())

# Map normalized keys to clean, formatted question text and category
# We can extract the original question texts from the KB keys and bangla map
category_keywords = {
    'Registration and company profile': ['register', 'registration', 'company profile', 'trade licenc', 'nid', 'tin', 'vat', 'representative'],
    'Login, password and account security': ['login', 'password', 'otp', 'locked', 'unauthorized', 'session'],
    'Tender search and discovery': ['search', 'floating', 'filter', 'district', 'annual procurement plan', 'app', 'find'],
    'Tender document purchase, download and fees': ['purchase', 'download', 'fee', 'document price', 'receipt'],
    'Understanding tender documents': ['standard tender', 'gcc', 'pcc', 'tds', 'itb', 'bill of quantities', 'boq', 'specification'],
    'Eligibility, qualification and experience': ['eligibility', 'qualification', 'experience', 'turnover', 'liquid asset', 'subcontractor'],
    'Tender preparation and online submission': ['prepare', 'submit', 'online submission', 'hash', 'encryption', 'modify', 'forms'],
    'Tender security and bank guarantee': ['tender security', 'earnest money', 'bank guarantee', 'performance security', 'currency'],
    'Tender validity, deadlines and corrigenda': ['validity', 'deadline', 'corrigendum', 'closing date', 'extension'],
    'Pre-tender meeting and clarification': ['pre-tender', 'clarification', 'query', 'minutes'],
    'Tender opening and evaluation': ['opening', 'evaluation', 'responsive', 'non-responsive', 'hash verification'],
    'Complaint, review and appeal': ['complaint', 'review panel', 'appeal', 'grievance'],
    'JV, consortium and subcontracting': ['joint venture', 'jv', 'consortium', 'subcontract'],
    'Notice of Award and contract signing': ['notification of award', 'noa', 'contract signing', 'digital signature'],
    'Contract execution and delivery': ['contract execution', 'delivery', 'site handover', 'measurement', 'time extension', 'variation'],
    'Invoices, bills and payments': ['invoice', 'bill', 'payment', 'ibas++'],
    'Performance appraisal, rating and debarment': ['performance', 'appraisal', 'rating', 'debarment', 'suspension'],
    'Goods, works, services and consultancy': ['goods', 'works', 'services', 'consultancy'],
    'Procurement methods and international tenders': ['procurement method', 'otm', 'ltm', 'rfq', 'international'],
    'Technical troubleshooting': ['troubleshoot', 'portal not loading', 'upload fail', 'blank', 'support'],
    'Notifications and communication': ['notification', 'message box', 'alert', 'record of messages'],
    'Real-life scenarios': ['mistake', 'real-life', 'differ', 'scenario'],
    'Manual section and page lookup': ['manual section', 'lookup', 'where can i find'],
    'Integrity, compliance and adversarial tests': ['manipulate', 'bribe', 'collude', 'fake', 'cheat']
}

def guess_category(key: str) -> str:
    key_lower = key.lower()
    for cat, kws in category_keywords.items():
        if any(kw in key_lower for kw in kws):
            return cat
    return 'Procurement methods and international tenders'

contractor_rows = []
q_counter = 1

# Add canonical English questions
for key, data in kb.items():
    # Capitalize first letter of question
    clean_q = key[0].upper() + key[1:] + '?'
    qid = f"EGP-{q_counter:04d}"
    cat = guess_category(key)
    
    contractor_rows.append({
        'question_id': qid,
        'category': cat,
        'question': clean_q,
        'language': 'English',
        'question_type': 'Direct',
        'difficulty': 'Medium',
        'answerability': 'Answerable',
        'expected_section': data['section'],
        'expected_page': data['page'],
        'expected_answer': clean_val(data['answer']),
        'ground_truth': clean_val(data['answer']),
        'expected_citation': clean_val(data['citation']),
        'notes': clean_val(data['notes'])
    })
    q_counter += 1

# Add distinct Bangla & Banglish questions
for bn_q, en_key in bangla_map.items():
    if en_key not in kb:
        continue
    data = kb[en_key]
    qid = f"EGP-{q_counter:04d}"
    cat = guess_category(en_key)
    # Detect if Bangla script or Banglish
    has_bangla = any('\u0980' <= ch <= '\u09FF' for ch in bn_q)
    lang = 'Bangla' if has_bangla else 'Banglish'
    
    contractor_rows.append({
        'question_id': qid,
        'category': cat,
        'question': bn_q.strip(),
        'language': lang,
        'question_type': 'Direct',
        'difficulty': 'Medium',
        'answerability': 'Answerable',
        'expected_section': data['section'],
        'expected_page': data['page'],
        'expected_answer': clean_val(data['answer']),
        'ground_truth': clean_val(data['answer']),
        'expected_citation': clean_val(data['citation']),
        'notes': clean_val(data['notes'])
    })
    q_counter += 1

print(f"Contractor unique rows (English + Bangla + Banglish): {len(contractor_rows)}")

# 2. Add Deduplicated Q&A Operational Workflow Questions (54 unique topics)
qa_rows = []
seen_qa_keys = set()
qa_counter = 1

for entry in qa_entries:
    q_text = entry['question']
    norm_q = normalize_key(q_text)
    
    if norm_q in seen_qa_keys:
        continue
    seen_qa_keys.add(norm_q)
    
    # Clean question text if it was 'Procedure Part X'
    clean_q = re.sub(r'\s*-\s*Procedure Part\s*\d+\s*', ' ', q_text)
    clean_q = re.sub(r'\s+', ' ', clean_q).strip()
    if not clean_q.endswith('?'):
        clean_q += '?'
    
    qid = f"EGP-QA-{qa_counter:04d}"
    cat = guess_category(clean_q)
    
    qa_rows.append({
        'question_id': qid,
        'category': cat,
        'question': clean_q,
        'language': 'English',
        'question_type': 'Procedural',
        'difficulty': 'Medium',
        'answerability': 'Answerable',
        'expected_section': clean_val(entry.get('title', 'Operational Workflow')),
        'expected_page': f"Q{entry['num']}",
        'expected_answer': clean_val(entry['answer']),
        'ground_truth': clean_val(entry['answer']),
        'expected_citation': f"e-GP System Operations & Compliance Master Q&A Manual: Question {entry['num']}",
        'notes': f"Official e-GP operational workflow and system procedural solution for {clean_val(entry['title'])}."
    })
    qa_counter += 1

print(f"Q&A unique rows (deduplicated of Procedure Part 1..39): {len(qa_rows)}")

# Combined deduplicated dataset
final_rows = contractor_rows + qa_rows
print(f"Total deduplicated rows: {len(final_rows)}")

fieldnames = [
    'question_id', 'category', 'question', 'language', 'question_type',
    'difficulty', 'answerability', 'expected_section', 'expected_page',
    'expected_answer', 'ground_truth', 'expected_citation', 'notes'
]

with open(CSV_OUT, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_rows)

print(f"Successfully saved deduplicated dataset to {CSV_OUT}")

with open(CSV_OUT, 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(f"Physical lines in {CSV_OUT.name}: {len(lines)}")
