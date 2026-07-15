# RAG operations troubleshooting

Use this checklist when RAG search, Chroma persistence, or embedding setup behaves unexpectedly.

## troubleshooting

- If new `data/` files are not reflected in search, rerun `python scripts/init_rag.py`.
- If Chroma returns stale results, clear the local `.chroma/` directory and rebuild the vector store.
- If embedding fails, check `LLM_API_KEY`, `LLM_BASE_URL`, and `EMBEDDING_MODEL`.
- If retrieval quality drops, inspect chunking, metadata, query wording, and category coverage.

For production, consider adding metadata filters, document versioning, and scheduled rebuild jobs.
