import sys
sys.path.insert(0, 'backend')
from app.services.retrieval_service import retrieval_service

context, sources = retrieval_service.retrieve("what is debarment?", top_k=5)
print(f"Retrieved {len(sources)} sources:")
for s in sources:
    print(f"Page {s['page']} (Chunk {s['chunk_id']}) Score: {s['score']:.3f}")
    print(f"  {s['snippet'][:120]}...\n")

