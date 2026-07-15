# JD Keywords and Concepts Guide

這份文件把 AI Builder / AI Agent Associate / AI Architect JD 裡的 keyword 和 concept 拆開解釋。格式刻意偏面試與履歷準備：每個概念都有定義、SORA 對應位置，以及 1-2 個例子。

## Extracted Keywords / Concepts

- AI Agents
- agentic workflows
- automation solutions
- business functions
- prompt engineering
- workflow orchestration
- agent testing
- performance optimization
- AI Agent solutions
- AI frameworks and tools
- emerging AI technologies
- agent frameworks
- practical business use cases
- AI models
- APIs
- MCP-enabled services
- third-party AI platforms
- data preparation
- knowledge base structuring
- RAG
- AI Agent benchmarking
- evaluation frameworks
- accuracy
- reliability
- user experience
- product, operations, and business collaboration
- automation opportunities
- operational efficiency
- documentation, reports, presentations, and technical summaries
- AI innovation, experimentation, and transformation projects
- LLM applications
- automation platforms
- workflow systems
- LangGraph
- CrewAI
- AutoGen
- Claude Code
- OpenAI Codex
- OpenHands
- Cursor
- Windsurf
- Manus
- Agentic AI
- MCP, Model Context Protocol
- multi-agent systems
- AI / Computer Science / Data Science / FinTech / Engineering
- curiosity, problem-solving, and strong academic foundation

## Concept Explanations

### AI Agents

AI Agents 是能理解任務、選擇工具、執行步驟、讀取結果並產出答案的 AI 系統。它不只是單次聊天，而是把 LLM、工具、資料、狀態和控制流程組合起來。

SORA 對應：`sora/nodes.py` 裡的 router、market analyst、compliance reviewer 就是三個 agent-like components。

例子：
- 使用者問「Analyze AAPL stock」，agent 先判斷要走 market analysis，再用 yfinance tool 取資料，最後交給 compliance reviewer 補合規聲明。
- 使用者問「Can we promise guaranteed returns?」，agent 不查股票價格，而是直接走 compliance review。

### Agentic Workflows

agentic workflows 是由多個 AI 或工具步驟組成的流程，每一步可以根據狀態決定下一步。重點是 conditional routing、state management、tool use 和 final review。

SORA 對應：`sora/graph.py` 使用 LangGraph 建立 `START -> router -> analyst/reviewer -> END`。

例子：
- 市場問題：router -> analyst -> reviewer。
- 純合規問題：router -> reviewer。

### Automation Solutions

automation solutions 是把重複、規則明確、需要資料整合的工作自動化，例如報告初稿、合規檢查、資料摘要、內部查詢。

SORA 對應：把「市場資料查詢 + 合規審查」自動串成一個流程。

例子：
- 每日自動生成股票簡報草稿。
- 自動檢查銷售話術是否包含「保證回報」等高風險表述。

### Business Functions

business functions 指公司內不同部門或流程，例如 operations、research、compliance、sales、product、customer support。

SORA 對應：Market Analyst 支援 research，Compliance Reviewer 支援 compliance，Gradio UI 支援 operations 或 business users 試用。

例子：
- Research team 用 SORA 快速產出市場摘要。
- Compliance team 用 SORA 檢查外發內容是否缺少風險披露。

### Prompt Engineering

prompt engineering 是設計 system prompt、user prompt、工具說明和輸出格式，讓 LLM 更穩定地完成任務。它包含角色設定、約束條件、few-shot examples、格式要求和失敗 fallback。

SORA 對應：`sora/nodes.py` 裡 router、analyst、reviewer 的 LLM prompt。

例子：
- router prompt 要求只輸出 `market_analysis` 或 `compliance_check`，減少分類結果漂移。
- reviewer prompt 要求必須引用 retrieved policy rules，避免只靠模型記憶做合規判斷。

### Workflow Orchestration

workflow orchestration 是管理多步驟流程的順序、分支、狀態和錯誤處理。AI agent 系統不能只靠一個 prompt，還需要清楚的流程控制。

SORA 對應：LangGraph `StateGraph` 管理 `AgentState`，讓 `messages`、`ticker`、`analyst_report`、`compliance_status` 在節點之間傳遞。

例子：
- router 決定是否需要 analyst。
- analyst 完成後一定進 reviewer，確保市場報告有合規 guardrail。

### Agent Testing

agent testing 是測試 agent 在不同輸入、工具結果、LLM 失敗和邊界情況下是否穩定。測試不只看答案像不像，還要看 route、tool calls、state update 和 fallback。

SORA 對應：`tests/test_graph_nodes.py`、`tests/test_llm_integration.py`、`tests/test_mcp_integration.py`。

例子：
- 測試 `Analyze AAPL stock` 是否先走 analyst 再走 reviewer。
- mock LLM 失敗，確認 deterministic fallback 不會讓 graph 崩潰。

### Performance Optimization

performance optimization 是降低 latency、成本、錯誤率和不必要的 LLM/tool calls。AI 系統的效能不只代表速度，也包含穩定性與可維護性。

SORA 對應：router 避免所有問題都查市場資料；RAG eval 量測 retrieval latency；MCP client 有 timeout。

例子：
- 純合規問題直接走 reviewer，省掉 yfinance call。
- 對 RAG 查詢量測 average latency 和 p95 latency，找出慢查詢。

### AI Agent Solutions

AI Agent solutions 是完整可用的 agent 系統，不只是單一模型呼叫。它通常包含 UI、graph、tools、memory/state、RAG、observability 和 evaluation。

SORA 對應：Gradio UI、LangGraph workflow、MCP tools、Chroma RAG、LangSmith evals。

例子：
- 一個內部 compliance assistant。
- 一個 research operations assistant，自動查資料並生成合規版摘要。

### AI Frameworks and Tools

AI frameworks and tools 是用來建構 agent、RAG、tool calling、evaluation 或 coding workflow 的工具。JD 特別提到 LangGraph、CrewAI、AutoGen、Claude Code、OpenAI Codex、OpenHands、Cursor、Windsurf、Manus。

SORA 對應：主要使用 LangGraph；本專案開發過程可用 OpenAI Codex 協助重構、測試和文件化。

例子：
- LangGraph 適合需要明確 state 和 conditional edges 的 production-style workflow。
- OpenAI Codex 適合在 repo 中閱讀程式、修改檔案、跑測試、整理 README。

### LangGraph

LangGraph 是用 graph 方式建構 agent workflows 的框架。它適合多節點、多分支、需要狀態追蹤和可恢復流程的應用。

SORA 對應：`sora/graph.py` 建立 SORA 的 routing 和 review flow。

例子：
- 用 conditional edge 把 query 分到 market analyst 或 compliance reviewer。
- 把 analyst output 寫入 state，再交給 reviewer 讀取。

### OpenAI Codex

OpenAI Codex 是 coding agent，可在專案中閱讀上下文、修改程式、執行測試、做重構和產生文件。它不是 runtime agent framework，而是開發階段的 AI engineering assistant。

SORA 對應：可用 Codex 改 `sora/` package、補測試、更新 README、排查 LangGraph/MCP/RAG 問題。

例子：
- 要求 Codex 將 root wrapper files 移到 `sora/` package 並跑測試驗證。
- 要求 Codex 補一份 RAG evaluation 文件並更新 README file tree。

### CrewAI

CrewAI 是偏「角色分工」的 multi-agent framework，常用 crew、agent、task 的概念描述合作流程。

SORA 對應：SORA 沒使用 CrewAI，但 Market Analyst 和 Compliance Reviewer 可以映射成兩個 crew agents。

例子：
- Research agent 收集資料，Writer agent 寫報告，Reviewer agent 做合規審查。
- Sales enablement crew 自動整理客戶會議摘要和 follow-up draft。

### AutoGen

AutoGen 是多代理協作框架，常見用法是讓多個 assistant/user proxy agents 透過對話合作完成任務。

SORA 對應：SORA 用 LangGraph 做 deterministic orchestration；若改用 AutoGen，可以讓 analyst 和 reviewer 以對話方式互相修正報告。

例子：
- Analyst agent 產出初稿，Reviewer agent 回覆修改意見，Analyst agent 再產出修正版。
- Developer agent 和 Critic agent 協作生成測試與修 bug。

### Claude Code, Cursor, Windsurf, OpenHands, Manus

這些工具多屬於 AI coding agent 或 AI IDE 類別，用來協助開發者理解 codebase、修改程式、產生測試或自動完成工程任務。

SORA 對應：這些工具可用於開發階段；SORA runtime 本身仍以 LangGraph、LangChain、MCP 和 Chroma 為主。

例子：
- Cursor 或 Windsurf 可在 IDE 中補全 `nodes.py` prompt。
- OpenHands 或 Manus 可嘗試完成較長的 issue，例如新增一個 report export workflow。

### Emerging AI Technologies

emerging AI technologies 指快速演進的新技術，例如 tool calling、long-context models、multimodal models、agent memory、MCP、AI eval platforms。

SORA 對應：MCP、LangSmith、LangGraph、RAG 都是 JD 關心的新式 AI application stack。

例子：
- 評估 MCP 是否適合把內部資料庫工具接給 agent。
- 比較不同 LLM 在 compliance review 上的準確率與成本。

### Practical Business Use Cases

practical business use cases 是能真正改善業務流程的 AI 場景，不只是 demo。判斷標準包括節省時間、降低風險、提升一致性、改善使用者體驗。

SORA 對應：金融 research 和 compliance review 是明確 business use case。

例子：
- 自動檢查研究報告是否缺少風險披露。
- 將客服常見問題轉成 RAG assistant，減少人工查文件時間。

### AI Models

AI models 是負責理解、生成、分類或 embedding 的模型。LLM 常用於 reasoning 和 text generation，embedding model 常用於 RAG retrieval。

SORA 對應：`sora/llm.py` 建立 `ChatOpenAI`；`sora/rag.py` 使用 embeddings 建立 Chroma vector store。

例子：
- `gpt-4o-mini` 用來生成 analyst report。
- embedding model 把 compliance rules 轉成向量，支援 similarity search。

### APIs

APIs 是系統之間交換資料或能力的介面。AI application 常透過 API 呼叫 LLM、資料源、內部服務或第三方平台。

SORA 對應：OpenAI-compatible API、LangSmith API、yfinance data API-like library、MCP tool interface。

例子：
- 用 `LLM_BASE_URL` 指向 OpenAI-compatible endpoint。
- 用 yfinance 查 `AAPL` 或 `^HSI` 的市場資料。

### MCP-enabled Services

MCP, Model Context Protocol, 是讓 AI application 連接 tools、data sources 和 workflows 的標準協定。MCP-enabled service 可以把功能以 tool schema 暴露給 agent。

SORA 對應：`sora/mcp_server.py` 暴露 `get_stock_data` 和 `search_compliance_policy`；`sora/mcp_client.py` 優先透過 MCP 呼叫。

例子：
- 把 stock data lookup 包成 MCP tool。
- 把 compliance policy search 包成 MCP tool，讓 reviewer 透過標準協定查規則。

### Third-party AI Platforms

third-party AI platforms 是外部模型、工具、追蹤、資料或部署平台。使用時要注意 API key、資料安全、成本、延遲和可替換性。

SORA 對應：LangSmith、OpenAI-compatible LLM endpoint、Chroma、Gradio 都可視為外部或第三方 component。

例子：
- 使用 LangSmith 追蹤 LLM call 和 graph execution。
- 使用 Gradio 快速提供 business users 試用介面。

### Data Preparation

data preparation 是清理、切分、標註、去重和格式化資料，讓資料能被 RAG 或 evaluation 使用。資料品質通常直接影響 AI 輸出品質。

SORA 對應：`dummy_compliance.txt` 中每條規則被切成 document，並加上 `rule_id` metadata。

例子：
- 把 PDF policy 拆成 rule-level chunks。
- 為每條規則加上 department、effective_date、risk_level metadata。

### Knowledge Base Structuring

knowledge base structuring 是把知識庫整理成可搜尋、可引用、可維護的結構。它包含 chunking strategy、metadata design、版本管理和資料來源追蹤。

SORA 對應：compliance rules 以 rule id 和 source metadata 進入 Chroma。

例子：
- 將「不得保證回報」設為獨立 rule，方便 reviewer 精準引用。
- 用 metadata 區分 internal policy、regulatory guidance、FAQ。

### RAG

RAG, Retrieval-Augmented Generation, 是先從知識庫檢索相關資料，再把資料交給 LLM 生成答案。它能降低 hallucination，並讓答案引用最新或內部文件。

SORA 對應：Compliance Reviewer 必須先 retrieve policy rules，再 finalise report。

例子：
- 查詢「guaranteed returns」時命中 `RULE-001`。
- reviewer 根據 retrieved rules 補上 risk disclosure 和 not investment advice。

### Vector Database

Vector database 用向量儲存和搜尋語意相近的內容。它適合 RAG，因為使用者問題和文件不一定用完全相同字眼。

SORA 對應：ChromaDB local vector store。

例子：
- 使用者問「Can we promise profits?」也可能找回「Do not guarantee returns」。
- 用 hit@3 檢查前 3 筆 retrieval 是否包含正確 rule。

### AI Agent Benchmarking

benchmarking 是用固定測試集量測不同版本 agent 的表現，例如路由正確率、答案合規率、retrieval hit rate、latency、成本。

SORA 對應：`evals.py` 做 LangSmith evaluation；`rag_evals.py` 做 RAG retrieval metrics。

例子：
- 比較 prompt v1 和 v2 的 compliance disclaimer pass rate。
- 比較不同 embedding model 的 hit@1、hit@3 和 MRR。

### Evaluation Frameworks

evaluation frameworks 是系統化評估 AI output 的方法或工具，可以是 deterministic rules、LLM-as-judge、人手標註或混合方式。

SORA 對應：LangSmith `evaluate` 和 custom evaluator。

例子：
- deterministic evaluator 檢查 final response 是否包含「not investment advice」。
- route evaluator 檢查 stock query 是否走 `market_analysis`。

### Accuracy

accuracy 是答案是否正確、是否引用正確資料、是否符合預期任務。AI agent 的 accuracy 要拆成 retrieval accuracy、routing accuracy、generation accuracy。

SORA 對應：RAG eval 的 hit@k 和 graph route evaluator。

例子：
- `Analyze AAPL stock` 不應錯誤路由到純合規回答。
- `Can we promise guaranteed returns?` 應找回禁止保證回報的規則。

### Reliability

reliability 是系統在錯誤、缺資料、API timeout、LLM 失敗時仍能可預期地運作。金融場景特別需要可靠 fallback。

SORA 對應：MCP 失敗時 fallback 到 local tools；LLM 失敗時 fallback 到 deterministic template。

例子：
- LLM endpoint 暫時不可用時，仍能產生 basic compliance-safe report。
- 無效 ticker 不讓 graph crash，而是回傳可理解的錯誤訊息。

### User Experience

user experience 是使用者是否容易理解、信任和操作系統。AI UX 也包含透明度，例如顯示 route、ticker、compliance status 和 trace metadata。

SORA 對應：`app.py` Gradio UI 顯示 final report 與 metadata。

例子：
- 使用者看到 `route=market_analysis`，知道系統有先查市場資料。
- final report 清楚列出 retrieved policy rules，增加可審核性。

### Product, Operations, and Business Collaboration

AI agent 專案通常不是單純工程問題，需要和 product、operations、business users 對齊流程、痛點、成功指標和風險。

SORA 對應：SORA 把 research、operations、compliance 的需求放在同一個 PoC 裡。

例子：
- Product 定義使用者流程，operations 提供常見問題，compliance 提供政策規則。
- Business team 提出「哪類查詢最花時間」，AI team 將其轉成 automation workflow。

### Automation Opportunities

automation opportunities 是適合自動化的工作機會，通常具備高頻、規則清楚、資料來源穩定、人工成本高或錯誤風險高等特徵。

SORA 對應：市場摘要和合規檢查是兩個高頻、可標準化的機會。

例子：
- 每日市場摘要初稿。
- 外發 marketing copy 的合規掃描。

### Operational Efficiency

operational efficiency 是用更少時間、更少人工、更低錯誤率完成同樣或更高品質的工作。AI automation 的商業價值常由這一點衡量。

SORA 對應：把查市場資料、寫初稿、查合規規則、補 disclosure 串成單一流程。

例子：
- 將 20 分鐘人工查資料和審查縮短成 1 分鐘初稿。
- 讓 compliance reviewer 專注高風險案例，而不是每份都從零檢查。

### Documentation, Reports, Presentations, and Technical Summaries

這些是 AI initiative 的交付物，用來讓技術、業務和管理層理解系統目的、設計、限制、測試結果和下一步。

SORA 對應：README、`docs/rag.md`、`docs/ai_agent_interview_guide.md`、本文件，以及 `rag_eval_report.json`。

例子：
- 用 README 說明如何安裝和啟動 PoC。
- 用 RAG eval report 向 non-technical stakeholders 解釋 retrieval 效果。

### AI Innovation, Experimentation, and Transformation Projects

這類工作是快速探索新技術是否能帶來業務改變，通常先做 PoC，再根據效果決定是否 productionize。

SORA 對應：SORA 本身就是 AI transformation PoC。

例子：
- 先用 dummy compliance rules 驗證 workflow，再接真實 policy database。
- 比較 LangGraph 和其他 agent frameworks 是否更適合公司流程。

### LLM Applications

LLM applications 是把大型語言模型接入實際產品或內部流程的應用，不只是聊天，也包含摘要、分類、生成、抽取、審查和決策輔助。

SORA 對應：router classification、analyst report generation、compliance review generation。

例子：
- 用 LLM 將自然語言 query 分類成 market 或 compliance。
- 用 LLM 將 tool output 改寫成 business-readable report。

### Automation Platforms and Workflow Systems

automation platforms 和 workflow systems 是管理任務、觸發器、流程和整合的平台。它們可以是低代碼工具，也可以是程式化 orchestration。

SORA 對應：LangGraph 是程式化 workflow system；MCP 是工具整合邊界。

例子：
- 當新 research request 到達時自動觸發 SORA。
- 將 SORA output 接到 Slack、CRM 或 internal dashboard。

### Agentic AI

Agentic AI 是泛指具備目標導向、工具使用、多步推理、狀態管理和部分自主決策能力的 AI 系統。它和單次 prompt 最大差別是能執行流程。

SORA 對應：SORA 有 route decision、tool use、RAG retrieval、review guardrail 和 final answer。

例子：
- 不是直接回答股價，而是先查 yfinance，再整理結果。
- 不是只靠 LLM 判斷合規，而是先 retrieve policy rule。

### Multi-agent Systems

multi-agent systems 是由多個具不同角色或能力的 agents 協作完成任務的系統。每個 agent 可以專注在不同責任。

SORA 對應：Router、Market Analyst、Compliance Reviewer。

例子：
- Analyst 負責市場資料和初稿。
- Reviewer 負責政策檢索和合規聲明。

### Academic Background and Curiosity

JD 提到 AI、Computer Science、Data Science、FinTech、Engineering 和 strong curiosity，代表公司看重技術基礎與主動探索能力。Fresh graduate 也可以用作品集和 PoC 展示能力。

SORA 對應：SORA 可作為 portfolio project，展示 agent workflow、RAG、MCP、evaluation 和 documentation。

例子：
- 面試時展示如何用 tests 證明 reviewer 必須 retrieve 至少一條 rule。
- 說明為何金融場景需要 risk disclosure、not guaranteed returns 和 not investment advice。

## How To Answer Interview Questions

### Prompt Engineering

可以這樣回答：Prompt engineering 不只是寫一句提示，而是把角色、任務、限制、輸出格式和失敗處理設計清楚。在 SORA 裡，我會讓 router 只輸出固定 label，讓 reviewer 必須引用 retrieved policy rules。

例子：
- 「我會把 routing prompt 設計成 constrained classification，降低自由文字造成的 parsing 風險。」
- 「對 compliance reviewer，我會要求 final answer 必須包含 retrieved rules、risk disclosure 和 not investment advice。」

### Workflow Orchestration

可以這樣回答：Workflow orchestration 是把 LLM、tools、RAG 和 review steps 放進可控流程。LangGraph 適合這件事，因為它有 state、nodes、edges 和 conditional routing。

例子：
- 「市場查詢一定先進 analyst，再進 reviewer。」
- 「純合規查詢不需要 market tool，直接進 reviewer，節省 latency 和成本。」

### Agent Testing and Benchmarking

可以這樣回答：Agent testing 要測 route、tool use、state update、fallback 和 final answer，不只看文字好不好看。Benchmarking 則用固定 dataset 追蹤版本變化。

例子：
- 「我會測 LLM 失敗時 fallback 是否仍能完成流程。」
- 「我會用 hit@3、MRR、latency 評估 RAG retrieval。」

### Performance Optimization

可以這樣回答：Performance optimization 包含 latency、cost、token usage、tool call 數量和可靠性。不是所有 query 都應該呼叫所有工具。

例子：
- 「用 router 避免純合規問題查 yfinance。」
- 「用 MCP timeout 和 local fallback 避免工具服務中斷拖垮整個 graph。」

### RAG and Database

可以這樣回答：RAG 把內部知識庫檢索結果交給 LLM，讓答案可追溯且更少 hallucination。Vector database 負責語意搜尋，metadata 則讓結果可審核。

例子：
- 「我會把 compliance rules 按 rule 切 chunk，保留 rule_id 和 source metadata。」
- 「我會用 hit@1、hit@3、MRR 驗證 retrieval 是否找回正確政策。」
