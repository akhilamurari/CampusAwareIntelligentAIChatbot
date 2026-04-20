# src/nim_client.py
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

NIM_MODE = os.getenv("NIM_MODE", "cloud")

if NIM_MODE == "onprem":
    NIM_BASE_URL = os.getenv(
        "NIM_BASE_URL_ONPREM",
        "http://aiotcentre-03.latrobe.edu.au:8000/v1"
    )
    NIM_API_KEY = None
    print("🖥️  Using On-Premises NIM (aiotcentre-03)")
else:
    NIM_BASE_URL = os.getenv(
        "NIM_BASE_URL_CLOUD",
        "https://integrate.api.nvidia.com/v1"
    )
    NIM_API_KEY = os.getenv("NIM_API_KEY")
    print("☁️  Using NVIDIA Cloud API")

NIM_MODEL = os.getenv("NIM_MODEL", "meta/llama-3.1-70b-instruct")


def is_nim_running() -> bool:
    """Check if NIM server is up and running."""
    try:
        headers = {}
        if NIM_API_KEY:
            headers["Authorization"] = f"Bearer {NIM_API_KEY}"
        response = requests.get(
            f"{NIM_BASE_URL}/models",
            headers=headers,
            timeout=5
        )
        return response.status_code == 200
    except Exception:
        return False


def get_mode() -> str:
    """Return current NIM mode — cloud or onprem."""
    return NIM_MODE


def chat(user_message: str, system_prompt: str = None) -> str:
    """Send a message to NIM and get a response."""
    if not is_nim_running():
        if NIM_MODE == "onprem":
            return (
                "⚠️ On-premises NIM server (aiotcentre-03) is not available. "
                "IT ticket is raised — currently using Cloud API as fallback. "
                "Set NIM_MODE=cloud in .env to continue."
            )
        return "⚠️ NIM server is not available. Please check the server status."

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

    headers = {"Content-Type": "application/json"}
    if NIM_API_KEY:
        headers["Authorization"] = f"Bearer {NIM_API_KEY}"

    try:
        response = requests.post(
            f"{NIM_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error communicating with NIM: {str(e)}"


if __name__ == "__main__":
    print(f"Current NIM Mode: {get_mode().upper()}")
    print(f"NIM Base URL: {NIM_BASE_URL}")
    print(f"NIM Model: {NIM_MODEL}")
    print("─" * 50)
    print("Checking NIM server...")

    if is_nim_running():
        print(f"✅ NIM is running! ({get_mode().upper()})")
        response = chat("Hello! Are you working?")
        print(f"Response: {response}")
    else:
        if NIM_MODE == "onprem":
            print("❌ On-premises NIM not running — IT ticket pending")
            print("💡 Switch to cloud: set NIM_MODE=cloud in .env")
        else:
            print("❌ Cloud NIM not responding — check NIM_API_KEY in .env")
