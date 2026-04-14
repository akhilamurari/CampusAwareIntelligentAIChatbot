# src/nim_client.py
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# NIM server configuration (can be overridden via .env)
NIM_BASE_URL = os.getenv(
    "NIM_BASE_URL",
    "http://aiotcentre-03.latrobe.edu.au:8000/v1"
)
NIM_MODEL = os.getenv("NIM_MODEL", "meta/llama-3.1-8b-instruct")


def is_nim_running() -> bool:
    """Check if NIM server is up and running."""
    try:
        response = requests.get(f"{NIM_BASE_URL}/models", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def chat(user_message: str, system_prompt: str = None) -> str:
    """Send a message to NIM and get a response."""
    if not is_nim_running():
        return "NIM server is not available. Please check the server status."

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": NIM_MODEL,
        "messages": messages,
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            f"{NIM_BASE_URL}/chat/completions",
            json=payload,
            timeout=30
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error communicating with NIM: {str(e)}"


if __name__ == "__main__":
    print("Checking NIM server...")
    if is_nim_running():
        print("✅ NIM is running!")
        response = chat("Hello! Are you working?")
        print(f"Response: {response}")
    else:
        print("❌ NIM is not running yet — waiting on IT ticket")