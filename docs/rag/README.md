# RAG documentation map

This category map explains how SORA organizes RAG documentation after moving retrieval data into `data/`.

- `data_preparation.md`: how source files under `data/` become chunks with metadata.
- `retrieval_and_evaluation.md`: how Chroma retrieval is measured with hit@1, hit@3, MRR, and latency.
- `compliance_guardrails.md`: how retrieved rules become compliance guardrails.
- `operations_troubleshooting.md`: how to debug Chroma, embedding, and data refresh issues.

SORA now treats each first-level `data/` folder as a RAG category, such as `compliance`, `market`, `products`, and `risk`.
