"""
Test fixtures for Moltable pytest suite.
"""

from __future__ import annotations
import os
from unittest.mock import MagicMock, patch
import pytest

os.environ.pop("SUPABASE_URL", None)
os.environ.pop("SUPABASE_SERVICE_ROLE_KEY", None)
os.environ.pop("DEEPSEEK_API_KEY", None)
os.environ["_HERMES_TESTING"] = "1"
os.environ["API_KEY_PEPPER"] = "test-pepper-for-ci"

# ── Global mocks ─────────────────────────────────────
from services.vector_store import VectorStore
_test_store = VectorStore()

def _mock_get_store():
    return _test_store

patch("app_state.get_store", side_effect=_mock_get_store).start()

_mock_supabase = MagicMock()
_mock_supabase.auth.get_user.return_value = MagicMock(id="test-user-id")
_mock_supabase.table().select().eq().eq().eq().limit().execute.return_value.data = []
_mock_supabase.table().insert().execute.return_value.data = []
_mock_supabase.table().update().eq().eq().execute.return_value.data = []
patch("app_state.supabase", _mock_supabase).start()

# Patch embed in the memories route so tests don't load the ML model
_mock_embed_patch = patch("routes.memories.embed", return_value=[0.1, 0.2, 0.3, 0.4])
_mock_embed_patch.start()

# Patch embed in the MCP route too
_mock_embed_mcp = patch("routes.mcp.embed", return_value=[0.1, 0.2, 0.3, 0.4])
_mock_embed_mcp.start()


@pytest.fixture
def mock_supabase():
    return _mock_supabase


@pytest.fixture
def test_store():
    _test_store._store.clear()
    return _test_store


@pytest.fixture
def sample_embedding() -> list:
    return [0.1, 0.2, 0.3, 0.4]


@pytest.fixture
def anyio_backend():
    return "asyncio"
