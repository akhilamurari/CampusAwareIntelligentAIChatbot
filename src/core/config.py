"""
config.py
---------
Application configuration settings for CampusAware AI.
Uses pydantic-settings to load environment variables from .env file.

Environment Variables:
    NIM_MODE: "cloud" or "onprem" — switches between NVIDIA Cloud API and on-premises vLLM
    NIM_API_KEY: NVIDIA Cloud API key (required for cloud mode)
    NIM_BASE_URL_CLOUD: NVIDIA Cloud API endpoint
    NIM_BASE_URL_ONPREM: On-premises vLLM endpoint (default: localhost:8000)
    NIM_MODEL: Model name/path to use

Author: Ansu, Akhila
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.

    Supports two deployment modes:
        - cloud:  Uses NVIDIA NIM Cloud API (requires API key)
        - onprem: Uses local vLLM server on aiotcentre-03 (no API key needed)

    Example .env for on-premises:
        NIM_MODE=onprem
        NIM_BASE_URL_ONPREM=http://localhost:8000/v1
        NIM_MODEL=/data/shared/nobackup/Qwen2.5-7B-Instruct
        NIM_API_KEY=not-required

    Example .env for cloud:
        NIM_MODE=cloud
        NIM_API_KEY=nvapi-xxxxx
        NIM_MODEL=meta/llama-3.1-70b-instruct
    """

    # ── Application ────────────────────────────────────────────────────────────
    APP_NAME: str = "CampusAware-AI-Chatbot"

    # ── Deployment Mode ────────────────────────────────────────────────────────
    # "cloud"  → NVIDIA NIM Cloud API
    # "onprem" → On-premises vLLM on aiotcentre-03
    NIM_MODE: str = "cloud"

    # ── NVIDIA Cloud API ───────────────────────────────────────────────────────
    NIM_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""
    NIM_BASE_URL_CLOUD: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"

    # ── On-Premises vLLM (aiotcentre-03) ──────────────────────────────────────
    NIM_BASE_URL_ONPREM: str = "http://localhost:8000/v1"

    # ── Model Configuration ────────────────────────────────────────────────────
    # Cloud default:   meta/llama-3.1-70b-instruct
    # On-prem default: /data/shared/nobackup/Qwen2.5-7B-Instruct
    NIM_MODEL: str = "meta/llama-3.1-70b-instruct"
    MODEL_NAME: str = "meta/llama-3.1-70b-instruct"

    # ── Optional Flags ─────────────────────────────────────────────────────────
    AI_MODE: str = "nim"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Global settings instance — import this in other modules
settings = Settings()