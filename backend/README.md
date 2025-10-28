# Backend API

FastAPI backend for the full-stack application with support for PostgreSQL/SQL Server, MongoDB, and Redis.

## Features

- **Flexible Database Support**: Switch between PostgreSQL and SQL Server via configuration
- **MongoDB Integration**: For user preferences, themes, and application settings
- **Redis Integration**: For sessions, caching, and rate limiting
- **Authentication**: Local auth with MFA, OAuth (Google, Microsoft, Facebook), Firebase Auth support
- **Database Migrations**: Alembic for SQL schema migrations
- **Structured Logging**: JSON logging with request ID tracing
- **Health Checks**: Kubernetes-ready health, ready, and liveness endpoints
- **API Documentation**: Auto-generated Swagger/ReDoc documentation

## Prerequisites

- Python 3.11+
- Poetry (recommended) or pip
- PostgreSQL or SQL Server
- MongoDB
- Redis

## Installation

### Using Poetry (Recommended)

```bash
cd backend
poetry install
```

### Using pip

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt  # Generate from poetry: poetry export -f requirements.txt --output requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and configure:
   - Database settings (`DB_TYPE`, `DB_HOST`, etc.)
   - MongoDB connection (`MONGO_URI`)
   - Redis connection (`REDIS_URL`)
   - Secret keys (generate secure keys for production)
   - OAuth provider credentials (if using social auth)
   - MFA provider credentials (Twilio, Duo)

## Database Setup

### Initialize Database

Create the database in your SQL server:

**PostgreSQL:**
```bash
createdb appdb
```

**SQL Server:**
```sql
CREATE DATABASE appdb;
```

### Run Migrations

```bash
# Create initial migration
poetry run alembic revision --autogenerate -m "Initial migration"

# Apply migrations
poetry run alembic upgrade head
```

## Running the Application

### Development

```bash
poetry run python -m app.main
# or
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### Production

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_auth.py
```

## Database Migrations

```bash
# Create a new migration
poetry run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history

# View current revision
poetry run alembic current
```

## Project Structure

```
backend/
├── app/
│   ├── core/           # Core configuration, security, logging
│   ├── db/             # Database adapters, models, connections
│   ├── api/            # API routes
│   ├── services/       # Business logic
│   ├── schemas/        # Pydantic models
│   ├── middleware/     # Custom middleware
│   └── main.py         # FastAPI application
├── alembic/            # Database migrations
├── tests/              # Test files
├── pyproject.toml      # Dependencies
└── .env                # Environment variables
```

## API Endpoints

### Core
- `GET /` - Root endpoint
- `GET /health` - Health check (all services)
- `GET /ready` - Readiness check (Kubernetes)
- `GET /live` - Liveness check (Kubernetes)

### Authentication (Coming Soon)
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/oauth/{provider}/authorize` - OAuth authorization
- `GET /api/v1/auth/oauth/{provider}/callback` - OAuth callback

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DB_TYPE`: `postgresql` or `sqlserver`
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: SQL database connection
- `MONGO_URI`: MongoDB connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`, `JWT_SECRET_KEY`: Cryptographic keys (generate secure keys!)
- `USE_FIREBASE`: `true` to use Firebase Auth, `false` for custom OAuth
- `ENABLE_SOCIAL_AUTH`: Enable/disable social login
- `ENABLE_MFA`: Enable/disable multi-factor authentication

## Switching Between PostgreSQL and SQL Server

Simply change the `DB_TYPE` in `.env`:

```env
# For PostgreSQL
DB_TYPE=postgresql
DB_PORT=5432

# For SQL Server
DB_TYPE=sqlserver
DB_PORT=1433
```

The application will automatically use the correct database adapter.

## Development Tips

1. **Hot Reload**: Use `--reload` flag for auto-restart on code changes
2. **Logging**: Set `LOG_LEVEL=DEBUG` for detailed logs
3. **Debug Mode**: Set `DEBUG=true` for enhanced error messages
4. **API Docs**: Access Swagger UI at `/api/v1/docs` for interactive API testing

## Troubleshooting

### Database Connection Issues

- **PostgreSQL**: Ensure `asyncpg` is installed and server is running
- **SQL Server**: Ensure ODBC driver is installed:
  - Linux: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server
  - Windows: Usually pre-installed
  - macOS: https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos

### MongoDB Connection Issues

- Ensure MongoDB is running: `mongod`
- Check connection string format in `MONGO_URI`

### Redis Connection Issues

- Ensure Redis is running: `redis-server`
- Check `REDIS_URL` format

## License

Proprietary - All rights reserved
