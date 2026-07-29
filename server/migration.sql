-- Moltable pgvector 迁移脚本
-- 在 Supabase SQL Editor 中执行此脚本

-- 1. 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 创建 match_memories RPC 函数（pgvector 相似搜索）
-- ⚠️ 与 schema.sql 保持签名一致 — 两处必须同步
CREATE OR REPLACE FUNCTION match_memories(
    query_embedding vector(384),
    match_user_id text,
    match_count int DEFAULT 5,
    match_category text DEFAULT NULL,
    match_threshold float DEFAULT 0.5
) RETURNS TABLE (
    id uuid,
    content text,
    category text,
    source text,
    tags text[],
    similarity float,
    created_at timestamptz
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.content,
        m.category,
        m.source,
        m.tags,
        1 - (m.embedding <=> query_embedding) AS similarity,
        m.created_at
    FROM memories m
    WHERE m.user_id::text = match_user_id
      AND m.is_archived = false
      AND (match_category IS NULL OR m.category = match_category)
      AND 1 - (m.embedding <=> query_embedding) > match_threshold
    ORDER BY m.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 3. 确认 embedding 列类型
-- 如果 embedding 列不是 vector(384)，执行：
-- ALTER TABLE memories ALTER COLUMN embedding TYPE vector(384);

-- 4. 创建 HNSW 向量索引（推荐，比 IVFFlat 性能更好）
-- CREATE INDEX IF NOT EXISTS memories_embedding_idx 
--     ON memories USING hnsw (embedding vector_cosine_ops);
