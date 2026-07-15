from pathlib import Path


def test_sora_package_exposes_core_modules():
    import sora.graph
    import sora.nodes
    import sora.rag
    import sora.tools

    assert hasattr(sora.graph, "build_graph")
    assert hasattr(sora.nodes, "analyst_node")
    assert hasattr(sora.rag, "get_vector_store")
    assert hasattr(sora.tools, "get_stock_data")


def test_readme_contains_file_tree_map():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "## Project Structure" in readme
    assert "sora/" in readme
    assert "docs/" in readme
    assert "tests/" in readme
    assert "app.py" in readme


def test_root_does_not_duplicate_sora_core_module_names():
    duplicate_prone_modules = [
        "state.py",
        "tools.py",
        "market_symbols.py",
        "llm.py",
        "nodes.py",
        "graph.py",
        "mcp_client.py",
        "mcp_server.py",
        "rag.py",
    ]

    existing_duplicates = [name for name in duplicate_prone_modules if Path(name).exists()]

    assert existing_duplicates == []
