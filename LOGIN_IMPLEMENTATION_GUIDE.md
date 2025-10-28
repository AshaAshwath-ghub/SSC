# Login Implementation Complete - Testing Guide

This guide walks you through testing the complete end-to-end login functionality.

## What Was Implemented

### Backend Changes
- ✅ Created `/api/v1/auth/login` endpoint in FastAPI
- ✅ Implemented password verification with Argon2 hashing
- ✅ JWT token generation (access + refresh tokens)
- ✅ Session tracking with IP and user agent
- ✅ Account lockout after failed login attempts
- ✅ Comprehensive error handling and logging

### Frontend Changes
- ✅ Updated API base URL to point to local backend (`http://localhost:8000/`)
- ✅ Modified JWT login context to call new backend API
- ✅ Updated login form with correct test credentials
- ✅ Proper error handling for invalid credentials

### Database Changes
- ✅ User model with authentication fields
- ✅ Session model for tracking user sessions
- ✅ Database migrations setup
- ✅ Seed script for test user

---

## Step-by-Step Testing Instructions

### Step 1: Ensure Docker Containers Are Running

```powershell
# Check if containers are running
docker-compose ps

# Expected output: All containers should show "Up (healthy)"
# - postgres
# - mongodb
# - redis
# - backend
```

If containers are not running:
```powershell
docker-compose up -d
Start-Sleep -Seconds 30  # Wait for containers to be healthy
docker-compose ps
```

---

### Step 2: Setup Database and Seed Test User

#### Option A: Automated Setup (Recommended)
Run the automated setup script:
```powershell
.\setup_database.ps1
```

This script will:
1. Check Docker status
2. Wait for PostgreSQL to be ready
3. Run database migrations
4. Create test user
5. Test login API

#### Option B: Manual Setup
If you prefer to run commands manually:

```powershell
cd backend

# Set PYTHONPATH
$env:PYTHONPATH = "."

# Run migrations
alembic revision --autogenerate -m "Create initial tables"
alembic upgrade head

# Seed test user
python scripts/seed_test_user.py

cd ..
```

---

### Step 3: Verify Backend API

Test the login endpoint directly:

```powershell
# Test successful login
$body = @{
    email = "info@codedthemes.com"
    password = "12345"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

# View response
$response | ConvertTo-Json -Depth 10
```

**Expected Response:**
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

Test invalid credentials:
```powershell
$body = @{
    email = "info@codedthemes.com"
    password = "wrongpassword"
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body
} catch {
    $_.Exception.Response | ConvertTo-Json
}
```

**Expected Error:**
```json
{
  "detail": "Invalid credentials"
}
```

---

### Step 4: Start Frontend Development Server

```powershell
cd full-version
npm install  # If not already installed
npm run dev
```

The frontend should start on http://localhost:3000 or http://localhost:5173 (Vite default).

---

### Step 5: Test Login via Web Interface

1. Open your browser and navigate to:
   - http://localhost:3000/login (or)
   - http://localhost:5173/login

2. You should see the Mantis login page with pre-filled credentials:
   - **Email**: info@codedthemes.com
   - **Password**: 12345

3. Click the **Login** button

4. **Expected Behavior on Success:**
   - Login form submits
   - JWT token is stored in localStorage
   - User is redirected to the dashboard
   - No errors displayed

5. **Test Invalid Credentials:**
   - Change password to "wrongpassword"
   - Click Login
   - **Expected**: Error message "Invalid credentials" appears
   - User remains on login page

---

### Step 6: Verify Token Storage

After successful login, open browser DevTools:

1. Press **F12** to open DevTools
2. Go to **Application** tab → **Local Storage** → http://localhost:3000
3. Look for key: `serviceToken`
4. Value should be a JWT token starting with `eyJ...`

Decode the token at https://jwt.io to verify it contains:
```json
{
  "sub": "1",
  "email": "info@codedthemes.com",
  "username": "testuser",
  "exp": ...,
  "iat": ...,
  "type": "access"
}
```

---

### Step 7: Verify Session in Database

Check that the session was created in PostgreSQL:

```powershell
docker-compose exec postgres psql -U postgres -d appdb -c "SELECT id, user_id, ip_address, created_at FROM sessions ORDER BY created_at DESC LIMIT 1;"
```

You should see a session record with:
- user_id: 1
- ip_address: (your IP)
- recent created_at timestamp

---

### Step 8: Test Navigation After Login

After logging in successfully:

1. **Verify Dashboard Access:**
   - Navigate to http://localhost:3000/dashboard/analytics
   - You should see the dashboard (not redirected to login)

2. **Test Logout:**
   - Click on user menu (top right)
   - Click "Logout"
   - You should be redirected to login page
   - localStorage should no longer have `serviceToken`

3. **Test Protected Route Without Login:**
   - After logout, try to access http://localhost:3000/dashboard/analytics
   - You should be redirected back to login page

---

## API Documentation

You can also test the API using Swagger UI:

1. Open http://localhost:8000/api/v1/docs
2. Find the **POST /api/v1/auth/login** endpoint
3. Click "Try it out"
4. Enter credentials:
   ```json
   {
     "email": "info@codedthemes.com",
     "password": "12345"
   }
   ```
5. Click "Execute"
6. View the response

---

## Troubleshooting

### Error: "Cannot connect to backend"
**Solution:**
```powershell
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend

# Check if backend is accessible
curl http://localhost:8000/health
```

### Error: "No module named 'app'"
**Solution:**
```powershell
cd backend
$env:PYTHONPATH = "."
python scripts/seed_test_user.py
```

### Error: "User already exists"
This is expected if you've run the seed script before. The script checks for existing users.

### Error: Frontend shows "Wrong Services" or network error
**Solution:**
1. Check .env file has correct API URL:
   ```
   VITE_APP_API_URL=http://localhost:8000/
   ```
2. Restart frontend dev server:
   ```powershell
   # Press Ctrl+C to stop
   npm run dev
   ```

### Error: "Cross-Origin Request Blocked" (CORS error)
**Solution:**
The backend `.env` file should have:
```
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```
Restart backend:
```powershell
docker-compose restart backend
```

### Error: Password validation fails
The frontend has validation that password must be less than 10 characters. Our test password "12345" is within this limit.

---

## Testing Checklist

Use this checklist to verify everything works:

- [ ] Docker containers all running and healthy
- [ ] Database migrations completed successfully
- [ ] Test user created in database
- [ ] Backend login API returns JWT token for valid credentials
- [ ] Backend login API returns error for invalid credentials
- [ ] Frontend dev server running
- [ ] Login page loads correctly
- [ ] Login with valid credentials redirects to dashboard
- [ ] Login with invalid credentials shows error message
- [ ] JWT token stored in localStorage after login
- [ ] Session created in database after login
- [ ] Dashboard accessible after login
- [ ] Logout clears token and redirects to login
- [ ] Protected routes redirect to login when not authenticated

---

## Next Steps

After verifying login works:

1. **Phase 2 - Authentication Features:**
   - User registration
   - Email verification
   - Password reset flow
   - MFA (SMS, Email, Duo, TOTP)
   - Social login (Google, Microsoft, Facebook)
   - reCAPTCHA integration

2. **Additional Backend Endpoints:**
   - GET /api/v1/auth/me (get current user)
   - POST /api/v1/auth/logout (invalidate session)
   - POST /api/v1/auth/refresh (refresh access token)
   - POST /api/v1/auth/register (user registration)

3. **Frontend Enhancements:**
   - Remember me functionality
   - Show/hide password toggle (already implemented)
   - Social login buttons
   - Registration page integration

---

## Files Modified

### Backend
- **Created:**
  - `backend/app/api/auth.py` - Login endpoint
  - `backend/app/schemas/auth.py` - Request/response models
  - `backend/scripts/seed_test_user.py` - Database seed script
  - `DATABASE_SETUP.md` - Setup documentation
  - `setup_database.ps1` - Automated setup script

- **Modified:**
  - `backend/app/main.py` - Added auth router

### Frontend
- **Modified:**
  - `full-version/.env` - Updated API URL
  - `full-version/src/contexts/JWTContext.jsx` - Updated to call new API
  - `full-version/src/sections/auth/jwt/AuthLogin.jsx` - Updated test password

---

## API Response Examples

### Successful Login
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJpbmZvQGNvZGVkdGhlbWVzLmNvbSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJleHAiOjE3MzU4NjQwMDAsImlhdCI6MTczNTg2MDQwMCwidHlwZSI6ImFjY2VzcyJ9.xxx",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJpbmZvQGNvZGVkdGhlbWVzLmNvbSIsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJleHAiOjE3MzY0NjUyMDAsImlhdCI6MTczNTg2MDQwMCwidHlwZSI6InJlZnJlc2gifQ.yyy",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "info@codedthemes.com",
    "first_name": "Test",
    "last_name": "User",
    "is_active": true,
    "is_verified": true,
    "created_at": "2025-01-02T12:00:00.000000"
  },
  "requires_mfa": false
}
```

### Failed Login (Invalid Credentials)
```json
{
  "detail": "Invalid credentials"
}
```

### Account Locked (After 5 failed attempts)
```json
{
  "detail": "Account is locked until 2025-01-02T12:30:00"
}
```

---

## Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Review backend logs: `docker-compose logs backend`
3. Review frontend console: Browser DevTools → Console
4. Check database: `docker-compose exec postgres psql -U postgres -d appdb`

---

**Login implementation is complete and ready for testing!** 🚀
