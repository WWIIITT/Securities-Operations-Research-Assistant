from pathlib import Path


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

    assert len(documents) >= 3
    assert all(document.page_content.strip() for document in documents)
    assert all(document.metadata["source"] == "dummy_compliance.txt" for document in documents)
    assert documents[0].metadata["rule_id"] == "RULE-001"


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
