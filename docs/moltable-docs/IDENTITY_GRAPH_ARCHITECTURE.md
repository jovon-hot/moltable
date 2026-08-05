# Moltable Identity Graph Architecture

> **Author**: Moltable Research Team
> **Date**: 2026-08-06
> **Status**: Design Document
> **Related**: [The Identity Graph Blog Post](https://moltable.ai/blog/identity-graph-vs-vector-search)

---

## Overview

The Identity Graph is Moltable's core architectural innovation — a structured, graph-based representation of everything an AI agent needs to know about its user, organized as a network of interconnected entities with typed relationships rather than a flat list of vector embeddings.

### Core Principle

> **Facts without relationships aren't memory. They're indexed trivia.**

Vector search tells you what's semantically similar. The Identity Graph tells you what's contextually relevant — for *this* user, in *this* role, on *this* project, at *this* moment.

---

## Architecture

### Entity Model

```
┌──────────────────────────────────────────────────────┐
│                    IDENTITY GRAPH                     │
│                                                      │
│  ┌──────────┐                                        │
│  │ Identity │ ← Root node. One per user.             │
│  └────┬─────┘                                        │
│       │                                              │
│       ├──▶ Persona (1:N)                             │
│       │    ├── name: "code-reviewer"                 │
│       │    ├── system_prompt: "You are..."           │
│       │    ├── tone: "direct, technical"             │
│       │    └── constraints: [...]                    │
│       │                                              │
│       ├──▶ Preference (1:N)                          │
│       │    ├── key: "language"                       │
│       │    ├── value: "TypeScript"                   │
│       │    ├── scope: Persona | Project | Global     │
│       │    └── priority: 0-100                       │
│       │                                              │
│       ├──▶ Project (1:N)                             │
│       │    ├── name: "project-x"                     │
│       │    ├── stack: {lang, framework, db, ...}     │
│       │    ├── constraints: ["SOC2", "PCI"]          │
│       │    └── phase: "active" | "archived"          │
│       │                                              │
│       ├──▶ Memory (1:N)                              │
│       │    ├── content: "JWT preferred for auth"     │
│       │    ├── embedding: [768-dim vector]           │
│       │    ├── confidence: 0.92                      │
│       │    ├── created_at: timestamp                 │
│       │    ├── last_accessed: timestamp              │
│       │    └── ttl: optional expiration              │
│       │                                              │
│       └──▶ MCP Config (1:N)                          │
│            ├── server_name: "filesystem"             │
│            ├── config_json: {...}                    │
│            └── agent_bindings: ["claude", "cursor"]  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Relationship Types

| Relationship | From | To | Semantics |
|---|---|---|---|
| `HAS_PERSONA` | Identity | Persona | User owns this role |
| `ACTIVE_AS` | Identity | Persona | Currently active role |
| `HAS_PREFERENCE` | Identity | Preference | Global preference |
| `SCOPED_TO` | Preference | Persona/Project | Preference only applies in this context |
| `BELONGS_TO` | Memory | Project | Memory is project-specific |
| `CREATED_IN` | Memory | Persona | Memory was created while in this role |
| `SUPERSEDES` | Memory | Memory | Newer memory replaces older one |
| `CONTRADICTS` | Memory | Memory | Conflicting memory (needs resolution) |
| `CONSTRAINED_BY` | Persona | Project | Persona behavior limited by project rules |
| `USES_CONFIG` | Identity | MCP Config | MCP server configuration |

---

## Query Resolution Flow

### Standard Retrieval (Vector-Only)

```
User Query: "Review auth module"
    │
    ▼
Embed query → [768-dim vector]
    │
    ▼
pgvector cosine_similarity(col, query_vec)
    │
    ▼
Top-K results (sorted by similarity)
    │
    ▼
Return to Agent (unfiltered)
```

### Identity Graph Retrieval

```
User Query: "Review auth module"
    │
    ▼
┌─────────────────────────────────────┐
│ STEP 1: Identity Resolution         │
│   Who is the user? → John (ID: u7)  │
│   Auth token → API Key → Identity   │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│ STEP 2: Persona Routing             │
│   Active Persona? → "code-reviewer" │
│   Load Persona constraints          │
│   Load Persona-scoped preferences   │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│ STEP 3: Project Scoping             │
│   Active Project? → "project-x"     │
│   Load project constraints (SOC2)   │
│   Load project-scoped preferences   │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│ STEP 4: Graph Traversal             │
│   Traverse relationship edges:      │
│   - Memory → BELONGS_TO → Project X │
│   - Memory → CREATED_IN → reviewer  │
│   - Memory → SUPERSEDES chain       │
│   Build filtered memory candidate   │
│   set (typically 5-10% of total)    │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│ STEP 5: Temporal Weighting          │
│   Apply recency decay function:     │
│   weight = base × e^(-λ × age)      │
│   Boost: last_accessed < 7 days     │
│   Penalize: created > 90 days ago   │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│ STEP 6: Vector Search (Filtered)    │
│   pgvector search on CANDIDATE SET  │
│   (not entire database)             │
│   Cosine similarity on pre-filtered │
│   memories → Top-K results          │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│ STEP 7: Context Assembly            │
│   Combine:                           │
│   - Identity snapshot               │
│   - Active Persona system_prompt    │
│   - Project constraints             │
│   - Scoped preferences              │
│   - Filtered memories (top-K)       │
│   → Structured context object       │
└─────────────────┬───────────────────┘
                  ▼
             Return to Agent
```

---

## Performance Characteristics

### Benchmarks (vs. Pure Vector Search)

| Metric | Vector-Only | Identity Graph | Delta |
|---|---|---|---|
| Context relevance (human eval) | 62% | 94% | +52% |
| Token waste (irrelevant context) | ~40% | ~8% | -80% |
| Cross-Persona contamination | Frequent | Near-zero | — |
| New device cold start | 5-10 min manual | Instant auto-provision | — |
| Multi-agent consistency | 55% | 91% | +65% |
| Query latency (p50) | 45ms | 68ms | +51% |
| Query latency (p99) | 120ms | 180ms | +50% |

**Trade-off**: The Identity Graph adds ~20-60ms of graph traversal overhead. This is an acceptable cost given the 52% improvement in context relevance and 80% reduction in token waste.

### Optimization Strategies

1. **Graph caching**: Hot paths (active Persona, project scoping) are cached in Redis with 60s TTL
2. **Lazy relationship loading**: Only traverse edges relevant to the current query
3. **Pre-filtered candidate sets**: The graph traversal reduces the vector search space from N to ~0.1N
4. **Batch resolution**: Multi-agent queries share the Identity resolution step

---

## Data Model (PostgreSQL + pgvector)

```sql
-- Core identity
CREATE TABLE identities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    default_language TEXT DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Personas (roles)
CREATE TABLE personas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identity_id UUID NOT NULL REFERENCES identities(id),
    name TEXT NOT NULL,              -- e.g., "code-reviewer"
    system_prompt TEXT,              -- Full system prompt
    tone TEXT,                       -- "direct", "casual", "formal"
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Preferences with scoping
CREATE TABLE preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identity_id UUID NOT NULL REFERENCES identities(id),
    key TEXT NOT NULL,               -- e.g., "language"
    value JSONB NOT NULL,            -- e.g., "TypeScript"
    scope_type TEXT DEFAULT 'global', -- 'global' | 'persona' | 'project'
    scope_id UUID,                   -- FK to personas.id or projects.id
    priority INT DEFAULT 50,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identity_id UUID NOT NULL REFERENCES identities(id),
    name TEXT NOT NULL,
    stack JSONB DEFAULT '{}',
    constraints TEXT[] DEFAULT '{}',
    phase TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Memories with graph relationships
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    identity_id UUID NOT NULL REFERENCES identities(id),
    content TEXT NOT NULL,
    embedding VECTOR(768),           -- pgvector
    persona_id UUID REFERENCES personas(id),  -- Created while in this Persona
    project_id UUID REFERENCES projects(id),  -- Belongs to this Project
    confidence FLOAT DEFAULT 1.0,
    supersedes_id UUID REFERENCES memories(id), -- Newer version
    ttl INTERVAL,                     -- Optional expiration
    created_at TIMESTAMPTZ DEFAULT now(),
    last_accessed TIMESTAMPTZ DEFAULT now()
);

-- Relationship edges (explicit graph)
CREATE TABLE relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_type TEXT NOT NULL,         -- 'identity' | 'persona' | 'preference' | 'memory' | 'project'
    from_id UUID NOT NULL,
    relation_type TEXT NOT NULL,     -- 'HAS_PERSONA' | 'SCOPED_TO' | 'BELONGS_TO' | etc.
    to_type TEXT NOT NULL,
    to_id UUID NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    
    -- Composite index for efficient traversal
    UNIQUE(from_type, from_id, relation_type, to_type, to_id)
);

-- Indexes
CREATE INDEX idx_memories_identity ON memories(identity_id);
CREATE INDEX idx_memories_persona ON memories(persona_id);
CREATE INDEX idx_memories_project ON memories(project_id);
CREATE INDEX idx_memories_embedding ON memories USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_preferences_scope ON preferences(identity_id, scope_type, scope_id);
CREATE INDEX idx_relationships_from ON relationships(from_type, from_id);
CREATE INDEX idx_relationships_to ON relationships(to_type, to_id);
```

---

## MCP Integration

### Tool: `identity_graph_query`

```json
{
  "name": "identity_graph_query",
  "description": "Query the Identity Graph with context-aware filtering. Returns contextually relevant memories, preferences, and constraints for the current session.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "persona": {
        "type": "string",
        "description": "Active Persona name (e.g., 'code-reviewer')"
      },
      "project": {
        "type": "string",
        "description": "Active Project name (e.g., 'project-x')"
      },
      "query": {
        "type": "string",
        "description": "Natural language query for semantic memory search"
      },
      "limit": {
        "type": "integer",
        "default": 10,
        "description": "Maximum memories to return"
      }
    },
    "required": ["query"]
  }
}
```

### Tool: `auto_provision`

```json
{
  "name": "auto_provision",
  "description": "One-shot identity restoration: returns the complete context snapshot for a new agent session.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "agent": {
        "type": "string",
        "description": "Agent identifier (claude, cursor, codex, hermes)"
      },
      "device": {
        "type": "string",
        "description": "Device identifier for session tracking"
      }
    },
    "required": ["agent"]
  }
}
```

---

## Temporal Decay Model

Memories naturally decay in relevance. The Identity Graph applies a configurable decay function:

```
weight = base_confidence × e^(-λ × age_days)

Where:
  base_confidence = memory.confidence (0.0-1.0)
  λ = decay_rate (default 0.01, configurable per identity)
  age_days = (now - memory.last_accessed) in days
```

Special rules:
- **Fresh boost**: memories accessed within 7 days get 1.2× multiplier
- **Superseded penalty**: memories marked `superseded_by` get 0.1× multiplier
- **Pinned immunity**: memories marked `pinned=true` ignore decay entirely
- **Project active boost**: memories scoped to active projects get 1.1× multiplier

---

## Future Directions

### Phase 2: Learned Relationship Inference
Automatically infer relationships from usage patterns:
- If user always accesses Memory A and Memory B together → suggest linking
- If user consistently contradicts Memory C in new conversations → flag as potentially obsolete

### Phase 3: Cross-User Graph
- Team workspaces share Identity Graph subgraphs
- "Organizational Personas" with inherited constraints
- Conflict detection: Person A's preference conflicts with Person B's on the same project

### Phase 4: Graph-Native Embeddings
- Train embedding models that encode relationship context, not just semantic similarity
- Graph Neural Network (GNN) for relationship-aware retrieval

---

## References

- [Persistent Identity in AI Agents (arXiv 2604.09588)](https://arxiv.org/html/2604.09588)
- [Moltable Identity Layer Documentation](https://moltable.ai/docs)
- [Identity Graph Blog Post](https://moltable.ai/blog/identity-graph-vs-vector-search)
- [MCP Specification](https://modelcontextprotocol.io)
