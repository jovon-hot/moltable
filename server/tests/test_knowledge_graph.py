"""Tests: Knowledge graph service + API routes.

Covers entity extraction (all 7 categories), co-occurrence + pattern
relationships, query methods (related / connections / path), and the
/api/knowledge endpoints.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from services.knowledge_graph import (
    CONCEPT,
    LANGUAGE,
    LOCATION,
    ORG,
    PERSON,
    PROJECT,
    TOOL,
    KnowledgeGraphService,
    extract_entities,
    knowledge_graph_service,
)


# ── Entity extraction ─────────────────────────────────────
def test_extract_english_person():
    ents = extract_entities("Alice Smith works at OpenAI")
    names = {e[0]: e[1] for e in ents}
    assert names.get("Alice Smith") == PERSON
    assert names.get("OpenAI") == ORG


def test_extract_single_english_person_via_verb():
    ents = extract_entities("Alice works at OpenAI")
    names = {e[0]: e[1] for e in ents}
    assert names.get("Alice") == PERSON
    assert names.get("OpenAI") == ORG


def test_extract_chinese_person():
    ents = extract_entities("王小明在OpenAI工作")
    names = {e[0]: e[1] for e in ents}
    assert names.get("王小明") == PERSON
    assert names.get("OpenAI") == ORG


def test_extract_chinese_org():
    ents = extract_entities("我在腾讯科技上班")
    names = {e[0]: e[1] for e in ents}
    assert names.get("腾讯科技") == ORG


def test_extract_language_and_tool():
    ents = extract_entities("I write Python with FastAPI and PostgreSQL")
    names = {e[0]: e[1] for e in ents}
    assert names.get("Python") == LANGUAGE
    assert names.get("FastAPI") == TOOL
    assert names.get("PostgreSQL") == TOOL


def test_extract_project_and_concept():
    ents = extract_entities("Moltable is an AI Identity Sync layer")
    names = {e[0]: e[1] for e in ents}
    assert names.get("Moltable") == PROJECT
    assert names.get("AI") == CONCEPT
    assert names.get("Identity Sync") == CONCEPT


def test_extract_location():
    ents = extract_entities("Alice lives in San Francisco and works in New York")
    names = {e[0]: e[1] for e in ents}
    assert names.get("San Francisco") == LOCATION
    assert names.get("New York") == LOCATION


def test_precedence_location_over_person():
    # "San Francisco" must not be extracted as a person pair
    ents = extract_entities("I visited San Francisco last year")
    assert all(e[1] != PERSON for e in ents)


# ── Graph building ────────────────────────────────────────
def test_add_memory_builds_nodes_and_cooccurrence_edges():
    kg = KnowledgeGraphService()
    kg.clear()
    kg.add_memory("u1", {"id": "m1", "content": "Alice Smith works at OpenAI",
                         "category": "fact", "tags": [], "created_at": "2026-01-01"})
    graph = kg.get_graph("u1")
    node_names = {n["name"] for n in graph["nodes"]}
    assert "Alice Smith" in node_names
    assert "OpenAI" in node_names
    assert len(graph["edges"]) >= 1
    edge = graph["edges"][0]
    assert edge["weight"] == 1
    assert edge["relation"] == "works_at"


def test_edge_weight_increments_on_cooccurrence():
    kg = KnowledgeGraphService()
    kg.clear()
    kg.add_memory("u1", {"id": "m1", "content": "Alice likes Python"})
    kg.add_memory("u1", {"id": "m2", "content": "Alice uses Python daily"})
    graph = kg.get_graph("u1")
    edges = {frozenset((e["source"], e["target"])): e for e in graph["edges"]}
    key = frozenset(("Alice", "Python"))
    assert key in edges
    assert edges[key]["weight"] == 2
    assert sorted(edges[key]["memories"]) == ["m1", "m2"]


def test_add_memory_is_idempotent():
    kg = KnowledgeGraphService()
    kg.clear()
    mem = {"id": "m1", "content": "Alice likes Python"}
    assert kg.add_memory("u1", mem) is True
    assert kg.add_memory("u1", mem) is False
    graph = kg.get_graph("u1")
    assert len(graph["nodes"]) == 2
    assert graph["edges"][0]["weight"] == 1


def test_chinese_relation_pattern():
    kg = KnowledgeGraphService()
    kg.clear()
    kg.add_memory("u1", {"id": "m1", "content": "王小明在腾讯科技工作"})
    graph = kg.get_graph("u1")
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]["relation"] == "works_at"


def test_remove_memory():
    kg = KnowledgeGraphService()
    kg.clear()
    kg.add_memory("u1", {"id": "m1", "content": "Alice likes Python"})
    kg.add_memory("u1", {"id": "m2", "content": "Alice likes Rust"})
    assert kg.remove_memory("u1", "m1") is True
    graph = kg.get_graph("u1")
    node_names = {n["name"] for n in graph["nodes"]}
    assert "Python" not in node_names
    assert "Rust" in node_names


# ── Query methods ─────────────────────────────────────────
def _build_sample_graph(kg: KnowledgeGraphService):
    kg.clear()
    kg.add_memory("u1", {"id": "m1", "content": "Alice works at OpenAI"})
    kg.add_memory("u1", {"id": "m2", "content": "Alice likes Python"})
    kg.add_memory("u1", {"id": "m3", "content": "Bob works at OpenAI and likes Docker"})


def test_find_related_entities():
    kg = KnowledgeGraphService()
    _build_sample_graph(kg)
    related = kg.find_related_entities("u1", "Alice")
    names = {r["entity"] for r in related}
    assert "OpenAI" in names
    assert "Python" in names
    ranked = {r["entity"]: r["weight"] for r in related}
    assert ranked["OpenAI"] >= 1


def test_find_entity_connections():
    kg = KnowledgeGraphService()
    _build_sample_graph(kg)
    result = kg.find_entity_connections("u1", "alice")  # case-insensitive lookup
    assert result is not None
    assert result["entity"]["name"] == "Alice"
    assert result["total_connections"] >= 2


def test_find_entity_connections_missing():
    kg = KnowledgeGraphService()
    _build_sample_graph(kg)
    assert kg.find_entity_connections("u1", "Nobody") is None


def test_find_path():
    kg = KnowledgeGraphService()
    _build_sample_graph(kg)
    path = kg.find_path("u1", "Alice", "Bob")
    assert path is not None
    assert path["path"][0] == "Alice"
    assert path["path"][-1] == "Bob"
    assert path["length"] == 2  # Alice -> OpenAI -> Bob


def test_find_path_unreachable():
    kg = KnowledgeGraphService()
    kg.clear()
    kg.add_memory("u1", {"id": "m1", "content": "Alice likes Python"})
    kg.add_memory("u1", {"id": "m2", "content": "Bob likes Rust"})
    assert kg.find_path("u1", "Alice", "Bob") is None


# ── API routes ────────────────────────────────────────────
@pytest.fixture(autouse=True)
def _clean_kg(test_store):
    """Reset the shared knowledge graph singleton + memory store before each test."""
    knowledge_graph_service.clear()
    test_store._store.clear()
    yield
    knowledge_graph_service.clear()


@pytest.fixture
def client() -> TestClient:
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_header() -> dict:
    return {"Authorization": "Bearer test-token"}


def _save_memory(client, auth_header, content: str, category: str = "fact"):
    """Create a memory via the memories API so user_id matches auth resolution.
    Uses force=true to bypass duplicate detection (mock embeddings are identical)."""
    resp = client.post(
        "/api/memories/",
        json={"content": content, "category": category},
        params={"force": True},
        headers=auth_header,
    )
    assert resp.status_code == 200
    return resp.json()


def test_graph_endpoint_empty(client, auth_header):
    resp = client.get("/api/knowledge/graph", headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert data["nodes"] == []
    assert data["edges"] == []


def test_build_then_graph(client, auth_header):
    _save_memory(client, auth_header, "Alice Smith works at OpenAI")
    _save_memory(client, auth_header, "Alice likes Python")

    resp = client.post("/api/knowledge/build", headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "built"
    assert data["memories_processed"] == 2

    resp = client.get("/api/knowledge/graph", headers=auth_header)
    assert resp.status_code == 200
    graph = resp.json()
    node_names = {n["name"] for n in graph["nodes"]}
    assert "Alice Smith" in node_names
    assert "OpenAI" in node_names
    assert "Python" in node_names


def test_entity_endpoint(client, auth_header):
    _save_memory(client, auth_header, "Alice Smith works at OpenAI")
    client.post("/api/knowledge/build", headers=auth_header)

    resp = client.get("/api/knowledge/entity", params={"name": "Alice Smith"},
                      headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert data["entity"]["type"] == "person"
    assert any(c["entity"] == "OpenAI" for c in data["connections"])

    resp = client.get("/api/knowledge/entity", params={"name": "Ghost"},
                      headers=auth_header)
    assert resp.status_code == 404


def test_path_endpoint(client, auth_header):
    _save_memory(client, auth_header, "Alice works at OpenAI")
    _save_memory(client, auth_header, "Bob works at OpenAI")
    client.post("/api/knowledge/build", headers=auth_header)

    resp = client.get("/api/knowledge/path",
                      params={"source": "Alice", "target": "Bob"},
                      headers=auth_header)
    assert resp.status_code == 200
    data = resp.json()
    assert data["length"] == 2
    assert data["path"] == ["Alice", "OpenAI", "Bob"]


def test_knowledge_requires_auth(client):
    resp = client.get("/api/knowledge/graph")
    assert resp.status_code == 401
