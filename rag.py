from __future__ import annotations

import os
from pathlib import Path
from typing import Any

DEFAULT_POLICY_PATH = Path("dummy_compliance.txt")
DEFAULT_PERSIST_DIRECTORY = Path(".chroma")
COLLECTION_NAME = "sora_compliance_rules"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


try:
    from langchain_core.documents import Document
except ImportError:  # Keeps local contract tests useful before dependencies are installed.
    class Document:
        def __init__(self, page_content: str, metadata: dict[str, Any] | None = None):
            self.page_content = page_content
            self.metadata = metadata or {}


def load_policy_documents(policy_path: str | Path = DEFAULT_POLICY_PATH) -> list[Document]:
    """Load one compliance rule per non-empty line from the local policy file."""
    path = Path(policy_path)
    if not path.exists():
        raise FileNotFoundError(f"Compliance policy file not found: {path}")

    lines = [
        line.strip().lstrip("-*0123456789. ")
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    return [
        Document(
            page_content=line,
            metadata={
                "source": path.name,
                "rule_id": f"RULE-{index:03d}",
            },
        )
        for index, line in enumerate(lines, start=1)
    ]


def build_embeddings() -> Any:
    """Create OpenAI-compatible embeddings using the same endpoint style as the LLM."""
    try:
        from langchain_openai import OpenAIEmbeddings
    except ImportError as exc:
        raise RuntimeError(
            "langchain-openai is required to create embeddings. "
            "Install dependencies before initializing the vector store."
        ) from exc

    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)

    kwargs: dict[str, Any] = {"model": model}
    if api_key:
        kwargs["api_key"] = api_key
    if base_url:
        kwargs["base_url"] = base_url

    return OpenAIEmbeddings(**kwargs)


def initialize_vector_store(
    policy_path: str | Path = DEFAULT_POLICY_PATH,
    persist_directory: str | Path = DEFAULT_PERSIST_DIRECTORY,
    collection_name: str = COLLECTION_NAME,
    embeddings: Any | None = None,
    vector_store_cls: Any | None = None,
) -> Any:
    """Create or refresh the local Chroma compliance vector store."""
    if vector_store_cls is None:
        try:
            from langchain_chroma import Chroma
        except ImportError as exc:
            raise RuntimeError(
                "langchain-chroma is required to initialize the compliance vector store."
            ) from exc
        vector_store_cls = Chroma

    documents = load_policy_documents(policy_path)
    if not documents:
        raise ValueError(f"No compliance rules found in {policy_path}.")

    persist_path = Path(persist_directory)
    persist_path.mkdir(parents=True, exist_ok=True)

    return vector_store_cls.from_documents(
        documents=documents,
        embedding=embeddings or build_embeddings(),
        collection_name=collection_name,
        persist_directory=str(persist_path),
    )


def get_vector_store(
    persist_directory: str | Path = DEFAULT_PERSIST_DIRECTORY,
    collection_name: str = COLLECTION_NAME,
    embeddings: Any | None = None,
    vector_store_cls: Any | None = None,
) -> Any:
    """Return an existing Chroma store, initializing it from the policy file when needed."""
    if vector_store_cls is None:
        try:
            from langchain_chroma import Chroma
        except ImportError as exc:
            raise RuntimeError(
                "langchain-chroma is required to search the compliance vector store."
            ) from exc
        vector_store_cls = Chroma

    persist_path = Path(persist_directory)
    if not persist_path.exists():
        return initialize_vector_store(
            persist_directory=persist_path,
            collection_name=collection_name,
            embeddings=embeddings,
            vector_store_cls=vector_store_cls,
        )

    return vector_store_cls(
        collection_name=collection_name,
        persist_directory=str(persist_path),
        embedding_function=embeddings or build_embeddings(),
    )


if __name__ == "__main__":
    store = initialize_vector_store()
    print(f"Initialized Chroma collection '{COLLECTION_NAME}' at {DEFAULT_PERSIST_DIRECTORY}.")
    print(f"Loaded {len(load_policy_documents())} compliance rules.")
