# UP2D8 API Configuration Guide

This document explains how to configure the React Native app to connect to your backend API.

## Setting the Backend URL

The app needs to know where your FastAPI backend is running. You can configure this in two ways:

### Option 1: Using the Default Configuration (Recommended for Development)

The app uses automatic environment detection:

- **Development Mode** (`__DEV__ = true`): `http://localhost:8000`
- **Production Mode** (`__DEV__ = false`): `https://your-backend.azurewebsites.net`

To change the production URL, edit `/src/services/api.ts`:

```typescript
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000'
  : 'https://YOUR-ACTUAL-BACKEND.azurewebsites.net';  // Update this
```

### Option 2: Using Environment Variables (Recommended for Multiple Environments)

1. Install react-native-dotenv:
   ```bash
   npm install react-native-dotenv
   ```

2. Create a `.env` file in the root directory (copy from `.env.example`):
   ```
   API_BASE_URL=http://localhost:8000
   ```

3. Update `.env` for different environments:
   - Development: `http://localhost:8000`
   - Azure Dev: `https://up2d8-dev.azurewebsites.net`
   - Azure Prod: `https://up2d8.azurewebsites.net`

### Option 3: Runtime Configuration

You can dynamically set the API URL at runtime:

```typescript
import { setApiBaseUrl } from './services/api';

// Call this before making any API requests
setApiBaseUrl('https://your-custom-backend.com');
```

## Testing the Connection

### 1. Test Backend Connection

Before running the app, verify your backend is accessible:

```bash
# Test local backend
curl http://localhost:8000/api/articles

# Test Azure backend
curl https://your-backend.azurewebsites.net/api/articles
```

### 2. Test from the App

The app logs all API requests to the console. Look for:

```
[API] GET https://your-backend.azurewebsites.net/api/articles
[API Success] GET https://your-backend.azurewebsites.net/api/articles
```

Or errors:

```
[API Error] GET https://your-backend.azurewebsites.net/api/articles: Network error
```

## Common Issues

### Issue: "Network error. Please check your connection"

**Causes:**
- Backend is not running
- Incorrect URL
- CORS issues (backend not allowing mobile app origin)
- iOS ATS blocking HTTP connections

**Solutions:**

1. **Verify backend is running:**
   ```bash
   curl https://your-backend.azurewebsites.net/api/articles
   ```

2. **Check URL in api.ts:**
   ```typescript
   console.log(getApiBaseUrl());  // Add this to verify
   ```

3. **iOS HTTP (not HTTPS) connections:**

   iOS blocks HTTP by default. To allow HTTP for local development, add to `ios/up2d8ReactNative/Info.plist`:

   ```xml
   <key>NSAppTransportSecurity</key>
   <dict>
     <key>NSAllowsArbitraryLoads</key>
     <true/>
   </dict>
   ```

   **WARNING:** Only use this for development! Production must use HTTPS.

4. **CORS issues:**

   Ensure your FastAPI backend allows mobile requests:

   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # Or specific origins
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

### Issue: "Request failed with status 404"

**Causes:**
- Endpoint doesn't exist
- Incorrect API path

**Solutions:**

1. Verify endpoint exists:
   ```bash
   curl https://your-backend.azurewebsites.net/api/articles
   ```

2. Check API paths match backend documentation:
   - `/api/chat` - Chat endpoint
   - `/api/users` - User management
   - `/api/articles` - Articles endpoint

### Issue: "Request failed with status 500"

**Cause:** Backend error

**Solution:**

1. Check backend logs in Azure Portal
2. Test endpoint directly with curl
3. Verify backend environment variables are set

## Backend Endpoint Reference

The app expects these endpoints from the backend:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat` | POST | Send message to AI |
| `/api/users` | POST | Create user subscription |
| `/api/users/{user_id}` | GET | Get user profile |
| `/api/users/{user_id}` | PUT | Update user preferences |
| `/api/users/{user_id}` | DELETE | Delete user |
| `/api/articles` | GET | Get all articles |
| `/api/articles/{article_id}` | GET | Get single article |

See `docs/handoff/backend.md` for complete API documentation.

## Production Deployment Checklist

Before deploying to production:

- [ ] Update API_BASE_URL to production Azure URL
- [ ] Remove iOS ATS exception (use HTTPS only)
- [ ] Verify CORS is configured on backend
- [ ] Test all API endpoints
- [ ] Enable error tracking (Sentry, etc.)
- [ ] Test on physical devices
- [ ] Verify SSL certificate is valid
