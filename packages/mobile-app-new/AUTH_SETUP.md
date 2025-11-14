# Mobile App Authentication Setup Guide

Complete guide to setting up authentication for the UP2D8 React Native mobile app.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Environment Configuration](#environment-configuration)
5. [MSAL Integration](#msal-integration)
6. [iOS Configuration](#ios-configuration)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The mobile app supports two authentication methods:

1. **Basic Auth** (Email/Password) - For testing and development
2. **MSAL** (Microsoft Entra ID) - Production SSO matching web app

### Features

- ✅ Secure token storage (expo-secure-store with encryption)
- ✅ Automatic token refresh on 401 errors
- ✅ Auth navigation guard (login required for app access)
- ✅ Logout functionality with user profile
- ✅ Splash screen during auth initialization
- ✅ Form validation on login/signup
- ⏳ MSAL integration (requires configuration)

---

## Prerequisites

- Node.js >= 18
- React Native 0.76.1
- Xcode 15+ (for iOS)
- Azure Entra ID app registration (for MSAL)

---

## Quick Start

### 1. Install Dependencies

Already installed:
```bash
cd packages/mobile-app-new
# expo-secure-store and @azure/msal-react-native already installed
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
API_BASE_URL=http://localhost:8000/api
ENTRA_CLIENT_ID=your-client-id-here
ENTRA_TENANT_ID=your-tenant-id-here
ENTRA_REDIRECT_URI=msauth.com.up2d8.mobile://auth
ENTRA_API_SCOPE=api://your-api-client-id/access_as_user
```

### 3. Run the App

```bash
npm run ios
```

---

## Environment Configuration

### Development (.env)

```env
# Backend API
API_BASE_URL=http://localhost:8000/api
API_TIMEOUT=30000

# Azure Entra ID
ENTRA_CLIENT_ID=abc123-def456-...
ENTRA_TENANT_ID=xyz789-uvw012-...
ENTRA_REDIRECT_URI=msauth.com.up2d8.mobile://auth
ENTRA_API_SCOPE=api://abc123-def456-.../access_as_user
```

### Production

Update `API_BASE_URL` to production backend:
```env
API_BASE_URL=https://up2d8.azurewebsites.net/api
```

---

## MSAL Integration

### Step 1: Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com) → Entra ID → App Registrations
2. Use existing app registration (same as web app) OR create new one
3. Note **Application (client) ID** and **Directory (tenant) ID**

### Step 2: Configure Redirect URI

In Azure Portal → Your App → Authentication:

1. Add platform: **Mobile and desktop applications**
2. Add custom redirect URI: `msauth.com.up2d8.mobile://auth`
3. Enable **Access tokens** and **ID tokens**

### Step 3: Update .env

```env
ENTRA_CLIENT_ID=<your-client-id>
ENTRA_TENANT_ID=<your-tenant-id>
ENTRA_REDIRECT_URI=msauth.com.up2d8.mobile://auth
ENTRA_API_SCOPE=api://<your-api-client-id>/access_as_user
```

### Step 4: Complete MSAL Service

Edit `src/services/msalService.ts`:

```typescript
import { MSALClient } from '@azure/msal-react-native';

// Initialize MSAL client
const msalClient = new MSALClient({
  auth: {
    clientId: msalConfig.clientId,
    authority: getMSALAuthority(),
    redirectUri: msalConfig.redirectUri,
  },
});

// Implement acquireTokenInteractive
async acquireTokenInteractive(): Promise<MSALAuthResult> {
  const result = await msalClient.acquireTokenInteractive({
    scopes: msalConfig.scopes,
  });
  return result;
}

// Implement acquireTokenSilent
async acquireTokenSilent(account: MSALAccount): Promise<MSALAuthResult> {
  const result = await msalClient.acquireTokenSilent({
    scopes: msalConfig.scopes,
    account: account,
  });
  return result;
}

// Implement getAccounts and signOut...
```

---

## iOS Configuration

### Step 1: Update Info.plist

Add MSAL redirect URI scheme to `ios/up2d8ReactNative/Info.plist`:

```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>msauth.com.up2d8.mobile</string>
    </array>
  </dict>
</array>

<key>LSApplicationQueriesSchemes</key>
<array>
  <string>msauthv2</string>
  <string>msauthv3</string>
</array>
```

### Step 2: Install Pods

```bash
cd ios
pod install
cd ..
```

### Step 3: Keychain Sharing (Optional)

For token storage across app reinstalls:

1. Open Xcode
2. Select target → Signing & Capabilities
3. Add **Keychain Sharing** capability
4. Add keychain group: `com.up2d8.mobile`

---

## Testing

### Test Auth Flow

1. **Launch app** → Should show splash screen → Login screen
2. **Try basic login** → Should show "not yet implemented" error
3. **Click "Sign in with Microsoft"** → Should navigate to MSAL screen
4. **MSAL login** (after configuration) → Should authenticate and show main app
5. **Go to Settings** → Should see user profile
6. **Click "Sign Out"** → Should return to login screen
7. **Re-launch app** → Should stay logged in (token persisted)

### Test Token Refresh

1. Log in successfully
2. Wait for token to expire (or manually expire it)
3. Make API request
4. Should automatically refresh token and retry request
5. If refresh fails, should redirect to login

### Mock User for Testing

Temporarily bypass login in `src/stores/authStore.ts`:

```typescript
// In authStore.ts, add:
const mockUser = {
  id: 'test-user-id',
  email: 'test@example.com',
  name: 'Test User',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

// Set initial state:
user: __DEV__ ? mockUser : null,
isAuthenticated: __DEV__ ? true : false,
```

---

## Troubleshooting

### Issue: "MSAL not configured"

**Solution**: Set `ENTRA_CLIENT_ID` in `.env`

```bash
echo "ENTRA_CLIENT_ID=your-client-id" >> .env
```

### Issue: "Token storage failed"

**Solution**: Check expo-secure-store is installed

```bash
npm list expo-secure-store
# If missing:
npm install expo-secure-store
```

### Issue: "Network error"

**Solution**: Check backend is running

```bash
curl http://localhost:8000/api/health
```

### Issue: "401 Unauthorized"

**Causes**:
1. Token expired and refresh failed
2. Invalid token format
3. Backend not accepting token

**Solution**: Check backend auth configuration matches MSAL config

### Issue: iOS build fails

**Solution**: Clean build and reinstall pods

```bash
cd ios
rm -rf Pods Podfile.lock
pod install
cd ..
npm run ios
```

### Issue: Token not persisting

**Solution**: Check secure storage permissions

For iOS: Add Keychain Sharing capability
For Android: Check storage permissions in AndroidManifest.xml

---

## Architecture

### Auth Flow

```
App Launch
  ↓
Splash Screen
  ↓
Check SecureStore for token
  ↓
Token exists? → Yes → Load user → Main App
  ↓ No
Login Screen → MSAL/Basic Auth → Store token → Main App
```

### Token Refresh Flow

```
API Request (401)
  ↓
Interceptor detects 401
  ↓
Call refreshAccessToken()
  ↓
Success? → Retry request
  ↓ Fail
Clear auth → Redirect to Login
```

### Files

```
src/
├── stores/
│   └── authStore.ts              # Zustand auth state + secure storage
├── screens/Auth/
│   ├── LoginScreen.tsx           # Email/password login
│   ├── SignupScreen.tsx          # Registration
│   ├── MSALLoginScreen.tsx       # Microsoft SSO
│   └── SplashScreen.tsx          # Loading screen
├── navigation/
│   └── RootNavigator.tsx         # Auth guard + token refresh setup
├── services/
│   └── msalService.ts            # MSAL wrapper
└── config/
    └── msalConfig.ts             # MSAL configuration
```

### Shared Packages

```
packages/
├── shared-api/
│   └── src/client.ts             # API client with token refresh interceptor
└── shared-types/
    └── src/user.ts               # User type definitions
```

---

## Next Steps

1. ✅ Basic auth structure - **DONE**
2. ✅ Token refresh interceptor - **DONE**
3. ⏳ Complete MSAL service implementation
4. ⏳ Add backend login/signup endpoints
5. ⏳ Test end-to-end auth flow
6. ⏳ Add biometric authentication (Face ID/Touch ID)
7. ⏳ Add "Remember Me" functionality
8. ⏳ Add password reset flow

---

## References

- [MSAL React Native Docs](https://github.com/AzureAD/microsoft-authentication-library-for-react-native)
- [expo-secure-store Docs](https://docs.expo.dev/versions/latest/sdk/securestore/)
- [React Navigation Auth Flow](https://reactnavigation.org/docs/auth-flow/)
- [Azure App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)

---

## Support

For issues or questions:
1. Check this guide
2. Check backend `/api/docs` for API endpoints
3. Review web app MSAL config at `packages/web-app/src/config/msalConfig.ts`
4. Check Azure Portal app registration settings
