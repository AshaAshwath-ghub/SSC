#!/bin/bash

echo "======================================"
echo "Phase 1 Implementation Testing"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3

    echo -n "  Testing $name... "
    response=$(curl -s "$url" 2>/dev/null)

    if [ $? -eq 0 ] && echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        if [ $? -ne 0 ]; then
            echo "    Error: Could not connect to $url"
        else
            echo "    Expected substring: '$expected'"
            echo "    Got: ${response:0:100}..."
        fi
        ((FAILED++))
        return 1
    fi
}

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}1. Docker Services Status${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo -n "  Checking docker-compose... "
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓ FOUND${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ NOT FOUND${NC}"
    echo "    Please install docker-compose"
    ((FAILED++))
    exit 1
fi

echo -n "  Checking containers... "
running=$(docker-compose ps -q | wc -l)
if [ "$running" -gt 0 ]; then
    echo -e "${GREEN}✓ $running containers running${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ No containers running${NC}"
    echo "    Run: docker-compose up -d"
    ((FAILED++))
    exit 1
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}2. Backend API Endpoints${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

test_endpoint "Root endpoint" "http://localhost:8000/" "Application"
test_endpoint "Health check" "http://localhost:8000/health" "healthy"
test_endpoint "Ready probe" "http://localhost:8000/ready" "ready"
test_endpoint "Live probe" "http://localhost:8000/live" "alive"

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}3. HTTP Headers${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo -n "  Request ID header... "
header_test=$(curl -I -s http://localhost:8000/ 2>/dev/null | grep -i "x-request-id")
if [ ! -z "$header_test" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    echo "    $header_test"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "    X-Request-ID header not found"
    ((FAILED++))
fi

echo -n "  CORS headers... "
cors_test=$(curl -I -s -H "Origin: http://localhost:3000" http://localhost:8000/ 2>/dev/null | grep -i "access-control-allow")
if [ ! -z "$cors_test" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "    CORS headers not found"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}4. Database Services${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

# PostgreSQL
echo -n "  PostgreSQL connection... "
if docker-compose exec -T postgres psql -U postgres -d appdb -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "    Could not connect to PostgreSQL"
    ((FAILED++))
fi

# MongoDB
echo -n "  MongoDB connection... "
if docker-compose exec -T mongodb mongosh appdb --quiet --eval "db.runCommand({ping:1}).ok" 2>/dev/null | grep -q "1"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "    Could not connect to MongoDB"
    ((FAILED++))
fi

# Redis
echo -n "  Redis connection... "
redis_test=$(docker-compose exec -T redis redis-cli PING 2>/dev/null)
if echo "$redis_test" | grep -q "PONG"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "    Could not connect to Redis"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}5. Container Health${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

for container in app-postgres app-mongodb app-redis app-backend; do
    echo -n "  $container... "
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null)
        if [ "$status" = "healthy" ] || [ -z "$status" ]; then
            echo -e "${GREEN}✓ RUNNING${NC}"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠ UNHEALTHY${NC}"
            echo "    Status: $status"
            ((FAILED++))
        fi
    else
        echo -e "${RED}✗ NOT RUNNING${NC}"
        ((FAILED++))
    fi
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}6. Backend Logs Check${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo -n "  Checking for errors... "
errors=$(docker-compose logs backend 2>/dev/null | grep -i "error" | grep -v "ERROR_CODES" | wc -l)
if [ "$errors" -eq 0 ]; then
    echo -e "${GREEN}✓ No errors${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ Found $errors error(s)${NC}"
    echo "    Check logs with: docker-compose logs backend"
    # Don't fail the test for this, just warn
fi

echo -n "  Successful startup... "
if docker-compose logs backend 2>/dev/null | grep -q "All database connections initialized successfully"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "    Database initialization incomplete"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}7. API Documentation${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo -n "  Swagger UI... "
swagger=$(curl -s http://localhost:8000/api/v1/docs 2>/dev/null)
if echo "$swagger" | grep -q "swagger"; then
    echo -e "${GREEN}✓ PASS${NC}"
    echo "    Access at: http://localhost:8000/api/v1/docs"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo -n "  ReDoc... "
redoc=$(curl -s http://localhost:8000/api/v1/redoc 2>/dev/null)
if echo "$redoc" | grep -q "redoc"; then
    echo -e "${GREEN}✓ PASS${NC}"
    echo "    Access at: http://localhost:8000/api/v1/redoc"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}8. Performance Test${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"

echo -n "  Response time... "
start_time=$(date +%s%N)
curl -s http://localhost:8000/ > /dev/null 2>&1
end_time=$(date +%s%N)
duration=$(( (end_time - start_time) / 1000000 ))

if [ $duration -lt 1000 ]; then
    echo -e "${GREEN}✓ ${duration}ms (< 1000ms)${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ ${duration}ms (> 1000ms)${NC}"
    echo "    Response time is slow"
fi

echo ""
echo "======================================"
echo "Test Summary"
echo "======================================"
total=$((PASSED + FAILED))
percentage=$((PASSED * 100 / total))

echo -e "Total Tests: ${BLUE}$total${NC}"
echo -e "Passed:      ${GREEN}$PASSED${NC}"
echo -e "Failed:      ${RED}$FAILED${NC}"
echo -e "Success Rate: ${BLUE}$percentage%${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✓ ALL TESTS PASSED!                ║${NC}"
    echo -e "${GREEN}║   Phase 1 is working correctly!      ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════╝${NC}"
    echo ""
    echo "You can now proceed to Phase 2 (Authentication)"
    exit 0
else
    echo -e "${RED}╔═══════════════════════════════════════╗${NC}"
    echo -e "${RED}║   ✗ SOME TESTS FAILED                ║${NC}"
    echo -e "${RED}║   Please review the errors above     ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════╝${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check logs: docker-compose logs"
    echo "  2. Restart services: docker-compose restart"
    echo "  3. Check TESTING_PHASE_1.md for detailed guide"
    exit 1
fi
