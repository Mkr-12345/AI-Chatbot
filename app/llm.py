"""Thin wrapper around an OpenAI-compatible chat completions API."""

from openai import OpenAI

from app.config import Settings, load_settings


def build_client(settings: Settings | None = None) -> OpenAI:
    settings = settings or load_settings()
    return OpenAI(api_key=settings.api_key, base_url=settings.base_url)


def complete(messages: list[dict], settings: Settings | None = None, temperature: float = 0.7) -> str:
    settings = settings or load_settings()
    client = build_client(settings)
    response = client.chat.completions.create(
        model=settings.model,
        messages=messages,
        temperature=temperature,
    )
    content = response.choices[0].message.content
    return (content or "").strip()
