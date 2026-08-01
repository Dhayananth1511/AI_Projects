"""
config.py — Centralised application configuration.

Reads environment variables from the OS or from a local `.env` file
(via python-dotenv). Never hard-code secrets in this file; put real
values in `.env` and keep that file out of version control.
"""

import os
from dotenv import load_dotenv

# Load .env file if present (development only)
load_dotenv()


class Config:
    # ── Security ──────────────────────────────────────────────
    # Generate a strong key:  python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")

    # ── Database ──────────────────────────────────────────────
    # Leave MONGO_URI blank to fall back to local SQLite (chats.db)
    MONGO_URI: str | None = os.getenv("MONGO_URI") or None

    # ── Hugging Face Inference API ────────────────────────────
    HF_TOKEN: str | None  = os.getenv("HF_TOKEN")
    HF_API_URL: str       = "https://router.huggingface.co/v1/chat/completions"
    MODEL: str            = os.getenv("LLM_MODEL", "meta-llama/Llama-3.1-8B-Instruct")

    # ── Google OAuth ──────────────────────────────────────────
    # Obtain at: https://console.cloud.google.com > APIs & Services > Credentials
    GOOGLE_CLIENT_ID: str | None = os.getenv("GOOGLE_CLIENT_ID") or None
