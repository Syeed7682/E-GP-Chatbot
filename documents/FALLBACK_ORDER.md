# e-GP Retrieval Fallback Order

This document describes the current search and fallback sequence used by the e-GP assistant.

## Runtime order

```text
User question
    |
    v
1. Standard Q&A dataset search
    |
    |-- direct match found ----------------------> use Q&A result
    |
    |-- no direct match
    v
2. Contractor evaluation CSV search
    |
    |-- direct CSV match ------------------------> use direct CSV result
    |
    |-- scored CSV result >= 0.60 --------------> use CSV result
    |
    |-- no acceptable CSV result
    v
3. Manual retrieval
    |
    |-- semantic embeddings available -----------> FAISS dense search
    |                                               + keyword search
    |
    |-- embeddings unavailable -------------------> keyword search only
    v
4. Hybrid ranking
    |
    |-- combine FAISS and keyword scores
    |-- sort by final score
    |-- return top-k manual chunks
    v
5. If nothing is relevant
    |
    |-- return earlier Q&A/CSV context if available
    |-- otherwise return "No relevant context found in manuals."
```

## Embedding provider fallback

When creating a text embedding, the system tries providers in this order:

1. `FlagEmbedding` with the configured BGE model.
2. `sentence-transformers` with the configured model.
3. Hugging Face inference API when `HF_TOKEN` is configured.
4. Deterministic CRC32 hash vectors as the final embedding fallback.

The hash fallback is not semantically equivalent to the trained embedding model. Because it is incompatible with the existing semantic FAISS index, semantic FAISS search is skipped when semantic search is unavailable. Keyword retrieval still runs.

## CSV fallback conditions

The contractor evaluation CSV is checked before manual embedding retrieval when:

- the question is not a steps/procedure request, and
- the standard Q&A search has no direct match.

CSV results replace the Q&A results only when there is a direct CSV match or no Q&A result and the CSV score is at least `0.60`.

## Source files

- Text embedding provider fallback: `backend/app/embeddings/text_embedder.py`
- Retrieval and CSV fallback: `backend/app/services/retrieval_service.py`
- Embedding service availability: `backend/app/services/embedding_service.py`
