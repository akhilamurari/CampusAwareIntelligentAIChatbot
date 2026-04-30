# tests/conftest.py
# Registers custom pytest markers so they don't produce warnings.


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "ragas: marks tests as RAGAS evaluation (run on-demand with 'pytest -m ragas')",
    )
