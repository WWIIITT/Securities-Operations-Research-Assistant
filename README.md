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

The model itself does not know live prices. SORA must retrieve current market data through tools: `get_stock_data` uses yfinance, and nodes access it through the MCP client wrapper. Common index aliases such as `HK50` and `HSI` are mapped to yfinance symbols such as `^HSI`.

## Run

Initialize the local compliance vector store:

```powershell
python rag.py
```

Launch the Gradio app:

```powershell
python app.py
```

Run the local stdio MCP server directly for smoke testing:

```powershell
python mcp_server.py
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
python -m compileall .
```

## Notes

- `Analyze AAPL stock` routes through the market analyst and then the compliance reviewer.
- `Can we promise guaranteed returns?` routes directly to compliance review.
- The final report always includes retrieved compliance rules or a fallback disclosure rule.
- LangSmith LLM call counts only appear when the LLM-backed nodes successfully call `ChatOpenAI`; embedding or deterministic fallback paths are not chat-model analysis calls.
- MCP defaults to `MCP_ENABLED=true`; if the MCP package/server is unavailable, `mcp_client.py` falls back to local LangChain tools and records the fallback reason in the tool result.
- For live market questions, the LLM should summarize tool output. It should not answer from model memory or claim that no real-time data is available when yfinance returned current data.
- RAG details live in `docs/rag.md`; AI agent interview notes live in `docs/ai_agent_interview_guide.md`.
