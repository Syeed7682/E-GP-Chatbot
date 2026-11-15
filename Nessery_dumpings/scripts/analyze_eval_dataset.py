import csv
from collections import defaultdict

with open('egp_contractor_evaluation_dataset.csv', 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total rows: {len(rows)}")

# Print fields
print("Fields:", reader.fieldnames)

# Group by category and show question count and answerability
categories = defaultdict(list)
for r in rows:
    categories[r['category']].append(r)

for cat, items in categories.items():
    ans = sum(1 for x in items if x['answerability'] == 'Answerable')
    part = sum(1 for x in items if x['answerability'] == 'Partially Answerable')
    not_cov = sum(1 for x in items if x['answerability'] == 'Not Covered')
    print(f"\nCategory: {cat} (Total: {len(items)}, Ans: {ans}, Part: {part}, NotCov: {not_cov})")
    for r in items[:5]:
        print(f"  [{r['question_id']}] ({r['answerability']}) {r['question']}")
