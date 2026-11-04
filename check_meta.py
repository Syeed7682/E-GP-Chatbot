import json
with open('data/faiss_index/metadata.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
s = [x for x in d if x.get('image_path')]
print(f'Total chunks with image_path: {len(s)}')
if s:
    print('Sample:', s[0])
else:
    print('No image_path found. Showing first chunk:')
    print(d[0])

