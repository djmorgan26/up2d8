# Google OAuth 2.0 Setup Guide for UP2D8

This guide walks through implementing Google OAuth 2.0 authentication for UP2D8, allowing users to sign up and log in with their Gmail accounts.

---

## Why Google OAuth?

1. **User Convenience**: Users can sign up/login with one click, no password to remember
2. **Security**: No need to store user passwords
3. **Email Access**: We get verified email addresses from Google
4. **Trust**: Users trust Google authentication more than new services

---

## Prerequisites

- Azure Web App deployed and running
- Backend API accessible at `https://up2d8.azurewebsites.net`
- Admin access to Google Cloud Console

---

## Step 1: Create Google OAuth 2.0 Credentials

### 1.1 Go to Google Cloud Console

Visit: https://console.cloud.google.com/

### 1.2 Create a New Project (if needed)

1. Click on the project dropdown at the top
2. Click "NEW PROJECT"
3. Name: "UP2D8"
4. Click "CREATE"

### 1.3 Enable Google+ API

1. Go to "APIs & Services" > "Library"
2. Search for "Google+ API"
3. Click "ENABLE"

### 1.4 Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" (for public users)
3. Click "CREATE"

**App Information**:
- App name: `UP2D8`
- User support email: `davidjmorgan26@gmail.com`
- App logo: (optional, upload later)

**App Domain**:
- Application home page: `https://up2d8.azurewebsites.net`
- Privacy policy: `https://up2d8.azurewebsites.net/privacy` (create later)
- Terms of service: `https://up2d8.azurewebsites.net/terms` (create later)

**Developer Contact**:
- Email: `davidjmorgan26@gmail.com`

**Scopes**:
- Click "ADD OR REMOVE SCOPES"
- Select:
  - `userinfo.email` - See your primary Google Account email address
  - `userinfo.profile` - See your personal info, including any personal info you've made publicly available
  - `openid` - Associate you with your personal info on Google

**Test Users** (for testing before verification):
- Add `davidjmorgan26@gmail.com`

Click "SAVE AND CONTINUE"

### 1.5 Create OAuth 2.0 Client ID

1. Go to "APIs & Services" > "Credentials"
2. Click "CREATE CREDENTIALS" > "OAuth client ID"
3. Application type: "Web application"
4. Name: "UP2D8 Web Client"

**Authorized JavaScript origins**:
```
https://up2d8.azurewebsites.net
http://localhost:5173 (for local frontend development)
```

**Authorized redirect URIs**:
```
https://up2d8.azurewebsites.net/api/v1/auth/google/callback
http://localhost:8000/api/v1/auth/google/callback (for local testing)
```

Click "CREATE"

### 1.6 Save Credentials

You'll see a modal with:
- Client ID: `xxxxxxxxxxxx.apps.googleusercontent.com`
- Client Secret: `GOCSPX-xxxxxxxxxxxx`

**IMPORTANT**: Copy these values - you'll need them in Step 2!

---

## Step 2: Configure Azure Environment Variables

Add the Google OAuth credentials to Azure Web App settings:

```bash
az webapp config appsettings set \
  --resource-group personal-rg \
  --name up2d8 \
  --settings \
  "GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com" \
  "GOOGLE_CLIENT_SECRET=your_client_secret"
```

Or manually in Azure Portal:
1. Go to Azure Portal > App Services > up2d8
2. Click "Configuration" in left menu
3. Click "New application setting"
4. Add `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
5. Click "Save"

---

## Step 3: Install Python Dependencies

Add to `backend/requirements.txt`:

```txt
authlib==1.3.0  # OAuth library
httpx==0.25.2   # HTTP client (already included)
```

Install:
```bash
cd backend
pip install authlib==1.3.0
```

---

## Step 4: Implement OAuth Backend

### 4.1 Update Auth Router

Edit `backend/api/routers/auth.py`:

```python
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse
import os

# Initialize OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get("/google")
async def google_login(request: Request):
    """
    Redirect to Google OAuth login page.

    Frontend should redirect user here to start OAuth flow.
    """
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Database = Depends(get_db)):
    """
    Handle Google OAuth callback.

    Google redirects here after user authorizes the app.
    """
    try:
        # Get access token from Google
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')

        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")

        # Extract user information
        email = user_info.get('email')
        full_name = user_info.get('name', '')
        google_id = user_info.get('sub')  # Google's unique user ID
        picture_url = user_info.get('picture')  # Profile picture URL

        # Check if user already exists
        from api.db.cosmos_db import CosmosCollections
        existing_user = db[CosmosCollections.USERS].find_one({"email": email})

        if existing_user:
            # User exists - update last login
            db[CosmosCollections.USERS].update_one(
                {"id": existing_user["id"]},
                {
                    "$set": {
                        "last_login_at": datetime.utcnow(),
                        "oauth_provider": "google",
                        "oauth_id": google_id,
                    }
                }
            )
            user_id = existing_user["id"]
        else:
            # New user - create account
            from api.db.models import User
            new_user = User(
                email=email,
                full_name=full_name,
                oauth_provider="google",
                oauth_id=google_id,
                tier="free",
                status="active",
                onboarding_completed=False,
            )

            result = db[CosmosCollections.USERS].insert_one(new_user.dict())
            user_id = new_user.id

        # Generate JWT tokens
        from api.utils.auth import create_access_token, create_refresh_token
        access_token = create_access_token(data={"sub": user_id})
        refresh_token = create_refresh_token(data={"sub": user_id})

        # Return tokens to frontend
        # Option 1: Redirect to frontend with tokens in query params
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
        )

        # Option 2: Return JSON (if using fetch from frontend)
        # return {
        #     "access_token": access_token,
        #     "refresh_token": refresh_token,
        #     "token_type": "bearer",
        #     "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        #     "user": {
        #         "id": user_id,
        #         "email": email,
        #         "full_name": full_name,
        #         "picture_url": picture_url,
        #     }
        # }

    except Exception as e:
        print(f"OAuth error: {e}")
        raise HTTPException(status_code=400, detail=f"OAuth failed: {str(e)}")
```

### 4.2 Update User Model

Edit `backend/api/db/models.py` to add OAuth fields:

```python
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: Optional[str] = None  # Optional for OAuth users
    full_name: str
    tier: str = "free"
    status: str = "active"
    onboarding_completed: bool = False
    oauth_provider: Optional[str] = None  # "google", "microsoft", etc.
    oauth_id: Optional[str] = None  # Provider's unique user ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
```

---

## Step 5: Frontend Integration

### 5.1 React Component Example

```javascript
// src/components/GoogleLoginButton.jsx
import { Button } from '@/components/ui/button';

export function GoogleLoginButton() {
  const handleGoogleLogin = () => {
    // Redirect to backend OAuth endpoint
    window.location.href = 'https://up2d8.azurewebsites.net/api/v1/auth/google';
  };

  return (
    <Button onClick={handleGoogleLogin} variant="outline" className="w-full">
      <img src="/google-icon.svg" alt="Google" className="w-5 h-5 mr-2" />
      Continue with Google
    </Button>
  );
}
```

### 5.2 Handle OAuth Callback

```javascript
// src/pages/AuthCallback.jsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export function AuthCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    // Get tokens from URL query params
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get('access_token');
    const refreshToken = params.get('refresh_token');

    if (accessToken && refreshToken) {
      // Store tokens in localStorage or state management
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);

      // Redirect to dashboard
      navigate('/dashboard');
    } else {
      // Error handling
      navigate('/login?error=oauth_failed');
    }
  }, [navigate]);

  return <div>Processing login...</div>;
}
```

### 5.3 Add Route

```javascript
// src/App.jsx
import { AuthCallback } from './pages/AuthCallback';

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route path="/dashboard" element={<Dashboard />} />
    </Routes>
  );
}
```

---

## Step 6: Testing

### 6.1 Local Testing

1. **Start backend**:
```bash
cd backend
uvicorn api.main:app --reload
```

2. **Start frontend**:
```bash
cd frontend
npm run dev
```

3. **Test OAuth flow**:
   - Go to http://localhost:5173/login
   - Click "Continue with Google"
   - Authorize the app
   - Check if you're redirected back with tokens

### 6.2 Production Testing

1. **Deploy to Azure** (backend already deployed)
2. **Test OAuth flow**:
   - Go to https://up2d8.azurewebsites.net/docs
   - Find `/api/v1/auth/google` endpoint
   - Click "Try it out" > "Execute"
   - Follow Google login flow
   - Check if callback works

### 6.3 Manual Test with curl

```bash
# This won't work directly with curl (OAuth requires browser)
# But you can test if endpoints exist:

curl -I https://up2d8.azurewebsites.net/api/v1/auth/google
# Should return 307 Temporary Redirect (to Google)
```

---

## Step 7: Security Considerations

### 7.1 Production Checklist

- [ ] Change `JWT_SECRET_KEY` to a secure random value (64+ characters)
- [ ] Set `FRONTEND_URL` environment variable correctly
- [ ] Add real Privacy Policy and Terms of Service pages
- [ ] Verify OAuth consent screen before submitting for verification
- [ ] Add HTTPS-only cookies for token storage (more secure than localStorage)
- [ ] Implement CSRF protection
- [ ] Rate limit OAuth endpoints
- [ ] Log OAuth attempts for security monitoring

### 7.2 CSRF Protection

Add CSRF token to OAuth state:

```python
import secrets

@router.get("/google")
async def google_login(request: Request):
    # Generate CSRF token
    csrf_token = secrets.token_urlsafe(32)

    # Store in session or database
    request.session['oauth_csrf'] = csrf_token

    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
        state=csrf_token  # Google will return this in callback
    )

@router.get("/google/callback")
async def google_callback(request: Request):
    # Verify CSRF token
    state = request.query_params.get('state')
    stored_csrf = request.session.get('oauth_csrf')

    if not state or state != stored_csrf:
        raise HTTPException(status_code=400, detail="CSRF validation failed")

    # Continue with OAuth...
```

---

## Step 8: Troubleshooting

### Common Issues

**Issue**: "redirect_uri_mismatch"
- **Fix**: Make sure redirect URI in Google Console matches exactly:
  - `https://up2d8.azurewebsites.net/api/v1/auth/google/callback`

**Issue**: "invalid_client"
- **Fix**: Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` environment variables

**Issue**: "access_denied"
- **Fix**: User cancelled authorization or app is not verified yet

**Issue**: "Cookies are blocked"
- **Fix**: Authlib requires cookies for OAuth state. Enable cookies or use alternative state storage.

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Step 9: Google App Verification (Optional)

For production apps with many users:

1. **Submit for Verification**:
   - Go to OAuth consent screen
   - Click "PUBLISH APP"
   - Submit for verification

2. **Verification Requirements**:
   - Privacy Policy URL (must be accessible)
   - Terms of Service URL (must be accessible)
   - App homepage
   - YouTube video demo (optional but helps)

3. **Review Time**: 3-5 business days

**Note**: Unverified apps work but show a warning screen. For MVP/testing, unverified is fine.

---

## Estimated Timeline

| Task | Time |
|------|------|
| Google Cloud Console setup | 15 minutes |
| Azure environment configuration | 5 minutes |
| Backend implementation | 1 hour |
| Frontend implementation | 30 minutes |
| Testing | 30 minutes |
| **Total** | **~2-3 hours** |

---

## Next Steps

After OAuth is working:

1. Add Microsoft OAuth (similar process)
2. Add "Link Google Account" for existing users
3. Add profile picture from Google to user accounts
4. Implement "Sign in with Apple" (requires Apple Developer account)

---

## Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Authlib Documentation](https://docs.authlib.org/en/latest/)
- [Starlette OAuth Integration](https://docs.authlib.org/en/latest/client/starlette.html)
- [FastAPI OAuth Tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

---

**Last Updated**: October 31, 2025
