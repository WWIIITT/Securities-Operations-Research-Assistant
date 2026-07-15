from __future__ import annotations

import os
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

DEFAULT_LLM_MODEL = "gpt-4o-mini"
DEFAULT_LLM_BASE_URL = "https://api.vectorengine.cn/v1"
DEFAULT_LLM_TIMEOUT_SECONDS = 8.0
DEFAULT_LLM_MAX_RETRIES = 0


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


def build_chat_model(**overrides: Any) -> Any:
    """Build the OpenAI-compatible chat model used by SORA nodes."""
    if load_dotenv:
        load_dotenv()

    if os.getenv("LLM_ENABLED", "true").strip().lower() in {"0", "false", "no", "off"}:
        raise RuntimeError("LLM-backed analysis is disabled by LLM_ENABLED=false.")

    if ChatOpenAI is None:
        raise RuntimeError("langchain-openai is required for LLM-backed SORA nodes.")

    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("LLM_API_KEY or OPENAI_API_KEY is required for LLM-backed analysis.")

    kwargs: dict[str, Any] = {
        "model": os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL),
        "api_key": api_key,
        "base_url": os.getenv("LLM_BASE_URL", DEFAULT_LLM_BASE_URL),
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.1")),
        "timeout": _env_float("LLM_TIMEOUT_SECONDS", DEFAULT_LLM_TIMEOUT_SECONDS),
        "max_retries": _env_int("LLM_MAX_RETRIES", DEFAULT_LLM_MAX_RETRIES),
    }
    kwargs.update(overrides)
    return ChatOpenAI(**kwargs)


def message_content(response: Any) -> str:
    """Normalize a LangChain chat model response to text."""
    content = getattr(response, "content", response)
    if isinstance(content, list):
        return "\n".join(str(part) for part in content)
    return str(content or "").strip()
