-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS btree_gin; -- For composite indexes

-- Set timezone
SET timezone = 'UTC';