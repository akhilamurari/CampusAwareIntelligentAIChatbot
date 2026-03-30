def test_imports():
    import streamlit
    import langchain
    import langgraph
    import pandas
    assert True

def test_data_folder_exists():
    import os
    assert os.path.exists("data")

def test_requirements_exists():
    import os
    assert os.path.exists("requirements.txt")

def test_dockerfile_exists():
    import os
    assert os.path.exists("Dockerfile")
