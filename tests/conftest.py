import os
import pytest

@pytest.fixture(autouse=True)
def stub_mode_env():
    # Forzamos modo stub para tests rápidos y sin Ollama
    prev = os.environ.get("GENERATOR_MODE")
    os.environ["GENERATOR_MODE"] = "stub"
    yield
    if prev is None:
        os.environ.pop("GENERATOR_MODE", None)
    else:
        os.environ["GENERATOR_MODE"] = prev
