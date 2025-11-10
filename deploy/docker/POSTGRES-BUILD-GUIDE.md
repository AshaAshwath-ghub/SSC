# PostgreSQL Custom Image Build Guide

This guide explains how to build, test, and deploy a custom PostgreSQL image for the SSC Application.

## 📁 Files Created

```
deploy/docker/
├── Dockerfile.postgres              # Custom PostgreSQL Dockerfile
├── docker-compose.postgres.yml      # Local testing with Docker Compose
├── build-postgres.sh                # Build script (Linux/Mac)
├── build-postgres.bat               # Build script (Windows)
├── postgres-init-scripts/
│   ├── 01-init-database.sh         # Database initialization
│   └── 02-performance-tuning.sh    # Performance optimization
└── POSTGRES-BUILD-GUIDE.md         # This file
```

---

## 🎯 Quick Start

### Option 1: Test Locally with Docker Compose (Recommended First)

```bash
# Navigate to docker directory
cd deploy/docker

# Start PostgreSQL and pgAdmin
docker-compose -f docker-compose.postgres.yml up -d

# Check status
docker-compose -f docker-compose.postgres.yml ps

# View logs
docker-compose -f docker-compose.postgres.yml logs -f postgres

# Stop and cleanup
docker-compose -f docker-compose.postgres.yml down
```

**Access:**
- PostgreSQL: `localhost:5432`
  - User: `postgres`
  - Password: `postgres`
  - Database: `appdb`

- pgAdmin: `http://localhost:5050`
  - Email: `admin@ssc.local`
  - Password: `admin`

---

### Option 2: Build and Push to Azure Container Registry

#### For Windows:

```cmd
cd deploy\docker

REM Build locally
build-postgres.bat

REM Follow the interactive menu:
REM 1. Build locally only
REM 2. Build and test locally
REM 3. Build, test, and push to ACR  <-- Choose this for full workflow
REM 4. Push existing image to ACR
REM 5. Exit
```

#### For Linux/Mac:

```bash
cd deploy/docker

# Make script executable
chmod +x build-postgres.sh

# Run interactively
./build-postgres.sh

# Or run non-interactively
./build-postgres.sh build        # Build only
./build-postgres.sh test         # Build and test
./build-postgres.sh push         # Build, test, and push to ACR
./build-postgres.sh push-only    # Push existing image
```

---

## 🔧 Customization

### Environment Variables

You can customize the build using environment variables:

```bash
# Set your ACR name
export ACR_NAME="your-acr-name"

# Set custom version
export VERSION="16.1"

# Then run the build script
./build-postgres.sh push
```

For Windows:
```cmd
set ACR_NAME=your-acr-name
set VERSION=16.1
build-postgres.bat
```

### Adding Custom Initialization Scripts

Add new `.sh` or `.sql` files to `postgres-init-scripts/`:

```bash
deploy/docker/postgres-init-scripts/
├── 01-init-database.sh      # Existing
├── 02-performance-tuning.sh # Existing
└── 03-your-custom-script.sh # Your new script
```

Scripts are executed in alphabetical order when the database is initialized for the first time.

**Example custom script:**

```bash
#!/bin/bash
# 03-create-custom-tables.sh
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );
EOSQL
```

### Modifying the Dockerfile

Edit `deploy/docker/Dockerfile.postgres` to:
- Install additional PostgreSQL extensions
- Add custom configuration files
- Include backup scripts
- Modify performance settings

---

## 🚀 Deploying to Kubernetes

### Step 1: Build and Push Image

```bash
cd deploy/docker

# Windows
build-postgres.bat
# Select option 3 (Build, test, and push to ACR)

# Linux/Mac
./build-postgres.sh push
```

### Step 2: Update Kubernetes Deployment

Edit `deploy/aks/k8s/04-postgres.yaml`:

```yaml
containers:
  - name: postgres
    # Uncomment and update with your ACR name:
    image: sscappregistry.azurecr.io/ssc-postgres:latest
    # Comment out the default image:
    # image: postgres:16-alpine
```

Replace `sscappregistry` with your actual ACR name.

### Step 3: Deploy to Kubernetes

```bash
cd deploy/aks

# Deploy using the automated script
./deploy.sh
# Select option 2 (Deploy only)

# Or deploy manually
kubectl apply -f k8s/04-postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
```

### Step 4: Verify Deployment

```bash
# Check pod status
kubectl get pods -n ssc-app -l app=postgres

# Check logs
kubectl logs -n ssc-app -l app=postgres

# Test connection
kubectl exec -it -n ssc-app deployment/postgres -- psql -U postgres -d appdb -c "SELECT version();"
```

---

## 🔍 Testing Locally

### Test 1: Basic Connection Test

```bash
# Start container
docker run -d --name pg-test \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=testdb \
  -p 5433:5432 \
  ssc-postgres:latest

# Wait for startup
sleep 10

# Test connection
docker exec pg-test pg_isready -U postgres

# Run queries
docker exec pg-test psql -U postgres -d testdb -c "SELECT version();"

# Check extensions
docker exec pg-test psql -U postgres -d testdb -c "SELECT * FROM pg_extension;"

# Cleanup
docker rm -f pg-test
```

### Test 2: Performance Test

```bash
# Start container with performance tuning
docker run -d --name pg-perf \
  -e POSTGRES_PASSWORD=testpass \
  -p 5433:5432 \
  ssc-postgres:latest

# Check configuration
docker exec pg-perf psql -U postgres -c "SHOW shared_buffers;"
docker exec pg-perf psql -U postgres -c "SHOW max_connections;"

# Cleanup
docker rm -f pg-perf
```

### Test 3: Data Persistence Test

```bash
# Start with volume
docker run -d --name pg-persist \
  -e POSTGRES_PASSWORD=testpass \
  -v pg-data:/var/lib/postgresql/data \
  -p 5433:5432 \
  ssc-postgres:latest

# Create test data
docker exec pg-persist psql -U postgres -c "CREATE TABLE test (id serial, data text);"
docker exec pg-persist psql -U postgres -c "INSERT INTO test (data) VALUES ('hello');"

# Restart container
docker restart pg-persist
sleep 10

# Verify data persisted
docker exec pg-persist psql -U postgres -c "SELECT * FROM test;"

# Cleanup
docker rm -f pg-persist
docker volume rm pg-data
```

---

## 🎛️ Docker Compose Configuration

### Starting Services

```bash
cd deploy/docker

# Start all services
docker-compose -f docker-compose.postgres.yml up -d

# Start only PostgreSQL
docker-compose -f docker-compose.postgres.yml up -d postgres

# View logs
docker-compose -f docker-compose.postgres.yml logs -f
```

### Stopping Services

```bash
# Stop services (keeps data)
docker-compose -f docker-compose.postgres.yml stop

# Stop and remove containers (keeps volumes)
docker-compose -f docker-compose.postgres.yml down

# Remove everything including volumes
docker-compose -f docker-compose.postgres.yml down -v
```

### Connecting from Your Backend

Update your backend connection string to use the Docker network:

```python
# If backend is also running in Docker Compose
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/appdb"

# If backend is running on host machine
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/appdb"
```

---

## 🔐 Security Best Practices

### 1. Change Default Passwords

**For local testing:**
Edit `docker-compose.postgres.yml`:
```yaml
environment:
  POSTGRES_PASSWORD: your-strong-password-here
```

**For Kubernetes:**
Update `deploy/aks/k8s/02-secrets.yaml`:
```yaml
stringData:
  DB_PASSWORD: "your-strong-password-here"
```

### 2. Use Secrets Management

For production, use Azure Key Vault instead of hardcoded secrets:

```bash
# Create Key Vault
az keyvault create --name ssc-app-kv --resource-group ssc-app-rg --location eastus

# Store database password
az keyvault secret set --vault-name ssc-app-kv --name db-password --value "your-password"

# Reference in Kubernetes (requires CSI driver)
```

### 3. Network Security

- Use Kubernetes NetworkPolicies to restrict access
- Only allow backend pods to connect to PostgreSQL
- Never expose PostgreSQL directly to the internet

---

## 📊 Monitoring and Maintenance

### View Logs

```bash
# Docker Compose
docker-compose -f docker-compose.postgres.yml logs -f postgres

# Docker
docker logs -f ssc-postgres

# Kubernetes
kubectl logs -f -n ssc-app deployment/postgres
```

### Check Resource Usage

```bash
# Docker
docker stats ssc-postgres

# Kubernetes
kubectl top pod -n ssc-app -l app=postgres
```

### Backup Database

```bash
# Local Docker
docker exec ssc-postgres pg_dump -U postgres appdb > backup.sql

# Kubernetes
kubectl exec -n ssc-app deployment/postgres -- pg_dump -U postgres appdb > backup.sql

# Restore
docker exec -i ssc-postgres psql -U postgres appdb < backup.sql
```

---

## 🐛 Troubleshooting

### Issue: Container won't start

**Check logs:**
```bash
docker logs ssc-postgres
# or
kubectl logs -n ssc-app -l app=postgres
```

**Common causes:**
- Incorrect environment variables
- Port already in use
- Insufficient permissions
- Corrupted data directory

### Issue: Cannot connect to database

**Test connection:**
```bash
docker exec ssc-postgres pg_isready -U postgres
```

**Check network:**
```bash
docker network ls
docker network inspect bridge
```

### Issue: Performance is slow

**Check configuration:**
```bash
docker exec ssc-postgres psql -U postgres -c "SHOW ALL;"
```

**Monitor queries:**
```bash
docker exec -it ssc-postgres psql -U postgres
# Then run:
SELECT * FROM pg_stat_activity;
```

### Issue: Out of disk space

**Check disk usage:**
```bash
docker exec ssc-postgres du -sh /var/lib/postgresql/data
```

**Clean up:**
```bash
# Vacuum database
docker exec ssc-postgres psql -U postgres -d appdb -c "VACUUM FULL;"

# Remove old WAL files
docker exec ssc-postgres find /var/lib/postgresql/data/pg_wal -type f -mtime +7 -delete
```

---

## 📚 Additional Resources

### PostgreSQL Extensions Included

- `uuid-ossp` - UUID generation
- `pgcrypto` - Cryptographic functions
- `hstore` - Key-value store

### Useful Commands

```sql
-- List all databases
\l

-- List all tables
\dt

-- Describe table
\d table_name

-- List all extensions
\dx

-- Show current connections
SELECT * FROM pg_stat_activity;

-- Show database size
SELECT pg_size_pretty(pg_database_size('appdb'));
```

### Performance Tuning

Current settings in `02-performance-tuning.sh`:
- `max_connections`: 200
- `shared_buffers`: 256MB
- `effective_cache_size`: 1GB
- `work_mem`: 4MB

Adjust based on your workload and available resources.

---

## 🆘 Support

If you encounter issues:

1. Check logs first
2. Verify environment variables
3. Test connection locally
4. Review PostgreSQL documentation: https://www.postgresql.org/docs/
5. Check Kubernetes events: `kubectl get events -n ssc-app --sort-by='.lastTimestamp'`

---

## ✅ Checklist

Before deploying to production:

- [ ] Changed default PostgreSQL password
- [ ] Tested image builds successfully
- [ ] Tested database connection locally
- [ ] Verified initialization scripts run correctly
- [ ] Pushed image to ACR
- [ ] Updated Kubernetes deployment with correct image
- [ ] Configured persistent storage (PVC)
- [ ] Set up automated backups
- [ ] Configured monitoring and alerts
- [ ] Documented connection details for team
- [ ] Tested disaster recovery procedure

---

**Happy Database Building! 🚀**
