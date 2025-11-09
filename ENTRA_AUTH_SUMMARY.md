# Entra ID Authentication Implementation Summary

## What Was Implemented

### Single App Registration Approach
✅ Using one Entra ID app registration for both frontend and backend
- **Client ID**: `2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97`
- **Tenant ID**: `6f69caf6-bea0-4a54-a20c-7469005eadf4`

### Frontend (Web App) - MSAL Configuration

**Packages Installed:**
- `@azure/msal-browser@4.26.1`
- `@azure/msal-react@3.0.21`

**Files Created:**
1. `packages/web-app/src/auth/authConfig.ts` - MSAL configuration
2. `packages/web-app/src/auth/AuthProvider.tsx` - Auth context provider
3. `packages/web-app/src/hooks/useAuth.ts` - Custom hook for authentication
4. `packages/web-app/src/components/AuthExample.tsx` - Example component showing auth usage

**Files Modified:**
- `packages/web-app/src/main.tsx` - Wrapped app with AuthProvider
- `packages/web-app/.env` - Added MSAL configuration

**How to Use in Frontend:**
```tsx
import { useAuth } from './hooks/useAuth';

function MyComponent() {
  const { isAuthenticated, user, login, logout, getAccessToken } = useAuth();

  const callAPI = async () => {
    const token = await getAccessToken();
    const response = await fetch('http://localhost:8000/api/endpoint', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  };
}
```

### Backend (FastAPI) - JWT Validation

**Packages Installed:**
- `fastapi-azure-auth==5.2.0`
- `python-jose==3.5.0`
- `pyjwt==2.10.1`

**Files Created:**
1. `packages/backend-api/auth.py` - Azure AD auth configuration and user dependency
2. `packages/backend-api/api/auth.py` - Protected auth routes (/api/auth/me, /api/auth/protected)

**Files Modified:**
- `packages/backend-api/main.py` - Initialize Azure AD auth, add auth router
- `packages/backend-api/requirements.txt` - Added auth dependencies
- `packages/backend-api/.env` - Added Entra ID configuration

**How to Use in Backend:**
```python
from fastapi import APIRouter, Depends
from auth import get_current_user, User

router = APIRouter()

@router.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    return {
        "message": f"Hello {user.name}!",
        "user_id": user.sub,
        "email": user.email
    }
```

## Authentication Flow

```
┌──────────────┐      1. Login      ┌──────────────────┐
│   Web App    │ ──────────────────> │  Entra ID/Azure  │
│  (Frontend)  │                     │       AD         │
└──────────────┘                     └──────────────────┘
       │                                      │
       │              2. Access Token         │
       │ <────────────────────────────────────┘
       │
       │  3. API Call + Token
       │ ──────────────────────┐
       │                       ▼
       │                ┌──────────────┐
       │                │ Backend API  │
       │                │  (FastAPI)   │
       │                └──────────────┘
       │                       │
       │   4. Validate Token   │
       │                       │ (with Entra ID)
       │                       ▼
       │                ┌──────────────────┐
       │                │  Entra ID Verify │
       │                └──────────────────┘
       │                       │
       │    5. Protected Data  │
       │ <─────────────────────┘
       ▼
```

## Environment Configuration

### Frontend (.env)
```env
VITE_APP_ENTRA_CLIENT_ID=2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97
VITE_APP_ENTRA_TENANT_ID=6f69caf6-bea0-4a54-a20c-7469005eadf4
VITE_APP_ENTRA_REDIRECT_URI=http://localhost:5173
VITE_APP_ENTRA_API_SCOPE=api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97/access_as_user
```

### Backend (.env)
```env
ENTRA_TENANT_ID=6f69caf6-bea0-4a54-a20c-7469005eadf4
ENTRA_CLIENT_ID=2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97
ENTRA_AUDIENCE=api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97
```

## Testing

### 1. Start Backend
```bash
cd packages/backend-api
source venv/bin/activate
uvicorn main:app --reload
```

### 2. Start Frontend
```bash
cd packages/web-app
npm run dev
```

### 3. Test Auth Flow
1. Open `http://localhost:5173`
2. Add `<AuthExample />` component to your app
3. Click "Login with Microsoft"
4. Authenticate
5. Click "Test Protected API"
6. Verify response from backend

### 4. Test Backend Directly
```bash
# Get token from frontend first, then:
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/auth/me
```

## Available Endpoints

**Protected (requires auth):**
- `GET /api/auth/me` - Get current user profile
- `GET /api/auth/protected` - Example protected endpoint

**Public:**
- `GET /` - API root
- `GET /health` - Health check
- `GET /docs` - Swagger UI

## Next Steps

### Azure Portal Configuration
Before this works, you need to:

1. **Enable token issuance:**
   - Azure Portal → App Registrations → `up2d8-app-registration`
   - Authentication → Implicit grant and hybrid flows
   - ✅ Access tokens
   - ✅ ID tokens

2. **Verify API exposure:**
   - Expose an API → Ensure scope `access_as_user` exists

3. **Add API permissions (optional):**
   - API permissions → Microsoft Graph → User.Read

### Protect Existing Routes

To protect existing API routes, add the dependency:

```python
# Before (unprotected)
@router.get("/articles")
async def get_articles():
    return articles

# After (protected)
@router.get("/articles")
async def get_articles(user: User = Depends(get_current_user)):
    return articles
```

### Frontend Integration

Add login/logout buttons to your UI:

```tsx
import { useAuth } from './hooks/useAuth';

export const Header = () => {
  const { isAuthenticated, user, login, logout } = useAuth();

  return (
    <header>
      {isAuthenticated ? (
        <>
          <span>Welcome, {user.name}!</span>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <button onClick={login}>Login</button>
      )}
    </header>
  );
};
```

## Documentation

- Full setup guide: `AUTH_SETUP.md`
- This summary: `ENTRA_AUTH_SUMMARY.md`

## Commit

Changes committed with message:
```
Add Entra ID authentication for web-app and backend-api
```

96 files changed, including:
- Frontend auth setup (MSAL)
- Backend auth setup (fastapi-azure-auth)
- Example components and protected routes
- Documentation
