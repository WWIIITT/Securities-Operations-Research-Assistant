from __future__ import annotations

from typing import Any

from sora.graph import build_graph

APP_TITLE = "SORA - Securities Operations & Research Assistant"
DEFAULT_EXAMPLES = [
    "Analyze AAPL stock",
    "Can we promise guaranteed returns to clients?",
    "Review this statement: Tesla is guaranteed to outperform the market.",
    "What is the real time price of HK50 stock index?",
    "What is the current price of BTC in USD?",
]

APP_CSS = """
.sora-shell {max-width: 1180px; margin: 0 auto;}
.sora-title h1 {font-size: 28px; margin-bottom: 4px;}
.sora-title p {margin-top: 0; color: #475569;}
.sora-output textarea {font-family: ui-monospace, SFMono-Regular, Consolas, monospace;}
"""


def load_environment() -> None:
    """Load .env when python-dotenv is available."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def run_sora_query(query: str, graph_app: Any | None = None) -> tuple[str, dict[str, Any]]:
    """Run a user query through SORA and return the report plus trace-friendly metadata."""
    normalized_query = (query or "").strip()
    if not normalized_query:
        return (
            "Enter a financial or compliance question to run SORA.",
            {"status": "input_required"},
        )

    app = graph_app or build_graph()
    result = app.invoke({"messages": [{"role": "user", "content": normalized_query}]})
    report = result.get("analyst_report") or "SORA did not return a final report."

    metadata = {
        "status": "ok",
        "route": result.get("route", ""),
        "ticker": result.get("ticker", ""),
        "compliance_status": result.get("compliance_status", ""),
        "message_count": len(result.get("messages") or []),
    }
    return report, metadata


def build_demo() -> Any:
    """Create the Gradio UI. Gradio is imported lazily so tests can run without it."""
    try:
        import gradio as gr
    except ImportError as exc:
        raise RuntimeError(
            "gradio is required to launch the SORA UI. "
            "Install dependencies with: pip install -r requirements.txt"
        ) from exc

    load_environment()
    graph_app = build_graph()

    with gr.Blocks(title=APP_TITLE) as demo:
        gr.Markdown(
            "# SORA\nSecurities Operations & Research Assistant",
            elem_classes=["sora-title"],
        )
        with gr.Row(elem_classes=["sora-shell"]):
            with gr.Column(scale=4, min_width=320):
                query_box = gr.Textbox(
                    label="Query",
                    placeholder="Analyze AAPL stock",
                    lines=5,
                    autofocus=True,
                )
                run_button = gr.Button("Run analysis", variant="primary")
                gr.Examples(
                    examples=DEFAULT_EXAMPLES,
                    inputs=query_box,
                    label="Examples",
                )
            with gr.Column(scale=6, min_width=420):
                report_box = gr.Markdown(label="Final financial report")
                metadata_box = gr.JSON(label="Trace metadata")

        run_button.click(
            fn=lambda user_query: run_sora_query(user_query, graph_app=graph_app),
            inputs=query_box,
            outputs=[report_box, metadata_box],
        )
        query_box.submit(
            fn=lambda user_query: run_sora_query(user_query, graph_app=graph_app),
            inputs=query_box,
            outputs=[report_box, metadata_box],
        )

    return demo


def launch_demo() -> None:
    """Launch Gradio with visual configuration applied at runtime."""
    demo = build_demo()
    try:
        import gradio as gr
    except ImportError as exc:
        raise RuntimeError(
            "gradio is required to launch the SORA UI. "
            "Install dependencies with: pip install -r requirements.txt"
        ) from exc

    demo.launch(
        css=APP_CSS,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="cyan",
            neutral_hue="slate",
        ),
    )


if __name__ == "__main__":
    launch_demo()
