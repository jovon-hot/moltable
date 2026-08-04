-- Moltable A/B Testing Framework — Database Schema
-- Run this in your Supabase SQL Editor or it auto-creates in SQLite mode.

-- Experiments table
CREATE TABLE IF NOT EXISTS experiments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    variants TEXT NOT NULL DEFAULT '[]',  -- JSON array of {key, name, weight, description}
    goal TEXT DEFAULT 'conversion',
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'running', 'paused', 'completed')),
    traffic_pct REAL DEFAULT 100.0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- User-to-variant assignments
CREATE TABLE IF NOT EXISTS experiment_assignments (
    id SERIAL PRIMARY KEY,
    experiment_id TEXT NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    variant TEXT NOT NULL,
    assigned_at TEXT NOT NULL,
    UNIQUE(experiment_id, user_id)
);

-- Conversion events
CREATE TABLE IF NOT EXISTS experiment_conversions (
    id SERIAL PRIMARY KEY,
    experiment_id TEXT NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    variant TEXT NOT NULL,
    goal TEXT DEFAULT 'conversion',
    converted_at TEXT NOT NULL
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_exp_assignments_exp ON experiment_assignments(experiment_id);
CREATE INDEX IF NOT EXISTS idx_exp_assignments_user ON experiment_assignments(experiment_id, user_id);
CREATE INDEX IF NOT EXISTS idx_exp_conversions_exp ON experiment_conversions(experiment_id);
CREATE INDEX IF NOT EXISTS idx_exp_conversions_variant ON experiment_conversions(experiment_id, variant);
