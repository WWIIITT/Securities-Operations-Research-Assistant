# SORA - Securities Operations & Research Assistant

SORA is a production-style multi-agent PoC for routing financial queries between a market analyst and a compliance reviewer. It uses LangGraph for orchestration, LangChain tools, ChromaDB for local compliance RAG, Gradio for the UI, and LangSmith for tracing and evaluation.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `LLM_API_KEY`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, and any endpoint/model overrides. The default LangSmith endpoint is `https://api.smith.langchain.com`.

## Run

Initialize the local compliance vector store:

```powershell
python rag.py
```

Launch the Gradio app:

```powershell
python app.py
```

Run LangSmith evaluation after setting a LangSmith key:

```powershell
python evals.py
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
