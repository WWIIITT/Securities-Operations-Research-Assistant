# JD Keywords and Concepts Guide

這份文件用來準備 AI Builder / AI Agent Associate / AI Architect 類職位面試。它把 JD 裡的 keywords / concepts 拆成可回答、可舉例、可連回 SORA 專案的知識卡。每個概念都包含「詳細說明」、「SORA 實作細節」、「實務例子 A」、「實務例子 B」和「面試回答重點」。

## Extracted Keywords / Concepts

- AI Agents
- Agentic AI
- multi-agent systems
- agentic workflows
- workflow orchestration
- automation solutions
- business functions
- automation opportunities
- operational efficiency
- prompt engineering
- LLM applications
- AI models
- APIs
- MCP / Model Context Protocol
- MCP-enabled services
- third-party AI platforms
- AI frameworks and tools
- agent frameworks
- LangGraph
- CrewAI
- AutoGen
- Claude Code
- OpenAI Codex
- OpenHands
- Cursor
- Windsurf
- Manus
- data preparation
- knowledge base structuring
- RAG / retrieval-augmented generation
- vector database / database
- agent testing
- AI Agent benchmarking
- evaluation frameworks
- accuracy
- reliability
- user experience
- performance optimization
- product, operations, and business collaboration
- documentation, reports, presentations, and technical summaries
- emerging AI technologies
- practical business use cases
- AI innovation, experimentation, and transformation projects
- Artificial Intelligence / Computer Science / Data Science / FinTech / Engineering
- curiosity, problem-solving, and strong academic foundation

## 1. AI Agents

**詳細說明：**  
AI Agents 是能把「理解任務、規劃步驟、呼叫工具、讀取結果、更新狀態、產出答案」串起來的 AI 系統。它和普通 chatbot 的差別在於：chatbot 多數只回覆文字，agent 會主動使用外部能力，例如查市場資料、搜尋知識庫、檢查合規政策或執行 workflow。真正可用的 agent 通常需要 LLM、tools、state、guardrails、evaluation 和 observability。

**SORA 實作細節：**  
SORA 不是單一 prompt，而是由 router、Market Analyst、Compliance Reviewer 組成。router 判斷使用者問題要走市場分析還是合規檢查；Market Analyst 透過 MCP/yfinance 工具取得即時市場資料；Compliance Reviewer 透過 RAG 檢索合規規則，最後補上 risk disclosure、not guaranteed returns、not investment advice。

**實務例子 A：**  
使用者輸入 `Analyze AAPL stock`。AI Agent 不應只靠模型記憶回答 Apple 的情況，而是先抽取 ticker `AAPL`，呼叫 `get_stock_data` 取得價格、前收、公司資料，再用 LLM 產出市場摘要。最後 reviewer 檢索 compliance rules，確認報告沒有承諾回報，並加入必要風險聲明。

**實務例子 B：**  
使用者輸入 `Can we promise guaranteed returns to clients?`。AI Agent 應判斷這不是市場資料問題，而是合規問題，因此直接進入 reviewer，搜尋「guaranteed returns」相關規則，回覆不得保證回報，並說明應使用風險揭露與非投資建議聲明。

**面試回答重點：**  
可以說：「AI Agent 不只是 LLM 回答文字，而是 LLM 加上工具、狀態、流程和評估。以 SORA 為例，agent 會先 route，再查 yfinance 或 RAG，最後由 compliance reviewer 做 guardrail。」

## 2. Agentic AI

**詳細說明：**  
Agentic AI 指具備任務導向與行動能力的 AI 應用。它通常能把一個目標拆成多個步驟，根據中間結果調整流程，並透過工具取得模型本身不知道的資料。Agentic AI 的核心不是「模型變聰明」而已，而是把模型放在一個可控、可觀測、可測試的系統裡。

**SORA 實作細節：**  
SORA 的 agentic 行為包含 conditional routing、tool calling、RAG retrieval、compliance finalization。LLM 可以參與分類和寫報告，但工具結果與合規 guardrail 由程式流程強制執行，避免模型自由發揮造成風險。

**實務例子 A：**  
如果模型回答「我沒有即時資料」，但 yfinance 已經回傳最新價格，SORA 會要求報告以工具資料為準。這表示 agentic system 的資料來源不是模型記憶，而是外部工具。

**實務例子 B：**  
如果 reviewer LLM 沒有主動提到風險，SORA 的 reviewer node 仍會強制附上 retrieved policy rules 和 mandatory disclosure。這就是 agentic guardrail：把重要規則放進 workflow，而不是完全相信模型。

**面試回答重點：**  
可以說：「Agentic AI 的價值在於讓 LLM 可以和工具、資料、流程合作，但同時要有 deterministic guardrails，否則在金融或合規場景會很危險。」

## 3. Multi-agent Systems

**詳細說明：**  
Multi-agent systems 是把任務拆給多個角色或能力不同的 agents。每個 agent 專注在某一類責任，例如研究、寫作、審查、資料搜尋、風險控制。優點是責任清楚、測試容易、prompt 更聚焦；缺點是 orchestration、狀態同步和成本控制會更複雜。

**SORA 實作細節：**  
SORA 的三個角色是 Router、Market Analyst、Compliance Reviewer。Router 負責任務分類，Market Analyst 負責市場資料和初稿，Compliance Reviewer 負責政策檢索與合規補強。這樣的分工讓每個 node 都可以獨立測試。

**實務例子 A：**  
Market Analyst 只需要關心「市場資料是否正確、報告是否清楚」，不需要知道所有合規規則。Compliance Reviewer 則只需要檢查報告是否包含風險揭露和禁止保證回報等內容。

**實務例子 B：**  
在真實公司裡，可以加入第四個 agent：Report Formatter。它不做分析，只負責把 final report 轉成 email、PDF 或 internal dashboard 格式。

**面試回答重點：**  
可以說：「Multi-agent 不代表越多 agent 越好，而是當責任真的不同時才拆分。SORA 拆成 analyst 和 reviewer，是因為市場分析和合規審查的目標、資料來源和評估方式都不同。」

## 4. Agentic Workflows

**詳細說明：**  
Agentic workflows 是多步驟、可分支、可使用工具的 AI 工作流。它通常包含輸入解析、路由、工具呼叫、資料整合、LLM 生成、審查和輸出。好的 agentic workflow 會把不穩定的 LLM 行為限制在合適範圍，並用程式流程保證關鍵步驟一定發生。

**SORA 實作細節：**  
SORA 的 workflow 是 `START -> router -> analyst or reviewer -> END`，市場分析會走 `analyst -> reviewer`，合規問題直接走 `reviewer`。這讓市場報告一定經過 compliance guardrail。

**實務例子 A：**  
市場查詢：`Analyze TSLA` 會先查 TSLA 資料，再產生市場摘要，最後 reviewer 檢查是否有「guaranteed」等不當措辭。

**實務例子 B：**  
合規查詢：`Review this statement: Tesla is guaranteed to outperform` 會直接檢索合規政策，指出「guaranteed to outperform」可能違反不得保證回報的規則。

**面試回答重點：**  
可以說：「Agentic workflow 要把 AI 的自由度和業務流程結合。SORA 用 LangGraph 控制流程，確保重要步驟，例如 compliance review，不會被跳過。」

## 5. Workflow Orchestration

**詳細說明：**  
Workflow orchestration 是管理節點順序、條件分支、狀態傳遞、錯誤處理和終止條件。AI 系統如果只有 prompt，會很難保證一致性；orchestration 則把「什麼情況該做什麼」明確寫進 workflow。

**SORA 實作細節：**  
`sora/graph.py` 使用 LangGraph `StateGraph`。`AgentState` 包含 `messages`、`ticker`、`analyst_report`、`compliance_status` 等欄位。每個 node 都只更新自己負責的欄位，讓資料流可追蹤。

**實務例子 A：**  
如果 router 回傳 `market_analysis`，graph 會進 analyst；如果回傳 `compliance_check`，graph 會跳過 analyst。這種 conditional edge 比在單一 prompt 裡請模型「自己決定」更可控。

**實務例子 B：**  
如果 analyst 找不到 ticker，仍會產生清楚錯誤訊息並交給 reviewer 加上合規說明，而不是讓整個 graph crash。

**面試回答重點：**  
可以說：「Workflow orchestration 是 production AI agent 的骨架。LLM 負責語意和生成，但流程、狀態和 guardrails 要由 graph 或 workflow engine 控制。」

## 6. Automation Solutions

**詳細說明：**  
Automation solutions 是把重複、耗時、容易出錯或需要跨系統查資料的工作自動化。AI automation 不一定要完全取代人，它更常見的價值是產生初稿、預先檢查、整理資料、降低人工處理量。

**SORA 實作細節：**  
SORA 自動化了「市場資料查詢 -> 報告初稿 -> 合規規則檢索 -> 合規聲明補強」這條流程。它讓 analyst 或 compliance user 不需要每次都手動查價格、找 policy、寫 disclosure。

**實務例子 A：**  
研究團隊每天需要整理十隻股票的簡報。SORA 可以先產出每隻股票的初稿，研究員再校對和補充觀點。

**實務例子 B：**  
營運團隊收到大量銷售話術草稿。SORA 可以先標出疑似「保證回報」或「投資建議」的句子，讓 compliance reviewer 優先處理高風險內容。

**面試回答重點：**  
可以說：「我會優先找高頻、規則明確、資料來源穩定的流程做 AI automation，先做人機協作初稿，而不是一開始就追求全自動。」

## 7. Business Functions

**詳細說明：**  
Business functions 指公司內不同職能，例如 product、operations、research、compliance、sales、customer support、finance。AI agent 的設計要理解每個部門的目標和風險，不同部門需要的 output 格式和可靠性也不同。

**SORA 實作細節：**  
SORA 同時服務 research 和 compliance。Market Analyst 產出研究支援內容；Compliance Reviewer 確保內容有風險揭露；Gradio UI 讓非工程使用者可以測試 workflow。

**實務例子 A：**  
Research team 關心市場資料是否即時、摘要是否有洞察。對他們來說，ticker 抽取、yfinance 資料品質和報告可讀性很重要。

**實務例子 B：**  
Compliance team 關心是否引用正確政策、是否避免誤導性語句、是否保留審查證據。對他們來說，retrieved rule id、source metadata 和 traceability 更重要。

**面試回答重點：**  
可以說：「同一個 AI 系統面向不同 business functions 時，成功標準不同。研究部門看效率和資訊品質，合規部門看可追溯性和風險控制。」

## 8. Practical Business Use Cases

**詳細說明：**  
Practical business use cases 是能真的改善業務流程的 AI 場景。判斷一個 use case 是否實用，可以看它是否高頻、是否有清楚輸入輸出、是否能衡量節省時間、是否能降低錯誤或風險。

**SORA 實作細節：**  
SORA 的 use case 很明確：金融查詢和合規審查。它不提供交易或投資建議，而是定位成 research support 和 operations assistant。

**實務例子 A：**  
「股票報告初稿」是 practical use case，因為資料來源明確、格式可標準化、人工每次都要查類似資料。

**實務例子 B：**  
「檢查是否承諾回報」也是 practical use case，因為這是金融內容中常見且高風險的合規問題。

**面試回答重點：**  
可以說：「我會把 AI use case 從 business pain point 出發，而不是從模型能力出發。SORA 選金融 research 和 compliance，是因為流程清楚、風險可控、效果可評估。」

## 9. Automation Opportunities

**詳細說明：**  
Automation opportunities 是適合自動化的工作機會。常見特徵包括：重複性高、規則明確、資料來源穩定、人工處理時間長、錯誤成本高、可以接受人類 final review。

**SORA 實作細節：**  
SORA 把市場查詢和合規檢查視為 automation opportunity，但沒有把交易決策自動化。這是重要邊界，因為金融決策屬於高風險任務。

**實務例子 A：**  
可以自動化：每天讀取市場資料並生成摘要初稿。原因是資料客觀、流程固定、人工可審查。

**實務例子 B：**  
不應輕易自動化：直接替客戶下單或承諾投資結果。原因是涉及法律、合規、客戶風險承受能力和授權問題。

**面試回答重點：**  
可以說：「我會用 impact、frequency、risk、data readiness 來評估 automation opportunity。高影響但高風險的流程，先做輔助和審查，不做全自動決策。」

## 10. Operational Efficiency

**詳細說明：**  
Operational efficiency 是用更少時間、更少人工、更低錯誤率完成同樣或更高品質的工作。AI agent 的價值常體現在縮短 cycle time、減少重複操作、提升輸出一致性。

**SORA 實作細節：**  
SORA 讓使用者用一個自然語言 query 完成多個步驟：抽 ticker、查價格、寫摘要、查合規規則、補 disclosure。這降低了手動切換工具和複製貼上的時間。

**實務例子 A：**  
原本 analyst 可能要打開市場網站、查公司資料、寫摘要、再交給 compliance。SORA 可以先生成合規版草稿，讓 analyst 把時間放在判斷和補充洞察。

**實務例子 B：**  
Compliance reviewer 原本要閱讀整份內容找問題。SORA 可以先標出 retrieved rules 和 final disclaimer，讓 reviewer 專注確認高風險句子。

**面試回答重點：**  
可以說：「Operational efficiency 不是只看 AI 回答速度，而是看整個業務流程節省多少 handoff、查找和重工。」

## 11. Prompt Engineering

**詳細說明：**  
Prompt engineering 是設計 LLM 指令的工程方法，包括角色、任務、輸入資料、限制條件、輸出格式、few-shot examples、錯誤處理。好的 prompt 會降低 ambiguity，讓模型輸出更容易被程式解析和測試。

**SORA 實作細節：**  
SORA 的 router prompt 應限制只輸出 `market_analysis` 或 `compliance_check`。Analyst prompt 應要求使用 tool output，不可聲稱沒有即時資料。Reviewer prompt 應要求引用 retrieved policy rules 並補 mandatory disclosures。

**實務例子 A：**  
不好的 router prompt：「Tell me what this query is about。」模型可能輸出長句，難以解析。較好的 prompt：「Return exactly one label: market_analysis or compliance_check。」

**實務例子 B：**  
不好的 analyst prompt 可能讓模型說「截至我的知識日期」。較好的 prompt 要明確說：「You are given live tool output. Use the tool output as source of truth. Do not claim lack of real-time access if tool data is available。」

**面試回答重點：**  
可以說：「Prompt engineering 要和系統設計一起看。能用程式約束的地方不要只靠 prompt；但 prompt 要讓 LLM 清楚知道角色、資料來源和輸出格式。」

## 12. LLM Applications

**詳細說明：**  
LLM applications 是把大型語言模型接入實際流程，用於分類、摘要、生成、抽取、改寫、審查、問答等。成熟的 LLM application 通常會加入資料檢索、工具呼叫、權限控制、日誌和評估。

**SORA 實作細節：**  
SORA 使用 LLM 做三件事：router classification、market report generation、compliance review wording。但價格資料由 yfinance 提供，合規規則由 Chroma RAG 提供，LLM 不單獨決定事實。

**實務例子 A：**  
LLM 把 yfinance 回傳的 raw fields，例如 current price、previous close、sector，整理成業務使用者容易讀的分析段落。

**實務例子 B：**  
LLM 把 retrieved compliance rules 轉成清楚審查意見，例如指出某句話可能暗示 guaranteed return，並建議改寫方式。

**面試回答重點：**  
可以說：「LLM application 的重點是把模型放進可靠流程，而不是把所有事情都交給模型。事實資料和政策資料應由 tools 或 RAG 提供。」

## 13. AI Models

**詳細說明：**  
AI models 包含 chat model、embedding model、classification model、reranker 等。不同模型負責不同任務：chat model 擅長理解和生成；embedding model 擅長把文字轉成向量做語意搜尋；reranker 可改善 retrieval 排序。

**SORA 實作細節：**  
`sora/llm.py` 建立 OpenAI-compatible `ChatOpenAI`，讀取 `LLM_MODEL` 和 `LLM_BASE_URL`。`sora/rag.py` 使用 embedding model 建立 Chroma vector store。這讓生成和檢索可以分開調整。

**實務例子 A：**  
若 `gpt-4o-mini` 生成報告速度快、成本低，就適合 PoC 或高頻內部工具。若需要更嚴格推理，可以比較較強模型的準確率和成本。

**實務例子 B：**  
如果 RAG 常找不到正確 rule，問題可能不是 chat model，而是 embedding model、chunking 或 metadata 設計。這時應先看 retrieval metrics。

**面試回答重點：**  
可以說：「我會把模型選型拆成 generation model 和 embedding/retrieval model。不同環節有不同 metrics，例如 generation 看合規率，retrieval 看 hit@k 和 MRR。」

## 14. APIs

**詳細說明：**  
APIs 是系統間交換資料和功能的介面。AI agent 常需要呼叫 LLM API、內部資料 API、第三方市場資料 API、文件搜尋 API 或 workflow API。API 設計會影響可靠性、安全性和可替換性。

**SORA 實作細節：**  
SORA 使用 OpenAI-compatible endpoint 呼叫 LLM，使用 yfinance 查市場資料，使用 LangSmith API 做 evaluation/tracing，使用 MCP tool interface 把工具包成標準服務。

**實務例子 A：**  
如果公司未來把 yfinance 換成 Bloomberg 或內部 market data API，只要保持 `get_stock_data` tool 的輸出 schema 類似，graph 上層可以少改很多。

**實務例子 B：**  
如果 LLM provider 更換，只要支援 OpenAI-compatible API，就可以透過 `.env` 改 `LLM_BASE_URL` 和 `LLM_MODEL`，降低 vendor lock-in。

**面試回答重點：**  
可以說：「AI agent 的 API integration 要重視 schema、timeout、error handling 和 fallback。工具輸出越穩定，agent 越容易測試和維護。」

## 15. MCP / Model Context Protocol / MCP-enabled Services

**詳細說明：**  
MCP, Model Context Protocol, 是一種讓 AI applications 連接 tools、data sources 和 workflows 的標準協定。MCP-enabled service 會把功能以 tool schema 暴露出來，讓 client 可以列出工具、呼叫工具、取得結構化結果。

**SORA 實作細節：**  
`sora/mcp_server.py` 提供 `get_stock_data` 和 `search_compliance_policy`。`sora/mcp_client.py` 預設先透過 MCP stdio 呼叫工具，如果 MCP server 不可用，會 fallback 到 local LangChain tools，避免整個 graph 因工具服務失敗而中斷。

**實務例子 A：**  
Market Analyst 需要即時資料時，不直接在 node 裡寫 yfinance 細節，而是透過 MCP client 呼叫 `get_stock_data`。這讓工具可以被其他 MCP-compatible client 重用。

**實務例子 B：**  
Compliance Reviewer 需要查政策時，透過 `search_compliance_policy` MCP tool 取得 rules。未來可把工具背後從 local Chroma 換成公司內部 policy search service。

**面試回答重點：**  
可以說：「MCP 的價值是把 tools 和 data sources 標準化。對企業 AI agent 來說，這能降低整合成本，也讓工具權限和 schema 更清楚。」

## 16. Third-party AI Platforms

**詳細說明：**  
Third-party AI platforms 包含外部 LLM provider、observability platform、vector database、UI framework、automation platform 等。使用第三方平台時，要考慮資料安全、API key 管理、成本、延遲、服務穩定性和可替換性。

**SORA 實作細節：**  
SORA 使用 OpenAI-compatible LLM endpoint、LangSmith、ChromaDB、Gradio。這些元件都透過環境變數或獨立模組隔離，讓替換更容易。

**實務例子 A：**  
LangSmith 可追蹤每次 graph run、LLM call 和 evaluator 結果。若發現某次回答缺少 disclosure，可以回看 trace 找出是 retrieval 沒命中還是 reviewer prompt 沒執行好。

**實務例子 B：**  
Gradio 適合 PoC，因為可以快速給 business users 試用。但 production 可能改成內部 web app，後端仍可重用 `sora.graph`。

**面試回答重點：**  
可以說：「第三方平台要用得快，也要留替換空間。我會用環境變數、清楚 interface 和測試，避免整個系統被單一平台綁死。」

## 17. AI Frameworks and Tools

**詳細說明：**  
AI frameworks and tools 是建構、測試、部署或開發 AI agent 的工具集合。它們不只包括 runtime frameworks，也包括 coding agents、AI IDE、evaluation tools 和 workflow platforms。選型時要看任務是否需要明確流程、角色協作、工具整合、可觀測性或工程自動化。

**SORA 實作細節：**  
SORA runtime 選擇 LangGraph、LangChain、Chroma、MCP、LangSmith、Gradio。開發階段可以用 OpenAI Codex 協助讀 repo、改程式、補測試、整理文件。

**實務例子 A：**  
如果任務需要清楚 state 和 conditional routing，例如金融報告必須進 compliance review，LangGraph 會比單一 agent loop 更容易控制。

**實務例子 B：**  
如果任務是工程開發，例如把 root wrapper files 移到 `sora/` package，OpenAI Codex 這類 coding agent 能閱讀專案、修改檔案並跑測試。

**面試回答重點：**  
可以說：「我會區分 runtime agent framework 和 coding assistant。LangGraph 是 runtime workflow framework；OpenAI Codex 是開發時協助工程落地的 coding agent。」

## 18. LangGraph

**詳細說明：**  
LangGraph 是用 graph 建構 agent workflow 的框架。它適合需要多節點、多分支、狀態管理和可控流程的場景。和純 LangChain chain 相比，LangGraph 更適合有循環、條件邏輯或多 agent 協作的系統。

**SORA 實作細節：**  
`sora/graph.py` 用 `StateGraph` 建立節點和 conditional edges。`START` 後進 router，根據 route 決定進 analyst 或 reviewer；analyst 完成後一定進 reviewer；reviewer 後進 `END`。

**實務例子 A：**  
如果 router 判斷是 `market_analysis`，graph 會先查市場資料，再做合規審查。這比在一個 prompt 裡要求模型「記得合規」可靠。

**實務例子 B：**  
如果未來新增 `news_analysis` node，可以在 graph 加一個分支，而不是重寫整個 prompt。

**面試回答重點：**  
可以說：「LangGraph 的優勢是讓 agent workflow 顯式化。對金融場景，我會用 graph 保證合規審查是流程的一部分。」

## 19. OpenAI Codex

**詳細說明：**  
OpenAI Codex 是 coding agent，用於軟體開發階段。它可以讀取 codebase、理解架構、修改檔案、執行測試、整理文件。它和 SORA 這種 runtime AI agent 不同：Codex 是幫工程師建系統的工具，SORA 是系統本身。

**SORA 實作細節：**  
Codex 可以協助重構 `sora/` package、撰寫 tests、更新 README file tree、補 RAG/MCP 文件、檢查 compileall 和 pytest 結果。

**實務例子 A：**  
工程師要求：「避免 root 和 `sora/` 有同名檔。」Codex 可以搜尋 imports、刪除 wrapper files、建立 `scripts/` entrypoints、更新測試和 README。

**實務例子 B：**  
工程師要求：「補一份 JD keywords 文件。」Codex 可以根據 JD 抽取概念，寫成面試 guide，並加測試確保文件被 repo 追蹤。

**面試回答重點：**  
可以說：「Codex 類工具能提升工程效率，但我仍會用 tests 和 verification 控制品質。AI coding assistant 不是取代工程流程，而是加速閱讀、修改和驗證。」

## 20. CrewAI

**詳細說明：**  
CrewAI 是偏角色分工的 multi-agent framework，常用 crew、agent、task 描述協作。它適合把任務拆成多個角色，例如 researcher、writer、reviewer，並讓每個 agent 執行指定 task。

**SORA 實作細節：**  
SORA 沒有使用 CrewAI，但概念上 Market Analyst 和 Compliance Reviewer 可以映射成 CrewAI agents。差別是 SORA 選 LangGraph，是因為它需要更明確的 state 和 conditional routing。

**實務例子 A：**  
如果用 CrewAI 做金融報告，可以設計 Research Agent 查市場資料、Writer Agent 寫初稿、Compliance Agent 審查聲明。

**實務例子 B：**  
如果任務偏創作或研究協作，例如產生 market newsletter，CrewAI 的角色式設計可能很直觀。

**面試回答重點：**  
可以說：「CrewAI 適合角色導向的協作任務；LangGraph 適合流程和狀態控制更嚴格的任務。SORA 的合規 guardrail 讓 LangGraph 更合適。」

## 21. AutoGen

**詳細說明：**  
AutoGen 是 multi-agent conversation framework，常見模式是多個 agents 透過對話互相協作，例如 assistant、critic、user proxy。它適合需要 agents 反覆討論、修正和協調的場景。

**SORA 實作細節：**  
SORA 沒有採用 AutoGen，因為金融合規流程需要 predictable path。若改用 AutoGen，可讓 Analyst 和 Reviewer 以對話方式迭代報告，但要額外控制成本、終止條件和合規一致性。

**實務例子 A：**  
Analyst 產生初稿後，Reviewer 回覆「缺少風險披露」，Analyst 再產生修正版，直到 Reviewer 接受。

**實務例子 B：**  
Developer Agent 寫測試，Critic Agent review 測試覆蓋率，再由 Developer Agent 修正程式。

**面試回答重點：**  
可以說：「AutoGen 適合對話式多 agent 協作，但金融 workflow 若需要明確保證某步驟必定發生，我會偏向 LangGraph。」

## 22. Claude Code, Cursor, Windsurf, OpenHands, Manus

**詳細說明：**  
這些工具多屬於 AI coding agent、AI IDE 或 autonomous software engineering tools。它們的目標是幫工程師閱讀專案、生成程式、補測試、修改 bug、執行任務。它們不是同一類 runtime framework，但都是 JD 所謂「agentic AI platforms」的相關工具。

**SORA 實作細節：**  
SORA runtime 不依賴這些工具，但開發者可以用它們改善 SORA。例如用 Cursor 編輯 prompt，用 Claude Code 做 code review，用 OpenHands 嘗試實作 issue，用 Manus 做較高層任務規劃。

**實務例子 A：**  
Cursor / Windsurf 適合在 IDE 中補全或修改 `sora/nodes.py`，例如調整 analyst prompt，讓模型不要忽略 yfinance output。

**實務例子 B：**  
OpenHands / Manus 類工具可以嘗試處理較長任務，例如新增 report export、接 Slack webhook、加入更多 evaluation cases。

**面試回答重點：**  
可以說：「我會把這些工具視為 AI-assisted development tools。它們能加速工程，但重要變更仍要靠版本控制、測試、review 和驗證。」

## 23. Data Preparation

**詳細說明：**  
Data preparation 是把原始資料整理成 AI 系統可使用的形式。它包含清理、去重、切分、標註、metadata 補充、格式轉換、資料品質檢查。RAG 系統尤其依賴資料準備，因為資料切不好，檢索再強也可能找錯內容。

**SORA 實作細節：**  
`dummy_compliance.txt` 被讀取後，每條規則會轉成 document，並附上 `rule_id`、`source` 等 metadata。這讓 reviewer 可以引用具體規則，而不是只說「根據政策」。

**實務例子 A：**  
如果 compliance policy 是一份長 PDF，不應直接整份塞進一個 chunk。應按規則、章節或條款切分，讓「Do not guarantee returns」成為獨立可檢索單位。

**實務例子 B：**  
如果不同版本政策混在一起，應加入 `effective_date` 和 `version` metadata，避免 agent 引用過期規則。

**面試回答重點：**  
可以說：「RAG 的效果很大程度取決於 data preparation。好的 chunking 和 metadata 會讓答案更準確，也讓 compliance review 更可追溯。」

## 24. Knowledge Base Structuring

**詳細說明：**  
Knowledge base structuring 是設計知識庫如何組織、切分、標記和檢索。它不只是把文件丟進 vector database，而是要考慮使用者會怎樣問、答案需要引用什麼、哪些 metadata 能幫助過濾和審查。

**SORA 實作細節：**  
SORA 的合規知識庫以 rule-level documents 為單位，使用 `rule_id` 追蹤。Reviewer final report 會列出 retrieved policy rules，讓輸出可被人審核。

**實務例子 A：**  
將「不得保證回報」、「必須揭露風險」、「非投資建議」分成不同 rules，可以讓 evaluator 檢查 query 是否命中正確 rule。

**實務例子 B：**  
在 production 裡，可以為每條 rule 加上 `jurisdiction=HK`、`department=compliance`、`risk_level=high`，讓 retrieval 先做 metadata filtering，再做 semantic search。

**面試回答重點：**  
可以說：「Knowledge base 不只是資料存放，而是 AI agent 的 grounding layer。結構越清楚，RAG 越容易評估和維護。」

## 25. RAG / Retrieval-Augmented Generation

**詳細說明：**  
RAG 是 Retrieval-Augmented Generation。流程是先從知識庫檢索相關內容，再把檢索結果交給 LLM 生成回答。它能降低 hallucination，讓答案引用內部資料或最新資料。RAG 的核心指標包括 retrieval quality、generation faithfulness、latency 和 coverage。

**SORA 實作細節：**  
SORA 的 Compliance Reviewer 必須呼叫 `search_compliance_policy`，至少取得一條 rule 或 fallback rule。final report 必須包含 retrieved policy rules、risk disclosure、not guaranteed returns 和 not investment advice。

**實務例子 A：**  
Query：`Can we promise guaranteed returns?`  
RAG 應檢索到 `RULE-001: Do not guarantee returns`。Reviewer 再把它轉成清楚回答：「不可以承諾或暗示固定回報，應改成風險中性的表述。」

**實務例子 B：**  
Query：`Should market commentary disclose risk?`  
RAG 應檢索到「Always disclose risks」。Reviewer 應在 final report 補上「Securities prices may fluctuate, and investors may lose principal」這類風險揭露。

**面試回答重點：**  
可以說：「RAG 的目標是讓 LLM grounded in retrieved evidence。在金融合規場景，我會要求 final answer 顯示引用的 rule，不能只給模型自由判斷。」

## 26. Vector Database / Database

**詳細說明：**  
Vector database 用向量儲存文字語意，支援 similarity search。它適合找語意相近但字面不同的內容。傳統 database 適合結構化查詢，例如按日期、部門、ID 過濾；vector database 適合自然語言語意檢索。實務上常把兩者結合。

**SORA 實作細節：**  
SORA 使用 ChromaDB 作為 local vector store。`sora/rag.py` 將 compliance rules embedding 後持久化到 `.chroma/`。`rag_evals.py` 量測 hit@1、hit@3、MRR、latency。

**實務例子 A：**  
使用者說「Can we promise profits?」和文件中的「Do not guarantee returns」字面不同，但語意接近。Vector search 應該能找回這條規則。

**實務例子 B：**  
如果 production 有上千條政策，可以先用 metadata 過濾 `department=compliance` 和 `jurisdiction=HK`，再做 vector similarity search，提升準確率和速度。

**面試回答重點：**  
可以說：「Vector database 解決語意搜尋，傳統 database 解決結構化過濾。好的 RAG 系統通常需要兩者配合，而不是只靠向量。」

## 27. Agent Testing

**詳細說明：**  
Agent testing 要測的不只是 final text，還包括 route 是否正確、tool 是否被呼叫、state 是否更新、RAG 是否命中、fallback 是否生效、錯誤是否可理解。因為 agent 是流程系統，不是單一函式，所以測試要覆蓋流程和邊界情況。

**SORA 實作細節：**  
SORA 有 tests 檢查 router、analyst、reviewer、LLM fallback、MCP fallback、RAG pipeline、README docs。這讓每次改 prompt 或重構 package 時，都能快速知道是否破壞流程。

**實務例子 A：**  
測試 analyst node 時 mock `call_tool`，確認 `Analyze AAPL stock` 會呼叫 `get_stock_data` 且 payload 是 `{"ticker": "AAPL"}`。

**實務例子 B：**  
測試 reviewer node 時 mock RAG 回傳 `RULE-001`，確認 final report 一定包含「Do not guarantee returns」和「not investment advice」。

**面試回答重點：**  
可以說：「Agent testing 要測行為鏈路，不只測文字相似度。我會把 routing、tool call、state update、RAG result 和 final guardrail 都納入測試。」

## 28. AI Agent Benchmarking

**詳細說明：**  
Benchmarking 是用固定 dataset 比較不同版本 agent 的表現。它可以追蹤 prompt 改動、模型替換、retrieval 設定調整後的效果。常見 metrics 包括 route accuracy、task success rate、compliance pass rate、hit@k、MRR、latency、cost。

**SORA 實作細節：**  
`evals.py` 使用 LangSmith evaluation 檢查 final response 是否包含 required compliance topics，以及 route 是否符合預期。`rag_evals.py` 則專注測 retrieval，輸出 hit@1、hit@3、MRR、average latency、p95 latency。

**實務例子 A：**  
比較 prompt v1 和 v2：如果 v2 的 compliance disclaimer pass rate 從 80% 提升到 100%，但 latency 增加很少，就可能值得採用。

**實務例子 B：**  
比較 embedding model：如果 model A hit@3 是 0.75，model B hit@3 是 1.0，但 model B latency 高很多，就要看業務是否更重視準確率或速度。

**面試回答重點：**  
可以說：「Benchmarking 讓 agent 改進變成可量化，而不是靠感覺。我會固定 dataset，追蹤 accuracy、latency、cost 和 compliance metrics。」

## 29. Evaluation Frameworks

**詳細說明：**  
Evaluation frameworks 是評估 AI output 的方法和工具。可以是 deterministic evaluator、LLM-as-judge、人手標註、golden dataset、online feedback。好的 evaluation 會同時看 correctness、faithfulness、safety、format、latency 和 user usefulness。

**SORA 實作細節：**  
SORA 使用 LangSmith `evaluate`，並寫 custom evaluator 檢查 response 是否包含風險揭露、不得保證回報、非投資建議等必要內容。

**實務例子 A：**  
Deterministic evaluator：檢查 final response 是否包含 `not investment advice`。這種方法簡單、穩定、成本低。

**實務例子 B：**  
LLM-as-judge：可以請另一個模型評估回答是否忠於 retrieved rules。但這需要控制 judge prompt、抽樣檢查和成本。

**面試回答重點：**  
可以說：「我會先用 deterministic evaluator 覆蓋硬性要求，再用 LLM-as-judge 或人工 review 評估較主觀的品質，例如清晰度和完整性。」

## 30. Accuracy

**詳細說明：**  
Accuracy 在 AI agent 中不是單一概念。它至少包含 routing accuracy、retrieval accuracy、tool accuracy、generation accuracy。金融場景還要看合規準確性，即答案是否避免誤導或違規措辭。

**SORA 實作細節：**  
SORA 的 route evaluator 檢查 query 是否走對流程；RAG evaluator 檢查是否找回 expected rule ids；compliance evaluator 檢查 final response 是否包含必要聲明。

**實務例子 A：**  
如果 `Analyze AAPL stock` 被路由到 `compliance_check`，即使回答文字流暢，也是不準確，因為它沒有完成市場分析任務。

**實務例子 B：**  
如果 guaranteed returns query 沒找回禁止保證回報的 rule，final answer 可能漏掉最重要風險，這是 retrieval accuracy 問題。

**面試回答重點：**  
可以說：「我會把 accuracy 拆成 routing、retrieval、generation 和 compliance accuracy，分別測量，才知道問題出在哪一層。」

## 31. Reliability

**詳細說明：**  
Reliability 是系統在不同錯誤情況下仍能可預期運作。AI agent 常見失敗包括 LLM timeout、工具 API 失敗、RAG 無結果、輸入格式奇怪、模型輸出不符合格式。可靠系統需要 fallback、timeout、error messages 和 tests。

**SORA 實作細節：**  
SORA 有 LLM fallback 和 MCP fallback。LLM 不可用時，router 和 report generation 可用 deterministic fallback；MCP server 不可用時，client 會呼叫 local tools。

**實務例子 A：**  
如果 MCP server 沒啟動，SORA 不應直接 crash，而是 fallback 到 local `get_stock_data`，並在 tool result 記錄 fallback reason。

**實務例子 B：**  
如果使用者輸入無效 ticker，工具應回傳清楚錯誤，例如 `No market data found`，而不是讓 exception 泄漏到 UI。

**面試回答重點：**  
可以說：「Reliability 對 agent 很重要，因為它依賴多個外部服務。我會加 timeout、fallback、structured error 和 regression tests。」

## 32. User Experience

**詳細說明：**  
User experience 在 AI agent 裡不只是介面好不好看，也包括使用者是否能理解答案來源、是否知道系統做了什麼、是否能信任結果。AI UX 要避免黑箱，尤其在金融和合規場景。

**SORA 實作細節：**  
`app.py` 用 Gradio 顯示 query input、final report 和 trace metadata，例如 route、ticker、compliance_status、message_count。Final report 也列出 retrieved policy rules。

**實務例子 A：**  
使用者問 HK50 價格時，metadata 顯示 route 是 `market_analysis`，ticker 是 `^HSI`，使用者就能理解系統把 HK50 alias 轉成 Hang Seng Index symbol。

**實務例子 B：**  
合規報告列出 `RULE-001`，讓 compliance user 可以追蹤回答依據，而不是只能相信模型說法。

**面試回答重點：**  
可以說：「AI UX 要提供透明度和可審核性。對 business users，我會顯示 route、資料來源、合規狀態和必要 disclaimers。」

## 33. Performance Optimization

**詳細說明：**  
Performance optimization 包含 latency、cost、token usage、tool calls、retrieval speed、UI response time。AI 系統的效能優化不是一味使用最快模型，而是根據任務選擇合適模型、流程和資料策略。

**SORA 實作細節：**  
SORA 用 router 避免所有 query 都查市場資料。MCP client 設定 timeout。RAG eval 量測 average latency 和 p95 latency。LLM fallback 讓測試和本地開發不依賴外部服務。

**實務例子 A：**  
純合規問題不需要 yfinance，因此直接走 reviewer 可降低 latency 和外部 API 依賴。

**實務例子 B：**  
如果 RAG p95 latency 太高，可以嘗試縮小 collection、改善 metadata filtering、快取常見 query、或使用更快 embedding/vector store。

**面試回答重點：**  
可以說：「Performance optimization 要從 workflow 層面看。少做不必要步驟，比單純換快模型更有效。」

## 34. Product, Operations, and Business Collaboration

**詳細說明：**  
AI agent 專案通常需要跨部門合作。Product 定義使用者流程和成功指標；Operations 提供實際痛點和例外情況；Business team 定義價值；Compliance 或 Legal 定義風險邊界；Engineering 負責落地。

**SORA 實作細節：**  
SORA 的設計把 research、operations、compliance 放在同一流程。文件和 eval reports 讓 non-technical stakeholders 能理解系統如何運作。

**實務例子 A：**  
Product 可能提出：「使用者需要在 30 秒內得到初稿。」Engineering 就要優化 route、tool latency 和 UI feedback。

**實務例子 B：**  
Compliance 可能提出：「任何市場報告都必須包含非投資建議聲明。」Engineering 就把這條要求寫進 reviewer node 和 evaluator。

**面試回答重點：**  
可以說：「AI agent 成功不只靠模型能力，還要和業務流程對齊。我會把 stakeholder requirement 轉成 workflow rule、test 和 evaluation metric。」

## 35. Documentation, Reports, Presentations, and Technical Summaries

**詳細說明：**  
AI initiative 需要不同層次文件：README 給工程和使用者；technical summary 給技術團隊；evaluation report 給決策者；presentation 給 management 或 business stakeholders。好文件會說清楚目的、架構、限制、測試結果和下一步。

**SORA 實作細節：**  
SORA 有 README、RAG guide、AI agent interview guide、JD keyword guide、RAG eval report。README 包含 project structure 和 run commands，幫助 reviewer 快速理解專案。

**實務例子 A：**  
技術文件應說明 `sora/graph.py` 如何連接 nodes，讓工程師能快速修改 workflow。

**實務例子 B：**  
業務報告應用簡單語言說明：「目前 RAG hit@3 是多少、平均延遲是多少、有哪些限制、下一步需要哪些真實資料。」

**面試回答重點：**  
可以說：「我會根據讀者寫文件。工程文件講架構和指令，業務文件講價值、風險和指標。」

## 36. Emerging AI Technologies

**詳細說明：**  
Emerging AI technologies 指快速發展的新技術，例如 MCP、agent frameworks、LLM observability、long-context models、multimodal models、RAG evaluation、AI coding agents。研究新技術時要看它是否解決真問題，而不是只因為熱門就採用。

**SORA 實作細節：**  
SORA 引入 MCP 作為 tool boundary，LangGraph 作為 workflow orchestration，LangSmith 作為 observability/evaluation，Chroma 作為 local vector database。

**實務例子 A：**  
評估 MCP 時，可以看它是否讓工具更容易重用、是否支援清楚 schema、是否能和公司內部服務整合。

**實務例子 B：**  
評估新 agent framework 時，可以用同一組 SORA benchmark 比較 route accuracy、latency、開發複雜度和可觀測性。

**面試回答重點：**  
可以說：「我會用 PoC 和 metrics 評估 emerging technology，而不是只看 demo。重點是它是否提升準確率、可靠性、效率或可維護性。」

## 37. AI Innovation, Experimentation, and Transformation Projects

**詳細說明：**  
AI innovation 和 transformation projects 是把新 AI 能力導入業務流程的探索。通常會先做 PoC 驗證可行性，再做 pilot，最後才 productionize。每個階段都要有成功指標和風險控制。

**SORA 實作細節：**  
SORA 是一個 PoC：先用 dummy compliance rules、local Chroma、Gradio UI 和 LangSmith eval 展示概念。若要 productionize，需要接真實政策庫、權限控制、審計日誌、部署和監控。

**實務例子 A：**  
PoC 階段：證明 agent 可以 route、查資料、做 RAG、產出合規版報告。

**實務例子 B：**  
Production 階段：加入 user authentication、role-based access control、真實 market data vendor、policy versioning、human approval workflow。

**面試回答重點：**  
可以說：「我會把 AI transformation 拆成 PoC、pilot、production 三階段。每階段都要定義 metrics，例如準確率、節省時間、風險事件數和使用者滿意度。」

## 38. Artificial Intelligence / Computer Science / Data Science / FinTech / Engineering

**詳細說明：**  
這些學科背景代表 AI agent 工作需要跨領域能力。AI 提供模型和方法；Computer Science 提供資料結構、系統設計和軟體工程；Data Science 提供評估和實驗方法；FinTech 提供金融產品、合規和市場資料理解；Engineering 負責可靠落地。

**SORA 實作細節：**  
SORA 結合了 AI models、LangGraph software architecture、RAG evaluation metrics、金融市場資料、合規聲明和工程測試。

**實務例子 A：**  
Data Science 思維會要求你不要只看一兩個 demo，而是建立 dataset 和 metrics，量化 route accuracy 和 RAG hit rate。

**實務例子 B：**  
FinTech 思維會提醒你：金融內容不能保證回報，必須揭露風險，並避免讓使用者誤解成個人投資建議。

**面試回答重點：**  
可以說：「我會把 AI、CS、Data Science 和 FinTech 結合起來。模型負責語意能力，工程保證可靠性，評估保證可量化，金融知識保證風險邊界。」

## 39. Curiosity, Problem-solving, and Strong Academic Foundation

**詳細說明：**  
JD 歡迎 fresh graduates，代表公司看重學習速度和問題解決能力。Strong curiosity 不是只追新工具，而是願意理解問題本質、做實驗、比較方案、承認限制並持續改進。

**SORA 實作細節：**  
SORA 可以作為作品集展示：它不是只用 LLM 寫一段回答，而是包含 LangGraph、MCP、RAG、LangSmith eval、tests、docs 和 README。這能展示學術基礎和工程落地能力。

**實務例子 A：**  
面試時可以展示：「我發現 LangSmith LLM call 是 0，追查後知道原本 nodes 沒有真正呼叫 ChatOpenAI，所以補了 `sora/llm.py` 和 LLM integration。」

**實務例子 B：**  
可以說明：「我發現模型回答沒有即時資料，但系統有 yfinance tool，所以我調整 workflow，要求 analyst 使用 tool output，而不是模型記憶。」

**面試回答重點：**  
可以說：「我對 AI agent 的興趣不只是使用工具，而是理解 agent 如何可靠地接工具、資料和評估。我用 SORA 展示從 PoC 到測試文件的完整思路。」

## Compact Interview Answer Templates

### Prompt Engineering

我會把 prompt engineering 視為工程問題，而不是單純寫提示詞。以 SORA 為例，router prompt 需要限制輸出為固定 label，analyst prompt 需要明確要求使用 yfinance tool output，reviewer prompt 則必須引用 retrieved compliance rules。這樣可以降低 parsing error、hallucination 和合規風險。

### Workflow Orchestration

我會用 LangGraph 做 workflow orchestration，因為它能把 AI workflow 拆成 nodes、state 和 conditional edges。SORA 的市場查詢會走 router -> analyst -> reviewer，合規查詢會走 router -> reviewer。這樣能保證市場報告一定經過 compliance review。

### Agent Testing and Benchmarking

我會測 route、tool call、state update、RAG retrieval、fallback 和 final response。Benchmarking 方面，我會用固定 dataset 追蹤 route accuracy、compliance disclaimer pass rate、hit@3、MRR、average latency 和 p95 latency。

### Performance Optimization

我會先減少不必要步驟，例如純合規問題不查 yfinance。再看 timeout、cache、retrieval filtering、模型選型和 token usage。對 agent 來說，好的 workflow design 往往比單純換快模型更有效。

### RAG and Database

我會先做好 data preparation 和 knowledge base structuring，把 policy 按 rule 切分，保留 rule_id、source、version 等 metadata。Vector database 負責語意搜尋，傳統 metadata filtering 負責縮小範圍。最後用 hit@1、hit@3、MRR 和 latency 評估 retrieval 效果。
