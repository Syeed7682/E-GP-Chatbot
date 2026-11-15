import csv
import re
from collections import defaultdict

with open('egp_contractor_evaluation_dataset.csv', 'r', encoding='utf-8', errors='ignore') as f:
    rows = list(csv.DictReader(f))

def clean_q(q):
    q = re.sub(r'^(Please explain:\s*|As a tenderer,\s*)', '', q, flags=re.I).strip()
    return q.lower()

# Map by category and cleaned question
clean_map = defaultdict(list)
for r in rows:
    clean_map[clean_q(r['question'])].append(r)

print(f"Total rows: {len(rows)}")
print(f"Unique normalized questions: {len(clean_map)}")

# How many normalized questions have at least one answerable row?
ans_norm = 0
for norm, items in clean_map.items():
    if any(x['answerability'] in ('Answerable', 'Partially Answerable') for x in items):
        ans_norm += 1

print(f"Normalized questions with an existing answer: {ans_norm}")
