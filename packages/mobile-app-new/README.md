# UP2D8 Mobile App (New)

**Status:** 🚧 In Development - Phase 1.2 Complete

This is the rebuilt iOS mobile app for UP2D8, designed to match the web app's design and functionality.

## Overview

This app is being rebuilt from scratch to:
- Match the web app's design system exactly (same colors, typography, spacing)
- Share code with the web app via monorepo shared packages
- Implement all web app features on mobile (Dashboard, Feeds, Chat, Settings)
- Use modern React Native best practices

## Tech Stack

- **React Native** 0.76.1
- **TypeScript** 5.8.3
- **Navigation:** React Navigation v7 (Bottom Tabs + Stack)
- **State Management:** React Query + Zustand
- **Styling:** React Native StyleSheet with shared design tokens
- **Icons:** Lucide React Native
- **Forms:** React Hook Form + Zod validation
- **UI Effects:** react-native-blur, react-native-linear-gradient

## Shared Packages

This app uses shared packages from the monorepo:

- `@up2d8/shared-types` - TypeScript interfaces
- `@up2d8/shared-api` - API client
- `@up2d8/shared-theme` - Design tokens (colors, typography, spacing)
- `@up2d8/shared-utils` - Utilities (date formatting, validation, etc.)

## Setup

### Prerequisites

- Node.js 18+
- npm 9+
- Xcode 14+ (for iOS)
- CocoaPods (for iOS dependencies)

### Installation

From the monorepo root:

```bash
# Install all dependencies
npm run mobile-new:install

# Install iOS pods
npm run mobile-new:pods
```

### Running the App

```bash
# Start Metro bundler
npm run mobile-new

# Run on iOS simulator
npm run mobile-new:ios

# Run on Android emulator
npm run mobile-new:android
```

## Project Structure

```
/src
├── components/        # Reusable UI components
│   ├── ui/           # Core UI components (GlassCard, Button, Input)
│   ├── features/     # Feature-specific components
│   └── layout/       # Layout components (Header, TabBar)
├── screens/          # App screens
│   ├── Dashboard/
│   ├── Feeds/
│   ├── Chat/
│   ├── Settings/
│   ├── Onboarding/
│   └── Auth/
├── navigation/       # Navigation configuration
├── context/          # React contexts (Theme, Auth)
├── hooks/            # Custom React hooks
├── utils/            # Utility functions
└── theme/            # Theme integration
```

## Development Status

### Phase 1.2 - Complete ✅

- [x] Project structure created
- [x] TypeScript configured with strict mode
- [x] Metro bundler configured for monorepo
- [x] Babel configured with path aliases
- [x] ThemeProvider integrated with shared-theme
- [x] Base navigation structure (placeholder)
- [x] ESLint & Prettier configured

### Next: Phase 2 - Core Components

Building UI components to match web app:
- GlassCard
- GlassButton
- Input
- Avatar
- Badge
- And more...

## Design System

The app uses the exact same design system as the web app:

**Colors:**
- Primary: `#4169E1` (Royal Blue)
- Accent: `#A855F7` (Vibrant Purple)
- Gradient: Blue → Purple

**Typography:**
- Font sizes: 12px to 48px
- 8pt grid spacing system

**Glass Effects:**
- Blur intensity: 10-40
- Semi-transparent backgrounds
- Gradient borders

All design tokens are imported from `@up2d8/shared-theme`.

## Scripts

- `npm start` - Start Metro bundler
- `npm run ios` - Run on iOS
- `npm run android` - Run on Android
- `npm test` - Run tests
- `npm run lint` - Lint code
- `npm run typecheck` - Type check

## Notes

- This app will eventually replace `packages/mobile-app` (old app)
- iOS-focused initially, Android support planned
- Design matches web app exactly (95%+ visual similarity goal)
- All shared packages must be built before running: `npm run shared:build`

## Documentation

See root-level documentation:
- `MOBILE_APP_REBUILD_PLAN.md` - Complete rebuild plan
- `PHASE_1_SUMMARY.md` - Phase 1 accomplishments

---

**Last Updated:** 2025-11-10
