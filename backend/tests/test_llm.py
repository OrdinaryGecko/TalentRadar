from app.llm import LLMSettings


def test_llm_settings_from_env(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("LLM_MODEL", "llama-3.3-70b-versatile")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "45")

    settings = LLMSettings.from_env()

    assert settings.provider == "groq"
    assert settings.model == "llama-3.3-70b-versatile"
    assert settings.api_key == "test-key"
    assert settings.base_url == "https://api.groq.com/openai/v1"
    assert settings.timeout_seconds == 45.0
