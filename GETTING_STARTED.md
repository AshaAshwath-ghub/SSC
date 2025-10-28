# Getting Started Guide

Quick start guide for the full-stack application.

## Prerequisites

Choose one of the following setups:

### Option A: Docker (Recommended for Quick Start)
- Docker Desktop or Docker Engine
- Docker Compose

### Option B: Local Development
- Python 3.11+
- Node.js 20+
- PostgreSQL 16+ OR SQL Server 2022+
- MongoDB 7+
- Redis 7+

## Quick Start with Docker

### 1. Start All Services

```bash
# From project root
docker-compose up -d
```

This will start:
- ✅ PostgreSQL database (port 5432)
- ✅ MongoDB (port 27017)
- ✅ Redis (port 6379)
- ✅ Backend API (port 8000)

### 2. Verify Services

```bash
# Check all containers are running
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Should return:
# {
#   "status": "healthy",
#   "services": {
#     "sql_database": {"status": "healthy", "type": "postgresql"},
#     "mongodb": {"status": "healthy"},
#     "redis": {"status": "healthy"}
#   }
# }
```

### 3. Access API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### 4. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### 5. Stop Services

```bash
# Stop but keep data
docker-compose stop

# Stop and remove containers (keeps volumes/data)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

## Using SQL Server Instead of PostgreSQL

```bash
# Start with SQL Server
docker-compose --profile sqlserver up -d

# The backend will need to be configured to use SQL Server
# Edit backend/.env:
DB_TYPE=sqlserver
DB_HOST=sqlserver
DB_PORT=1433
DB_USER=sa
DB_PASSWORD=YourStrong@Passw0rd

# Restart backend
docker-compose restart backend
```

## Local Development Setup

### 1. Install Databases

**PostgreSQL:**
```bash
# macOS
brew install postgresql@16
brew services start postgresql@16

# Ubuntu/Debian
sudo apt install postgresql-16
sudo systemctl start postgresql

# Windows
# Download from: https://www.postgresql.org/download/windows/
```

**MongoDB:**
```bash
# macOS
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# Ubuntu/Debian
# Follow: https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/

# Windows
# Download from: https://www.mongodb.com/try/download/community
```

**Redis:**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# Windows
# Download from: https://github.com/microsoftarchive/redis/releases
```

### 2. Create Database

**PostgreSQL:**
```bash
psql -U postgres
CREATE DATABASE appdb;
\q
```

**SQL Server:**
```sql
CREATE DATABASE appdb;
GO
```

### 3. Setup Backend

```bash
cd backend

# Copy environment file
cp .env.example .env

# Edit .env and configure your database credentials
# At minimum, set:
# - DB_TYPE (postgresql or sqlserver)
# - DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
# - MONGO_URI
# - REDIS_URL
# - SECRET_KEY, JWT_SECRET_KEY (generate secure keys!)

# Install dependencies
pip install poetry
poetry install

# Run migrations
poetry run alembic upgrade head

# Start backend
poetry run python -m app.main
```

Backend will be available at: http://localhost:8000

### 4. Setup Frontend

```bash
cd full-version

# Install dependencies
npm install

# Start development server
npm run start
```

Frontend will be available at: http://localhost:3000

## Generating Secure Keys

For production, generate secure keys:

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32
```

Update `backend/.env`:
```env
SECRET_KEY=<your-generated-key>
JWT_SECRET_KEY=<your-generated-key>
```

## Running Database Migrations

```bash
cd backend

# Create a new migration (after modifying models)
poetry run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history

# View current version
poetry run alembic current
```

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# Ready check (Kubernetes)
curl http://localhost:8000/ready

# Live check (Kubernetes)
curl http://localhost:8000/live
```

### Using HTTPie

```bash
# Install httpie
pip install httpie

# Health check
http GET http://localhost:8000/health
```

### Using Swagger UI

1. Open http://localhost:8000/api/v1/docs
2. Expand any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

## Troubleshooting

### Backend won't start

1. **Check database connections:**
   ```bash
   # PostgreSQL
   psql -U postgres -h localhost -c "SELECT 1"

   # MongoDB
   mongosh --eval "db.adminCommand('ping')"

   # Redis
   redis-cli ping
   ```

2. **Check environment variables:**
   ```bash
   cd backend
   cat .env | grep -E "DB_|MONGO_|REDIS_"
   ```

3. **Check logs:**
   ```bash
   # Docker
   docker-compose logs backend

   # Local
   cd backend
   tail -f logs/app.log
   ```

### Database migration errors

```bash
# Check current version
poetry run alembic current

# If migrations are out of sync, you can:

# 1. Stamp the current version (if you know it)
poetry run alembic stamp head

# 2. Or reset and recreate (CAUTION: loses data)
# Drop all tables in database, then:
poetry run alembic upgrade head
```

### Port already in use

```bash
# Find process using port
# macOS/Linux
lsof -i :8000
lsof -i :5432

# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Kill the process or change port in .env
```

### Docker issues

```bash
# Clean up Docker resources
docker-compose down -v
docker system prune -a

# Rebuild images
docker-compose build --no-cache

# Start fresh
docker-compose up -d --force-recreate
```

### Connection refused errors

1. **Ensure services are running:**
   ```bash
   docker-compose ps
   ```

2. **Check network connectivity:**
   ```bash
   # From host to container
   docker-compose exec backend ping postgres

   # From container to host
   # Use host.docker.internal instead of localhost
   ```

3. **Verify Docker network:**
   ```bash
   docker network ls
   docker network inspect vite_app-network
   ```

## Next Steps

1. ✅ Verify all services are running
2. ⏳ Wait for Phase 2 (Authentication) to be implemented
3. ⏳ Test authentication endpoints when available
4. ⏳ Connect frontend to backend

## Additional Resources

- **Backend Documentation**: See `backend/README.md`
- **Project Status**: See `PROJECT_STATUS.md`
- **Repository Guide**: See `CLAUDE.md`
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **React/Vite Docs**: https://vitejs.dev/

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `PROJECT_STATUS.md` for known issues
3. Check logs: `docker-compose logs -f` or `backend/logs/app.log`
