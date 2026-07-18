# TradeFlow — Frontend / Backend Integration Contract

**Date:** 2026-07-18
**Status:** Approved — Awaiting Implementation Approval

---

## 1. API Base URL

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

All API requests are prefixed with `/api/v1`.

---

## 2. Authentication

### 2.1 JWT Strategy

- **Access Token**: Short-lived (15 minutes). Sent in `Authorization: Bearer <token>` header.
- **Refresh Token**: Opaque, long-lived, stored in Redis. Sent via HTTP-only cookie or request body.

### 2.2 Token Storage

- Access token: In-memory (React state / context)
- Refresh token: HTTP-only cookie (preferred) or localStorage (fallback)

### 2.3 Login Flow

1. User submits email + password
2. Backend returns `access` + `refresh` tokens
3. Frontend stores access token in context/state
4. Frontend stores refresh token in HTTP-only cookie or localStorage
5. Axios interceptor attaches `Authorization: Bearer <access>` to all requests

### 2.4 Refresh Flow

1. Access token expires (401 response)
2. Axios interceptor catches 401
3. Interceptor calls `/auth/token/refresh/` with refresh token
4. Backend returns new access token
5. Interceptor retries original request with new access token
6. If refresh fails, redirect to login

### 2.5 Logout Flow

1. Frontend calls `/auth/logout/`
2. Backend invalidates refresh token in Redis
3. Frontend clears access token from state
4. Redirect to login

---

## 3. API Response Envelope

All responses follow the standard envelope:

### Success Response

```json
{
  "data": { ... }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

### Paginated Response

```json
{
  "data": [ ... ],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

---

## 4. Error Handling

### 4.1 Axios Interceptor

```typescript
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Attempt refresh
    }
    // Extract { success, error } from backend
    const { success, error: apiError } = error.response?.data || {};
    if (!success && apiError) {
      // Show notification with apiError.message
    }
    return Promise.reject(error);
  }
);
```

### 4.2 Error Codes

Common error codes exposed by backend:

| Code | Meaning |
|------|---------|
| `VALIDATION_ERROR` | Input validation failed |
| `NOT_FOUND` | Resource not found |
| `PERMISSION_DENIED` | Missing RBAC permission |
| `TENANT_CONTEXT_MISSING` | No tenant resolved |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Server error |

---

## 5. Tenant Awareness

### 5.1 Tenant Resolution

- Backend resolves tenant from:
  - Subdomain (`tenant.tradeflow.co.za`)
  - JWT `tid` claim
  - Request headers

### 5.2 Frontend Behavior

- Frontend never explicitly handles tenant resolution
- All API requests include `Authorization` header with JWT containing `tid`
- Backend enforces tenant isolation automatically
- If tenant context is missing or invalid, backend returns `TENANT_CONTEXT_MISSING`

### 5.3 Tenant Switching (Admin Only)

- Super admin may switch tenant context via header `X-Tenant-Id`
- Frontend exposes tenant switcher in user menu when user has global permissions

---

## 6. RBAC Integration

### 6.1 Permission Loading

On login, backend returns user permissions in JWT claims and/or via `/auth/me/`.

### 6.2 Permission Storage

```typescript
interface AuthState {
  user: {
    id: string;
    email: string;
    permissions: string[];
    roles: string[];
  };
  tenant: {
    id: string;
    name: string;
  };
}
```

### 6.3 Permission Checking

Frontend uses permissions for:

- Route guards (hide/show menu items)
- Button visibility (`<Can permission="platform.branches.create">`)
- API request guards (optional — backend is source of truth)

```typescript
function Can({ permission, children }: { permission: string; children: React.ReactNode }) {
  const { user } = useAuth();
  if (!user.permissions.includes(permission) && !user.permissions.includes('*')) {
    return null;
  }
  return children;
}
```

---

## 7. Environment Configuration

### 7.1 Required Variables

```env
# Backend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_APP_NAME=TradeFlow

# Feature flags
NEXT_PUBLIC_ENABLE_SALES=true
NEXT_PUBLIC_ENABLE_INVENTORY=true
```

### 7.2 Environment Files

- `.env.local` — Local development
- `.env.development` — Development build
- `.env.staging` — Staging build
- `.env.production` — Production build

---

## 8. API Versioning

- URL versioning: `/api/v1/`, `/api/v2/`
- Breaking changes require new version
- Backward-compatible additions (new fields, new endpoints) stay in current version

---

## 9. File Upload Strategy

### 9.1 Upload Flow

1. Frontend requests signed upload URL from backend: `POST /files/presign/`
2. Backend returns presigned URL + fields
3. Frontend uploads file directly to storage provider (S3/minio)
4. Frontend calls `POST /files/` with metadata:
   ```json
   {
     "entity_type": "product",
     "entity_id": "uuid",
     "storage_provider": "s3",
     "storage_path": "tenant_id/product/image.jpg",
     "original_filename": "image.jpg",
     "mime_type": "image/jpeg",
     "file_size": 102400
   }
   ```
5. Backend creates `StoredFile` record

### 9.2 Limits

- Max file size: 10MB per file
- Allowed types: images, PDFs, CSVs
- Storage: S3 or minio (configurable)

---

## 10. CORS Configuration

Backend must allow frontend origin:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://tradeflow-app.vercel.app",
]
```

---

## 11. Request/Response Flow

```
Frontend Component
    ↓
TanStack Query hook
    ↓
Feature service (branches.service.ts)
    ↓
Axios instance (lib/axios.ts)
    ↓
Axios interceptor (attach token, handle refresh)
    ↓
Backend API endpoint
    ↓
DRF View → Service → Repository → Database
    ↓
Response envelope { data } or { success, error }
    ↓
Axios interceptor (handle errors)
    ↓
TanStack Query (cache, update)
    ↓
Component re-render
```

---

## 12. Type Safety

- Frontend types should mirror backend entities (manual sync or codegen)
- Zod schemas validate requests and infer response types
- API client methods typed with domain types

---

**Last Updated:** 2026-07-18