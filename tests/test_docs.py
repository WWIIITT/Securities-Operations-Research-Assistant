from pathlib import Path


def test_rag_documentation_covers_pipeline_and_evaluation():
    content = Path("docs/rag.md").read_text(encoding="utf-8")

    for phrase in [
        "資料來源",
        "chunking",
        "embedding",
        "Chroma",
        "retrieval flow",
        "guardrail",
        "hit@3",
        "MRR",
    ]:
        assert phrase in content


def test_ai_agent_interview_guide_covers_required_topics_with_examples():
    content = Path("docs/ai_agent_interview_guide.md").read_text(encoding="utf-8")

    for phrase in [
        "Prompt engineering",
        "Workflow orchestration",
        "Agent testing",
        "Performance optimization",
        "RAG",
        "Vector database",
        "benchmarking",
        "user experience",
        "例子",
    ]:
        assert phrase in content


def test_jd_keyword_concepts_doc_covers_role_keywords_and_examples():
    content = Path("docs/jd_keyword_concepts.md").read_text(encoding="utf-8")

    for phrase in [
        "AI Agents",
        "agentic workflows",
        "prompt engineering",
        "workflow orchestration",
        "MCP",
        "RAG",
        "LangGraph",
        "OpenAI Codex",
        "benchmarking",
        "operational efficiency",
        "例子",
    ]:
        assert phrase in content
