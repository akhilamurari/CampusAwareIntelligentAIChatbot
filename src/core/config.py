from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Cisco-LaTrobe-Chatbot"

    # ── Sprint 4 (CF1CT-24 — Akhila): NIM Mode Switching ──
    NIM_MODE: str = "cloud"

    # ── NVIDIA Cloud API ──
    NIM_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""  # ← ADD THIS for ChatNVIDIA in nodes.py
    NIM_BASE_URL_CLOUD: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"  # ← ADD THIS

    # ── On-Premises NIM (aiotcentre-03) ──
    NIM_BASE_URL_ONPREM: str = "http://aiotcentre-03.latrobe.edu.au:8000/v1"

    # ── Sprint 3 (CF1CT-22 — Ansu): Model Configuration ──
    NIM_MODEL: str = "meta/llama-3.1-70b-instruct"
    MODEL_NAME: str = "meta/llama-3.1-70b-instruct"

    # ── Optional app mode flags ──
    AI_MODE: str = "nim"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

settings = Settings()