"""Relationship Inference Engine — auto-detect memory relationships.

Detects SUPERSEDES, CONTRADICTS, and EXTENDS relationships between memories
using semantic similarity + keyword patterns. Integrates with the existing
smart-merge pipeline and knowledge graph service.

Relationship types:
  - SUPERSEDES:  high similarity (>0.85), newer → replaces old
  - CONTRADICTS: moderate-high similarity (>0.60), opposing fact detected
  - EXTENDS:     moderate similarity (0.45-0.85), adds detail to existing
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("moltable.relationship_inference")

# ── Thresholds ──────────────────────────────────────────────
SUPERSEDE_SIMILARITY = 0.85        # Very high overlap → newer replaces older
CONTRADICT_SIMILARITY = 0.60       # Substantial overlap + contradiction signs
EXTEND_SIMILARITY_LOW = 0.45       # Minimum for "extends" relationship
EXTEND_SIMILARITY_HIGH = 0.85      # Maximum for "extends" (above = supersede)

# ── Contradiction detection patterns ────────────────────────
# Words/phrases that indicate contradiction or correction
_CONTRADICTION_PATTERNS = re.compile(
    r"\b(?:"
    r"no[,;]?\s+actually|that['\u2019]s\s+not\s+(?:right|correct|true|accurate)|"
    r"incorrect|wrong|mistaken|misunderstanding|"
    r"i\s+meant|actually[,;]?\s+it['\u2019]s|"
    r"correction|to\s+clarify|to\s+be\s+clear|"
    r"unlike\s+(?:what\s+)?(?:I|you|we)\s+(?:said|thought|mentioned)|"
    r"contrary\s+to|on\s+the\s+contrary|"
    r"scratch\s+that|forget\s+(?:what\s+)?(?:I|you|we)\s+said|"
    r"update[ds]?\s+to|replaced\s+by|"
    r"no\s+longer|not\s+anymore|"
    r"\u4e0d\u5bf9|"
    r"\u4e0d\u662f|"
    r"\u4fee\u6b63|"
    r"\u66f4\u6b63|"
    r"\u5b9e\u9645\u4e0a|"
    r"\u5176\u5b9e|"
    r"\u4e0d\u662f\u8fd9\u6837|"
    r"\u5e94\u8be5\u662f|"
    r"\u5df2\u7ecf\u6539\u4e86|"
    r"\u5df2\u66f4\u65b0|"
    r"\u4e0d\u518d"
    r")\b",
    re.IGNORECASE,
)

# Negation words that flip a fact (used for lightweight contradiction check)
_NEGATION_WORDS = {
    "not", "no", "never", "neither", "nor",
    "don't", "doesn't", "didn't", "won't", "wouldn't", "shouldn't", "can't", "couldn't",
    "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't", "hadn't",
    "\u4e0d", "\u6ca1\u6709", "\u4e0d\u662f", "\u65e0", "\u975e",
}

# Key-value fact patterns for contradiction detection
# e.g., "uses Python" vs "uses TypeScript" → same key, different value
_FACT_PATTERNS = [
    re.compile(
        r"\b(uses?|using|works?\s+with|prefers?|likes?|"
        r"writes?\s+in|codes?\s+in|programs?\s+in|built\s+with|"
        r"builds?\s+with|deploys?\s+to|deployed\s+to|"
        r"hosts?\s+on|hosted\s+on|runs?\s+on|running\s+on|"
        r"is\s+(?:a|an)|is\s+the|lives?\s+in|based\s+in|located\s+in|"
        r"works?\s+at|employed\s+at|"
        r"\u4f7f\u7528|\u559c\u6b22|\u504f\u597d|\u5c45\u4f4f\u5728|\u5728.*\u5de5\u4f5c|"
        r"\u662f(?:一[个位名])"
        r")\s+(.{3,80})",
        re.IGNORECASE,
    ),
]

# ── Key-value pair extraction ───────────────────────────────
def _extract_key_value_pairs(text: str) -> List[Tuple[str, str]]:
    """Extract (key, value) pairs from memory text for fact comparison.

    Key is the normalized fact type (e.g., "uses", "lives in").
    Value is the normalized fact value (e.g., "Python", "Beijing").
    """
    pairs = []
    text_lower = text.lower()

    for pattern in _FACT_PATTERNS:
        for m in pattern.finditer(text_lower):
            key = m.group(1).strip().lower()
            value = m.group(2).strip().rstrip(".,;!?")
            if len(value) >= 2:
                pairs.append((key, value))

    return pairs


def _has_contradiction_signals(text: str) -> bool:
    """Check if text contains contradiction/correction language."""
    return bool(_CONTRADICTION_PATTERNS.search(text))


def _count_negations(text: str) -> int:
    """Count negation words in text (English + Chinese)."""
    count = 0
    text_lower = text.lower()
    # English: match words including contractions (don't, isn't, etc.)
    en_words = re.findall(r"\b\w+(?:'\w+)?\b", text_lower)
    for w in en_words:
        if w in _NEGATION_WORDS:
            count += 1
    # Chinese: match individual characters that are negation words
    # Chinese negation chars are single chars; match them directly
    zh_negation_chars = {"不", "没", "无", "非"}
    for ch in text:
        if ch in zh_negation_chars:
            # Check if it's part of a multi-char negation word
            count += 1
    return count


def _detect_fact_conflict(
    pairs_a: List[Tuple[str, str]],
    pairs_b: List[Tuple[str, str]],
) -> Optional[Tuple[str, str, str]]:
    """Detect if two memories have conflicting facts.

    Returns (key, value_a, value_b) if a conflict is found, None otherwise.
    A conflict means: same key, different values for the same fact.
    """
    keys_a = dict(pairs_a)
    keys_b = dict(pairs_b)

    for key in keys_a:
        if key in keys_b and keys_a[key] != keys_b[key]:
            # Same fact type, different values → potential contradiction
            return (key, keys_a[key], keys_b[key])

    return None


# ── Relationship inference ─────────────────────────────────
def infer_relationships(
    new_memory: dict,
    existing_memories: List[dict],
    similarity_func=None,
) -> Dict[str, list]:
    """Infer relationships between a new memory and existing memories.

    Args:
        new_memory: Dict with at least {id, content, created_at}.
        existing_memories: List of existing memory dicts to compare against.
        similarity_func: Optional callable(a_text, b_text) → float (0-1).
                         If not provided, only pattern-based detection is used.

    Returns:
        {
            "supersedes": [{id, similarity, content_preview}],
            "contradicts": [{id, similarity, fact_key, old_value, new_value}],
            "extends": [{id, similarity, content_preview}],
        }
    """
    new_content = (new_memory.get("content") or "").strip()
    new_id = str(new_memory.get("id", ""))
    new_created = new_memory.get("created_at", "")

    if not new_content:
        return {"supersedes": [], "contradicts": [], "extends": []}

    new_pairs = _extract_key_value_pairs(new_content)
    has_contradiction_lang = _has_contradiction_signals(new_content)
    new_negations = _count_negations(new_content)

    supersedes_list = []
    contradicts_list = []
    extends_list = []

    for existing in existing_memories:
        existing_id = str(existing.get("id", ""))
        existing_content = (existing.get("content") or "").strip()

        if not existing_content or existing_id == new_id:
            continue

        # Compute similarity if func provided
        similarity = None
        if similarity_func:
            try:
                similarity = similarity_func(new_content, existing_content)
            except Exception:
                continue

        # ── SUPERSEDES detection ──────────────────────
        if similarity is not None and similarity >= SUPERSEDE_SIMILARITY:
            # Very high similarity + newer timestamp → supersede
            if new_created and existing.get("created_at", ""):
                if new_created > existing.get("created_at", ""):
                    supersedes_list.append({
                        "id": existing_id,
                        "similarity": round(similarity, 4),
                        "content_preview": existing_content[:150],
                    })
            else:
                # Can't determine which is newer, flag as potential
                supersedes_list.append({
                    "id": existing_id,
                    "similarity": round(similarity, 4),
                    "content_preview": existing_content[:150],
                    "warning": "Cannot determine temporal order",
                })

        # ── CONTRADICTS detection ────────────────────
        elif similarity is not None and similarity >= CONTRADICT_SIMILARITY:
            existing_pairs = _extract_key_value_pairs(existing_content)
            conflict = _detect_fact_conflict(new_pairs, existing_pairs)

            if conflict:
                key, new_val, old_val = conflict
                contradicts_list.append({
                    "id": existing_id,
                    "similarity": round(similarity, 4),
                    "fact_key": key,
                    "old_value": old_val,
                    "new_value": new_val,
                })
            elif has_contradiction_lang:
                # New content has contradiction language → likely supersedes
                contradicts_list.append({
                    "id": existing_id,
                    "similarity": round(similarity, 4),
                    "fact_key": None,
                    "old_value": existing_content[:150],
                    "new_value": new_content[:150],
                    "detected_by": "contradiction_language",
                })
            elif new_negations >= 2 and _count_negations(existing_content) == 0:
                # New has negations, old doesn't → potential correction
                contradicts_list.append({
                    "id": existing_id,
                    "similarity": round(similarity, 4),
                    "fact_key": None,
                    "old_value": existing_content[:150],
                    "new_value": new_content[:150],
                    "detected_by": "negation_mismatch",
                })

        # ── EXTENDS detection ─────────────────────────
        elif (similarity is not None
              and EXTEND_SIMILARITY_LOW <= similarity < EXTEND_SIMILARITY_HIGH):
            extends_list.append({
                "id": existing_id,
                "similarity": round(similarity, 4),
                "content_preview": existing_content[:150],
            })

    return {
        "supersedes": supersedes_list,
        "contradicts": contradicts_list,
        "extends": extends_list,
    }


# ── Scoring helpers ─────────────────────────────────────────
def relationship_impact_score(relationships: Dict[str, list]) -> float:
    """Calculate an impact score (0-10) for discovered relationships.

    Higher score = more significant relationships found = more actionable.
    """
    score = 0.0
    score += len(relationships.get("supersedes", [])) * 3.0
    score += len(relationships.get("contradicts", [])) * 4.0
    score += len(relationships.get("extends", [])) * 0.5
    return min(score, 10.0)


def relationship_summary(relationships: Dict[str, list]) -> str:
    """Human-readable summary of discovered relationships."""
    parts = []
    n_sup = len(relationships.get("supersedes", []))
    n_con = len(relationships.get("contradicts", []))
    n_ext = len(relationships.get("extends", []))

    if n_sup:
        parts.append(f"{n_sup} supersedes")
    if n_con:
        parts.append(f"{n_con} contradicts")
    if n_ext:
        parts.append(f"{n_ext} extends")

    if not parts:
        return "No significant relationships found"

    return ", ".join(parts)


# ── Sanitization (remove PII-like trailing noise) ───────────
def sanitize_relationship_data(relationships: Dict[str, list]) -> Dict[str, list]:
    """Strip sensitive content from relationship data for logging/analytics.

    Only keeps relationship metadata (id, similarity, type), drops content.
    """
    sanitized = {}
    for rel_type, rels in relationships.items():
        sanitized[rel_type] = []
        for r in rels:
            entry = {
                "id": r.get("id"),
                "similarity": r.get("similarity"),
            }
            if "fact_key" in r:
                entry["fact_key"] = r["fact_key"]
            if "detected_by" in r:
                entry["detected_by"] = r["detected_by"]
            sanitized[rel_type].append(entry)
    return sanitized
