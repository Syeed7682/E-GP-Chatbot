"""
Build the full updated evaluation dataset:
1. Cover all 636 previously 'Not Covered' questions with grounded answers from the manual, Q&A, and procurement rules.
2. Add the 1,000 Q&A entries from e-GP System Q&A.txt with their step-by-step procedural ground truth.
Outputs:
- egp_contractor_evaluation_dataset_NEW.csv
- Tries to update egp_contractor_evaluation_dataset.csv if not locked.
"""

import csv
import re
import shutil
import sys
from pathlib import Path

# Add scripts directory
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'scripts'))

import populate_contractor_dataset
import additional_kb

CSV_ORIGINAL = BASE_DIR / 'egp_contractor_evaluation_dataset.csv'
CSV_BACKUP = BASE_DIR / 'egp_contractor_evaluation_dataset_backup.csv'
CSV_NEW = BASE_DIR / 'egp_contractor_evaluation_dataset_NEW.csv'
QA_FILE = BASE_DIR / 'data' / 'raw' / 'e-GP System Q&A.txt'

# Map 25 modules to the standard 24 categories
MODULE_CATEGORY_MAP = {
    1: 'Registration and company profile',
    2: 'Notifications and communication',
    3: 'Tender search and discovery',
    4: 'Procurement methods and international tenders',
    5: 'Understanding tender documents',
    6: 'Understanding tender documents',
    7: 'Tender security and bank guarantee',
    8: 'Pre-tender meeting and clarification',
    9: 'Tender validity, deadlines and corrigenda',
    10: 'Tender opening and evaluation',
    11: 'Tender opening and evaluation',
    12: 'Tender opening and evaluation',
    13: 'Tender opening and evaluation',
    14: 'Pre-tender meeting and clarification',
    15: 'Tender opening and evaluation',
    16: 'Tender opening and evaluation',
    17: 'Notice of Award and contract signing',
    18: 'Notice of Award and contract signing',
    19: 'Notice of Award and contract signing',
    20: 'Contract execution and delivery',
    21: 'Invoices, bills and payments',
    22: 'Contract execution and delivery',
    23: 'Invoices, bills and payments',
    24: 'Performance appraisal, rating and debarment',
    25: 'Complaint, review and appeal',
}

def parse_all_1000_qa():
    """Parse all 1000 Q&A items from e-GP System Q&A.txt."""
    with open(QA_FILE, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = text.split('\n')
    current_module_num = 1
    current_module_name = 'Module 1: Portal Access, Account Registration, NID & OTP Security Controls'

    module_pattern = re.compile(r'^Module\s+(\d+):\s*(.+)$')
    question_pattern = re.compile(r'^Question\s+(\d+):\s*(.+)$')

    entries = []
    cur_q_num = None
    cur_q_title = ''
    cur_q_text = ''
    cur_ans = []

    for line in lines:
        m_mod = module_pattern.match(line.strip())
        if m_mod:
            current_module_num = int(m_mod.group(1))
            current_module_name = line.strip()
            continue
        m_q = question_pattern.match(line.strip())
        if m_q:
            if cur_q_num is not None:
                entries.append({
                    'num': cur_q_num,
                    'module_num': current_module_num,
                    'module_name': current_module_name,
                    'title': cur_q_title,
                    'question': cur_q_text,
                    'answer': '\n'.join(cur_ans).strip()
                })
            cur_q_num = int(m_q.group(1))
            cur_q_title = m_q.group(2).strip()
            cur_q_text = cur_q_title
            cur_ans = []
            continue

        if cur_q_num is not None:
            if line.strip().startswith('Q:'):
                cur_q_text = line.strip()[2:].strip()
            else:
                cur_ans.append(line)

    if cur_q_num is not None:
        entries.append({
            'num': cur_q_num,
            'module_num': current_module_num,
            'module_name': current_module_name,
            'title': cur_q_title,
            'question': cur_q_text,
            'answer': '\n'.join(cur_ans).strip()
        })

    return entries

def main():
    print("=" * 70)
    print("STEP 1: Load Knowledge Bases & Bangla/Banglish Mappings")
    print("=" * 70)
    
    qa_entries = populate_contractor_dataset.parse_qa_file()
    kb = populate_contractor_dataset.build_answer_kb(qa_entries)
    extra_kb = additional_kb.get_additional_kb()
    kb.update(extra_kb)
    print(f"Total KB entries: {len(kb)}")

    bangla_map = dict(populate_contractor_dataset.BANGLA_MAP)
    bangla_map.update(additional_kb.get_additional_bangla_map())
    print(f"Total Bangla/Banglish mapped entries: {len(bangla_map)}")

    print("\n" + "=" * 70)
    print("STEP 2: Read Existing Evaluation Dataset & Fill All Not Covered Rows")
    print("=" * 70)
    
    with open(CSV_ORIGINAL, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        existing_rows = list(reader)

    print(f"Total existing rows: {len(existing_rows)}")
    
    updated_count = 0
    preserved_count = 0

    for row in existing_rows:
        if row['answerability'] != 'Not Covered':
            preserved_count += 1
            continue

        q = row['question'].strip()
        qid = row['question_id']

        # 1. Check Bangla/Banglish map
        mapped_key = bangla_map.get(q)
        if mapped_key and mapped_key in kb:
            entry = kb[mapped_key]
            row['answerability'] = 'Answerable'
            row['expected_section'] = entry['section']
            row['expected_page'] = entry['page']
            row['expected_answer'] = entry['answer']
            row['ground_truth'] = entry['answer']
            row['expected_citation'] = entry['citation']
            row['notes'] = entry['notes']
            updated_count += 1
            continue

        # 2. Match against KB with fuzzy matching threshold 0.45
        best_key, score = populate_contractor_dataset.find_best_match(q, kb, threshold=0.45)
        if best_key and best_key in kb:
            entry = kb[best_key]
            row['answerability'] = 'Answerable'
            row['expected_section'] = entry['section']
            row['expected_page'] = entry['page']
            row['expected_answer'] = entry['answer']
            row['ground_truth'] = entry['answer']
            row['expected_citation'] = entry['citation']
            row['notes'] = entry['notes']
            updated_count += 1
            continue

        # Fallback if any somehow missed
        print(f"Warning: question {qid} was not matched: {q}")

    print(f"Updated previously uncovered rows: {updated_count}")
    print(f"Preserved previously answered rows: {preserved_count}")
    print(f"Total processed original rows: {len(existing_rows)}")

    print("\n" + "=" * 70)
    print("STEP 3: Parse and Append All 1,000 Q&A.txt Questions with Ground Truth")
    print("=" * 70)
    
    all_qa = parse_all_1000_qa()
    print(f"Parsed {len(all_qa)} questions from e-GP System Q&A.txt")

    new_qa_rows = []
    for entry in all_qa:
        q_num = entry['num']
        qid = f"EGP-QA-{q_num:04d}"
        mod_num = entry['module_num']
        mod_name = entry['module_name']
        category = MODULE_CATEGORY_MAP.get(mod_num, 'Procurement methods and international tenders')
        
        # Format answer nicely
        ans_text = entry['answer']
        
        row = {
            'question_id': qid,
            'category': category,
            'question': entry['question'],
            'language': 'English',
            'question_type': 'Procedural',
            'difficulty': 'Medium',
            'answerability': 'Answerable',
            'expected_section': mod_name,
            'expected_page': f"Q{q_num} (Module {mod_num})",
            'expected_answer': ans_text,
            'ground_truth': ans_text,
            'expected_citation': f"e-GP System Operations & Compliance Master Q&A Manual: {mod_name}, Question {q_num}",
            'notes': f"Official e-GP operational workflow and system procedural solution for {entry['title']}."
        }
        new_qa_rows.append(row)

    print(f"Generated {len(new_qa_rows)} Q&A evaluation rows")

    # Combined dataset
    combined_rows = existing_rows + new_qa_rows
    print(f"Total rows in combined dataset: {len(combined_rows)}")

    print("\n" + "=" * 70)
    print("STEP 4: Write to CSV Files")
    print("=" * 70)

    # 1. Always write to CSV_NEW
    with open(CSV_NEW, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_rows)
    print(f"Successfully wrote {len(combined_rows)} rows to:\n  {CSV_NEW}")

    # 2. Try to overwrite CSV_ORIGINAL (if Excel is closed)
    try:
        with open(CSV_ORIGINAL, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(combined_rows)
        print(f"Successfully updated original CSV at:\n  {CSV_ORIGINAL}")
    except PermissionError:
        print(f"Note: {CSV_ORIGINAL.name} is currently open in Excel/another program.")
        print("  The full dataset has been saved to egp_contractor_evaluation_dataset_NEW.csv.")
        print("  Once you close Excel, the NEW file can be copied over or used directly.")

    print("\n" + "=" * 70)
    print("SUMMARY VERIFICATION")
    print("=" * 70)
    from collections import Counter
    ans_counts = Counter(r['answerability'] for r in combined_rows)
    print("Answerability counts across all rows:", dict(ans_counts))
    lang_counts = Counter(r['language'] for r in combined_rows)
    print("Language counts:", dict(lang_counts))
    cat_counts = Counter(r['category'] for r in combined_rows)
    print(f"Categories ({len(cat_counts)}):")
    for cat, count in cat_counts.most_common():
        print(f"  - {cat}: {count}")

if __name__ == '__main__':
    main()
