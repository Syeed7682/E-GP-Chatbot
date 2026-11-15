"""Parse all 1000 Q&A entries and show the ones relevant to tenderer/contractor topics."""
import re

with open('e:/E-gp Project manual/data/raw/e-GP System Q&A.txt', 'r', encoding='utf-8') as f:
    txt = f.read()

# Parse Q&A blocks
blocks = re.findall(r'Question\s+(\d+):\s*(.*?)(?=Question\s+\d+:|$)', txt, re.DOTALL)
print(f"Total Q&A blocks parsed: {len(blocks)}")

# Search for keywords relevant to tenderer questions
keywords = [
    'register', 'registration', 'vendor', 'tenderer', 'contractor',
    'company profile', 'trade licen', 'NID', 'OTP', 'login', 'password',
    'business category', 'experience', 'authorized representative',
    'VAT', 'tax', 'email', 'mobile', 'account lock', 'session',
    'tender search', 'tender document', 'purchase', 'download',
    'eligibility', 'qualification', 'tender preparation', 'submission',
    'tender security', 'bank guarantee', 'earnest money',
    'closing date', 'deadline', 'corrigendum', 'validity',
    'pre-tender meeting', 'clarification',
    'tender opening', 'evaluation',
    'complaint', 'review', 'appeal',
    'joint venture', 'JV', 'consortium', 'subcontract',
    'award', 'NOA', 'contract sign',
    'contract execution', 'delivery',
    'invoice', 'bill', 'payment',
    'performance', 'rating', 'debarment',
    'goods', 'works', 'services', 'consultancy',
    'procurement method', 'international tender', 'OTM', 'LTM', 'RFQ',
    'troubleshoot', 'error', 'browser', 'upload fail',
    'notification', 'SMS', 'alert',
]

matched = {}
for num, content in blocks:
    content_lower = content.lower()
    for kw in keywords:
        if kw.lower() in content_lower:
            if num not in matched:
                matched[num] = []
            matched[num].append(kw)

print(f"\nQ&A entries matching tenderer keywords: {len(matched)}")
print("\n--- Relevant Q&A titles ---")
for num, content in blocks:
    if num in matched:
        title = content.strip().split('\n')[0][:120]
        kws = ', '.join(matched[num][:5])
        print(f"Q{num}: {title}  [{kws}]")

# Show full content of a few key Q&As
key_qs = ['1', '2', '3', '4', '5']
for num, content in blocks:
    if num in key_qs:
        print(f"\n{'='*80}")
        print(f"FULL Q{num}:")
        print(content[:800])
