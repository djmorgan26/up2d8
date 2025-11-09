---
type: component
name: Web App Frontend
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - packages/web-app/src/App.tsx
  - packages/web-app/src/main.tsx
  - packages/web-app/src/pages/Dashboard.tsx
  - packages/web-app/src/pages/Feeds.tsx
  - packages/web-app/src/pages/Chat.tsx
  - packages/web-app/src/pages/Settings.tsx
  - packages/web-app/src/pages/Onboarding.tsx
  - packages/web-app/src/components/Layout.tsx
  - packages/web-app/src/components/Sidebar.tsx
  - packages/web-app/src/lib/api.ts
  - packages/web-app/package.json
  - packages/web-app/vite.config.ts
  - packages/web-app/tailwind.config.ts
related:
  - .ai/knowledge/features/entra-id-authentication.md
tags: [frontend, react, vite, typescript, shadcn-ui, web-app, spa]
---

# Web App Frontend

## What It Does

Modern React single-page application (SPA) for the UP2D8 news aggregation platform. Provides a web-based UI for browsing personalized news feeds, managing RSS subscriptions, chatting with AI about articles, and configuring user settings. Built with Vite, TypeScript, and shadcn/ui component library.

**Key capability:** Full-featured web client for UP2D8 that consumes the FastAPI backend, with authentication, responsive design, and modern UX patterns.

## Architecture Overview

```
┌────────────────────────────────────────────────────┐
│                   Web App (SPA)                    │
│                                                    │
│  ┌──────────────┐      ┌──────────────────────┐  │
│  │   Router     │      │   Auth (MSAL)        │  │
│  │  (6 routes)  │      │   - Login/Logout     │  │
│  └──────────────┘      │   - Token mgmt       │  │
│                        └──────────────────────┘  │
│  ┌──────────────┐      ┌──────────────────────┐  │
│  │   Pages      │      │   API Client         │  │
│  │  Dashboard   │◄─────┤   (Axios)            │  │
│  │  Feeds       │      │   - Articles         │  │
│  │  Chat        │      │   - Feeds            │  │
│  │  Settings    │      │   - Chat             │  │
│  └──────────────┘      └──────────────────────┘  │
│                                │                   │
│  ┌──────────────┐             │                   │
│  │  UI Library  │             │                   │
│  │  shadcn/ui   │             │                   │
│  │  49 comps    │             │                   │
│  └──────────────┘             │                   │
└────────────────────────────────┼───────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │  FastAPI Backend     │
                    │  (localhost:8000)    │
                    └──────────────────────┘
```

## Tech Stack

### Core Framework
- **React 18.3.1** - UI framework
- **TypeScript 5.8.3** - Type safety
- **Vite 5.4.19** - Build tool (fast HMR, optimized builds)

### Routing & State
- **React Router DOM 6.30.1** - Client-side routing
- **TanStack Query 5.83.0** - Server state management
- **Zustand** - Client state (if needed, imported via lib)

### UI & Styling
- **shadcn/ui** - Component library (49 components)
- **Radix UI** - Accessible primitives
- **Tailwind CSS 3.4.17** - Utility-first styling
- **Lucide React 0.462.0** - Icon library
- **next-themes** - Dark mode support

### Forms & Validation
- **React Hook Form 7.61.1** - Form management
- **Zod 3.25.76** - Schema validation
- **@hookform/resolvers** - Hook form + Zod integration

### Authentication
- **@azure/msal-browser 4.26.1** - MSAL core
- **@azure/msal-react 3.0.21** - React integration

### HTTP Client
- **Axios 1.13.2** - API requests

### Additional Libraries
- **date-fns 3.6.0** - Date utilities
- **recharts 2.15.4** - Charts/graphs
- **sonner 1.7.4** - Toast notifications
- **cmdk 1.1.1** - Command palette

## Project Structure

```
packages/web-app/
├── src/
│   ├── App.tsx              # Main app component (routing, providers)
│   ├── main.tsx             # Entry point (AuthProvider wrap)
│   ├── index.css            # Global styles + Tailwind
│   │
│   ├── pages/               # Route pages
│   │   ├── Dashboard.tsx    # Article feed (main page)
│   │   ├── Feeds.tsx        # RSS feed management
│   │   ├── Chat.tsx         # AI chat about articles
│   │   ├── Settings.tsx     # User settings
│   │   ├── Onboarding.tsx   # First-time user flow
│   │   └── NotFound.tsx     # 404 page
│   │
│   ├── components/          # Custom components
│   │   ├── Layout.tsx       # App layout wrapper
│   │   ├── Sidebar.tsx      # Navigation sidebar
│   │   ├── ArticleCard.tsx  # Article display card
│   │   ├── AuthExample.tsx  # Auth testing component
│   │   ├── GlassCard.tsx    # Glassmorphism card
│   │   ├── LoadingSkeleton.tsx  # Loading states
│   │   ├── NavLink.tsx      # Sidebar nav item
│   │   ├── ProtectedFeature.tsx # Auth-gated components
│   │   └── ui/              # shadcn/ui components (49)
│   │
│   ├── auth/                # Authentication
│   │   ├── authConfig.ts    # MSAL configuration
│   │   └── AuthProvider.tsx # Auth context provider
│   │
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.ts       # Auth hook
│   │   ├── use-toast.ts     # Toast hook
│   │   └── use-mobile.tsx   # Mobile detection
│   │
│   ├── lib/                 # Utilities
│   │   ├── api.ts           # API client functions
│   │   └── utils.ts         # Helper functions
│   │
│   └── config/              # Configuration
│       └── msalConfig.ts    # MSAL config (duplicate of auth/authConfig.ts)
│
├── public/                  # Static assets
│   ├── favicon.ico
│   ├── placeholder.svg
│   └── robots.txt
│
├── package.json             # Dependencies & scripts
├── vite.config.ts           # Vite configuration
├── tailwind.config.ts       # Tailwind configuration
├── components.json          # shadcn/ui config
├── tsconfig.json            # TypeScript config
└── README.md                # Project documentation
```

## Key Features

### 1. Routing (App.tsx:20)

Six routes defined:
- `/` - Dashboard (article feed)
- `/feeds` - RSS feed management
- `/chat` - AI chat
- `/settings` - User settings
- `/onboarding` - First-time setup
- `*` - 404 Not Found

All routes except `/onboarding` and `*` are wrapped in `<Layout>` component for consistent nav/sidebar.

### 2. Authentication Integration

**MSAL Provider:** `App.tsx:21`
```tsx
<MsalProvider instance={msalInstance}>
  {/* app content */}
</MsalProvider>
```

**Auth Config:** `packages/web-app/src/auth/authConfig.ts:4`
- Client ID, Tenant ID from environment
- Redirect URI for post-login
- API scope for backend access

**Usage in Components:** `packages/web-app/src/pages/Feeds.tsx:24`
```tsx
const { instance, accounts } = useMsal();
const isAuthenticated = accounts.length > 0;
```

Protected features prompt login if not authenticated.

### 3. API Client (lib/api.ts:1)

Centralized API functions using Axios:

**Articles:**
- `getArticles()` - Fetch all articles
- `getArticle(id)` - Fetch single article

**RSS Feeds:**
- `getRSSFeeds()` - List user's feeds
- `addRSSFeed(url)` - Add new feed
- `deleteRSSFeed(id)` - Remove feed

**Chat:**
- `sendChatMessage(message)` - AI chat interaction

**User:**
- `updateUserSettings(settings)` - Save preferences

All functions handle authentication tokens automatically (future enhancement needed).

### 4. Page Components

**Dashboard (pages/Dashboard.tsx:17):**
- Fetches articles from API
- Displays in card grid
- Loading skeletons while fetching
- Empty state if no articles

**Feeds (pages/Feeds.tsx:19):**
- List RSS feeds
- Add new feed (auth required)
- Delete existing feeds
- Uses MSAL for auth gating

**Chat (pages/Chat.tsx):**
- AI chat interface
- Send messages about articles
- Displays conversation history

**Settings (pages/Settings.tsx):**
- User preferences
- Theme selection
- Notification settings

**Onboarding (pages/Onboarding.tsx):**
- First-time user setup
- Feed selection
- Preference configuration

### 5. UI Component Library

**shadcn/ui Integration:**

49 components from shadcn/ui in `src/components/ui/`:
- Forms: Input, Textarea, Select, Checkbox, Switch, Radio
- Feedback: Toast, Alert, Dialog, Popover
- Navigation: Tabs, Accordion, Menubar, Sidebar
- Layout: Card, Separator, Resizable, Scroll Area
- Data: Table, Chart (recharts integration)
- Overlays: Sheet, Drawer, Tooltip, Hover Card
- And more...

**Custom Components:**

- `ArticleCard` - News article display
- `GlassCard` - Glassmorphism styled card
- `LoadingSkeleton` - Loading state placeholders
- `Sidebar` - App navigation
- `Layout` - Page wrapper with sidebar

### 6. Styling System

**Tailwind CSS:**
- Utility-first styling
- Custom theme in `tailwind.config.ts`
- Dark mode support (`next-themes`)

**Design Tokens:**
```ts
// tailwind.config.ts
colors: {
  primary: {...},
  accent: {...},
  background: {...},
  foreground: {...},
  // ... more
}
```

**Animations:**
- Fade in, slide up, shimmer
- Configured in `tailwind.config.ts`

## Environment Configuration

**Required variables (.env):**
```env
VITE_APP_ENTRA_CLIENT_ID=xxx
VITE_APP_ENTRA_TENANT_ID=xxx
VITE_APP_ENTRA_REDIRECT_URI=http://localhost:5173
VITE_APP_ENTRA_API_SCOPE=api://xxx/access_as_user
VITE_API_BASE_URL=http://localhost:8000  # (not yet in use)
```

**Vite Environment Variables:**
- Prefix with `VITE_` to expose to client
- Access via `import.meta.env.VITE_*`

## Development Workflow

### Start Dev Server
```bash
cd packages/web-app
npm run dev
# Opens http://localhost:5173
```

### Build for Production
```bash
npm run build           # Production build
npm run build:dev       # Development build
npm run preview         # Preview production build
```

### Linting
```bash
npm run lint
```

## Important Decisions

### Decision 1: Vite over Create React App
**Rationale:** Vite offers significantly faster HMR, better dev experience, optimized builds with esbuild.

**Benefits:**
- Instant server start
- Lightning-fast HMR
- Native ES modules in dev
- Smaller production bundles

### Decision 2: shadcn/ui Component Library
**Rationale:** Not a dependency, components are copied into project (full control), built on Radix UI (accessibility), Tailwind-based (consistent styling).

**Benefits:**
- Full ownership of code
- Easy customization
- Great accessibility (Radix)
- TypeScript native
- No black box dependencies

### Decision 3: TanStack Query for Server State
**Rationale:** Better than useState + useEffect for API data. Handles caching, refetching, loading states, error handling.

**Benefits:**
- Automatic caching
- Background refetching
- Optimistic updates
- Less boilerplate

### Decision 4: React Router DOM (not Next.js)
**Rationale:** SPA (not SSR), simpler deployment, no backend needed for routing, Vite optimized for SPAs.

**Alternatives considered:** Next.js - rejected due to overkill for this use case.

## Integration with Backend

**API Base URL:** `http://localhost:8000` (currently hardcoded in api.ts)

**Authentication Flow:**
1. Frontend: User logs in via MSAL
2. Frontend: Gets access token
3. Frontend: Sends token in `Authorization: Bearer <token>` header
4. Backend: Validates token with Entra ID
5. Backend: Returns protected data

**API Endpoints Used:**
- `GET /api/articles` - Article list
- `GET /api/articles/:id` - Single article
- `GET /api/rss-feeds` - User's feeds
- `POST /api/rss-feeds` - Add feed
- `DELETE /api/rss-feeds/:id` - Remove feed
- `POST /api/chat` - AI chat message

## Usage Examples

### Creating a New Page

1. **Create page file:**
```tsx
// src/pages/MyNewPage.tsx
import { GlassCard } from "@/components/GlassCard";

const MyNewPage = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">My New Page</h1>
      <GlassCard>
        <p>Content here</p>
      </GlassCard>
    </div>
  );
};

export default MyNewPage;
```

2. **Add route:**
```tsx
// src/App.tsx
import MyNewPage from "./pages/MyNewPage";

<Route path="/my-page" element={<Layout><MyNewPage /></Layout>} />
```

3. **Add nav item:**
```tsx
// src/components/Sidebar.tsx
<NavLink to="/my-page" icon={Icon}>My Page</NavLink>
```

### Adding API Function

```tsx
// src/lib/api.ts
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export const getMyData = async () => {
  const response = await axios.get(`${API_BASE}/api/my-data`);
  return response.data;
};
```

### Using in Component

```tsx
import { useEffect, useState } from 'react';
import { getMyData } from '@/lib/api';

const MyComponent = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    getMyData().then(setData);
  }, []);

  return <div>{data ? JSON.stringify(data) : 'Loading...'}</div>;
};
```

## Testing

**Current state:** No tests implemented yet.

**Recommended approach:**
- Vitest for unit tests
- React Testing Library for component tests
- Playwright for E2E tests

**Test files structure:**
```
src/
├── pages/
│   ├── Dashboard.tsx
│   └── Dashboard.test.tsx
├── components/
│   ├── ArticleCard.tsx
│   └── ArticleCard.test.tsx
```

## Common Issues

### Issue: CORS errors when calling backend

**Cause:** Backend CORS not configured for frontend URL.

**Solution:** Ensure backend allows `http://localhost:5173`:
```python
# packages/backend-api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Environment variables not loading

**Cause:** Missing `VITE_` prefix or not restarted dev server.

**Solution:**
1. Prefix all variables with `VITE_`
2. Restart `npm run dev`

### Issue: Tailwind classes not working

**Cause:** PostCSS/Tailwind not configured or syntax error.

**Solution:**
1. Check `postcss.config.js` exists
2. Verify `@tailwind` directives in `index.css`
3. Check for class name typos

### Issue: Auth not working

**Cause:** MSAL config incorrect or Azure Portal not configured.

**Solution:** See [entra-id-authentication.md](.ai/knowledge/features/entra-id-authentication.md) for full setup.

## Performance Considerations

**Bundle Size:**
- Current: ~500KB gzipped (with all shadcn components)
- Can reduce by removing unused UI components
- Tree-shaking enabled by Vite

**Code Splitting:**
- Route-based splitting with React Router
- Lazy load pages: `const Dashboard = lazy(() => import('./pages/Dashboard'))`

**Optimizations:**
- Vite build optimizations (enabled by default)
- TanStack Query caching reduces API calls
- Image optimization (consider adding next/image equivalent)

## Security Considerations

1. **XSS Protection:**
   - React escapes strings by default
   - Avoid `dangerouslySetInnerHTML`

2. **CORS:**
   - Backend enforces CORS
   - Only allow trusted origins in production

3. **Authentication:**
   - Tokens stored in localStorage (see auth docs for risks)
   - Consider httpOnly cookies for production

4. **Environment Variables:**
   - Never commit `.env` to git
   - Use different values for dev/staging/prod

## Related Knowledge

- [Entra ID Authentication](../features/entra-id-authentication.md) - Auth integration
- [FastAPI Backend](../backend/backend-api-structure.md) - *(not yet created)* - API integration

## Future Enhancements

- [ ] Add comprehensive test suite (Vitest + RTL + Playwright)
- [ ] Implement progressive web app (PWA) features
- [ ] Add offline support with service workers
- [ ] Optimize bundle size (lazy load UI components)
- [ ] Add performance monitoring (Web Vitals)
- [ ] Implement error boundary components
- [ ] Add accessibility audit and improvements
- [ ] Create component storybook
- [ ] Add E2E test coverage
- [ ] Implement API response caching strategy
- [ ] Add internationalization (i18n)
- [ ] Create design system documentation

## Build & Deployment

**Production Build:**
```bash
npm run build
# Output: dist/
```

**Preview Build:**
```bash
npm run preview
# Serves dist/ on http://localhost:4173
```

**Deployment Options:**
1. **Vercel** - Recommended for Vite apps
2. **Netlify** - Static site hosting
3. **Azure Static Web Apps** - Integrated with Azure ecosystem
4. **S3 + CloudFront** - AWS solution

**Deployment Checklist:**
- [ ] Update `.env` with production values
- [ ] Configure backend CORS for production domain
- [ ] Update Azure Entra ID redirect URIs
- [ ] Enable HTTPS
- [ ] Set up CI/CD pipeline
- [ ] Configure CDN for static assets

## Notes

- **shadcn/ui:** All 49 components are committed to repo (not installed as dependency)
- **Monorepo Integration:** Web app shares root-level git but has independent package.json
- **Favicon:** Multiple formats available (SVG, ICO) with light/dark mode variants
