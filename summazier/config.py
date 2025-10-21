from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv(override=False)


@dataclass(frozen=True)
class AppConfig:
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    provider: str = "openai"  # "openai" or "ollama"
    base_url: str | None = None  # e.g., http://localhost:11434 for Ollama
    default_role: str = (
        "You are a research analyst in biomedical AI. Your outputs must be rigorous, "
        "concise, faithful to the paper, and useful for downstream research."
    )
    max_words_default: int = 300
    output_dir: str = "output"
    tmp_dir: str = "tmp"

    @staticmethod
    def from_env() -> "AppConfig":
        provider = os.getenv("PROVIDER", "openai").strip().lower()
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if provider == "openai" and not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set. Provide it via env or .env, or set PROVIDER=ollama.")
        return AppConfig(
            openai_api_key=api_key,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            provider=provider,
            base_url=os.getenv("BASE_URL") or None,
            default_role=os.getenv("DEFAULT_ROLE", AppConfig.default_role),
            max_words_default=int(os.getenv("MAX_WORDS", str(AppConfig.max_words_default))),
            output_dir=os.getenv("OUTPUT_DIR", "output"),
            tmp_dir=os.getenv("TMP_DIR", "tmp"),
        )


def ensure_directories_exist(config: AppConfig) -> None:
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.tmp_dir, exist_ok=True)
