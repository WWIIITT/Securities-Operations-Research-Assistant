# AI Agent 面試與技術說明指南

這份文件用 SORA 作為例子，說明 JD 裡常見的 AI Builder / AI Agent / AI Architect 概念。中文說明搭配英文術語，方便面試時直接對應題目。

## Prompt engineering

Prompt engineering 是設計模型輸入的方式，讓 LLM 產生穩定、可控、符合業務需求的輸出。好的 prompt 會說清楚角色、任務、輸入資料、輸出格式、禁止事項和評估標準。

在 SORA 中，router prompt 要求模型只輸出 `market_analysis` 或 `compliance_check`；reviewer prompt 要求模型不可移除 mandatory disclosures。

例子：

1. Routing prompt：`Respond with exactly market_analysis or compliance_check.` 這能降低下游 conditional edge 解析失敗。
2. Compliance prompt：要求「不得保證回報、必須揭露風險、不是投資建議」，讓 LLM 的自然語言能力受到合規規則約束。

## Workflow orchestration

Workflow orchestration 是把多個步驟、工具、agent 和條件分支組成可控制的流程。它回答「誰先做、下一步去哪、失敗怎麼辦」。

SORA 使用 LangGraph：`router -> analyst -> reviewer`，若是純合規問題則 `router -> reviewer`。這比單一 chat prompt 更容易測試、觀察與擴充。

例子：

1. 市場查詢：Router 判斷是 market query，Analyst 先拿 yfinance data，Reviewer 再做合規審核。
2. 合規查詢：Router 直接送 Reviewer，避免無意義查股價。

## Agent testing

Agent testing 是驗證 agent 是否按預期使用工具、更新 state、處理錯誤和遵守規則。它不只測 final answer，也測中間步驟。

SORA 的測試包含 router route、analyst report、reviewer disclosure、MCP fallback、RAG metrics 和 LangSmith evaluator。

例子：

1. Mock `ChatOpenAI`，確認 router/analyst/reviewer 真的呼叫 LLM。
2. Mock MCP tool，確認 analyst 透過 `call_tool("get_stock_data", ...)` 而不是直接耦合本地函式。

## Performance optimization

Performance optimization 是改善速度、成本和穩定性。Agent 系統常見瓶頸包括 LLM latency、tool latency、RAG retrieval、外部 API rate limit 和 trace 上傳。

SORA 的策略是保留 deterministic fallback、限制 RAG `k=3`、用小模型 `gpt-4o-mini`，並把 RAG latency 寫入 eval report。

例子：

1. 如果 reviewer latency 太高，可以 cache compliance retrieval 結果，因為 policy rules 不常改。
2. 如果 analyst node 太慢，可以先回 yfinance raw data，再非同步補充 LLM summary。

## Real-time tool use

LLM 本身不是即時行情資料庫；它的知識可能過期，也不能自己保證最新價格。Agent 的做法是讓 LLM 呼叫工具，例如 yfinance、MCP server、內部 market data API，再由模型整理工具結果。

在 SORA 中，`HK50` 會被轉成 yfinance 的 `^HSI`，再由 `get_stock_data` 查詢。若工具已有資料，LLM 不應回答「我沒有 real-time data access」，而應引用工具輸出並保留合規聲明。

例子：

1. 使用者問「what is the price of HK50 now」：Router 走 market analysis，Analyst 透過 MCP/yfinance 查 `^HSI`，Reviewer 補合規披露。
2. 使用者問「is this guaranteed to rise?」：即使拿到即時價格，Reviewer 仍必須說明 returns are not guaranteed。

## RAG

RAG 是 Retrieval-Augmented Generation，意思是先從知識庫檢索相關資料，再交給 LLM 產生答案。它降低 hallucination，並提供可追溯來源。

SORA 用 RAG 找 compliance policy rules，Reviewer 必須帶著 retrieved rules 產生 final report。

例子：

1. 查詢「Can we guarantee returns?」應命中 `COMPLIANCE-001`。
2. 查詢「Should we disclose risks?」應命中 `RULE-002`。

## Vector database / database

Database 儲存結構化或非結構化資料；Vector database 則儲存 embedding vectors，支援 similarity search。傳統資料庫擅長精確查詢，向量資料庫擅長語意相似查詢。

SORA 使用 Chroma 作為本地 vector database。每條 policy rule 都有 `page_content` 和 metadata，例如 `rule_id`、`source`。

例子：

1. SQL 適合查「客戶 ID 123 的交易紀錄」。
2. Chroma 適合查「哪些規則和 guaranteed returns 有關」。

## AI agent benchmarking

Benchmarking 是用固定測試集量度 agent 表現，避免只靠 demo 感覺。Benchmark 應包含正常案例、邊界案例、錯誤案例和業務重要案例。

SORA 有兩層 benchmark：LangSmith eval 測 final response 是否有 disclosure，`rag_evals.py` 測 retrieval 是否命中 expected rule。

例子：

1. Route benchmark：`Analyze AAPL stock` 預期 route 是 `market_analysis`。
2. RAG benchmark：`Can we guarantee returns?` 預期 top 3 包含 `COMPLIANCE-001`。

## Evaluation for accuracy, reliability, and user experience

Evaluation 是持續衡量答案品質。Accuracy 看答案是否正確；reliability 看不同情況下是否穩定；user experience 看輸出是否清楚、可操作、符合使用者工作流。

SORA 的 evaluator 檢查 disclosures、route match、RAG hit rate 和 latency。這些指標能對應業務風險，而不是只看模型文字是否「看起來合理」。

例子：

1. Accuracy：市場分析是否使用正確 ticker 和 tool data。
2. Reliability：RAG 失敗時 reviewer 是否仍提供 fallback disclosure，而不是直接崩潰。
3. User experience：Gradio UI 顯示 final report 與 trace metadata，方便營運同事理解系統做了什麼。
