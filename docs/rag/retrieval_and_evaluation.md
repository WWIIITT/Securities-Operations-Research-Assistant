# RAG retrieval and evaluation

SORA stores chunks from `data/` in a local Chroma collection named `sora_compliance_rules`. `search_compliance_policy` runs similarity search with `k=3`, then returns the retrieved content and metadata to the Compliance Reviewer.

## Metrics

- `hit@1`: whether the first retrieved rule matches the expected rule.
- `hit@3`: whether any of the top three retrieved rules match the expected rule.
- `MRR`: Mean Reciprocal Rank, which rewards correct rules appearing earlier.
- `avg_latency_ms`: average retrieval latency.
- `p95_latency_ms`: tail latency for slower retrievals.

Run:

```powershell
python rag_evals.py
```

The report is written to `rag_eval_report.json`.
