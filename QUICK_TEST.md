# Quick Phase 1 Test Guide

## 🚀 Fastest Way to Test (30 seconds)

### Windows (PowerShell)
```powershell
# Start services
docker-compose up -d

# Run automated tests
.\test_phase1.ps1
```

### Linux/Mac (Bash)
```bash
# Start services
docker-compose up -d

# Run automated tests
chmod +x test_phase1.sh
./test_phase1.sh
```

---

## ✅ Quick Manual Test (2 minutes)

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Check Status
```bash
docker-compose ps
# All should show "Up (healthy)"
```

### 3. Test Health Endpoint
```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "services": {
    "sql_database": {"status": "healthy"},
    "mongodb": {"status": "healthy"},
    "redis": {"status": "healthy"}
  }
}
```

### 4. Open API Docs
Open in browser: http://localhost:8000/api/v1/docs

✅ **If you see Swagger UI, Phase 1 is working!**

---

## 🔍 Individual Service Tests

### PostgreSQL
```bash
docker-compose exec postgres psql -U postgres -d appdb -c "SELECT 1"
```
✅ Should return: `1`

### MongoDB
```bash
docker-compose exec mongodb mongosh appdb --eval "db.runCommand({ping:1})"
```
✅ Should return: `{ ok: 1 }`

### Redis
```bash
docker-compose exec redis redis-cli PING
```
✅ Should return: `PONG`

### Backend Logs
```bash
docker-compose logs backend | grep "successfully"
```
✅ Should see:
- "PostgreSQL connection initialized successfully"
- "MongoDB connected successfully"
- "Redis connected successfully"

---

## 🐛 Quick Troubleshooting

### Services won't start
```bash
docker-compose down -v
docker system prune -a
docker-compose up -d
```

### Backend unhealthy
```bash
docker-compose logs backend
docker-compose restart backend
```

### Port in use
```bash
# Change ports in docker-compose.yml or stop conflicting service
docker-compose down
# Edit docker-compose.yml
docker-compose up -d
```

---

## 📊 Success Criteria

✅ All containers show "Up (healthy)"
✅ Health endpoint returns all services healthy
✅ Swagger UI loads
✅ All databases connectable
✅ No errors in backend logs

---

## 🎯 One-Liner Health Check

```bash
curl -s http://localhost:8000/health | python -m json.tool
```

Or with jq:
```bash
curl -s http://localhost:8000/health | jq
```

---

## 📝 Complete Test Suite

For comprehensive testing, see:
- **TESTING_PHASE_1.md** - Full test guide (17 tests)
- **test_phase1.sh** - Automated Linux/Mac tests
- **test_phase1.ps1** - Automated Windows tests

---

## 🚦 Test Results Interpretation

### ✅ All Green
```
✓ ALL TESTS PASSED!
Phase 1 is working correctly!
```
**Action:** Proceed to Phase 2

### ⚠️ Some Yellow
```
⚠ UNHEALTHY
⚠ Found errors
```
**Action:** Check logs, may still be starting up

### ❌ Any Red
```
✗ FAIL
✗ NOT RUNNING
```
**Action:** See troubleshooting section or TESTING_PHASE_1.md

---

## 🔗 Quick Links

- API Docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc
- Health Check: http://localhost:8000/health
- PostgreSQL: localhost:5432
- MongoDB: localhost:27017
- Redis: localhost:6379

---

## 📞 Need Help?

1. Check logs: `docker-compose logs <service>`
2. Review: `TESTING_PHASE_1.md`
3. Review: `GETTING_STARTED.md`
4. Check: `PROJECT_STATUS.md` for known issues
