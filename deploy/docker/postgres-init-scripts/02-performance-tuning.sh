#!/bin/bash
set -e

echo "Applying performance tuning configurations..."

# Performance tuning for PostgreSQL
# These are optimized for development/small production workloads
# Adjust based on your server specs

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Connection settings
    ALTER SYSTEM SET max_connections = '200';

    -- Memory settings (adjust based on available RAM)
    ALTER SYSTEM SET shared_buffers = '256MB';
    ALTER SYSTEM SET effective_cache_size = '1GB';
    ALTER SYSTEM SET maintenance_work_mem = '64MB';
    ALTER SYSTEM SET work_mem = '4MB';

    -- Write-Ahead Logging settings
    ALTER SYSTEM SET wal_buffers = '8MB';
    ALTER SYSTEM SET checkpoint_completion_target = '0.9';

    -- Query planner
    ALTER SYSTEM SET random_page_cost = '1.1';
    ALTER SYSTEM SET effective_io_concurrency = '200';

    -- Logging
    ALTER SYSTEM SET log_statement = 'mod';
    ALTER SYSTEM SET log_duration = 'on';
    ALTER SYSTEM SET log_min_duration_statement = '1000';

    -- Locale and encoding
    SHOW lc_collate;
    SHOW lc_ctype;
    SHOW server_encoding;
EOSQL

echo "Performance tuning applied! (requires restart to take full effect)"
