import csv

with open('egp_contractor_evaluation_dataset.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print(f"Total rows: {len(rows)}")
print("\nFirst 15 questions:")
for r in rows[:15]:
    print(f"  {r['question_id']}: {r['question']}")

print("\nQuestions 40 to 55:")
for r in rows[40:55]:
    print(f"  {r['question_id']}: {r['question']}")
