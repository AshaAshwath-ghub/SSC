# Login API Error Responses - Industry Standard Format

This document describes the structured error response format implemented for the login API endpoint.

## Error Response Format

All error responses follow this industry-standard structure:

```json
{
  "detail": "Error summary",
  "error_code": "MACHINE_READABLE_CODE",
  "message": "Human-readable error message explaining what went wrong",
  "request_id": "unique-request-id-for-tracing"
}
```

### Fields:
- **detail**: Short error summary (for logging/debugging)
- **error_code**: Machine-readable error code (for programmatic handling)
- **message**: User-friendly error message (display to end users)
- **request_id**: Unique request ID for troubleshooting and log tracing

---

## Error Scenarios

### 1. Invalid Email or Wrong Password

**HTTP Status**: `401 Unauthorized`

**When**: User provides incorrect email or password

**Response**:
```json
{
  "detail": "Invalid credentials",
  "error_code": "AUTHENTICATION_FAILED",
  "message": "The email or password you entered is incorrect",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Security Note**: ✅ This response intentionally does not reveal whether the email exists or not, preventing user enumeration attacks.

**Test**:
```powershell
# Invalid email
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"nonexistent@test.com\",\"password\":\"12345\"}"

# Valid email, wrong password
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"user@codedthemes.com\",\"password\":\"wrongpass\"}"
```

---

### 2. Account Locked (Too Many Failed Attempts)

**HTTP Status**: `423 Locked`

**When**: User has exceeded maximum login attempts (default: 5 attempts)

**Response**:
```json
{
  "detail": "Account locked",
  "error_code": "ACCOUNT_LOCKED",
  "message": "Your account has been locked due to too many failed login attempts. Please try again after 2025-10-23 15:30:00 UTC",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Configuration**:
- Max attempts: 5 (configurable via `MAX_LOGIN_ATTEMPTS`)
- Lockout duration: 30 minutes (configurable via `ACCOUNT_LOCKOUT_DURATION`)

**Test**:
```powershell
# Make 5 failed login attempts
for ($i=1; $i -le 5; $i++) {
    curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"user@codedthemes.com\",\"password\":\"wrong\"}"
}

# 6th attempt will return account locked error
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"user@codedthemes.com\",\"password\":\"user1234\"}"
```

---

### 3. Account Inactive

**HTTP Status**: `401 Unauthorized`

**When**: User account has been deactivated by an administrator

**Response**:
```json
{
  "detail": "Account inactive",
  "error_code": "ACCOUNT_INACTIVE",
  "message": "Your account has been deactivated. Please contact support for assistance",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Test**:
```sql
-- Set user account to inactive
UPDATE users SET is_active = false WHERE email = 'user@codedthemes.com';
```

---

### 4. Internal Server Error

**HTTP Status**: `500 Internal Server Error`

**When**: An unexpected error occurs during the login process

**Response**:
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "message": "An unexpected error occurred during login. Please try again later",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Success Response

**HTTP Status**: `200 OK`

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 4,
    "username": "regularuser",
    "email": "user@codedthemes.com",
    "first_name": "Regular",
    "last_name": "User",
    "is_active": true,
    "is_verified": true,
    "created_at": "2025-10-23T18:29:12.402790Z"
  },
  "requires_mfa": false
}
```

---

## Frontend Error Handling

### TypeScript/JavaScript Example

```typescript
interface LoginErrorResponse {
  detail: string;
  error_code: string;
  message: string;
  request_id?: string;
}

async function handleLogin(email: string, password: string) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error: LoginErrorResponse = await response.json();

      // Handle specific error codes
      switch (error.error_code) {
        case 'AUTHENTICATION_FAILED':
          // Show: "The email or password you entered is incorrect"
          showErrorMessage(error.message);
          break;

        case 'ACCOUNT_LOCKED':
          // Show: "Your account has been locked..."
          showErrorMessage(error.message);
          // Optionally disable login form
          disableLoginForm();
          break;

        case 'ACCOUNT_INACTIVE':
          // Show: "Your account has been deactivated..."
          showErrorMessage(error.message);
          // Show contact support button
          showSupportContact();
          break;

        case 'INTERNAL_ERROR':
          // Show generic error
          showErrorMessage(error.message);
          // Log to monitoring service
          logError(error.request_id);
          break;

        default:
          showErrorMessage(error.message);
      }

      return null;
    }

    const data = await response.json();
    // Handle successful login
    storeTokens(data.access_token, data.refresh_token);
    redirectToDashboard();

    return data;

  } catch (err) {
    // Network error or parsing error
    showErrorMessage('Unable to connect to server. Please try again.');
    return null;
  }
}
```

### React Example

```jsx
import { useState } from 'react';

function LoginForm() {
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const formData = new FormData(e.target);
    const email = formData.get('email');
    const password = formData.get('password');

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (!response.ok) {
        // Display the user-friendly message
        setError(data.message);
        return;
      }

      // Success
      localStorage.setItem('access_token', data.access_token);
      window.location.href = '/dashboard';

    } catch (err) {
      setError('Unable to connect to server. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="email" name="email" required />
      <input type="password" name="password" required />

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      <button type="submit">Login</button>
    </form>
  );
}
```

---

## Error Code Reference

| Error Code | HTTP Status | Description |
|-----------|-------------|-------------|
| `AUTHENTICATION_FAILED` | 401 | Invalid email or password |
| `ACCOUNT_LOCKED` | 423 | Account locked due to failed attempts |
| `ACCOUNT_INACTIVE` | 401 | Account deactivated by admin |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## Security Best Practices

### ✅ What We Do (Secure)

1. **Generic Error Messages**: Don't reveal if email exists
   - ❌ Bad: "Email not found" or "Wrong password"
   - ✅ Good: "Invalid email or password"

2. **Rate Limiting**: Lock account after failed attempts
   - Prevents brute force attacks
   - Configurable threshold (default: 5 attempts)

3. **Request Tracing**: Include request_id for debugging
   - Helps support team troubleshoot issues
   - Doesn't expose sensitive information

4. **Structured Errors**: Machine-readable error codes
   - Frontend can handle errors programmatically
   - Consistent error format across API

### 🔒 Security Features

- **No User Enumeration**: Same error for invalid email and wrong password
- **Account Lockout**: Automatic after 5 failed attempts
- **Audit Logging**: All login attempts logged with IP and user agent
- **Password Hashing**: Argon2id (industry standard)
- **JWT Tokens**: HS256 algorithm with secure secrets

---

## Configuration

Add these to your `.env` file to customize behavior:

```env
# Maximum failed login attempts before account lockout
MAX_LOGIN_ATTEMPTS=5

# Account lockout duration in minutes
ACCOUNT_LOCKOUT_DURATION=30

# JWT token expiration
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## API Documentation

View interactive API documentation at:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

The error response examples are included in the OpenAPI specification.

---

## Testing Guide

### PowerShell Test Script

```powershell
# Test 1: Invalid Email
Write-Host "Test 1: Invalid Email" -ForegroundColor Yellow
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d "{\"email\":\"invalid@test.com\",\"password\":\"12345\"}"

# Test 2: Wrong Password
Write-Host "`nTest 2: Wrong Password" -ForegroundColor Yellow
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d "{\"email\":\"user@codedthemes.com\",\"password\":\"wrongpass\"}"

# Test 3: Valid Login
Write-Host "`nTest 3: Valid Login" -ForegroundColor Yellow
curl -X POST http://localhost:8000/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d "{\"email\":\"user@codedthemes.com\",\"password\":\"user1234\"}"
```

---

## Support

For issues or questions:
1. Check the `request_id` in the error response
2. Search backend logs for that request_id
3. Review the error details and stack trace

**Log Location**: `backend/logs/app.log`

**Example Log Search**:
```powershell
docker-compose logs backend | grep "550e8400-e29b-41d4-a716-446655440000"
```

---

**Error Response Format Version**: 1.0
**Last Updated**: October 23, 2025
**Implements**: Industry-standard error handling (Option B)
