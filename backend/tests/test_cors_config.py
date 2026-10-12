from app.core.config import Settings


def test_cors_origins_default_to_local_vite_origins(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://user:pass@localhost/db",
    )

    assert settings.cors_origin_list == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def test_cors_origins_parse_comma_separated_values_and_trim_whitespace():
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://user:pass@localhost/db",
        cors_origins=" https://rbi-saathi.pages.dev, https://example.org ,, ",
    )

    assert settings.cors_origin_list == [
        "https://rbi-saathi.pages.dev",
        "https://example.org",
    ]
