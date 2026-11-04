"""Load LLM settings from the environment."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    model: str


def load_settings() -> Settings:
    load_dotenv()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").strip()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
    if not api_key:
        raise RuntimeError(
            "LLM_API_KEY is not set. Copy .env.example to .env and add a key."
        )
    if not base_url:
        raise RuntimeError("LLM_BASE_URL is empty.")
    if not model:
        raise RuntimeError("LLM_MODEL is empty.")
    return Settings(api_key=api_key, base_url=base_url, model=model)


def describe_settings() -> dict:
    """Return non-secret status for the web UI."""
    load_dotenv()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").strip()
    model = os.getenv("LLM_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    return {
        "configured": bool(api_key),
        "base_url": base_url,
        "model": model,
    }
