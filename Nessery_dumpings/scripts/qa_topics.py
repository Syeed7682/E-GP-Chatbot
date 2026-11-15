"""Extract unique Q&A topic groups and show representative titles."""
import re

with open('e:/E-gp Project manual/data/raw/e-GP System Q&A.txt', 'r', encoding='utf-8') as f:
    txt = f.read()

blocks = re.findall(r'Question\s+(\d+):\s*(.*?)(?=Question\s+\d+:|$)', txt, re.DOTALL)

# Group by base title (strip " - Procedure Part N" suffix)
groups = {}
for num, content in blocks:
    title = content.strip().split('\n')[0].strip()
    base = re.sub(r'\s*-\s*Procedure Part\s*\d+\s*$', '', title)
    if base not in groups:
        groups[base] = []
    groups[base].append(int(num))

print(f"Unique topic groups: {len(groups)}")
print()
for base, nums in sorted(groups.items(), key=lambda x: x[1][0]):
    print(f"Q{nums[0]}-Q{nums[-1]} ({len(nums)} parts): {base[:100]}")

# Now show full content of Q4 (vendor registration) as example
print("\n" + "="*80)
for num, content in blocks:
    if num == '4':
        print(f"FULL Q4:\n{content[:2000]}")
