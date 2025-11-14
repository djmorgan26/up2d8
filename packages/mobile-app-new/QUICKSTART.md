# UP2D8 Mobile App - Quick Start Guide

Get the mobile app running in under 5 minutes!

## Prerequisites

- Node.js >= 18
- React Native CLI
- Xcode 15+ (for iOS)
- Android Studio (for Android)

## Step 1: Install Dependencies

```bash
cd packages/mobile-app-new
npm install
```

## Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
# Backend API (use localhost for development)
API_BASE_URL=http://localhost:8000/api

# MSAL (optional - leave blank to use mock auth)
ENTRA_CLIENT_ID=
ENTRA_TENANT_ID=common
```

## Step 3: Start Backend (Optional)

In another terminal:
```bash
cd packages/backend-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Step 4: Run the App

### iOS

```bash
# Install pods (first time only)
cd ios
pod install
cd ..

# Run app
npm run ios
```

### Android

```bash
npm run android
```

## Quick Test (Skip Auth)

To test the app without setting up authentication:

1. Open `src/stores/authStore.ts`
2. Add mock user:

```typescript
// In authStore.ts, change initial state:
user: __DEV__ ? {
  id: 'test-user',
  email: 'test@example.com',
  name: 'Test User',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
} : null,
isAuthenticated: __DEV__ ? true : false,
```

3. Restart app - you'll bypass login and go straight to the app!

## Troubleshooting

### "No bundle URL present"
```bash
npm start -- --reset-cache
```

### iOS build fails
```bash
cd ios
rm -rf Pods Podfile.lock
pod install --repo-update
cd ..
```

### Metro bundler not starting
```bash
npx react-native start --reset-cache
```

### Can't connect to backend
- Check backend is running: `curl http://localhost:8000/api/health`
- Update API_BASE_URL in `.env`
- For iOS simulator, use `http://localhost:8000/api`
- For Android emulator, use `http://10.0.2.2:8000/api`

## What's Next?

- **Set up auth**: See [AUTH_SETUP.md](./AUTH_SETUP.md)
- **Full documentation**: See [README.md](./README.md)
- **API reference**: Visit http://localhost:8000/docs

## Project Structure

```
src/
├── components/         # Reusable UI components
│   ├── ui/            # Core components (GlassCard, Button, etc.)
│   ├── features/      # Feature-specific components
│   └── error/         # Error boundary
├── screens/           # App screens
│   ├── Dashboard/     # Main dashboard
│   ├── Feeds/         # RSS feed management
│   ├── Chat/          # AI chat
│   ├── Settings/      # User settings
│   └── Auth/          # Login/signup screens
├── navigation/        # React Navigation setup
├── stores/            # Zustand state management
├── services/          # External services (MSAL, etc.)
├── config/            # Configuration files
└── utils/             # Utility functions
```

## Key Features

- ✅ **Authentication** - MSAL (Entra ID) or email/password
- ✅ **Dashboard** - News overview with stats
- ✅ **RSS Feeds** - Add and manage news sources
- ✅ **AI Chat** - Chat with Gemini about your news
- ✅ **Dark Mode** - System-aware theme switching
- ✅ **Offline Support** - Cached data with React Query
- ✅ **Error Handling** - Error boundaries and graceful failures

## Commands

```bash
# Development
npm start                 # Start Metro bundler
npm run ios              # Run on iOS simulator
npm run android          # Run on Android emulator

# Quality
npm run lint             # Lint code
npm run typecheck        # TypeScript check
npm test                 # Run tests

# Production
npm run ios --configuration Release    # iOS production build
npm run android -- --mode release      # Android production build
```

## Tips

1. **Use mock data during development** - Add mock user to skip auth
2. **Reset cache if things break** - `npm start -- --reset-cache`
3. **Check backend health** - Visit http://localhost:8000/docs
4. **Enable Flipper** - For React Native debugging
5. **Hot reload** - Shake device/press Cmd+D for dev menu

## Support

- **Auth issues**: See [AUTH_SETUP.md](./AUTH_SETUP.md)
- **Build issues**: See [README.md](./README.md)
- **API issues**: Check backend logs
- **Other issues**: Check React Native docs

---

**Ready to build?** Follow the steps above and you'll be running in minutes!

For production deployment, see [README.md](./README.md) for complete instructions.
