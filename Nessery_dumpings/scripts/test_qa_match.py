import re
import difflib

# Load 1000 Q&A
with open('data/raw/e-GP System Q&A.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

qa_blocks = re.findall(r'Question (\d+): (.*?)\n(Q: .*?)(?=(?:Question \d+:)|$)', text, re.DOTALL)
print(f"Extracted {len(qa_blocks)} QA blocks from Master Q&A")

qa_dict = {}
for qnum, title, body in qa_blocks:
    qa_dict[int(qnum)] = {
        'title': title.strip(),
        'body': body.strip()
    }

# Check sample
print("Sample Q1:", qa_dict[1]['title'])
print("Sample Q4:", qa_dict[4]['title'])
