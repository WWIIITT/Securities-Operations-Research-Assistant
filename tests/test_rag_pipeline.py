from pathlib import Path
from types import SimpleNamespace


class FakeVectorStore:
    last_call = None

    @classmethod
    def from_documents(cls, documents, embedding, collection_name, persist_directory):
        cls.last_call = {
            "documents": documents,
            "embedding": embedding,
            "collection_name": collection_name,
            "persist_directory": persist_directory,
        }
        return cls()


def test_dummy_compliance_file_contains_required_rules():
    content = Path("dummy_compliance.txt").read_text(encoding="utf-8")

    assert "Do not guarantee returns" in content
    assert "Always disclose risks" in content
    assert "not investment advice" in content.lower()


def test_load_policy_documents_creates_one_document_per_rule():
    from sora.rag import load_policy_documents

    documents = load_policy_documents()

    assert len(documents) >= 8
    assert all(document.page_content.strip() for document in documents)
    assert all(document.metadata["source"].startswith(("compliance/", "market/", "products/", "risk/")) for document in documents)
    assert {document.metadata["category"] for document in documents} >= {
        "compliance",
        "market",
        "products",
        "risk",
    }
    assert documents[0].metadata["rule_id"].startswith("COMPLIANCE-")


def test_load_policy_documents_reads_all_supported_files_from_data_directory(tmp_path):
    from sora.rag import load_policy_documents

    compliance_dir = tmp_path / "compliance"
    risk_dir = tmp_path / "risk"
    compliance_dir.mkdir()
    risk_dir.mkdir()
    (compliance_dir / "rules.txt").write_text(
        "Do not guarantee returns.\nAlways disclose risks.\n",
        encoding="utf-8",
    )
    (risk_dir / "crypto.md").write_text(
        "# Crypto\n- Digital assets may be volatile.\n",
        encoding="utf-8",
    )

    documents = load_policy_documents(data_directory=tmp_path)

    assert [document.page_content for document in documents] == [
        "Do not guarantee returns.",
        "Always disclose risks.",
        "Digital assets may be volatile.",
    ]
    assert [document.metadata["category"] for document in documents] == [
        "compliance",
        "compliance",
        "risk",
    ]
    assert documents[2].metadata["section"] == "Crypto"


def test_initialize_vector_store_uses_documents_and_persistent_chroma_path(tmp_path):
    from sora.rag import COLLECTION_NAME, initialize_vector_store

    embedding = object()

    vector_store = initialize_vector_store(
        persist_directory=tmp_path,
        embeddings=embedding,
        vector_store_cls=FakeVectorStore,
    )

    assert isinstance(vector_store, FakeVectorStore)
    assert FakeVectorStore.last_call["embedding"] is embedding
    assert FakeVectorStore.last_call["collection_name"] == COLLECTION_NAME
    assert FakeVectorStore.last_call["persist_directory"] == str(tmp_path)
    assert len(FakeVectorStore.last_call["documents"]) >= 3


def test_build_embeddings_sets_timeout_and_disables_retries(monkeypatch):
    import sys
    from sora.rag import build_embeddings

    captured = {}

    class FakeOpenAIEmbeddings:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setitem(
        sys.modules,
        "langchain_openai",
        SimpleNamespace(OpenAIEmbeddings=FakeOpenAIEmbeddings),
    )
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("EMBEDDING_TIMEOUT_SECONDS", "6")
    monkeypatch.setenv("EMBEDDING_MAX_RETRIES", "0")

    build_embeddings()

    assert captured["timeout"] == 6.0
    assert captured["max_retries"] == 0
