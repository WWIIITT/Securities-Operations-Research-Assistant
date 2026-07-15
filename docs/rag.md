# SORA RAG 說明與評估

## 資料來源

SORA 的 compliance RAG 目前使用 `dummy_compliance.txt` 作為示範政策來源。每一行代表一條合規規則，例如不得保證回報、必須揭露風險、不可把研究輸出包裝成投資建議。正式環境可以把資料來源替換成內部 policy manual、審批指引、產品風險聲明或 FAQ。

## Chunking

目前的 chunking 策略很簡單：一行 policy rule 就是一個 chunk。這適合 PoC，因為每條規則短、邊界清楚、可直接回傳 `RULE-001` 這類 metadata。若文件變長，建議改成段落級 chunking，並保留章節標題、文件版本、有效日期、適用產品等 metadata。

## Embedding

`rag.py` 使用 `OpenAIEmbeddings` 建立 embedding，並讀取 `LLM_API_KEY`、`LLM_BASE_URL` 與 `EMBEDDING_MODEL`。預設 embedding model 是 `text-embedding-3-small`。Embedding 的工作是把 policy chunk 轉成向量，讓語意相近的查詢可以找到相關規則。

## Chroma Persistence

向量資料存放在本地 `.chroma/`，collection 名稱是 `sora_compliance_rules`。`initialize_vector_store()` 會從 policy file 建立 Chroma collection；`get_vector_store()` 會讀取既有 collection，若不存在則初始化。`.chroma/` 被 `.gitignore` 忽略，避免把本機向量資料提交進 repo。

## retrieval flow

1. `reviewer_node` 取得 analyst report 或使用者 query。
2. 透過 MCP wrapper 呼叫 `search_compliance_policy`。
3. `search_compliance_policy` 使用 Chroma `similarity_search(query, k=3)`。
4. Reviewer 至少帶回一條 policy rule；若向量庫失敗，會使用 fallback disclosure rule。
5. 最終報告固定附上 retrieved policy rules、Risk disclosure、Returns are not guaranteed、not investment advice。

## guardrail

RAG 在這裡不是只為了補充內容，而是 compliance guardrail。Reviewer 不可以只靠 LLM 自己判斷，必須檢索 policy rule 並把 rule 放進 final report。這能讓審核有 evidence trail，也方便 LangSmith trace 和 evaluator 檢查。

## RAG 效率與準確率評估

`rag_evals.py` 提供最小 retrieval benchmark：

- `hit@1`：第一筆 retrieved rule 是否命中 expected rule。
- `hit@3`：前三筆 retrieved rules 是否至少一筆命中。
- `MRR`：Mean Reciprocal Rank，命中越前面分數越高。
- `avg_latency_ms`：平均 retrieval latency。
- `p95_latency_ms`：95 百分位 latency，用來觀察尾端延遲。

執行：

```powershell
python rag_evals.py
```

輸出會寫到 `rag_eval_report.json`。如果 `hit@3` 偏低，通常代表 chunk 太粗、query phrasing 與 policy wording 差太遠、embedding model 不適合，或 metadata/filtering 設計不足。

## 限制與 troubleshooting

- 如果 endpoint 不支援 embeddings，`rag.py` 會在初始化向量庫時失敗；可設定 `EMBEDDING_MODEL` 或改用支援 embedding 的 provider。
- 如果 `.chroma/` 舊資料和 `dummy_compliance.txt` 不一致，重新執行 `python rag.py` 或清理本地 Chroma directory。
- 如果 compliance search 回傳空結果，先檢查 `dummy_compliance.txt` 是否存在，再看 `.env` 的 API key/base URL。
- 如果 latency 過高，先量測 embedding API、Chroma IO、以及 query 數量；PoC 中 `k=3` 已足夠。
