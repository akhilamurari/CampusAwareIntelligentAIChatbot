# tests/test_agent.py
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import run_agent

def test_agent_nl2sql_connection():
    """Test NL2SQL tool returns correct SQLite results via on-premises LLM"""
    response = run_agent("Which room had the highest CO2 levels?")
    assert response is not None
    assert len(response) > 0
    # Should mention a room name
    rooms = ["Library", "Lab", "Lecture", "Cafeteria", "Study-Room"]
    assert any(room in response for room in rooms), f"Expected room name in response: {response}"
    print(f"✅ NL2SQL test passed: {response[:80]}")

def test_agent_rag_retrieval():
    """Test RAG tool retrieves correct campus PDF content"""
    response = run_agent("How do I connect to eduroam WiFi?")
    assert response is not None
    assert len(response) > 0
    # Should mention WiFi or network related content
    keywords = ["wifi", "WiFi", "network", "connect", "eduroam", "password", "username"]
    assert any(kw in response for kw in keywords), f"Expected WiFi info in response: {response}"
    print(f"✅ RAG retrieval test passed: {response[:80]}")

def test_agent_rag_retrieval_specifically():
    """Test RAG retrieves specific campus document information"""
    response = run_agent("What are the library opening hours?")
    assert response is not None
    assert len(response) > 0
    # Should mention library or hours
    keywords = ["library", "Library", "hours", "open", "Monday", "Tuesday", "time"]
    assert any(kw in response for kw in keywords), f"Expected library info in response: {response}"
    print(f"✅ RAG specific retrieval test passed: {response[:80]}")

def test_agent_multi_turn():
    """Test multi-turn conversation history works correctly"""
    # First turn
    response1 = run_agent("Which room had high CO2?")
    assert response1 is not None
    assert len(response1) > 0

    # Second turn — follow up question
    response2 = run_agent("What is the temperature in that room?")
    assert response2 is not None
    assert len(response2) > 0

    # Should mention temperature
    keywords = ["temperature", "degrees", "celsius", "°C", "warm", "cool"]
    assert any(kw in response2 for kw in keywords), f"Expected temperature in response: {response2}"
    print(f"✅ Multi-turn test passed: {response2[:80]}")

if __name__ == "__main__":
    print("🧪 Running CampusAware Agent Tests...")
    print("─" * 50)
    
    tests = [
        ("test_agent_nl2sql_connection", test_agent_nl2sql_connection),
        ("test_agent_rag_retrieval", test_agent_rag_retrieval),
        ("test_agent_rag_retrieval_specifically", test_agent_rag_retrieval_specifically),
        ("test_agent_multi_turn", test_agent_multi_turn),
    ]
    
    passed = 0
    failed = 0
    
    for name, test in tests:
        try:
            test()
            print(f"✅ {name} PASSED")
            passed += 1
        except AssertionError as e:
            print(f"❌ {name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {name} ERROR: {e}")
            failed += 1
        print("─" * 50)
    
    print(f"\n📊 Results: {passed} passed, {failed} failed out of {len(tests)} tests")
