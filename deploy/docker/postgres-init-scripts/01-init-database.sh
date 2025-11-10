#!/bin/bash
set -e

echo "Initializing SSC Application Database..."

# Create extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable UUID extension
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- Enable pgcrypto for password hashing
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";

    -- Enable hstore for key-value pairs
    CREATE EXTENSION IF NOT EXISTS "hstore";

    -- Display installed extensions
    SELECT * FROM pg_extension;
EOSQL

echo "Database initialization completed successfully!"
