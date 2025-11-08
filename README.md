# UP2D8 - Personal News Digest Platform

A full-stack monorepo containing the backend API, Azure Functions, and React Native mobile app for personalized news digests and information management.

## Architecture Overview

```
┌─────────────────────┐
│  React Native App   │ (Mobile Client - iOS/Android)
│  packages/mobile-app│
└──────────┬──────────┘
           │ REST API
           ↓
┌─────────────────────┐      ┌──────────────────────┐
│  Backend API        │◄─────┤  Azure Functions     │
│  packages/backend-api│      │  packages/functions  │
│  (FastAPI)          │      │  (Background Tasks)  │
└──────────┬──────────┘      └──────────┬───────────┘
           │                             │
           └─────────────────────────────┘
                        ↓
              ┌──────────────────┐
              │  Cosmos DB       │
              │  (MongoDB API)   │
              └──────────────────┘
```

## Packages

### 📱 Mobile App (`packages/mobile-app/`)
React Native mobile application (iOS & Android)
- **Tech**: React Native 0.82.1, TypeScript, React Navigation 7.x
- **Features**: News browsing, AI chat, personalized digests, offline support
- **Docs**: [Mobile App README](./packages/mobile-app/README.md)

### 🔧 Backend API (`packages/backend-api/`)
FastAPI REST API providing core services
- **Tech**: Python, FastAPI, MongoDB, Azure Key Vault, Google Gemini
- **Endpoints**: Articles, Users, RSS Feeds, Chat, Analytics, Feedback
- **Docs**: [Backend API README](./docs/development/backend-api-readme.md)

### ⚡ Azure Functions (`packages/functions/`)
Serverless background tasks and automation
- **Tech**: Python, Azure Functions, LangChain, Playwright
- **Functions**: RSS scraping, newsletter generation, web crawling
- **Docs**: [Functions README](./docs/development/functions-readme.md)

### 🔀 Shared (`packages/shared/`)
Common types, schemas, and utilities shared across packages
- **Contents**: TypeScript types, Pydantic schemas, constants, utilities
- **Docs**: [Shared Package README](./packages/shared/README.md)

## Quick Start

### Prerequisites

- **Node.js** >= 18
- **Python** >= 3.10
- **npm** >= 9
- **React Native** development environment (for mobile)
- **Azure CLI** (for Functions deployment)

### One-Command Setup

```bash
./scripts/setup-dev.sh
```

This will:
1. Install mobile app dependencies
2. Create Python virtual environments for backend and functions
3. Install all Python dependencies

### Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
```

See [.env.example](./.env.example) for all available options.

### Running Services

**Backend API:**
```bash
npm run backend:dev
# Backend available at http://localhost:8000
```

**Mobile App (iOS):**
```bash
npm run mobile:ios
```

**Mobile App (Android):**
```bash
npm run mobile:android
```

**Azure Functions (local):**
```bash
npm run functions:dev
```

### Testing

**Run all tests:**
```bash
./scripts/test-all.sh
# or
npm run test:all
```

**Test individual packages:**
```bash
npm run test:backend
npm run test:functions
npm run test:mobile
```

## Development Workflow

1. **Setup** - Run `./scripts/setup-dev.sh` once
2. **Configure** - Copy `.env.example` to `.env` and configure
3. **Start Backend** - Run `npm run backend:dev` for API
4. **Start Mobile** - Run `npm run mobile:ios` or `mobile:android`
5. **Develop** - Make changes, tests run automatically
6. **Test** - Run `npm run test:all` before committing
7. **Document** - Run `/capture` to update AI knowledge base

## Documentation

### Development
- [Backend Setup Guide](./docs/development/backend-setup.md)
- [Backend API README](./docs/development/backend-api-readme.md)
- [Functions README](./docs/development/functions-readme.md)

### Architecture
- [Integration Architecture](./docs/architecture/integration-architecture.md)

### Deployment
- [Functions Deployment Guide](./docs/deployment/functions-deployment.md)

### AI Knowledge Base
- [INDEX.md](./.ai/INDEX.md) - Knowledge base dashboard
- [GUIDE.md](./.ai/GUIDE.md) - Navigation guide
- [claude.md](./claude.md) - AI assistant orientation

## Tech Stack

### Backend
- **API**: FastAPI (Python)
- **Database**: MongoDB (Azure Cosmos DB)
- **AI**: Google Gemini API
- **Security**: Azure Key Vault (Managed Identity)

### Functions
- **Runtime**: Azure Functions (Python)
- **AI**: LangChain, Google Gemini
- **Web**: Playwright (browser automation)
- **Scheduling**: Timer triggers, Durable Functions

### Mobile
- **Framework**: React Native 0.82.1
- **Language**: TypeScript
- **Navigation**: React Navigation 7.x
- **State**: Zustand
- **UI**: Custom theme system with dark mode

## Monorepo Structure

```
up2d8/
├── packages/
│   ├── backend-api/     # FastAPI REST API
│   ├── functions/       # Azure Functions
│   ├── mobile-app/      # React Native app
│   └── shared/          # Common code
├── infrastructure/      # Deployment configs
├── docs/               # Consolidated documentation
├── scripts/            # Development scripts
├── .ai/                # AI knowledge base
├── package.json        # Root workspace config
└── pyproject.toml      # Python monorepo config
```

## NPM Scripts

```bash
npm run mobile              # Start mobile Metro bundler
npm run mobile:ios          # Run iOS app
npm run mobile:android      # Run Android app
npm run backend:dev         # Start backend API
npm run functions:dev       # Start Azure Functions locally
npm run test:all            # Run all tests
npm run test:backend        # Test backend only
npm run test:functions      # Test functions only
npm run test:mobile         # Test mobile only
```

## Contributing

1. Follow the coding standards in `.ai/preferences/`
2. Run tests before committing
3. Use `/capture` to document new features
4. Update knowledge base with significant changes

## Migration History

This monorepo was created on 2025-11-08 by consolidating three repositories:
- `UP2D8-BACKEND` → `packages/backend-api/`
- `UP2D8-Function` → `packages/functions/`
- `up2d8-frontend` → `packages/mobile-app/`

All original repositories are tagged with `archive-pre-monorepo-2025-01-08` for reference.

## License

MIT
