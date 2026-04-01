from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Cisco-LaTrobe-Chatbot"

    # NVIDIA NIM
    NVIDIA_API_KEY: str
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    MODEL_NAME: str = "meta/llama-3.1-8b-instruct"

    # Optional app mode flags
    AI_MODE: str = "nim"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()