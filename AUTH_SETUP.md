# Entra ID Authentication Setup

This monorepo uses a **single Entra ID app registration** for both frontend and backend authentication.

## Configuration

### App Registration Details

- **Client ID**: `2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97`
- **Tenant ID**: `6f69caf6-bea0-4a54-a20c-7469005eadf4`
- **API Scope**: `api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97/access_as_user`

### Environment Variables

**Frontend (`packages/web-app/.env`)**:
```env
VITE_APP_ENTRA_CLIENT_ID=2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97
VITE_APP_ENTRA_TENANT_ID=6f69caf6-bea0-4a54-a20c-7469005eadf4
VITE_APP_ENTRA_REDIRECT_URI=http://localhost:5173
VITE_APP_ENTRA_API_SCOPE=api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97/access_as_user
```

**Backend (`packages/backend-api/.env`)**:
```env
ENTRA_TENANT_ID=6f69caf6-bea0-4a54-a20c-7469005eadf4
ENTRA_CLIENT_ID=2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97
ENTRA_AUDIENCE=api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97
```

## How It Works

### Authentication Flow

```
1. User clicks "Login" in frontend
2. Frontend redirects to Microsoft login (popup or redirect)
3. User authenticates with Microsoft
4. Frontend receives access token from Entra ID
5. Frontend sends token in Authorization header to backend
6. Backend validates token against Entra ID
7. Backend extracts user info and grants access
```

### Frontend Usage

**Login/Logout**:
```tsx
import { useAuth } from './hooks/useAuth';

function MyComponent() {
  const { isAuthenticated, user, login, logout } = useAuth();

  return (
    <div>
      {isAuthenticated ? (
        <>
          <p>Welcome, {user.name}!</p>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <button onClick={login}>Login</button>
      )}
    </div>
  );
}
```

**Make Authenticated API Calls**:
```tsx
import { useAuth } from './hooks/useAuth';

function MyComponent() {
  const { getAccessToken } = useAuth();

  const fetchData = async () => {
    const token = await getAccessToken();

    const response = await fetch('http://localhost:8000/api/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await response.json();
    console.log(data);
  };

  return <button onClick={fetchData}>Fetch User Data</button>;
}
```

### Backend Usage

**Protect a Route**:
```python
from fastapi import APIRouter, Depends
from auth import get_current_user, User

router = APIRouter()

@router.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    return {
        "message": f"Hello {user.name}!",
        "user_id": user.sub,
        "email": user.email,
    }
```

**Optional Protection** (allow both authenticated and unauthenticated):
```python
from fastapi import APIRouter, Depends
from auth import User
from typing import Optional

@router.get("/optional-auth")
async def optional_auth_route(user: Optional[User] = Depends(get_current_user)):
    if user:
        return {"message": f"Hello {user.name}!", "authenticated": True}
    else:
        return {"message": "Hello guest!", "authenticated": False}
```

## Testing

### Test Frontend Auth

1. Start the web app:
   ```bash
   cd packages/web-app
   npm run dev
   ```

2. Open browser to `http://localhost:5173`
3. Click login button
4. Authenticate with Microsoft account
5. Check console for access token

### Test Backend Auth

1. Start the backend:
   ```bash
   cd packages/backend-api
   source venv/bin/activate
   uvicorn main:app --reload
   ```

2. Get an access token from frontend
3. Test protected endpoint:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/auth/me
   ```

4. Or use FastAPI docs at `http://localhost:8000/docs` and click "Authorize"

## Available Endpoints

**Protected Endpoints**:
- `GET /api/auth/me` - Get current user profile
- `GET /api/auth/protected` - Example protected route

**Public Endpoints**:
- `GET /` - API root
- `GET /health` - Health check

## Troubleshooting

### Frontend Issues

**"Login popup blocked"**:
- Check browser popup settings
- Or use redirect flow instead of popup

**"Token acquisition failed"**:
- Check that redirect URI matches in Azure portal
- Verify client ID and tenant ID are correct

### Backend Issues

**"Invalid token"**:
- Ensure token is being sent in Authorization header
- Check that backend .env has correct tenant/client IDs
- Verify API scope matches in both frontend and backend

**"CORS error"**:
- Check that CORS is configured in main.py
- Verify frontend URL is allowed

## Azure Portal Checklist

Verify these settings in Azure Portal → App Registrations → `up2d8-app-registration`:

- [ ] **Authentication** → Implicit grant: Access tokens ✅, ID tokens ✅
- [ ] **Authentication** → Redirect URIs: `http://localhost:5173` (SPA)
- [ ] **Expose an API** → Application ID URI: `api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97`
- [ ] **Expose an API** → Scope: `access_as_user` exists
- [ ] **API Permissions** → Microsoft Graph → User.Read (optional)

## Production Deployment

Before deploying:

1. **Update redirect URIs** in Azure portal with production URLs
2. **Update CORS** in backend main.py with specific frontend domain
3. **Update .env files** with production URLs
4. **Enable HTTPS** for both frontend and backend
5. **Consider token caching** strategy for better performance

## Security Notes

- Tokens are stored in localStorage (change to sessionStorage if needed)
- Access tokens expire after 1 hour (automatic refresh implemented)
- Always use HTTPS in production
- Never commit .env files to git
- Rotate client secrets regularly (if using confidential client)
