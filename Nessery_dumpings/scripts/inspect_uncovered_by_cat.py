import csv
from collections import defaultdict

with open('egp_contractor_evaluation_dataset.csv', 'r', encoding='utf-8', errors='ignore') as f:
    rows = list(csv.DictReader(f))

categories = defaultdict(list)
for r in rows:
    categories[r['category']].append(r)

print(f"Categories count: {len(categories)}")

for cat, items in categories.items():
    not_cov = [x for x in items if x['answerability'] == 'Not Covered']
    print(f"\n==========================================")
    print(f"CATEGORY: {cat} (Total: {len(items)}, Not Covered: {len(not_cov)})")
    print(f"==========================================")
    for x in not_cov[:5]:
        print(f"  {x['question_id']} [{x['language']}]: {x['question']}")
