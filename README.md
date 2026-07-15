# SORA - Securities Operations & Research Assistant

SORA is a production-style multi-agent PoC for routing financial queries between a market analyst and a compliance reviewer. It uses LangGraph for orchestration, LangChain tools, ChromaDB for local compliance RAG, MCP for local tool boundaries, Gradio for the UI, and LangSmith for tracing and evaluation.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `LLM_API_KEY`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, and any endpoint/model overrides. The default LangSmith endpoint is `https://api.smith.langchain.com`.

The LLM-backed nodes use `LLM_MODEL` through `langchain-openai` / `ChatOpenAI`. If `LLM_API_KEY` is missing or the model endpoint is unavailable, SORA falls back to deterministic routing and template reports so local tests still run.

The model itself does not know live prices. SORA retrieves current market data through tools: `get_stock_data` uses yfinance, `get_crypto_price` calls the external CoinGecko API through MCP, and nodes access both through the MCP client wrapper. Common index aliases such as `HK50` and `HSI` are mapped to yfinance symbols such as `^HSI`.

Runtime calls are bounded by timeout settings so slow external APIs do not make one query hang for minutes. The defaults are `LLM_TIMEOUT_SECONDS=8`, `EMBEDDING_TIMEOUT_SECONDS=8`, `YFINANCE_TIMEOUT_SECONDS=8`, `EXTERNAL_API_TIMEOUT_SECONDS=8`, `LLM_MAX_RETRIES=0`, and `EMBEDDING_MAX_RETRIES=0`.

## Run

Initialize the local compliance vector store:

```powershell
python scripts/init_rag.py
```

Launch the Gradio app:

```powershell
python app.py
```

Run the local stdio MCP server directly for smoke testing:

```powershell
python scripts/run_mcp_server.py
```

Run LangSmith evaluation after setting a LangSmith key:

```powershell
python evals.py
```

Run RAG retrieval efficiency evaluation:

```powershell
python rag_evals.py
```

Run tests:

```powershell
python -m pytest tests -q
python -m compileall app.py evals.py rag_evals.py scripts sora tests
```

## Project Structure

```text
Securities-Operations-Research-Assistant/
|-- app.py                         # Gradio UI entrypoint
|-- evals.py                       # LangSmith evaluation entrypoint
|-- rag_evals.py                   # RAG retrieval benchmark entrypoint
|-- scripts/                       # CLI wrappers; avoids root/core module name clashes
|   |-- init_rag.py                # Chroma vector-store initialization
|   `-- run_mcp_server.py          # Local stdio MCP server launcher
|-- data/                          # Categorized RAG source documents
|   |-- compliance/
|   |-- market/
|   |-- products/
|   `-- risk/
|-- sora/                          # Core SORA package
|   |-- graph.py                   # LangGraph workflow construction
|   |-- nodes.py                   # Router, market analyst, compliance reviewer nodes
|   |-- llm.py                     # ChatOpenAI / OpenAI-compatible model factory
|   |-- mcp_client.py              # MCP-first tool caller with local fallback
|   |-- mcp_server.py              # FastMCP tool server implementation
|   |-- tools.py                   # yfinance, external crypto, and compliance RAG LangChain tools
|   |-- rag.py                     # Chroma vector-store pipeline
|   |-- market_symbols.py          # Market/index alias mapping, e.g. HK50 -> ^HSI
|   `-- state.py                   # LangGraph AgentState TypedDict
|-- docs/
|   |-- rag.md                     # RAG pipeline and retrieval evaluation guide
|   |-- rag/                       # Category-specific RAG operations docs
|   |-- ai_agent_interview_guide.md
|   `-- jd_keyword_concepts.md     # JD keyword map with examples
|-- tests/                         # Unit, integration, and regression tests
|-- dummy_compliance.txt           # Legacy fallback sample compliance rules
|-- requirements.txt
`-- README.md
```

Root-level files are reserved for app/evaluation entrypoints and documentation. Core modules live under `sora/` only, so imports should use `sora.graph`, `sora.nodes`, `sora.rag`, and related package paths.

## Notes

- `Analyze AAPL stock` routes through the market analyst and then the compliance reviewer.
- `What is Bitcoin price now?` routes through the external crypto MCP tool and then the compliance reviewer.
- `Can we promise guaranteed returns?` routes directly to compliance review.
- RAG loads categorized source documents from `data/` by default; `dummy_compliance.txt` is only a legacy fallback.
- The final report always includes retrieved compliance rules or a fallback disclosure rule.
- LangSmith LLM call counts only appear when the LLM-backed nodes successfully call `ChatOpenAI`; embedding or deterministic fallback paths are not chat-model analysis calls.
- MCP defaults to `MCP_ENABLED=true`; if the MCP package/server is unavailable, `sora.mcp_client` falls back to local LangChain tools and records the fallback reason in the tool result.
- For live market questions, the LLM should summarize tool output. It should not answer from model memory or claim that no real-time data is available when yfinance returned current data.
- If a provider is slow, lower `LLM_TIMEOUT_SECONDS`, `EMBEDDING_TIMEOUT_SECONDS`, `YFINANCE_TIMEOUT_SECONDS`, `EXTERNAL_API_TIMEOUT_SECONDS`, or set `LLM_ENABLED=false` for deterministic local fallback during demos.
- RAG details live in `docs/rag.md`; AI agent interview notes live in `docs/ai_agent_interview_guide.md`; JD keyword explanations live in `docs/jd_keyword_concepts.md`.
