# Shared Types and Constants

This directory contains shared TypeScript types and constants that are used across both frontend and backend.

## Files

### `types.ts`
Contains all TypeScript interfaces and types for:
- User & Authentication
- MFA (Multi-Factor Authentication)
- OAuth
- User Preferences
- Dashboards & Widgets
- API Responses
- Branding & PWA
- Translations
- RBAC (Roles & Permissions)
- Audit Logs

### `constants.ts`
Contains shared constants including:
- API endpoints
- Token configuration
- Pagination defaults
- Widget types
- MFA types
- OAuth providers
- Theme options
- Supported locales
- HTTP status codes
- Error codes
- Grid configuration
- Date formats
- Storage keys

## Usage

### In Frontend (TypeScript/React)

```typescript
import { User, LoginRequest, LoginResponse } from '@/shared/types';
import { AUTH_ENDPOINTS, TOKEN_CONFIG } from '@/shared/constants';

// Use types for API calls
const loginUser = async (credentials: LoginRequest): Promise<LoginResponse> => {
  const response = await fetch(AUTH_ENDPOINTS.LOGIN, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials)
  });
  return response.json();
};

// Use constants
localStorage.setItem(TOKEN_CONFIG.ACCESS_TOKEN_KEY, token);
```

### In Backend (Python)

Create corresponding Pydantic schemas that match these TypeScript types:

```python
from pydantic import BaseModel
from typing import Optional

# Match TypeScript User interface
class User(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    last_login: Optional[str] = None
    created_at: str
    updated_at: str
```

## Keeping Types in Sync

To ensure frontend and backend types stay synchronized:

1. **Use TypeScript types as the source of truth** for API contracts
2. **Generate Pydantic schemas** that match TypeScript interfaces
3. **Use schema validation** on both ends
4. **Version your API** to handle breaking changes
5. **Document changes** when updating types

## Type Naming Conventions

- **Interfaces**: PascalCase (e.g., `User`, `LoginRequest`)
- **Type aliases**: PascalCase (e.g., `MFAType`, `WidgetType`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_PREFIX`, `AUTH_ENDPOINTS`)
- **Enums**: PascalCase for name, UPPER_SNAKE_CASE for values

## Adding New Types

When adding new types:

1. Add TypeScript interface/type to `types.ts`
2. Add related constants to `constants.ts`
3. Create corresponding Pydantic schema in backend
4. Update this README if adding a new category
5. Test both frontend and backend implementations

## API Response Format

All API responses should follow the `ApiResponse<T>` format:

```typescript
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  message?: string;
  requestId?: string;
}
```

Example success response:
```json
{
  "success": true,
  "data": { "id": 1, "username": "john" },
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

Example error response:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid username or password"
  },
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Pagination

Use `PaginatedResponse<T>` for list endpoints:

```typescript
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
```

## Date/Time Handling

- All dates from API should be ISO 8601 format: `2025-10-23T10:30:00Z`
- Use `DateString` type alias for clarity
- Frontend should parse and format based on user locale
- Backend should always use UTC for storage

## Error Handling

Use `ERROR_CODES` constants for consistent error handling:

```typescript
if (response.error?.code === ERROR_CODES.INVALID_CREDENTIALS) {
  // Handle invalid credentials
}
```

## Notes

- Keep this directory in sync with backend Pydantic schemas
- Update version numbers when making breaking changes
- Document any deviations from TypeScript types in backend
- Use code generation tools if maintaining sync becomes difficult
