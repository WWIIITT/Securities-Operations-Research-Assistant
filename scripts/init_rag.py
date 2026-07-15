from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sora.rag import COLLECTION_NAME, DEFAULT_PERSIST_DIRECTORY, initialize_vector_store


def main() -> None:
    initialize_vector_store()
    print(
        "Initialized SORA compliance vector store "
        f"collection={COLLECTION_NAME} path={DEFAULT_PERSIST_DIRECTORY}"
    )


if __name__ == "__main__":
    main()
