import csv
from collections import Counter

rows = list(csv.DictReader(open('e:/E-gp Project manual/egp_contractor_evaluation_dataset.csv', 'r', encoding='utf-8')))
nc = [r for r in rows if r['answerability'] == 'Not Covered']
print(f"Total: {len(rows)}, Not Covered: {len(nc)}")
print(f"Answerability breakdown: {Counter(r['answerability'] for r in rows)}")
print()

# Show categories of Not Covered
cats = Counter(r['category'] for r in nc)
for cat, count in cats.most_common():
    print(f"  {cat}: {count}")

print(f"\n--- First 30 Not Covered questions ---")
for r in nc[:30]:
    gt = r.get('ground_truth', '')[:60]
    print(f"{r['question_id']} | {r['question'][:70]} | GT: {gt}")
