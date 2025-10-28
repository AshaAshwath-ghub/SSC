# Testing Phase 1 Implementation

This guide will walk you through testing all Phase 1 components to ensure everything is working correctly.

---

## Prerequisites Check

Before testing, verify you have the required tools installed:

```bash
# Check Docker
docker --version
docker-compose --version

# Check Python (if testing locally)
python --version  # Should be 3.11+

# Check Node.js (optional for frontend)
node --version  # Should be 20+
```

---

## Test 1: Docker Environment Startup

### 1.1 Start All Services

```bash
cd C:\workspace\Projects\SSC\VITE

# Start all services
docker-compose up -d

# Expected output:
# Creating network "vite_app-network"
# Creating volume "vite_postgres_data"
# Creating volume "vite_mongodb_data"
# Creating volume "vite_redis_data"
# Creating app-postgres ... done
# Creating app-mongodb ... done
# Creating app-redis ... done
# Creating app-backend ... done
```

### 1.2 Verify All Containers Are Running

```bash
docker-compose ps

# Expected output:
# NAME           IMAGE              STATUS         PORTS
# app-postgres   postgres:16        Up (healthy)   0.0.0.0:5432->5432/tcp
# app-mongodb    mongo:7            Up (healthy)   0.0.0.0:27017->27017/tcp
# app-redis      redis:7            Up (healthy)   0.0.0.0:6379->6379/tcp
# app-backend    vite-backend       Up (healthy)   0.0.0.0:8000->8000/tcp
```

**✅ Pass Criteria:** All containers show "Up (healthy)" status

**❌ If containers are not healthy, check logs:**
```bash
docker-compose logs <service-name>
```

---

## Test 2: Backend API Health Check

### 2.1 Root Endpoint Test

```bash
curl http://localhost:8000/

# Expected JSON response:
{
  "name": "Application",
  "version": "1.0.0",
  "environment": "development",
  "status": "running"
}
```

**✅ Pass:** Returns JSON with app info
**❌ Fail:** Connection refused or no response

### 2.2 Full Health Check

```bash
curl http://localhost:8000/health

# Expected JSON response:
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "sql_database": {
      "status": "healthy",
      "type": "postgresql"
    },
    "mongodb": {
      "status": "healthy"
    },
    "redis": {
      "status": "healthy"
    }
  }
}
```

**✅ Pass:** All services show "healthy" status
**❌ Fail:** Any service shows "unhealthy" or "degraded"

### 2.3 Kubernetes Probes

```bash
# Readiness check
curl http://localhost:8000/ready
# Expected: {"status": "ready"}

# Liveness check
curl http://localhost:8000/live
# Expected: {"status": "alive"}
```

**✅ Pass:** Both return expected JSON
**❌ Fail:** Any error or wrong response

---

## Test 3: API Documentation

### 3.1 Swagger UI

Open in browser: http://localhost:8000/api/v1/docs

**✅ Pass Criteria:**
- Page loads without errors
- Shows "Application" title
- Shows version "1.0.0"
- API endpoints are visible (even if empty for now)
- Can expand and view endpoint details

### 3.2 ReDoc

Open in browser: http://localhost:8000/api/v1/redoc

**✅ Pass Criteria:**
- Page loads without errors
- Shows API documentation
- Navigation menu on the left
- Dark/light theme toggle works

---

## Test 4: PostgreSQL Database

### 4.1 Connection Test

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d appdb

# Once connected, run:
SELECT version();

# Expected: PostgreSQL 16.x version string

# Check database exists
\l

# Expected: appdb in the list

# Exit
\q
```

**✅ Pass:** Successfully connects and shows database
**❌ Fail:** Connection refused or authentication error

### 4.2 Database Ready for Migrations

```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d appdb

# Check if any tables exist (should be none yet)
\dt

# Expected: "Did not find any relations" or empty list

# Exit
\q
```

**✅ Pass:** Database is empty and ready
**❌ Fail:** Connection issues

---

## Test 5: MongoDB

### 5.1 Connection Test

```bash
# Connect to MongoDB
docker-compose exec mongodb mongosh appdb

# Once connected, run:
db.runCommand({ ping: 1 })

# Expected: { ok: 1 }

# Check collections (should be empty)
show collections

# Expected: No collections yet

# Exit
exit
```

**✅ Pass:** Successfully connects and pings
**❌ Fail:** Connection refused

### 5.2 Create Test Collection

```bash
# Connect to MongoDB
docker-compose exec mongodb mongosh appdb

# Create a test document
db.test.insertOne({ message: "Phase 1 test", timestamp: new Date() })

# Query it back
db.test.find()

# Expected: Shows the document you just inserted

# Clean up
db.test.drop()

# Exit
exit
```

**✅ Pass:** Can insert and query documents
**❌ Fail:** Permission errors or connection issues

---

## Test 6: Redis

### 6.1 Connection Test

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Test connection
PING

# Expected: PONG

# Set a test key
SET phase1:test "Hello from Phase 1"

# Get it back
GET phase1:test

# Expected: "Hello from Phase 1"

# Check which database we're in
SELECT 0
# Expected: OK

# Clean up
DEL phase1:test

# Exit
exit
```

**✅ Pass:** All Redis commands work
**❌ Fail:** Connection refused or command errors

### 6.2 Test Multiple Databases

```bash
docker-compose exec redis redis-cli

# Test main DB (0)
SELECT 0
SET main:test "Main DB"
GET main:test
# Expected: "Main DB"

# Test session DB (1)
SELECT 1
SET session:test "Session DB"
GET session:test
# Expected: "Session DB"

# Test cache DB (2)
SELECT 2
SET cache:test "Cache DB"
GET cache:test
# Expected: "Cache DB"

# Clean up
SELECT 0
DEL main:test
SELECT 1
DEL session:test
SELECT 2
DEL cache:test

exit
```

**✅ Pass:** Can switch between databases
**❌ Fail:** Cannot select databases

---

## Test 7: Backend Logs

### 7.1 Check Application Logs

```bash
# View backend logs
docker-compose logs backend

# Expected log entries:
# - "Starting Application v1.0.0"
# - "Environment: development"
# - "Database type: postgresql"
# - "Initializing database connections..."
# - "PostgreSQL connection initialized successfully"
# - "MongoDB connected successfully"
# - "Redis connected successfully"
# - "All database connections initialized successfully"
```

**✅ Pass:** All connection messages show "successfully"
**❌ Fail:** Any connection errors or exceptions

### 7.2 Follow Logs in Real-Time

```bash
# Follow logs
docker-compose logs -f backend

# In another terminal, make a request:
curl http://localhost:8000/

# In the logs, you should see:
# - "GET /"
# - "GET / - 200"
# - Request ID in logs

# Press Ctrl+C to stop following
```

**✅ Pass:** See request logs with timestamps
**❌ Fail:** No logs or errors

---

## Test 8: Request ID Tracing

### 8.1 Verify Request IDs

```bash
# Make a request and capture headers
curl -v http://localhost:8000/ 2>&1 | grep -i "x-request-id"

# Expected: X-Request-ID: <some-uuid>

# Make multiple requests and verify different IDs
curl -I http://localhost:8000/ | grep -i "x-request-id"
curl -I http://localhost:8000/ | grep -i "x-request-id"
curl -I http://localhost:8000/ | grep -i "x-request-id"

# Each should have a different UUID
```

**✅ Pass:** Each request has unique X-Request-ID header
**❌ Fail:** No header or same ID

---

## Test 9: CORS Configuration

### 9.1 Test CORS Headers

```bash
# Test preflight request
curl -X OPTIONS http://localhost:8000/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v 2>&1 | grep -i "access-control"

# Expected headers:
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Credentials: true
# Access-Control-Allow-Methods: *
```

**✅ Pass:** CORS headers present
**❌ Fail:** No CORS headers

---

## Test 10: Database Adapter Pattern

### 10.1 Test PostgreSQL Connection

```bash
# Check backend logs for PostgreSQL
docker-compose logs backend | grep -i "postgresql"

# Expected:
# "Database type: postgresql"
# "Initializing PostgreSQL connection"
# "PostgreSQL connection initialized successfully"
```

### 10.2 Switch to SQL Server (Optional)

```bash
# Stop backend
docker-compose stop backend

# Start SQL Server
docker-compose --profile sqlserver up -d sqlserver

# Wait for SQL Server to be healthy
docker-compose ps sqlserver

# Update backend/.env
# Change: DB_TYPE=sqlserver
# Note: You'll need to edit the file manually or use sed:

# Start backend
docker-compose up -d backend

# Check logs
docker-compose logs backend | grep -i "sql server"

# Expected:
# "Database type: sqlserver"
# "Initializing SQL Server connection"
# "SQL Server connection initialized successfully"

# Switch back to PostgreSQL
# Stop backend, change DB_TYPE=postgresql, restart backend
```

**✅ Pass:** Can switch between databases
**❌ Fail:** Adapter selection fails

---

## Test 11: Configuration Loading

### 11.1 Verify Environment Variables

```bash
# Check backend environment
docker-compose exec backend env | grep -E "DB_|MONGO_|REDIS_|APP_"

# Expected output includes:
# DB_TYPE=postgresql
# DB_HOST=postgres
# MONGO_URI=mongodb://mongodb:27017
# REDIS_URL=redis://redis:6379/0
# APP_NAME=Application
```

**✅ Pass:** All required environment variables are set
**❌ Fail:** Missing critical variables

---

## Test 12: Shared Types

### 12.1 Verify Shared Directory

```bash
# List shared directory
ls shared/

# Expected files:
# types.ts
# constants.ts
# index.ts
# package.json
# tsconfig.json
# README.md
```

### 12.2 Check TypeScript Types (Optional)

```bash
cd shared

# Install dependencies (if needed)
npm install

# Type check
npx tsc --noEmit

# Expected: No errors
```

**✅ Pass:** All files present, no TypeScript errors
**❌ Fail:** Missing files or type errors

---

## Test 13: Performance Test

### 13.1 Response Time Test

```bash
# Test response time (requires 'time' command)
time curl -s http://localhost:8000/ > /dev/null

# Expected: < 1 second for first request
# Expected: < 100ms for subsequent requests
```

### 13.2 Load Test (Optional)

```bash
# Install apache bench (ab) or use curl in a loop
for i in {1..100}; do
  curl -s http://localhost:8000/ > /dev/null
done

# Check backend logs - should handle all requests
docker-compose logs --tail=100 backend

# Expected: All requests return 200 OK
```

**✅ Pass:** Fast response times, handles load
**❌ Fail:** Slow or timeouts

---

## Test 14: Docker Health Checks

### 14.1 Verify Health Check Configuration

```bash
# Check PostgreSQL health
docker inspect app-postgres | grep -A 10 "Health"

# Check backend health
docker inspect app-backend | grep -A 10 "Health"

# Wait a minute, then check status
docker-compose ps

# All should show (healthy)
```

**✅ Pass:** All containers report healthy
**❌ Fail:** Any container unhealthy

---

## Test 15: Graceful Shutdown

### 15.1 Test Application Shutdown

```bash
# Stop backend gracefully
docker-compose stop backend

# Check logs for shutdown messages
docker-compose logs --tail=20 backend

# Expected:
# "Shutting down application..."
# "Closing PostgreSQL connections"
# "MongoDB connection closed"
# "Redis connections closed"
# "Application shutdown complete"
```

**✅ Pass:** Clean shutdown with proper cleanup
**❌ Fail:** Errors during shutdown

### 15.2 Restart Test

```bash
# Start backend again
docker-compose start backend

# Check logs
docker-compose logs --tail=20 backend

# Expected:
# "Starting Application..."
# All connections initialized successfully
```

**✅ Pass:** Restarts cleanly
**❌ Fail:** Fails to restart

---

## Test 16: Volume Persistence

### 16.1 Test Data Persistence

```bash
# Create test data in PostgreSQL
docker-compose exec postgres psql -U postgres -d appdb -c "CREATE TABLE test (id int, name text); INSERT INTO test VALUES (1, 'Phase 1');"

# Stop all services
docker-compose down

# Start services again
docker-compose up -d

# Wait for services to be healthy
sleep 10

# Check if data persists
docker-compose exec postgres psql -U postgres -d appdb -c "SELECT * FROM test;"

# Expected: Shows the row we inserted

# Clean up
docker-compose exec postgres psql -U postgres -d appdb -c "DROP TABLE test;"
```

**✅ Pass:** Data persists across restarts
**❌ Fail:** Data lost

---

## Test 17: Network Connectivity

### 17.1 Test Inter-Service Communication

```bash
# Backend should be able to reach PostgreSQL
docker-compose exec backend ping -c 2 postgres

# Backend should be able to reach MongoDB
docker-compose exec backend ping -c 2 mongodb

# Backend should be able to reach Redis
docker-compose exec backend ping -c 2 redis
```

**✅ Pass:** All services reachable
**❌ Fail:** Network connectivity issues

---

## Automated Test Script

### Create Test Script

```bash
# Create test script
cat > test_phase1.sh << 'EOF'
#!/bin/bash

echo "======================================"
echo "Phase 1 Implementation Testing"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3

    echo -n "Testing $name... "
    response=$(curl -s "$url")

    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  Expected: $expected"
        echo "  Got: $response"
        ((FAILED++))
    fi
}

# Start tests
echo "1. Testing Backend Root Endpoint"
test_endpoint "Root" "http://localhost:8000/" "Application"

echo ""
echo "2. Testing Health Check"
test_endpoint "Health" "http://localhost:8000/health" "healthy"

echo ""
echo "3. Testing Ready Check"
test_endpoint "Ready" "http://localhost:8000/ready" "ready"

echo ""
echo "4. Testing Live Check"
test_endpoint "Live" "http://localhost:8000/live" "alive"

echo ""
echo "5. Testing Request ID Header"
header_test=$(curl -I -s http://localhost:8000/ | grep -i "x-request-id")
if [ ! -z "$header_test" ]; then
    echo -e "Request ID Header... ${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "Request ID Header... ${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo ""
echo "6. Testing Database Services"

# PostgreSQL
echo -n "PostgreSQL... "
if docker-compose exec -T postgres psql -U postgres -d appdb -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# MongoDB
echo -n "MongoDB... "
if docker-compose exec -T mongodb mongosh appdb --eval "db.runCommand({ping:1})" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Redis
echo -n "Redis... "
if docker-compose exec -T redis redis-cli PING | grep -q "PONG"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo ""
echo "======================================"
echo "Test Results"
echo "======================================"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed! ✗${NC}"
    exit 1
fi
EOF

# Make executable
chmod +x test_phase1.sh

# Run tests
./test_phase1.sh
```

---

## Quick Checklist

Use this checklist to quickly verify Phase 1:

```
□ Docker services start: docker-compose up -d
□ All containers healthy: docker-compose ps
□ Root endpoint works: curl http://localhost:8000/
□ Health check passes: curl http://localhost:8000/health
□ Swagger UI loads: http://localhost:8000/api/v1/docs
□ PostgreSQL connects: docker-compose exec postgres psql -U postgres -d appdb
□ MongoDB connects: docker-compose exec mongodb mongosh appdb
□ Redis connects: docker-compose exec redis redis-cli PING
□ Backend logs clean: docker-compose logs backend
□ No errors in logs: docker-compose logs | grep -i error
```

---

## Troubleshooting

### Issue: Containers not starting

```bash
# Check Docker is running
docker info

# Check disk space
df -h

# Remove old containers/volumes
docker-compose down -v
docker system prune -a
docker-compose up -d
```

### Issue: Backend not healthy

```bash
# Check backend logs
docker-compose logs backend

# Check if databases are ready
docker-compose ps

# Restart backend
docker-compose restart backend
```

### Issue: Port already in use

```bash
# Check what's using the port
# Linux/Mac:
lsof -i :8000
lsof -i :5432

# Windows:
netstat -ano | findstr :8000

# Kill the process or change port in docker-compose.yml
```

### Issue: Database connection refused

```bash
# Check if database container is running
docker-compose ps

# Check database logs
docker-compose logs postgres

# Restart the database
docker-compose restart postgres

# Wait for health check
sleep 10
docker-compose ps
```

---

## Expected Final State

After all tests pass, you should have:

1. ✅ All 4 Docker containers running and healthy
2. ✅ Backend API responding on port 8000
3. ✅ PostgreSQL accessible on port 5432
4. ✅ MongoDB accessible on port 27017
5. ✅ Redis accessible on port 6379
6. ✅ Swagger UI accessible at /api/v1/docs
7. ✅ Health check returning all services healthy
8. ✅ Clean logs with no errors
9. ✅ Request IDs in all responses
10. ✅ Data persisting across restarts

---

## Next Steps

Once all tests pass:
1. ✅ Phase 1 is verified and working
2. 📝 Document any issues encountered
3. 🚀 Ready to proceed with Phase 2 (Authentication)

---

## Support

If any tests fail:
1. Check the specific section's troubleshooting guide
2. Review logs: `docker-compose logs <service>`
3. Verify `.env` configuration
4. Check `GETTING_STARTED.md` for setup instructions
5. Review `PHASE_1_COMPLETE.md` for expected behavior
