#!/usr/bin/env pwsh
# Database Setup Script for Windows PowerShell
# This script sets up the database, runs migrations, and seeds the test user

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Database Setup Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if Docker is running
Write-Host "[1/5] Checking Docker..." -ForegroundColor Yellow
try {
    $dockerStatus = docker-compose ps --format json | ConvertFrom-Json
    if ($dockerStatus) {
        Write-Host "✓ Docker containers are running" -ForegroundColor Green
    } else {
        Write-Host "✗ No Docker containers found. Please run: docker-compose up -d" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Wait for PostgreSQL to be ready
Write-Host "`n[2/5] Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
$maxRetries = 10
$retryCount = 0
$isReady = $false

while (-not $isReady -and $retryCount -lt $maxRetries) {
    try {
        $result = docker-compose exec -T postgres pg_isready -U postgres 2>&1
        if ($result -match "accepting connections") {
            $isReady = $true
            Write-Host "✓ PostgreSQL is ready" -ForegroundColor Green
        } else {
            $retryCount++
            Write-Host "  Waiting... (attempt $retryCount/$maxRetries)" -ForegroundColor Gray
            Start-Sleep -Seconds 2
        }
    } catch {
        $retryCount++
        Write-Host "  Waiting... (attempt $retryCount/$maxRetries)" -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $isReady) {
    Write-Host "✗ PostgreSQL is not ready after $maxRetries attempts" -ForegroundColor Red
    exit 1
}

# Run migrations
Write-Host "`n[3/5] Running database migrations..." -ForegroundColor Yellow
Push-Location backend
try {
    # Set PYTHONPATH
    $env:PYTHONPATH = "."

    # Check if alembic is installed
    try {
        alembic --version | Out-Null
    } catch {
        Write-Host "✗ Alembic not found. Installing..." -ForegroundColor Yellow
        pip install alembic
    }

    # Auto-generate migration
    Write-Host "  Generating migration..." -ForegroundColor Gray
    alembic revision --autogenerate -m "Create initial tables" 2>&1 | Out-Null

    # Run migration
    Write-Host "  Applying migration..." -ForegroundColor Gray
    $migrationOutput = alembic upgrade head 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Database migrations completed" -ForegroundColor Green
    } else {
        Write-Host "✗ Migration failed:" -ForegroundColor Red
        Write-Host $migrationOutput -ForegroundColor Red
        Pop-Location
        exit 1
    }
} catch {
    Write-Host "✗ Error running migrations: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Seed test user
Write-Host "`n[4/5] Seeding test user..." -ForegroundColor Yellow
try {
    $seedOutput = python scripts/seed_test_user.py 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host $seedOutput
    } else {
        Write-Host "✗ Seed failed:" -ForegroundColor Red
        Write-Host $seedOutput -ForegroundColor Red
        Pop-Location
        exit 1
    }
} catch {
    Write-Host "✗ Error seeding database: $_" -ForegroundColor Red
    Pop-Location
    exit 1
}

Pop-Location

# Test login API
Write-Host "`n[5/5] Testing login API..." -ForegroundColor Yellow
try {
    $body = @{
        email = "info@codedthemes.com"
        password = "12345"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -ErrorAction Stop

    if ($response.access_token) {
        Write-Host "✓ Login API test successful" -ForegroundColor Green
        Write-Host "`n  User: $($response.user.email)" -ForegroundColor Gray
        Write-Host "  Username: $($response.user.username)" -ForegroundColor Gray
        Write-Host "  Token: $($response.access_token.Substring(0, 50))..." -ForegroundColor Gray
    } else {
        Write-Host "✗ Login API test failed: No access token received" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Login API test failed: $_" -ForegroundColor Red
    exit 1
}

# Success summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Database Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nTest Credentials:" -ForegroundColor Green
Write-Host "  Email:    info@codedthemes.com" -ForegroundColor White
Write-Host "  Password: 12345" -ForegroundColor White
Write-Host "`nAPI Endpoints:" -ForegroundColor Green
Write-Host "  Login:    http://localhost:8000/api/v1/auth/login" -ForegroundColor White
Write-Host "  Docs:     http://localhost:8000/api/v1/docs" -ForegroundColor White
Write-Host "  Health:   http://localhost:8000/health" -ForegroundColor White
Write-Host "`nNext Steps:" -ForegroundColor Green
Write-Host "  1. Update frontend login page to call backend API" -ForegroundColor White
Write-Host "  2. Test end-to-end login flow" -ForegroundColor White
Write-Host "  3. Implement additional auth features (Phase 2)" -ForegroundColor White
Write-Host "`n========================================`n" -ForegroundColor Cyan
