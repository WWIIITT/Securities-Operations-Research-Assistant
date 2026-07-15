# RAG data preparation

SORA reads RAG source files from `data/` by default. The old `dummy_compliance.txt` remains as a legacy fallback, but new knowledge should be placed in category folders such as `data/compliance/`, `data/risk/`, `data/market/`, and `data/products/`.

## chunking

The current chunking strategy is intentionally simple: each non-empty bullet or line becomes one retrievable document. Markdown headings are stored as `section` metadata instead of becoming searchable chunks.

## metadata

Each chunk receives metadata:

- `source`: relative file path under `data/`
- `category`: first-level folder name, such as `compliance` or `risk`
- `rule_id`: category-scoped id, such as `COMPLIANCE-001`
- `section`: nearest Markdown heading when available
- `file_type`: `.txt` or `.md`

This structure lets SORA show which policy, risk, market, or product document grounded the compliance review.
