# 📱 iOS Mobile App Rebuild Plan

**Project:** UP2D8 Mobile App Rebuild
**Goal:** Replace existing React Native mobile app with new iOS app matching web app design & functionality
**Started:** 2025-11-10
**Status:** 🟡 IN PROGRESS

---

## 📋 Executive Summary

**What We're Building:**
A new iOS mobile app that matches the web app's design, features, and user experience.

**Why We're Rebuilding:**
- Current mobile app missing core features (Dashboard, Feeds Management)
- Design not fully aligned with web app
- Placeholder functionality throughout
- No authentication implementation
- Subscription page not aligned with web vision

**Success Criteria:**
- ✅ Feature parity with web app
- ✅ 95%+ visual similarity to web app
- ✅ Azure authentication working
- ✅ All core features functional
- ✅ Smooth 60fps performance
- ✅ iOS-native experience

---

## 🎯 Phase Overview

| Phase | Focus | Status | Duration | Dependencies |
|-------|-------|--------|----------|--------------|
| **Phase 1.1** | Shared Packages | ✅ COMPLETE | 1 day | None |
| **Phase 1.2** | Initialize Mobile App | ✅ COMPLETE | 1 day | Phase 1.1 |
| **Phase 1.3** | Design System Setup | 🟡 NEXT | 1-2 days | Phase 1.2 |
| **Phase 2** | Core Components | ⏸️ PENDING | 1 week | Phase 1 |
| **Phase 3** | Screen Development | ⏸️ PENDING | 2-3 weeks | Phase 2 |
| **Phase 4** | Navigation Structure | ⏸️ PENDING | 3 days | Phase 3 |
| **Phase 5** | Feature Parity | ⏸️ PENDING | 1-2 weeks | Phase 4 |
| **Phase 6** | Polish & Optimization | ⏸️ PENDING | 1 week | Phase 5 |
| **Phase 7** | Migration & Cleanup | ⏸️ PENDING | 2-3 days | Phase 6 |

**Estimated Total Timeline:** 6-8 weeks

---

## 🔧 Technology Stack

### New Mobile App Stack
```json
{
  "framework": "React Native (latest stable)",
  "language": "TypeScript 5.8+",
  "navigation": "React Navigation v7 (Tab + Stack)",
  "state_management": {
    "server": "React Query (@tanstack/react-query)",
    "client": "Zustand"
  },
  "auth": "Azure MSAL for React Native",
  "forms": "React Hook Form + Zod validation",
  "icons": "Lucide React Native (matches web)",
  "styling": "StyleSheet with shared design tokens",
  "ui_effects": "react-native-blur, react-native-linear-gradient",
  "notifications": "react-native-toast-message"
}
```

### Shared Packages Architecture
```
/packages/
  ├── mobile-app-new/     # New iOS app (will replace mobile-app)
  ├── web-app/            # Existing web app (reference design)
  ├── shared-types/       # TypeScript interfaces, models
  ├── shared-api/         # API client, auth logic
  ├── shared-theme/       # Design tokens
  └── shared-utils/       # Common utilities
```

---

## 📐 Design System Alignment

### Color Palette (Exact Match to Web)
```javascript
{
  primary: '#4169E1',      // Royal Blue (HSL 221, 83%, 53%)
  accent: '#A855F7',       // Vibrant Purple (HSL 262, 83%, 58%)
  gradient: ['#4169E1', '#7C3AED', '#A855F7'],

  light: {
    background: ['#EBF2FF', '#FAF5FF', '#FCE7F3'], // Blue-50 → Purple-50 → Pink-50
    surface: 'rgba(255, 255, 255, 0.4)',
    border: 'rgba(255, 255, 255, 0.2)',
    text: {
      primary: '#0A0A0A',
      secondary: '#525252',
      tertiary: '#A3A3A3',
    }
  },

  dark: {
    background: ['#0A0A0A', '#1E1B4B', '#581C87'], // Gray-900 → Blue-900 → Purple-900
    surface: 'rgba(255, 255, 255, 0.05)',
    border: 'rgba(255, 255, 255, 0.1)',
    text: {
      primary: '#FAFAFA',
      secondary: '#A3A3A3',
      tertiary: '#525252',
    }
  }
}
```

### Typography Scale (Web → Mobile Conversion)
```javascript
{
  fontSize: {
    xs: 12,    // 0.75rem
    sm: 14,    // 0.875rem
    base: 16,  // 1rem
    lg: 18,    // 1.125rem
    xl: 20,    // 1.25rem
    '2xl': 24, // 1.5rem
    '3xl': 30, // 1.875rem
    '4xl': 36, // 2.25rem
    '5xl': 48, // 3rem
  },
  fontWeight: {
    regular: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
  lineHeight: {
    tight: 1.2,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2,
  }
}
```

### Spacing System (Tailwind → React Native)
```javascript
{
  spacing: {
    0: 0,
    1: 4,    // 0.25rem
    2: 8,    // 0.5rem
    3: 12,   // 0.75rem
    4: 16,   // 1rem
    5: 20,   // 1.25rem
    6: 24,   // 1.5rem
    8: 32,   // 2rem
    10: 40,  // 2.5rem
    12: 48,  // 3rem
    16: 64,  // 4rem
    20: 80,  // 5rem
    24: 96,  // 6rem
  }
}
```

### Border Radius
```javascript
{
  borderRadius: {
    none: 0,
    sm: 4,
    md: 6,
    lg: 8,
    xl: 12,
    '2xl': 16,
    '3xl': 24,
    full: 9999,
  }
}
```

---

## 📱 Screen Structure

### Web App Pages → Mobile Screens Mapping

| Web App Route | Mobile Screen | Tab | Status | Notes |
|--------------|---------------|-----|--------|-------|
| `/` (Dashboard) | DashboardScreen | Home | ⏸️ TO BUILD | Stats, featured articles, recent articles |
| `/feeds` | FeedsScreen | Feeds | ⏸️ TO BUILD | RSS management, AI suggestions |
| `/feeds/add` | AddFeedScreen | Feeds Stack | ⏸️ TO BUILD | Add new RSS feed |
| `/feeds/:id` | EditFeedScreen | Feeds Stack | ⏸️ TO BUILD | Edit existing feed |
| `/chat` | ChatScreen | Chat | ✅ EXISTS (enhance) | Keep existing, align styling |
| `/settings` | SettingsScreen | Settings | ✅ EXISTS (enhance) | Make functional, add preferences |
| `/onboarding` | OnboardingScreen | Modal | ⏸️ TO BUILD | First-time user flow |
| N/A (Auth) | LoginScreen | Auth Stack | ⏸️ TO BUILD | Azure MSAL authentication |

### New Bottom Tab Structure
```
┌─────────────────────────────────┐
│    Home    Feeds    Chat   ⚙️   │
└─────────────────────────────────┘
```

**Tabs:**
1. **Home** (🏠) → DashboardScreen
2. **Feeds** (📡) → FeedsScreen
3. **Chat** (💬) → ChatScreen
4. **Settings** (⚙️) → SettingsScreen

**Removed:**
- Subscribe tab (not in web app scope)

---

## 🗂️ Detailed Phase Breakdown

### ✅ Phase 1: Foundation & Setup (1-2 weeks)
**Status:** 🟡 IN PROGRESS

#### 1.1 Create Shared Packages
- [ ] `packages/shared-types/` - TypeScript interfaces
  - [ ] User types (User, UserPreferences)
  - [ ] Feed types (Feed, Article)
  - [ ] Chat types (Message, Conversation)
  - [ ] API response types
- [ ] `packages/shared-api/` - API client
  - [ ] Base API client (Axios/Fetch)
  - [ ] Auth interceptors
  - [ ] Feed endpoints
  - [ ] Chat endpoints
  - [ ] User endpoints
- [ ] `packages/shared-theme/` - Design tokens
  - [ ] Color palette
  - [ ] Typography scale
  - [ ] Spacing system
  - [ ] Border radius
  - [ ] Shadows/elevation
- [ ] `packages/shared-utils/` - Common utilities
  - [ ] Date formatters
  - [ ] Validators (Zod schemas)
  - [ ] String helpers
  - [ ] URL helpers

#### 1.2 Initialize New Mobile App
- [ ] Create new React Native project
  - [ ] Set up TypeScript configuration
  - [ ] Configure Metro bundler
  - [ ] Set up iOS project in Xcode
- [ ] Install core dependencies
  - [ ] React Navigation
  - [ ] React Query
  - [ ] Zustand
  - [ ] Azure MSAL React Native
  - [ ] React Hook Form + Zod
  - [ ] Lucide React Native
- [ ] Configure development environment
  - [ ] ESLint + Prettier
  - [ ] TypeScript strict mode
  - [ ] Path aliases (@components, @screens, etc.)

#### 1.3 Port Design System
- [ ] Convert web Tailwind config to RN tokens
- [ ] Create theme provider
- [ ] Set up light/dark mode
- [ ] Create color system
- [ ] Create typography system
- [ ] Create spacing system

---

### ⏸️ Phase 2: Core Components (1 week)
**Status:** PENDING
**Dependencies:** Phase 1 complete

#### 2.1 UI Components (Match Web Shadcn Components)
- [ ] `GlassCard` - Glassmorphism card with blur
- [ ] `GlassButton` - Primary, secondary, outline, ghost variants
- [ ] `Input` - Text input with validation states
- [ ] `Avatar` - User profile pictures with fallback
- [ ] `Badge` - Status badges, tags, labels
- [ ] `Dialog` / `BottomSheet` - Modal dialogs
- [ ] `Switch` - Toggle switches
- [ ] `Skeleton` - Loading placeholders
- [ ] `Toast` - Notification toasts
- [ ] `Separator` - Divider lines
- [ ] `ScrollArea` - Scrollable container

#### 2.2 Layout Components
- [ ] `SafeAreaLayout` - Screen wrapper with safe areas
- [ ] `Header` - Screen header with gradient
- [ ] `TabBar` - Custom bottom tab bar (glass effect)
- [ ] `EmptyState` - Empty views with illustrations
- [ ] `ErrorBoundary` - Error handling UI
- [ ] `LoadingOverlay` - Full-screen loading

#### 2.3 Feature Components
- [ ] `ArticleCard` - Article preview card
- [ ] `FeedCard` - RSS feed card
- [ ] `StatCard` - Dashboard stats card
- [ ] `MessageBubble` - Chat message bubble
- [ ] `CategoryChip` - Filter chips
- [ ] `SearchBar` - Search input with icon

---

### ⏸️ Phase 3: Screen Development (2-3 weeks)
**Status:** PENDING
**Dependencies:** Phase 2 complete

#### 3.1 Dashboard Screen (NEW)
- [ ] Layout structure
- [ ] Stats cards (feeds, articles, read count)
- [ ] Featured articles section
- [ ] Recent articles list
- [ ] Pull to refresh
- [ ] Loading states (skeletons)
- [ ] Empty states
- [ ] Error handling

#### 3.2 Feeds Screen (NEW)
- [ ] Feed list with categories
- [ ] Floating "Add Feed" button
- [ ] Search bar
- [ ] Category filters
- [ ] Swipe actions (edit, delete)
- [ ] Pull to refresh
- [ ] Empty state
- [ ] Loading skeletons

#### 3.3 Add/Edit Feed Screens (NEW)
- [ ] Feed URL input with validation
- [ ] Category selector
- [ ] AI feed suggestions dialog
- [ ] Save/cancel buttons
- [ ] Form validation
- [ ] Loading states
- [ ] Error handling

#### 3.4 Chat Screen (ENHANCE EXISTING)
- [ ] Port existing chat UI
- [ ] Match web app message styling
- [ ] Add conversation persistence
- [ ] Add clear chat button
- [ ] Improve source link rendering
- [ ] Add typing indicators
- [ ] Character count display
- [ ] Error state improvements

#### 3.5 Settings Screen (ENHANCE EXISTING)
- [ ] Make all items functional (remove placeholders)
- [ ] Theme switcher (keep existing)
- [ ] Notification preferences dialog
- [ ] Account settings screen
- [ ] Content preferences dialog
- [ ] About/version info
- [ ] Privacy policy link
- [ ] Terms of service link

#### 3.6 Onboarding Screen (NEW)
- [ ] Welcome screen
- [ ] Topic selection (multi-select chips)
- [ ] API integration (save preferences)
- [ ] Skip option
- [ ] Completion transition to dashboard
- [ ] Progress indicator

#### 3.7 Authentication Screens (NEW)
- [ ] Login screen (Azure MSAL button)
- [ ] Loading screen during auth
- [ ] Error screen (auth failed)
- [ ] Logout confirmation dialog
- [ ] Protected route wrapper

---

### ⏸️ Phase 4: Navigation Structure (3 days)
**Status:** PENDING
**Dependencies:** Phase 3 complete

#### 4.1 Bottom Tab Navigator
- [ ] Create TabNavigator with 4 tabs
- [ ] Custom TabBar component (glass effect)
- [ ] Active tab indicator
- [ ] Tab icons (Lucide)
- [ ] Tab labels
- [ ] Badge support (notification counts)

#### 4.2 Stack Navigators
- [ ] Home Stack (Dashboard → Article Detail)
- [ ] Feeds Stack (List → Add → Edit)
- [ ] Chat Stack (single screen)
- [ ] Settings Stack (Settings → Sub-screens)
- [ ] Auth Stack (Login → Register → Forgot Password)

#### 4.3 Root Navigator
- [ ] Auth flow (logged out)
- [ ] App flow (logged in)
- [ ] Onboarding flow (first time)
- [ ] Deep linking configuration
- [ ] Navigation type safety

---

### ⏸️ Phase 5: Feature Parity (1-2 weeks)
**Status:** PENDING
**Dependencies:** Phase 4 complete

#### 5.1 API Integration
- [ ] Use shared API package
- [ ] Implement React Query hooks
  - [ ] `useFeeds()` - Get all feeds
  - [ ] `useAddFeed()` - Add new feed
  - [ ] `useUpdateFeed()` - Update feed
  - [ ] `useDeleteFeed()` - Delete feed
  - [ ] `useArticles()` - Get articles
  - [ ] `useChatMessages()` - Chat history
  - [ ] `useSendMessage()` - Send chat message
  - [ ] `useUserProfile()` - User data
- [ ] Add auth interceptors (Azure tokens)
- [ ] Error handling & retry logic
- [ ] Offline mode support
- [ ] Cache management

#### 5.2 Data Management
- [ ] React Query setup
- [ ] Zustand stores (UI state)
- [ ] AsyncStorage persistence
- [ ] Cache invalidation
- [ ] Optimistic updates

#### 5.3 Authentication Flow
- [ ] Azure MSAL configuration
- [ ] Login flow
- [ ] Logout flow
- [ ] Token refresh
- [ ] Protected routes
- [ ] Auth context provider
- [ ] Session persistence

#### 5.4 Onboarding Integration
- [ ] First-time user detection
- [ ] Topic selection API
- [ ] Skip onboarding
- [ ] Persist onboarding status

---

### ⏸️ Phase 6: Polish & Optimization (1 week)
**Status:** PENDING
**Dependencies:** Phase 5 complete

#### 6.1 iOS-Specific Features
- [ ] Haptic feedback (light, medium, success, error)
- [ ] Native share sheet (share articles)
- [ ] Safari View Controller (in-app browser)
- [ ] Push notifications setup
- [ ] Push notification permissions
- [ ] Biometric authentication (Face ID / Touch ID)
- [ ] Dynamic type support (accessibility)
- [ ] VoiceOver accessibility labels
- [ ] Dark mode support (system-based)

#### 6.2 Performance Optimization
- [ ] FlatList virtualization (article lists)
- [ ] Image lazy loading
- [ ] Image caching
- [ ] Code splitting with React.lazy
- [ ] Bundle size analysis
- [ ] Startup performance (measure)
- [ ] Memory leak detection
- [ ] Frame rate monitoring (60fps)

#### 6.3 Testing
- [ ] Unit tests (Jest)
  - [ ] Component tests
  - [ ] Utility function tests
  - [ ] Hook tests
- [ ] Integration tests
  - [ ] Navigation tests
  - [ ] API integration tests
  - [ ] Auth flow tests
- [ ] E2E tests (Detox)
  - [ ] Login flow
  - [ ] Add feed flow
  - [ ] Chat flow
- [ ] Manual QA checklist

#### 6.4 Accessibility
- [ ] Accessibility labels on all interactive elements
- [ ] Minimum 44x44pt touch targets
- [ ] Color contrast ratios (WCAG AA)
- [ ] VoiceOver support
- [ ] Dynamic type support
- [ ] Reduce motion support

---

### ⏸️ Phase 7: Migration & Cleanup (2-3 days)
**Status:** PENDING
**Dependencies:** Phase 6 complete

#### 7.1 Migration Tasks
- [ ] Data migration script (if needed)
- [ ] Update package.json dependencies
- [ ] Update iOS build configuration
- [ ] Update environment variables
- [ ] Update CI/CD pipelines (GitHub Actions)
- [ ] Update app icon & splash screen
- [ ] Update app name & bundle ID

#### 7.2 Remove Old Mobile App
- [ ] Backup old app code (git tag)
- [ ] Delete `/packages/mobile-app/` directory
- [ ] Rename `/packages/mobile-app-new/` to `/packages/mobile-app/`
- [ ] Update monorepo references
- [ ] Update documentation
- [ ] Clean up unused dependencies
- [ ] Update README files

#### 7.3 Documentation
- [ ] Update README with new setup instructions
- [ ] Document component API
- [ ] Document navigation structure
- [ ] Document API hooks
- [ ] Document environment variables
- [ ] Document build process
- [ ] Document deployment process

---

## 🔄 Component Mapping: Web → Mobile

| Web Component (Shadcn/UI) | Mobile Component | Implementation Notes |
|---------------------------|------------------|----------------------|
| `<Card>` | `<GlassCard>` | Match blur intensity, gradient borders |
| `<Button variant="default">` | `<GlassButton variant="primary">` | Gradient background |
| `<Button variant="outline">` | `<GlassButton variant="outline">` | Transparent with border |
| `<Button variant="ghost">` | `<GlassButton variant="ghost">` | No background, text only |
| `<Input>` | `<Input>` | Match border, focus states, validation |
| `<Dialog>` | `<BottomSheet>` | Mobile uses bottom sheets |
| `<Avatar>` | `<Avatar>` | Circular image with fallback initials |
| `<Badge>` | `<Badge>` | Small pill-shaped labels |
| `<Skeleton>` | `<Skeleton>` | Shimmer loading animation |
| `<Toaster>` | `<Toast>` | react-native-toast-message |
| `<Switch>` | `<Switch>` | Native RN Switch |
| `<Select>` | `<BottomSheet>` or native `<Picker>` | iOS-native picker |
| `<Tabs>` | `<TabView>` | Horizontal swipeable tabs |
| `<ScrollArea>` | `<ScrollView>` | Native scrolling |
| `<Separator>` | `<Separator>` | Horizontal divider line |

---

## 📊 Success Metrics

### Feature Parity
- [ ] All web app features implemented on mobile
- [ ] Dashboard with stats cards
- [ ] Full RSS feed CRUD operations
- [ ] AI chat with sources
- [ ] Azure authentication
- [ ] Onboarding flow
- [ ] Settings with preferences

### Design Match
- [ ] 95%+ visual similarity to web app
- [ ] Exact color palette match
- [ ] Typography scale alignment
- [ ] Consistent spacing
- [ ] Glassmorphism effect matches
- [ ] Gradient usage matches

### Performance
- [ ] App launches in < 2 seconds
- [ ] Smooth 60fps animations
- [ ] No memory leaks
- [ ] Efficient list rendering (FlatList)
- [ ] Optimized bundle size

### Code Quality
- [ ] 80%+ test coverage
- [ ] TypeScript strict mode
- [ ] ESLint passing
- [ ] No console warnings
- [ ] Documentation complete

### User Experience
- [ ] Haptic feedback on interactions
- [ ] Loading states everywhere
- [ ] Error handling everywhere
- [ ] Empty states with helpful messages
- [ ] Accessibility labels
- [ ] VoiceOver support

---

## 📝 Progress Log

### 2025-11-10 - Phase 1.1 Complete ✅

**Foundation & Setup - Day 1**

- ✅ Created comprehensive rebuild plan document
- ✅ Analyzed web app vs mobile app (detailed comparison)
- ✅ Created 4 shared packages:
  - ✅ **@up2d8/shared-types** - All TypeScript interfaces (User, Feed, Article, Chat, Topic, API)
  - ✅ **@up2d8/shared-theme** - Complete design system (colors, typography, spacing, shadows, glass effects)
  - ✅ **@up2d8/shared-api** - Unified API client with all endpoints
  - ✅ **@up2d8/shared-utils** - Common utilities (date, string, array, validators)
- ✅ Updated monorepo configuration (workspaces + npm scripts)
- ✅ Installed dependencies for all packages
- ✅ Built all shared packages successfully
- ✅ Converted web app HSL colors to React Native hex/rgba (perfect match)
- ✅ Created Phase 1 summary document

**Metrics:**
- Files created: 30+
- Lines of code: ~2,500
- Type definitions: 25+
- API endpoints: 25+
- Utility functions: 30+
- Design tokens: 100+

**Next:** Phase 1.2 - Initialize React Native project

---

### 2025-11-10 - Phase 1.2 Complete ✅

**Initialize React Native Project - Day 1**

- ✅ Created new React Native project structure (`packages/mobile-app-new`)
- ✅ Configured TypeScript with strict mode and path aliases
- ✅ Configured Metro bundler for monorepo (watches shared packages)
- ✅ Configured Babel with module resolver for path aliases
- ✅ Created package.json with all dependencies:
  - React Native 0.76.1
  - React Navigation v7
  - React Query
  - Zustand
  - Lucide icons
  - React Hook Form + Zod
- ✅ Created ThemeProvider using @up2d8/shared-theme
- ✅ Created RootNavigator with placeholder screen
- ✅ Created App.tsx with providers (SafeArea, Query, Theme)
- ✅ Configured ESLint, Prettier, .gitignore
- ✅ Updated monorepo workspaces and scripts
- ✅ Created comprehensive README

**Project Structure:**
```
mobile-app-new/
├── src/
│   ├── components/{ui,features,layout}/
│   ├── screens/{Dashboard,Feeds,Chat,Settings,Onboarding,Auth}/
│   ├── navigation/
│   ├── context/
│   ├── hooks/
│   ├── utils/
│   └── theme/
├── App.tsx
├── index.js
└── Configuration files
```

**Key Features:**
- Full monorepo integration with shared packages
- Path aliases (@components, @screens, @shared/*)
- ThemeProvider with light/dark mode (uses shared-theme)
- Placeholder navigation working
- Ready for Phase 2 component development

**Metrics:**
- Files created: 15+
- Configuration files: 7
- Dependencies: 25+
- Development ready: ✅

**Next:** Phase 2 - Build core UI components

### [Future progress will be logged here]

---

## 🚨 Risks & Mitigation

| Risk | Impact | Mitigation Strategy |
|------|--------|---------------------|
| Azure MSAL not working on RN | HIGH | Test early, use community package, fallback to custom OAuth |
| Design system conversion issues | MEDIUM | Create token converter script, validate each token |
| Performance issues on older devices | MEDIUM | Test on iPhone 8, optimize FlatList, lazy load |
| API not ready for mobile | HIGH | Use mock data fallback, build UI first |
| Scope creep | MEDIUM | Stick to web app feature parity, defer "nice-to-haves" |

---

## 📚 Resources

### Documentation
- [React Navigation Docs](https://reactnavigation.org/)
- [React Query Docs](https://tanstack.com/query/latest)
- [Azure MSAL React Native](https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/lib/msal-react-native)
- [React Hook Form Docs](https://react-hook-form.com/)
- [Zod Docs](https://zod.dev/)

### Web App Reference Files
- `/packages/web-app/src/App.tsx` - Routing
- `/packages/web-app/src/components/Layout.tsx` - Layout structure
- `/packages/web-app/src/components/GlassCard.tsx` - Glass component
- `/packages/web-app/tailwind.config.ts` - Design tokens
- `/packages/web-app/src/lib/api.ts` - API client

### Current Mobile App Reference
- `/packages/mobile-app/src/theme/tokens.ts` - Design system
- `/packages/mobile-app/src/components/GlassCard.tsx` - Glass component
- `/packages/mobile-app/src/screens/ChatPage.tsx` - Chat UI (keep this)

---

## ✅ Next Steps

1. **Immediate (Today):**
   - Set up shared packages structure
   - Create shared-types package
   - Port design tokens from web app

2. **This Week:**
   - Complete Phase 1 (Foundation & Setup)
   - Initialize new mobile app project
   - Set up development environment

3. **Next Week:**
   - Start Phase 2 (Core Components)
   - Build GlassCard, GlassButton, Input components
   - Set up component Storybook (optional)

---

**Last Updated:** 2025-11-10
**Next Review:** Weekly or at phase completion
