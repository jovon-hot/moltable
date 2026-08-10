-- Migration: Add temporal_facts table for fact-change timeline tracking
-- Created: 2026-08-06
-- Feature: Temporal Memory Timeline (Zep competitive feature gap)
--
-- This table stores fact change events to build per-entity timelines.
-- Each row represents one fact transition (old_value → new_value).

-- Enable pgcrypto for UUID generation (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Main temporal facts table
CREATE TABLE IF NOT EXISTS temporal_facts (
    id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id     TEXT NOT NULL,
    entity      TEXT NOT NULL,              -- e.g. "preferred_language", "current_role"
    attribute   TEXT NOT NULL DEFAULT 'value', -- e.g. "value", "status", "version"
    old_value   TEXT,                       -- NULL = first time tracking
    new_value   TEXT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_memory_id TEXT,                  -- FK to memories.id if auto-detected
    confidence  REAL NOT NULL DEFAULT 0.8,  -- 0.0-1.0
    persona_id  TEXT,                       -- FK to personas.id if persona-scoped

    -- Indexes for fast queries
    CONSTRAINT temporal_facts_pkey PRIMARY KEY (id)
);

-- Fast lookup: get timeline for a specific entity
CREATE INDEX IF NOT EXISTS idx_temporal_user_entity
    ON temporal_facts (user_id, entity, attribute, recorded_at);

-- Recent changes feed
CREATE INDEX IF NOT EXISTS idx_temporal_user_recent
    ON temporal_facts (user_id, recorded_at DESC);

-- Look up by source memory
CREATE INDEX IF NOT EXISTS idx_temporal_source_memory
    ON temporal_facts (source_memory_id);

-- Persona-scoped queries
CREATE INDEX IF NOT EXISTS idx_temporal_persona
    ON temporal_facts (user_id, persona_id, recorded_at DESC);

-- Enable Row-Level Security
ALTER TABLE temporal_facts ENABLE ROW LEVEL SECURITY;

-- Users can only see their own temporal facts
CREATE POLICY "Users can view own temporal facts"
    ON temporal_facts FOR SELECT
    USING (auth.uid()::text = user_id);

-- Users can insert their own temporal facts
CREATE POLICY "Users can insert own temporal facts"
    ON temporal_facts FOR INSERT
    WITH CHECK (auth.uid()::text = user_id);
