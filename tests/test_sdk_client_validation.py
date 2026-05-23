import os
import pytest
from unittest.mock import patch
from src.sdk.client import OrchestratorClient

def test_client_init_success_with_argument():
    client = OrchestratorClient(api_key="valid-key-123")
    assert client.api_key == "valid-key-123"

def test_client_init_success_with_env_var():
    with patch.dict(os.environ, {"AO_API_KEY": "env-key-456"}):
        client = OrchestratorClient()
        assert client.api_key == "env-key-456"

def test_client_init_raises_on_missing_or_empty():
    # Both argument and environment variable are missing
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="API key is missing, empty, or whitespace-only"):
            OrchestratorClient()

    # Empty string argument
    with pytest.raises(ValueError, match="API key is missing, empty, or whitespace-only"):
        OrchestratorClient(api_key="")

    # Whitespace string argument
    with pytest.raises(ValueError, match="API key is missing, empty, or whitespace-only"):
        OrchestratorClient(api_key="    ")

    # Invalid type
    with pytest.raises(ValueError, match="API key is missing, empty, or whitespace-only"):
        OrchestratorClient(api_key=12345)
