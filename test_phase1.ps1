# PowerShell Test Script for Phase 1
# Run with: .\test_phase1.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Phase 1 Implementation Testing" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$PASSED = 0
$FAILED = 0

# Test function
function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Expected
    )

    Write-Host "  Testing $Name... " -NoNewline

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
        $content = $response.Content

        if ($content -match $Expected) {
            Write-Host "✓ PASS" -ForegroundColor Green
            $script:PASSED++
            return $true
        } else {
            Write-Host "✗ FAIL" -ForegroundColor Red
            Write-Host "    Expected: $Expected" -ForegroundColor Yellow
            Write-Host "    Got: $($content.Substring(0, [Math]::Min(100, $content.Length)))..." -ForegroundColor Yellow
            $script:FAILED++
            return $false
        }
    } catch {
        Write-Host "✗ FAIL" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor Yellow
        $script:FAILED++
        return $false
    }
}

Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
Write-Host "1. Docker Services Status" -ForegroundColor Blue
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue

Write-Host "  Checking docker-compose... " -NoNewline
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    Write-Host "✓ FOUND" -ForegroundColor Green
    $PASSED++
} else {
    Write-Host "✗ NOT FOUND" -ForegroundColor Red
    Write-Host "    Please install docker-compose" -ForegroundColor Yellow
    $FAILED++
    exit 1
}

Write-Host "  Checking containers... " -NoNewline
$containers = docker-compose ps -q
if ($containers) {
    $count = ($containers | Measure-Object).Count
    Write-Host "✓ $count containers running" -ForegroundColor Green
    $PASSED++
} else {
    Write-Host "✗ No containers running" -ForegroundColor Red
    Write-Host "    Run: docker-compose up -d" -ForegroundColor Yellow
    $FAILED++
    exit 1
}

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
Write-Host "2. Backend API Endpoints" -ForegroundColor Blue
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue

Test-Endpoint -Name "Root endpoint" -Url "http://localhost:8000/" -Expected "Application"
Test-Endpoint -Name "Health check" -Url "http://localhost:8000/health" -Expected "healthy"
Test-Endpoint -Name "Ready probe" -Url "http://localhost:8000/ready" -Expected "ready"
Test-Endpoint -Name "Live probe" -Url "http://localhost:8000/live" -Expected "alive"

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
Write-Host "3. HTTP Headers" -ForegroundColor Blue
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue

Write-Host "  Request ID header... " -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 5
    if ($response.Headers["X-Request-ID"]) {
        Write-Host "✓ PASS" -ForegroundColor Green
        Write-Host "    $($response.Headers["X-Request-ID"])" -ForegroundColor Gray
        $PASSED++
    } else {
        Write-Host "✗ FAIL" -ForegroundColor Red
        Write-Host "    X-Request-ID header not found" -ForegroundColor Yellow
        $FAILED++
    }
} catch {
    Write-Host "✗ FAIL" -ForegroundColor Red
    $FAILED++
}

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
Write-Host "4. Database Services" -ForegroundColor Blue
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue

# PostgreSQL
Write-Host "  PostgreSQL connection... " -NoNewline
$pgResult = docker-compose exec -T postgres psql -U postgres -d appdb -c "SELECT 1" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PASS" -ForegroundColor Green
    $PASSED++
} else {
    Write-Host "✗ FAIL" -ForegroundColor Red
    Write-Host "    Could not connect to PostgreSQL" -ForegroundColor Yellow
    $FAILED++
}

# MongoDB
Write-Host "  MongoDB connection... " -NoNewline
$mongoResult = docker-compose exec -T mongodb mongosh appdb --quiet --eval "db.runCommand({ping:1}).ok" 2>&1
if ($mongoResult -match "1") {
    Write-Host "✓ PASS" -ForegroundColor Green
    $PASSED++
} else {
    Write-Host "✗ FAIL" -ForegroundColor Red
    Write-Host "    Could not connect to MongoDB" -ForegroundColor Yellow
    $FAILED++
}

# Redis
Write-Host "  Redis connection... " -NoNewline
$redisResult = docker-compose exec -T redis redis-cli PING 2>&1
if ($redisResult -match "PONG") {
    Write-Host "✓ PASS" -ForegroundColor Green
    $PASSED++
} else {
    Write-Host "✗ FAIL" -ForegroundColor Red
    Write-Host "    Could not connect to Redis" -ForegroundColor Yellow
    $FAILED++
}

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
Write-Host "5. Container Health" -ForegroundColor Blue
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue

$containers = @("app-postgres", "app-mongodb", "app-redis", "app-backend")
foreach ($container in $containers) {
    Write-Host "  $container... " -NoNewline
    $running = docker ps --format "{{.Names}}" | Select-String -Pattern "^$container$"
    if ($running) {
        Write-Host "✓ RUNNING" -ForegroundColor Green
        $PASSED++
    } else {
        Write-Host "✗ NOT RUNNING" -ForegroundColor Red
        $FAILED++
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue
Write-Host "6. API Documentation" -ForegroundColor Blue
Write-Host "═══════════════════════════════════════" -ForegroundColor Blue

Write-Host "  Swagger UI... " -NoNewline
try {
    $swagger = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/docs" -UseBasicParsing -TimeoutSec 5
    if ($swagger.Content -match "swagger") {
        Write-Host "✓ PASS" -ForegroundColor Green
        Write-Host "    Access at: http://localhost:8000/api/v1/docs" -ForegroundColor Gray
        $PASSED++
    } else {
        Write-Host "✗ FAIL" -ForegroundColor Red
        $FAILED++
    }
} catch {
    Write-Host "✗ FAIL" -ForegroundColor Red
    $FAILED++
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$total = $PASSED + $FAILED
$percentage = [math]::Round(($PASSED / $total) * 100, 2)

Write-Host "Total Tests:  $total" -ForegroundColor Blue
Write-Host "Passed:       $PASSED" -ForegroundColor Green
Write-Host "Failed:       $FAILED" -ForegroundColor Red
Write-Host "Success Rate: $percentage%" -ForegroundColor Blue
Write-Host ""

if ($FAILED -eq 0) {
    Write-Host "╔═══════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   ✓ ALL TESTS PASSED!                ║" -ForegroundColor Green
    Write-Host "║   Phase 1 is working correctly!      ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now proceed to Phase 2 (Authentication)" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "╔═══════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║   ✗ SOME TESTS FAILED                ║" -ForegroundColor Red
    Write-Host "║   Please review the errors above     ║" -ForegroundColor Red
    Write-Host "╚═══════════════════════════════════════╝" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check logs: docker-compose logs" -ForegroundColor Yellow
    Write-Host "  2. Restart services: docker-compose restart" -ForegroundColor Yellow
    Write-Host "  3. Check TESTING_PHASE_1.md for detailed guide" -ForegroundColor Yellow
    exit 1
}
