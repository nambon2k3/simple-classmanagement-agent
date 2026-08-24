"""Settings validation tests."""

from __future__ import annotations

from app.core.config import Settings


def test_groq_base_url_strips_openai_v1_suffix():
    settings = Settings(groq_base_url="https://api.groq.com/openai/v1")
    assert settings.groq_base_url == "https://api.groq.com"


def test_groq_base_url_defaults_to_api_root():
    settings = Settings()
    assert settings.groq_base_url == "https://api.groq.com"
