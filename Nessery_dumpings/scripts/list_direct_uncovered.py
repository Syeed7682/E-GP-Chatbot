import csv
from collections import defaultdict

with open('egp_contractor_evaluation_dataset.csv', 'r', encoding='utf-8', errors='ignore') as f:
    rows = list(csv.DictReader(f))

categories = defaultdict(list)
for r in rows:
    categories[r['category']].append(r)

for cat, items in categories.items():
    not_cov_direct = [x for x in items if x['answerability'] == 'Not Covered' and x['language'] == 'English' and not x['question'].startswith(('Please explain:', 'As a tenderer,'))]
    print(f"\nCategory: {cat} (Direct English Not Covered: {len(not_cov_direct)})")
    for x in not_cov_direct:
        print(f"  [{x['question_id']}] {x['question']}")
