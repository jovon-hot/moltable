"""Embedding service — configurable local sentence-transformers model.

Supports:
- all-MiniLM-L6-v2 (default, 384-dim, English-optimized, fast)
- paraphrase-multilingual-MiniLM-L12-v2 (384-dim, 50+ languages incl. Chinese)
- Any sentence-transformers model via MOLTABLE_EMBED_MODEL env var
- Fallback: char-trigram hash embedding when sentence_transformers not installed

Includes a simple in-memory cache to avoid re-encoding identical texts.
"""

import hashlib
import logging
import os
import struct
from threading import Lock

logger = logging.getLogger("moltable.embedding")

_model = None
_has_sentence_transformers = None  # lazy detection
_DIM = 384

# Configurable model name — set MOLTABLE_EMBED_MODEL for Chinese support
_MODEL_NAME = os.getenv(
    "MOLTABLE_EMBED_MODEL",
    "all-MiniLM-L6-v2"  # default: English-optimized
)

# ── Embedding Cache ──────────────────────────────────
_cache: dict[str, list[float]] = {}
_cache_lock = Lock()
_MAX_CACHE_SIZE = int(os.getenv("MOLTABLE_EMBED_CACHE_SIZE", "1000"))


def _text_hash(text: str) -> str:
    """Fast hash for cache key (prefix + sha256 first 16 chars)."""
    return hashlib.sha256(text[:8000].encode()).hexdigest()[:16]


def _check_sentence_transformers() -> bool:
    """Lazy check if sentence-transformers is available."""
    global _has_sentence_transformers
    if _has_sentence_transformers is None:
        try:
            import sentence_transformers  # noqa: F401
            _has_sentence_transformers = True
        except ImportError:
            _has_sentence_transformers = False
            logger.info("sentence-transformers 未安装 — 使用 trigram hash 嵌入（功能受限但可工作）")
    return _has_sentence_transformers


def _fallback_embed(text: str) -> list[float]:
    """Char-trigram hash embedding when sentence-transformers is unavailable.
    
    Produces a deterministic 384-dim sparse vector usable for basic keyword
    matching. Not semantically meaningful, but allows the system to function
    without the heavy sentence-transformers dependency.
    """
    vec = [0.0] * _DIM
    t = text.lower()
    # Extract all char trigrams, hash to bin index
    for i in range(len(t) - 2):
        trigram = t[i:i+3]
        h = hashlib.md5(trigram.encode()).digest()
        idx = struct.unpack("<I", h[:4])[0] % _DIM
        vec[idx] += 1.0
    # Short text (< 3 chars): hash the whole text and first char
    if sum(v for v in vec) == 0 and t:
        h = hashlib.md5(t.encode()).digest()
        idx = struct.unpack("<I", h[:4])[0] % _DIM
        vec[idx] = 1.0
        if len(t) > 0:
            # also hash individual chars for short text
            for ch in t:
                h = hashlib.md5(ch.encode()).digest()
                idx = struct.unpack("<I", h[:4])[0] % _DIM
                vec[idx] += 0.5
    # Normalize
    total = (sum(v * v for v in vec)) ** 0.5
    if total > 0:
        vec = [v / total for v in vec]
    return vec


def _load_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: %s (dim=%d, cache=%d)", _MODEL_NAME, _DIM, _MAX_CACHE_SIZE)
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed(text: str) -> list[float]:
    """Generate embedding vector for a text string.
    Truncates input to 8000 characters. Results are cached.
    Falls back to trigram hash if sentence_transformers not installed.
    """
    if len(text) > 8000:
        text = text[:8000]

    # Check cache
    key = _text_hash(text)
    with _cache_lock:
        if key in _cache:
            return _cache[key]

    # Encode: use real model or fallback
    if _check_sentence_transformers():
        model = _load_model()
        vec = model.encode(text, normalize_embeddings=True).tolist()
    else:
        vec = _fallback_embed(text)

    # Store in cache
    with _cache_lock:
        if len(_cache) >= _MAX_CACHE_SIZE:
            evict_count = max(1, _MAX_CACHE_SIZE // 10)
            for k in list(_cache.keys())[:evict_count]:
                del _cache[k]
        _cache[key] = vec

    return vec


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Batch embed multiple texts. Uses cache for individual texts."""
    results = []
    uncached: list[tuple[int, str, str]] = []

    with _cache_lock:
        for i, text in enumerate(texts):
            t = text[:8000] if len(text) > 8000 else text
            key = _text_hash(t)
            if key in _cache:
                results.append((i, _cache[key]))
            else:
                uncached.append((i, t, key))

    if uncached:
        if _check_sentence_transformers():
            model = _load_model()
            raw_texts = [item[1] for item in uncached]
            vecs = model.encode(raw_texts, normalize_embeddings=True)
            with _cache_lock:
                for (idx, _, key), vec in zip(uncached, vecs):
                    vec_list = vec.tolist()
                    if len(_cache) < _MAX_CACHE_SIZE:
                        _cache[key] = vec_list
                    results.append((idx, vec_list))
        else:
            for idx, text, key in uncached:
                vec_list = _fallback_embed(text)
                with _cache_lock:
                    if len(_cache) < _MAX_CACHE_SIZE:
                        _cache[key] = vec_list
                results.append((idx, vec_list))

    results.sort(key=lambda x: x[0])
    return [r[1] for r in results]


def embed_dim() -> int:
    return _DIM


def model_name() -> str:
    return _MODEL_NAME if _check_sentence_transformers() else "trigram-hash-fallback"


def cache_stats() -> dict:
    with _cache_lock:
        return {"size": len(_cache), "max": _MAX_CACHE_SIZE}


def cache_clear():
    with _cache_lock:
        _cache.clear()
        logger.info("Embedding cache cleared")
