# PostgreSQL Quick Start Guide

## 🚀 Quick Commands

### Test Locally (Easiest)

```bash
cd deploy/docker
docker-compose -f docker-compose.postgres.yml up -d
```

Connect to:
- **PostgreSQL**: `localhost:5432` (user: postgres, pass: postgres)
- **pgAdmin**: `http://localhost:5050` (email: admin@ssc.local, pass: admin)

---

### Build Custom Image

**Windows:**
```cmd
cd deploy\docker
build-postgres.bat
```

**Linux/Mac:**
```bash
cd deploy/docker
chmod +x build-postgres.sh
./build-postgres.sh
```

---

### Push to Azure Container Registry

```bash
# Set your ACR name
export ACR_NAME="sscappregistry"  # Windows: set ACR_NAME=sscappregistry

# Build and push
./build-postgres.sh push          # Windows: build-postgres.bat (select option 3)
```

---

### Deploy to Kubernetes

```bash
# 1. Update image in deploy/aks/k8s/04-postgres.yaml
# Change line 39 to:
#   image: sscappregistry.azurecr.io/ssc-postgres:latest

# 2. Deploy
cd deploy/aks
kubectl apply -f k8s/04-postgres.yaml

# 3. Wait for ready
kubectl wait --for=condition=ready pod -l app=postgres -n ssc-app --timeout=300s

# 4. Verify
kubectl get pods -n ssc-app -l app=postgres
```

---

### Connect to PostgreSQL

**From Local Machine (Port Forward):**
```bash
kubectl port-forward svc/postgres 5432:5432 -n ssc-app
# Then connect to localhost:5432
```

**From Inside Kubernetes:**
```bash
kubectl exec -it -n ssc-app deployment/postgres -- psql -U postgres -d appdb
```

**From Temporary Pod:**
```bash
kubectl run -it --rm --image=postgres:16-alpine pg-client -n ssc-app -- psql -h postgres -U postgres -d appdb
```

---

### Useful PostgreSQL Commands

```bash
# Check status
kubectl exec -n ssc-app deployment/postgres -- pg_isready -U postgres

# View logs
kubectl logs -f -n ssc-app deployment/postgres

# Backup database
kubectl exec -n ssc-app deployment/postgres -- pg_dump -U postgres appdb > backup.sql

# Restore database
kubectl exec -i -n ssc-app deployment/postgres -- psql -U postgres appdb < backup.sql

# Connect to psql shell
kubectl exec -it -n ssc-app deployment/postgres -- psql -U postgres -d appdb
```

---

### Stop Services

**Docker Compose:**
```bash
docker-compose -f docker-compose.postgres.yml down
```

**Kubernetes:**
```bash
kubectl delete -f deploy/aks/k8s/04-postgres.yaml
```

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `Dockerfile.postgres` | Custom PostgreSQL image definition |
| `docker-compose.postgres.yml` | Local testing with Docker Compose |
| `build-postgres.sh` / `.bat` | Build and push scripts |
| `postgres-init-scripts/` | Database initialization scripts |
| `deploy/aks/k8s/04-postgres.yaml` | Kubernetes deployment |

---

## 📋 Common Issues

### Port already in use
```bash
# Find process using port 5432
netstat -ano | findstr :5432  # Windows
lsof -i :5432                  # Linux/Mac

# Stop Docker Compose
docker-compose -f docker-compose.postgres.yml down
```

### Cannot connect
```bash
# Check if container is running
docker ps | grep postgres

# Check logs
docker logs ssc-postgres
```

### Need to reset database
```bash
# Docker Compose
docker-compose -f docker-compose.postgres.yml down -v

# Kubernetes
kubectl delete pvc postgres-pvc -n ssc-app
```

---

## 📞 Connection Details for Team

### Local Development
```
Host: localhost
Port: 5432
Database: appdb
Username: postgres
Password: postgres
```

### Kubernetes (via port-forward)
```bash
# Team member runs:
kubectl port-forward svc/postgres 5432:5432 -n ssc-app

# Then connects to:
Host: localhost
Port: 5432
Database: appdb
Username: postgres
Password: [from secrets]
```

### From Backend Application
```
Host: postgres
Port: 5432
Database: appdb
Username: postgres
Password: [from secrets]

Connection String:
postgresql://postgres:password@postgres:5432/appdb
```

---

For detailed information, see [POSTGRES-BUILD-GUIDE.md](./POSTGRES-BUILD-GUIDE.md)
