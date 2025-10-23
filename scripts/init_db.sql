-- UP2D8 Database Initialization
-- This script runs when the PostgreSQL container is first created

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- For UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";    -- For encryption functions

-- Note: pgvector extension for vector similarity search
-- Uncomment below if using pgvector instead of ChromaDB
-- CREATE EXTENSION IF NOT EXISTS vector;

-- Database is already created by POSTGRES_DB env var
-- This script is just for extensions and initial setup

-- Verify setup
SELECT version();
SELECT 'UP2D8 database initialized successfully!' AS status;
