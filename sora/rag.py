from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

DEFAULT_DATA_DIRECTORY = Path("data")
DEFAULT_POLICY_PATH = Path("dummy_compliance.txt")
DEFAULT_PERSIST_DIRECTORY = Path(".chroma")
COLLECTION_NAME = "sora_compliance_rules"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_EMBEDDING_TIMEOUT_SECONDS = 8.0
DEFAULT_EMBEDDING_MAX_RETRIES = 0
SUPPORTED_DATA_EXTENSIONS = {".txt", ".md"}


try:
    from langchain_core.documents import Document
except ImportError:  # Keeps local contract tests useful before dependencies are installed.
    class Document:
        def __init__(self, page_content: str, metadata: dict[str, Any] | None = None):
            self.page_content = page_content
            self.metadata = metadata or {}


def _clean_rule_line(line: str) -> str:
    return line.strip().lstrip("-*0123456789. ").strip()


def _category_from_path(path: Path, data_directory: Path) -> str:
    try:
        relative = path.relative_to(data_directory)
    except ValueError:
        return path.parent.name or "general"
    return relative.parts[0] if len(relative.parts) > 1 else "general"


def _rule_prefix(category: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", category).strip("_")
    return (normalized or "RULE").upper()


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _load_single_policy_file(
    policy_path: str | Path,
    *,
    category: str = "legacy",
    source_name: str | None = None,
) -> list[Document]:
    """Load one rule per non-empty line from a single policy file."""
    path = Path(policy_path)
    if not path.exists():
        raise FileNotFoundError(f"Compliance policy file not found: {path}")

    source = source_name or path.name
    lines = [_clean_rule_line(line) for line in path.read_text(encoding="utf-8").splitlines()]
    lines = [line for line in lines if line]

    return [
        Document(
            page_content=line,
            metadata={
                "source": source,
                "category": category,
                "rule_id": f"{_rule_prefix(category)}-{index:03d}",
                "file_type": path.suffix.lower(),
            },
        )
        for index, line in enumerate(lines, start=1)
    ]


def load_data_documents(data_directory: str | Path = DEFAULT_DATA_DIRECTORY) -> list[Document]:
    """Load RAG documents from categorized files under the data directory."""
    root = Path(data_directory)
    if not root.exists():
        return []

    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_DATA_EXTENSIONS
    )
    documents: list[Document] = []
    category_counts: dict[str, int] = {}

    for path in files:
        category = _category_from_path(path, root)
        source = path.relative_to(root).as_posix()
        section = ""
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                section = stripped.lstrip("#").strip()
                continue

            content = _clean_rule_line(stripped)
            if not content:
                continue

            category_counts[category] = category_counts.get(category, 0) + 1
            metadata = {
                "source": source,
                "category": category,
                "rule_id": f"{_rule_prefix(category)}-{category_counts[category]:03d}",
                "file_type": path.suffix.lower(),
            }
            if section:
                metadata["section"] = section

            documents.append(Document(page_content=content, metadata=metadata))

    return documents


def load_policy_documents(
    policy_path: str | Path | None = None,
    data_directory: str | Path = DEFAULT_DATA_DIRECTORY,
) -> list[Document]:
    """Load policy/RAG documents, preferring categorized files under data/."""
    if policy_path is not None:
        return _load_single_policy_file(policy_path)

    documents = load_data_documents(data_directory)
    if documents:
        return documents

    if DEFAULT_POLICY_PATH.exists():
        return _load_single_policy_file(DEFAULT_POLICY_PATH)

    raise FileNotFoundError(
        f"No RAG data files found in {data_directory} and fallback file "
        f"{DEFAULT_POLICY_PATH} does not exist."
    )


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
    kwargs["timeout"] = _env_float("EMBEDDING_TIMEOUT_SECONDS", DEFAULT_EMBEDDING_TIMEOUT_SECONDS)
    kwargs["max_retries"] = _env_int("EMBEDDING_MAX_RETRIES", DEFAULT_EMBEDDING_MAX_RETRIES)

    return OpenAIEmbeddings(**kwargs)


def initialize_vector_store(
    policy_path: str | Path | None = None,
    data_directory: str | Path = DEFAULT_DATA_DIRECTORY,
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

    documents = load_policy_documents(policy_path=policy_path, data_directory=data_directory)
    if not documents:
        raise ValueError(f"No RAG documents found in {data_directory}.")

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
