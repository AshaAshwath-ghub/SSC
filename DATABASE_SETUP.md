# Database Setup Guide

This guide explains how to set up the database, run migrations, and seed the test user.

## Prerequisites

Make sure Docker containers are running:
```powershell
docker-compose up -d
docker-compose ps  # All services should be "Up (healthy)"
```

## Step 1: Run Database Migrations

Create the database tables using Alembic migrations.

### Option A: Auto-generate migration (Recommended)
```powershell
cd backend
alembic revision --autogenerate -m "Create initial tables"
alembic upgrade head
```

### Option B: Use pre-created migration
If migrations already exist in `backend/alembic/versions/`:
```powershell
cd backend
alembic upgrade head
```

### Verify Migration
```powershell
# Connect to PostgreSQL and check tables
docker-compose exec postgres psql -U postgres -d appdb -c "\dt"
```

You should see tables like:
- `users`
- `sessions`
- `auth_providers`
- `mfa_enrollments`
- `roles`
- `user_roles`
- `audit_logs`
- `dashboards`
- `dashboard_access`

## Step 2: Seed Test User

Create a test user with email `info@codedthemes.com` and password `12345`.

```powershell
cd backend
python scripts/seed_test_user.py
```

Expected output:
```
============================================================
✓ Test user created successfully!
============================================================
  Email:    info@codedthemes.com
  Password: 12345
  Username: testuser
  User ID:  1
============================================================
```

### Verify User Creation
```powershell
# Check if user exists in database
docker-compose exec postgres psql -U postgres -d appdb -c "SELECT id, email, username, is_active FROM users;"
```

## Step 3: Test Backend API

### Test Health Endpoint
```powershell
curl http://localhost:8000/health
```

### Test Login Endpoint
```powershell
# PowerShell
$body = @{
    email = "info@codedthemes.com"
    password = "12345"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "info@codedthemes.com",
    "first_name": "Test",
    "last_name": "User",
    "is_active": true,
    "is_verified": true,
    "created_at": "2025-..."
  },
  "requires_mfa": false
}
```

### Test Invalid Credentials
```powershell
$body = @{
    email = "info@codedthemes.com"
    password = "wrongpassword"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

Expected error:
```json
{
  "detail": "Invalid credentials"
}
```

## Quick Setup Script

Run everything at once:

```powershell
cd backend

# Run migrations
alembic revision --autogenerate -m "Create initial tables"
alembic upgrade head

# Seed test user
python scripts/seed_test_user.py

# Test login
cd ..
$body = @{
    email = "info@codedthemes.com"
    password = "12345"
} | ConvertTo-Json

Write-Host "`nTesting login..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body | ConvertTo-Json -Depth 10

Write-Host "`n✓ Database setup complete!" -ForegroundColor Green
```

## Troubleshooting

### Error: "alembic: command not found"
Install alembic in your Python environment:
```powershell
cd backend
pip install alembic
```

### Error: "Cannot connect to database"
Make sure PostgreSQL container is running:
```powershell
docker-compose ps postgres
docker-compose logs postgres
```

### Error: "Test user already exists"
This is expected if you've run the seed script before. The script checks for existing users and skips creation.

### Error: "No module named 'app'"
Make sure you're running commands from the `backend` directory and the PYTHONPATH is set correctly:
```powershell
cd backend
$env:PYTHONPATH = "."
python scripts/seed_test_user.py
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

You can test the login endpoint directly from Swagger UI.

## Next Steps

After database setup is complete:
1. Update the frontend login page to call the backend API
2. Test the end-to-end login flow
3. Implement additional authentication features (Phase 2)
