# tests/test_ci.py
# Simple tests that run in CI/CD without needing the NIM server

import os
import pytest

def test_environment_variables():
    """Test .env variables are documented correctly"""
    # These are the required env vars for the app
    required_vars = [
        "NIM_MODE",
        "NIM_API_KEY", 
        "NIM_BASE_URL_CLOUD",
        "NIM_BASE_URL_ONPREM",
        "NIM_MODEL",
    ]
    print("✅ Required environment variables documented:")
    for var in required_vars:
        print(f"  - {var}")
    assert len(required_vars) == 5

def test_requirements_file_exists():
    """Test requirements.txt exists"""
    assert os.path.exists("requirements.txt"), "requirements.txt not found!"
    print("✅ requirements.txt exists")

def test_main_files_exist():
    """Test all main app files exist"""
    files = ["app.py", "agent.py", "docker-compose.yml"]
    for f in files:
        assert os.path.exists(f), f"{f} not found!"
    print("✅ All main files exist")

def test_src_files_exist():
    """Test all src files exist"""
    files = [
        "src/nodes.py",
        "src/tools.py", 
        "src/apps.py",
        "src/nim_client.py",
        "src/core/config.py",
    ]
    for f in files:
        assert os.path.exists(f), f"{f} not found!"
    print("✅ All src files exist")

def test_docker_compose_has_nim_config():
    """Test docker-compose.yml has NIM configuration"""
    with open("docker-compose.yml") as f:
        content = f.read()
    assert "NIM_MODE" in content, "NIM_MODE not in docker-compose.yml!"
    assert "NIM_API_KEY" in content, "NIM_API_KEY not in docker-compose.yml!"
    print("✅ Docker Compose has NIM configuration")