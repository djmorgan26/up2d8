---
type: feature
name: Entra ID Authentication
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - packages/backend-api/auth.py
  - packages/backend-api/api/auth.py
  - packages/backend-api/main.py
  - packages/web-app/src/auth/authConfig.ts
  - packages/web-app/src/auth/AuthProvider.tsx
  - packages/web-app/src/hooks/useAuth.ts
  - packages/web-app/src/components/AuthExample.tsx
  - AUTH_SETUP.md
  - ENTRA_AUTH_SUMMARY.md
related:
  - .ai/context/decisions/003-single-app-registration.md
tags: [auth, entra-id, azure-ad, msal, jwt, fastapi, security]
---

# Entra ID Authentication

## What It Does

Single sign-on authentication system using Microsoft Entra ID (Azure AD) for both web frontend and backend API. Uses a **single app registration** approach where the frontend authenticates users via MSAL (Microsoft Authentication Library), obtains access tokens, and the backend validates those tokens using JWT verification.

**Key capability:** Users login once with their Microsoft account and gain secure access to all protected API endpoints.

## Architecture Overview

```
┌─────────────┐     1. Login Request    ┌──────────────────┐
│  Web App    │ ───────────────────────> │   Entra ID       │
│  (React)    │                          │   (Azure AD)     │
└─────────────┘                          └──────────────────┘
      │                                           │
      │        2. Access Token (JWT)              │
      │ <─────────────────────────────────────────┘
      │
      │  3. API Call + Authorization: Bearer <token>
      └───────────────────────┐
                              ▼
                    ┌────────────────────┐
                    │   FastAPI Backend  │
                    │   Validates Token  │
                    └────────────────────┘
                              │
                              │ 4. Verify with Entra ID
                              ├────────────────────────> [Entra ID validates]
                              │
                              │ 5. Extract user claims
                              │ 6. Return protected data
                              ▼
                    ┌────────────────────┐
                    │   User: {          │
                    │     sub, email,    │
                    │     name, oid      │
                    │   }                │
                    └────────────────────┘
```

## How It Works

### Frontend (MSAL Authentication)

**Configuration:** `packages/web-app/src/auth/authConfig.ts:4`

MSAL is configured with:
- Client ID from Entra ID app registration
- Tenant ID (organization)
- Redirect URI for post-login
- API scope: `api://{CLIENT_ID}/access_as_user`

**Provider Setup:** `packages/web-app/src/auth/AuthProvider.tsx:8`

`MsalProvider` wraps the entire app, initializing the MSAL instance and making auth context available to all components.

**Auth Hook:** `packages/web-app/src/hooks/useAuth.ts:4`

Custom hook providing:
- `login()` - Opens Microsoft login popup
- `logout()` - Signs user out
- `getAccessToken()` - Retrieves valid token (silent renewal or popup)
- `isAuthenticated` - Boolean auth status
- `user` - User account object

**Token Acquisition Flow:**
1. User calls `login()` → MSAL popup opens
2. User authenticates with Microsoft
3. Token stored in localStorage
4. `getAccessToken()` retrieves token:
   - First tries silent acquisition (uses cached token)
   - Falls back to popup if token expired
   - Returns null if both fail

### Backend (JWT Validation)

**Auth Module:** `packages/backend-api/auth.py:1`

Uses `fastapi-azure-auth` library to:
- Validate JWT signature with Entra ID public keys
- Verify token audience, issuer, expiration
- Extract user claims (sub, email, name, oid)

**Configuration:**
```python
azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=CLIENT_ID,
    tenant_id=TENANT_ID,
    scopes={f"{AUDIENCE}/access_as_user": "Access as user"},
)
```

**User Dependency:** `packages/backend-api/auth.py:35`

`get_current_user()` is a FastAPI dependency that:
1. Extracts Authorization header
2. Validates JWT token via `azure_scheme`
3. Parses claims into User model
4. Returns authenticated user or raises 401

**Protected Routes:** `packages/backend-api/api/auth.py:1`

Example endpoints:
- `GET /api/auth/me` - Returns current user profile
- `GET /api/auth/protected` - Example protected endpoint

**Usage pattern:**
```python
@router.get("/protected")
async def my_route(user: User = Depends(get_current_user)):
    # user is guaranteed to be authenticated here
    return {"user_id": user.sub, "email": user.email}
```

## Important Decisions

### Decision 1: Single App Registration
**Rationale:** Simplifies configuration and reduces maintenance. Frontend and backend share the same client ID, with the backend exposing an API scope that the frontend requests.

**Alternative considered:** Separate registrations for frontend and backend - rejected due to added complexity for a personal project.

### Decision 2: MSAL Popup Flow (not Redirect)
**Rationale:** Popup flow keeps user on the page, better UX for SPA. Redirect flow would navigate away and back.

**Fallback:** Can switch to redirect flow by changing `loginPopup` to `loginRedirect` in useAuth.ts.

### Decision 3: localStorage for Token Caching
**Rationale:** Tokens persist across sessions, so users don't need to re-login frequently.

**Security consideration:** Acceptable for this use case. For higher security, can switch to sessionStorage or in-memory storage.

### Decision 4: fastapi-azure-auth Library
**Rationale:** Provides automatic JWT validation with Entra ID, handling key rotation and verification logic.

**Alternative considered:** Manual JWT validation with python-jose - rejected in favor of battle-tested library.

## Environment Configuration

**Frontend (.env):**
```env
VITE_APP_ENTRA_CLIENT_ID=2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97
VITE_APP_ENTRA_TENANT_ID=6f69caf6-bea0-4a54-a20c-7469005eadf4
VITE_APP_ENTRA_REDIRECT_URI=http://localhost:5173
VITE_APP_ENTRA_API_SCOPE=api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97/access_as_user
```

**Backend (.env):**
```env
ENTRA_TENANT_ID=6f69caf6-bea0-4a54-a20c-7469005eadf4
ENTRA_CLIENT_ID=2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97
ENTRA_AUDIENCE=api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97
```

## Usage Examples

### Frontend: Login Component

```tsx
import { useAuth } from './hooks/useAuth';

export const LoginButton = () => {
  const { isAuthenticated, user, login, logout } = useAuth();

  if (isAuthenticated) {
    return (
      <div>
        <span>Welcome, {user.name}!</span>
        <button onClick={logout}>Logout</button>
      </div>
    );
  }

  return <button onClick={login}>Login with Microsoft</button>;
};
```

### Frontend: Authenticated API Call

```tsx
import { useAuth } from './hooks/useAuth';

export const FetchData = () => {
  const { getAccessToken } = useAuth();

  const fetchProtectedData = async () => {
    const token = await getAccessToken();

    const response = await fetch('http://localhost:8000/api/articles', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await response.json();
    return data;
  };

  // ... rest of component
};
```

### Backend: Protecting a Route

```python
from fastapi import APIRouter, Depends
from auth import get_current_user, User

router = APIRouter()

@router.get("/api/articles")
async def get_user_articles(user: User = Depends(get_current_user)):
    """
    Protected route - requires valid Entra ID token.
    User object contains authenticated user info.
    """
    articles = fetch_articles_for_user(user.sub)
    return articles
```

### Backend: Optional Authentication

```python
from typing import Optional

@router.get("/api/articles")
async def get_articles(user: Optional[User] = Depends(get_current_user)):
    """
    Works for both authenticated and unauthenticated users.
    Authenticated users get personalized content.
    """
    if user:
        return fetch_personalized_articles(user.sub)
    else:
        return fetch_public_articles()
```

## Testing

### Manual Testing Flow

1. **Start backend:**
   ```bash
   cd packages/backend-api
   source venv/bin/activate
   uvicorn main:app --reload
   ```

2. **Start frontend:**
   ```bash
   cd packages/web-app
   npm run dev
   ```

3. **Test login:**
   - Navigate to `http://localhost:5173`
   - Import and render `<AuthExample />` component
   - Click "Login with Microsoft"
   - Authenticate with Microsoft account
   - Verify token is stored in localStorage

4. **Test protected API:**
   - In AuthExample component, click "Test Protected API"
   - Should see user profile returned from `/api/auth/me`

5. **Test with curl:**
   ```bash
   # Get token from browser localStorage first
   TOKEN="<paste-token-here>"

   curl -H "Authorization: Bearer $TOKEN" \
        http://localhost:8000/api/auth/me
   ```

### Integration Tests

Not yet implemented - future addition.

## Dependencies

**Frontend:**
- `@azure/msal-browser@4.26.1` - Core MSAL library
- `@azure/msal-react@3.0.21` - React integration for MSAL

**Backend:**
- `fastapi-azure-auth==5.2.0` - Azure AD integration for FastAPI
- `python-jose==3.5.0` - JWT utilities (dependency of fastapi-azure-auth)
- `pyjwt==2.10.1` - JWT library (used by fastapi-azure-auth)

## Common Issues

### Issue: "Login popup blocked by browser"

**Solution:** User must allow popups for localhost, or switch to redirect flow:

```tsx
// Change in useAuth.ts
await instance.loginRedirect(loginRequest);  // instead of loginPopup
```

### Issue: "Token validation failed"

**Causes:**
1. Entra ID app registration not configured correctly
2. Access tokens not enabled in Azure Portal
3. Audience mismatch between frontend scope and backend validation

**Solution:** Verify Azure Portal settings (see AUTH_SETUP.md checklist).

### Issue: "CORS error when calling backend"

**Solution:** Ensure CORS is configured in `packages/backend-api/main.py:8`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: "Token expired" errors

**Solution:** `getAccessToken()` automatically handles token renewal. If manual refresh needed:

```tsx
const token = await instance.acquireTokenSilent({
  ...loginRequest,
  account,
  forceRefresh: true,  // Force token refresh
});
```

## Azure Portal Configuration Checklist

Before this feature works, complete these Azure Portal steps:

**App Registration: `up2d8-app-registration`**

1. **Authentication:**
   - [ ] Platform: Single-page application added
   - [ ] Redirect URI: `http://localhost:5173` added
   - [ ] Implicit grant: Access tokens ✅
   - [ ] Implicit grant: ID tokens ✅

2. **Expose an API:**
   - [ ] Application ID URI: `api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97`
   - [ ] Scope: `access_as_user` created
   - [ ] Scope: Admins and users can consent

3. **API Permissions (optional):**
   - [ ] Microsoft Graph → User.Read (delegated)

## Related Knowledge

- [Decision: Single App Registration](.ai/context/decisions/003-single-app-registration.md)
- [Pattern: Protected API Routes](.ai/knowledge/patterns/protected-routes.md) - *(not yet created)*
- [Component: Auth Middleware](.ai/knowledge/backend/auth-middleware.md) - *(not yet created)*

## Future Enhancements

- [ ] Add refresh token rotation
- [ ] Implement role-based access control (RBAC)
- [ ] Add integration tests for auth flow
- [ ] Support redirect flow as alternative to popup
- [ ] Add token caching strategy for mobile app
- [ ] Implement session management (track active sessions)
- [ ] Add logout from all devices functionality
- [ ] Create admin portal for user management

## Documentation Files

- **Setup Guide:** `AUTH_SETUP.md` - Comprehensive setup and troubleshooting
- **Summary:** `ENTRA_AUTH_SUMMARY.md` - Quick reference and implementation summary
- **This File:** Detailed technical documentation

## Key Files Reference

**Frontend:**
- `packages/web-app/src/auth/authConfig.ts` - MSAL configuration
- `packages/web-app/src/auth/AuthProvider.tsx` - React context provider
- `packages/web-app/src/hooks/useAuth.ts` - Custom auth hook
- `packages/web-app/src/components/AuthExample.tsx` - Example usage component
- `packages/web-app/src/main.tsx` - App wrapped with AuthProvider

**Backend:**
- `packages/backend-api/auth.py` - Auth configuration and user dependency
- `packages/backend-api/api/auth.py` - Protected auth endpoints
- `packages/backend-api/main.py` - Azure AD initialization

**Configuration:**
- `packages/web-app/.env` - Frontend environment variables
- `packages/backend-api/.env` - Backend environment variables
- `packages/backend-api/requirements.txt` - Python dependencies

## Security Considerations

1. **Token Storage:** Tokens in localStorage are accessible via XSS. For production, consider:
   - Using httpOnly cookies (requires backend token management)
   - Switching to sessionStorage (session-only tokens)
   - Implementing Content Security Policy (CSP)

2. **CORS:** Currently allows all origins (`allow_origins=["*"]`). For production:
   - Specify exact frontend domain
   - Use environment variable for dynamic CORS config

3. **Token Expiration:** Access tokens expire after 1 hour. Backend handles this automatically.

4. **HTTPS Required:** In production, both frontend and backend must use HTTPS.

5. **Secret Management:** Client ID and Tenant ID are not secrets (they're public). Backend has no client secret (public client flow).

## Performance Notes

- Token acquisition is cached - subsequent calls return cached token
- Silent token renewal happens before expiration (no user interaction)
- Backend validates tokens on every request (consider caching validation results for high-traffic scenarios)

## Migration Notes

If migrating from another auth system:

1. Export existing user data
2. Map user IDs to Entra ID object IDs (oid)
3. Update database with new user identifiers
4. Maintain backward compatibility during transition
5. Consider hybrid auth during migration period
