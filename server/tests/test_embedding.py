"""Unit tests: Embedding service — local sentence-transformers (384-dim).

These tests mock the SentenceTransformer model so no real ML model is loaded.
When sentence_transformers is unavailable, the module falls back to trigram hash
— tests must also patch _check_sentence_transformers to force the mock path.
"""

from __future__ import annotations
from unittest.mock import MagicMock, patch
import pytest
import numpy as np


@pytest.fixture(autouse=True)
def reset_model():
    from services import embedding
    embedding._model = None
    embedding._has_sentence_transformers = None
    yield


class TestEmbed:
    def test_embed_returns_vector(self):
        """embed() should call model.encode() and return list of floats."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([0.1, 0.2, 0.3, 0.4])

        with patch("services.embedding._load_model", return_value=mock_model), \
             patch("services.embedding._check_sentence_transformers", return_value=True):
            from services.embedding import embed
            result = embed("Hello world")
            assert isinstance(result, list)
            assert all(isinstance(v, float) for v in result)
            assert result == [0.1, 0.2, 0.3, 0.4]

    def test_embed_normalizes(self):
        """embed() should call encode with normalize_embeddings=True."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([0.1, 0.2])

        with patch("services.embedding._load_model", return_value=mock_model), \
             patch("services.embedding._check_sentence_transformers", return_value=True):
            from services.embedding import embed
            embed("test")
            mock_model.encode.assert_called_once_with(
                "test", normalize_embeddings=True
            )

    def test_embed_caches_model(self):
        """_load_model() should return the same instance on repeat calls."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([0.0])

        import services.embedding
        services.embedding._model = mock_model  # inject directly
        services.embedding._has_sentence_transformers = True

        model1 = services.embedding._load_model()
        model2 = services.embedding._load_model()
        assert model1 is model2


class TestEmbedBatch:
    def test_batch_returns_vectors(self):
        """embed_batch() should return list of lists."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])

        with patch("services.embedding._load_model", return_value=mock_model), \
             patch("services.embedding._check_sentence_transformers", return_value=True):
            from services.embedding import embed_batch
            results = embed_batch(["Hello", "World"])
            assert len(results) == 2
            assert results[0] == [0.1, 0.2]
            assert results[1] == [0.3, 0.4]


class TestEmbedDim:
    def test_embed_dim_is_384(self):
        from services.embedding import embed_dim
        assert embed_dim() == 384
        assert isinstance(embed_dim(), int)
