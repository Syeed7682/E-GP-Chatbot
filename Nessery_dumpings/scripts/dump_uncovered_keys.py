import csv
import re
from collections import defaultdict

with open('egp_contractor_evaluation_dataset.csv', 'r', encoding='utf-8', errors='ignore') as f:
    rows = list(csv.DictReader(f))

def normalize_key(q: str) -> str:
    s = q.strip().lower()
    s = re.sub(r'^(please explain:\s*|as a tenderer,\s*|i am a contractor\.\s*)', '', s)
    s = re.sub(r'[?.,!;:"]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

cat_to_keys = defaultdict(dict)
for r in rows:
    if r['answerability'] == 'Not Covered':
        k = normalize_key(r['question'])
        if k not in cat_to_keys[r['category']]:
            cat_to_keys[r['category']][k] = []
        cat_to_keys[r['category']][k].append(r['question_id'])

print("Summary of Not Covered canonical questions per category:")
for cat, kdict in cat_to_keys.items():
    print(f"\n{cat} ({len(kdict)} unique canonical keys):")
    for k, qids in kdict.items():
        print(f"  {qids} -> {k}")
