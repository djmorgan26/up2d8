# Backend Setup Guide for up2d8 Mobile App

This guide explains how to connect your up2d8 React Native mobile app to your backend and Azure Function App.

## Overview

The up2d8 mobile app is designed to work with:
1. **Backend API** - Provides articles, user management, and chat endpoints
2. **Azure Function App** - Handles RSS feed processing and newsletter generation
3. **Mock Data Fallback** - Works offline with demo data when backend is unavailable

## Architecture

```
┌─────────────────┐
│  React Native   │
│   Mobile App    │
└────────┬────────┘
         │
         │ HTTP/HTTPS
         ↓
┌─────────────────┐      ┌──────────────────┐
│  Backend API    │◄─────┤ Azure Functions  │
│  (Express/etc)  │      │  (RSS/Newsletter)│
└────────┬────────┘      └──────────────────┘
         │
         ↓
┌─────────────────┐
│   Cosmos DB     │
│  (Users/Articles)│
└─────────────────┘
```

## Quick Start

### 1. Configure Backend URL

Edit `up2d8ReactNative/src/services/api.ts`:

```typescript
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000'  // ← Update for local dev
  : 'https://your-backend.azurewebsites.net';  // ← Update for production
```

**For iOS Simulator:**
- Use `http://localhost:8000`

**For Android Emulator:**
- Use `http://10.0.2.2:8000` (Android maps this to host machine)

**For Physical Device:**
- Use your computer's IP address: `http://192.168.1.X:8000`
- OR use ngrok for secure tunnel: `https://abc123.ngrok.io`

### 2. Test Backend Connection

Run your backend locally and test the endpoints:

```bash
# Test health check
curl http://localhost:8000/health

# Test articles endpoint
curl http://localhost:8000/api/articles

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me about AI news"}'
```

### 3. Run the Mobile App

```bash
cd up2d8ReactNative
npm start

# In another terminal:
npm run ios     # For iOS
npm run android # For Android
```

## Required Backend Endpoints

Your backend must implement these endpoints:

### Chat
- `POST /api/chat` - Send message to Gemini AI
  ```json
  Request: { "prompt": "string" }
  Response: { "text": "string", "sources": [...] }
  ```

### Articles
- `GET /api/articles` - Get all articles
- `GET /api/articles/:id` - Get specific article

### Users
- `POST /api/users` - Create user subscription
- `GET /api/users/:id` - Get user profile
- `PUT /api/users/:id` - Update user preferences
- `DELETE /api/users/:id` - Delete user

See [Backend API Documentation](https://github.com/yourrepo/backend/docs/api.md) for full spec.

## Mock Data Mode

The app automatically detects when the backend is offline and switches to demo mode:

**Features in Demo Mode:**
- ✅ Browse 8 sample articles
- ✅ Chat with mock AI responses
- ✅ Subscribe/unsubscribe (simulated)
- ✅ Full UI functionality
- 🔴 Red indicator showing "Demo Mode"

**How it Works:**
1. App tries to connect to backend
2. If connection fails or times out (10s)
3. App enables mock data mode
4. All service calls return demo data
5. When backend comes online, app auto-switches back

## Development Workflow

### Local Development

1. **Start your backend:**
   ```bash
   cd ../backend
   npm run dev  # Runs on http://localhost:8000
   ```

2. **Start React Native:**
   ```bash
   cd up2d8ReactNative
   npm start
   npm run ios
   ```

3. **Test with Metro:**
   - Shake device/simulator
   - Tap "Reload" to see changes

### Testing on Physical Device

**Option 1: Use your local network**

1. Find your computer's IP:
   ```bash
   # macOS/Linux
   ifconfig | grep "inet "
   # Look for 192.168.x.x
   ```

2. Update `api.ts`:
   ```typescript
   const API_BASE_URL = __DEV__
     ? 'http://192.168.1.100:8000'  // Your IP
     : '...';
   ```

3. Make sure your phone and computer are on same WiFi

**Option 2: Use ngrok**

1. Install ngrok: https://ngrok.com/download

2. Start tunnel:
   ```bash
   ngrok http 8000
   ```

3. Copy the https URL (e.g., `https://abc123.ngrok.io`)

4. Update `api.ts` with the ngrok URL

## Production Deployment

### Deploy Backend to Azure

1. Deploy your backend to Azure App Service
2. Update production URL in `api.ts`:
   ```typescript
   const API_BASE_URL = __DEV__
     ? '...'
     : 'https://up2d8-backend.azurewebsites.net';
   ```

3. Ensure CORS is enabled for your mobile app

4. Test with production build:
   ```bash
   npm run ios --configuration Release
   npm run android --variant release
   ```

### Environment Variables (Optional)

For better configuration management, you can use `react-native-config`:

1. Install:
   ```bash
   npm install react-native-config
   cd ios && pod install
   ```

2. Create `.env`:
   ```
   API_BASE_URL=https://your-backend.azurewebsites.net
   ```

3. Update `api.ts`:
   ```typescript
   import Config from 'react-native-config';
   const API_BASE_URL = Config.API_BASE_URL || 'http://localhost:8000';
   ```

## Troubleshooting

### Backend Connection Issues

**"Network error" in app:**
- Check backend is running: `curl http://localhost:8000/health`
- Verify URL in `api.ts` matches your backend
- Check firewall isn't blocking connections
- For Android emulator, use `10.0.2.2` instead of `localhost`

**Timeout errors:**
- Backend may be slow to respond
- Check backend logs for errors
- Increase timeout in `api.ts` (currently 10s)

**CORS errors:**
- Add mobile app origin to backend CORS config
- For development, allow all origins: `app.use(cors())`

### Mock Data Not Showing

If backend is offline but mock data isn't showing:
1. Check console logs for "[API] Mock data enabled"
2. Verify `mockData.ts` exists
3. Restart Metro bundler

### Can't Open Article Links

If articles don't open:
1. Check article URLs are valid in backend data
2. Test with: `Linking.canOpenURL(url)`
3. Ensure iOS/Android has web browser installed

## Monitoring

The app logs all API requests:

```
[API] GET http://localhost:8000/api/articles
[API Success] GET http://localhost:8000/api/articles
[ArticlesService] Fetched 8 articles
```

Watch Metro console or device logs for these messages.

## Next Steps

1. ✅ Configure backend URL
2. ✅ Test endpoints
3. ✅ Run mobile app
4. ⬜ Deploy backend to production
5. ⬜ Update production URL
6. ⬜ Test on physical devices
7. ⬜ Submit to App Store/Play Store

## Support

- **Backend Issues**: Check your backend repository
- **Mobile App Issues**: Check this repository's issues
- **API Contract**: See backend API documentation

---

**Quick Reference:**

| Environment | Backend URL | Notes |
|-------------|-------------|-------|
| iOS Simulator | `http://localhost:8000` | Same machine |
| Android Emulator | `http://10.0.2.2:8000` | Android mapping |
| Physical Device (WiFi) | `http://192.168.1.X:8000` | Your computer's IP |
| Physical Device (Tunnel) | `https://xyz.ngrok.io` | ngrok tunnel |
| Production | `https://your-app.azurewebsites.net` | Deployed backend |
