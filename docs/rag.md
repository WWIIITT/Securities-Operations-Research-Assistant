# SORA RAG 說明與評估

## 資料來源

SORA 的 RAG 預設從 `data/` 目錄讀取資料，而不是只讀單一 `dummy_compliance.txt`。`data/` 的第一層資料夾代表知識類別：

- `data/compliance/`: 核心合規規則，例如不得保證回報、必須揭露風險、非投資建議。
- `data/risk/`: 風險披露資料，例如數位資產、流動性、監管與本金損失風險。
- `data/market/`: 市場評論撰寫規範，例如資料來源、假設、前瞻性語句限制。
- `data/products/`: 產品相關注意事項，例如 Grayscale Bitcoin Mini Trust 的產品風險提示。

`dummy_compliance.txt` 仍保留作為 legacy fallback。如果 `data/` 沒有可讀取的 `.txt` 或 `.md` 文件，系統才會退回讀取 `dummy_compliance.txt`。

## Chunking

目前 chunking 策略很直接：每一個非空 bullet 或文字行會變成一個 retrievable document。Markdown heading 不會變成 chunk，而是保存為 `section` metadata。

這種策略適合 PoC，因為 compliance rules 通常短、邊界清楚、容易對應到 `COMPLIANCE-001` 這類 rule id。正式環境可以改成 paragraph-level chunking，並加入版本、有效日期、部門、產品、司法管轄區等 metadata。

## Metadata

每個 chunk 都會帶 metadata：

- `source`: `data/` 下的相對路徑，例如 `compliance/core_policy_rules.txt`
- `category`: 第一層資料夾，例如 `compliance`
- `rule_id`: category-scoped id，例如 `COMPLIANCE-001`
- `section`: Markdown heading，例如 `Digital Asset Risk Disclosures`
- `file_type`: `.txt` 或 `.md`

這讓 Compliance Reviewer 可以在 final report 裡列出 retrieved policy rules，形成 evidence trail。

## Embedding

`sora/rag.py` 使用 `OpenAIEmbeddings` 建立 embedding，讀取：

- `LLM_API_KEY`
- `LLM_BASE_URL`
- `EMBEDDING_MODEL`

預設 embedding model 是 `text-embedding-3-small`。Embedding 的工作是把 policy chunk 轉成向量，讓語意相近的 query 可以找到相關規則。

## Chroma Persistence

向量資料存放在本地 `.chroma/`，collection 名稱是 `sora_compliance_rules`。

- `initialize_vector_store()` 會從 `data/` 讀取文件並建立 Chroma collection。
- `get_vector_store()` 會讀取既有 collection；若 `.chroma/` 不存在則初始化。
- `.chroma/` 被 `.gitignore` 忽略，避免提交本地向量資料。

## retrieval flow

1. `reviewer_node` 取得 analyst report 或 user query。
2. 透過 MCP wrapper 呼叫 `search_compliance_policy`。
3. `search_compliance_policy` 使用 Chroma `similarity_search(query, k=3)`。
4. Reviewer 至少帶回一條 policy rule；若 retrieval 失敗，使用 fallback disclosure rule。
5. Final report 固定附上 retrieved policy rules、risk disclosure、returns are not guaranteed、not investment advice。

## guardrail

RAG 在 SORA 裡是 compliance guardrail，不只是補充背景。Reviewer 不能只靠 LLM 自己判斷，必須檢索 policy rule 並把 rule 放入 final report。這能讓審核有 evidence trail，也方便 LangSmith trace 和 evaluator 檢查。

## RAG 效率與準確率評估

`rag_evals.py` 提供最小 retrieval benchmark：

- `hit@1`: 第一筆 retrieved rule 是否命中 expected rule。
- `hit@3`: 前三筆 retrieved rules 是否至少一筆命中。
- `MRR`: Mean Reciprocal Rank，命中越前面分數越高。
- `avg_latency_ms`: 平均 retrieval latency。
- `p95_latency_ms`: 95 百分位 latency，用來觀察尾端延遲。

執行：

```powershell
python rag_evals.py
```

輸出會寫到 `rag_eval_report.json`。如果 `hit@3` 偏低，通常代表 chunk 太粗、query phrasing 與 policy wording 差太遠、embedding model 不適合，或 metadata/filtering 設計不足。

## 分類文件

更多分門別類的 RAG 文件位於 `docs/rag/`：

- `docs/rag/README.md`
- `docs/rag/data_preparation.md`
- `docs/rag/retrieval_and_evaluation.md`
- `docs/rag/compliance_guardrails.md`
- `docs/rag/operations_troubleshooting.md`

## 限制與 troubleshooting

- 如果 endpoint 不支援 embeddings，`sora/rag.py` 會在初始化向量庫時失敗；可設定 `EMBEDDING_MODEL` 或改用支援 embedding 的 provider。
- 如果 `.chroma/` 舊資料和 `data/` 不一致，重新執行 `python scripts/init_rag.py` 或清理本地 Chroma directory。
- 如果 compliance search 回傳空結果，先檢查 `data/` 是否有 `.txt` 或 `.md` 文件，再看 `.env` 的 API key/base URL。
- 如果 latency 過高，先量測 embedding API、Chroma IO、query 數量；PoC 中 `k=3` 已足夠。
