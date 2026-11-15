import csv

with open('egp_contractor_evaluation_dataset.csv', 'r', encoding='utf-8', errors='ignore') as f:
    rows = list(csv.DictReader(f))

print(f"Total rows: {len(rows)}")

# Print question_id range by category
from collections import defaultdict
cat_ranges = defaultdict(list)
for r in rows:
    cat_ranges[r['category']].append(r['question_id'])

for cat, qids in cat_ranges.items():
    print(f"{cat:45} | Count: {len(qids):3} | Range: {qids[0]} -> {qids[-1]}")
