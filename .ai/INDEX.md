# AI Knowledge Base Index - UP2D8 Monorepo

**Last Updated**: 2025-11-09
**Project Type**: Monorepo (Backend API + Azure Functions + Mobile App + Web App)
**Knowledge Items**: 12 features • 4 components • 4 patterns • 3 decisions

---

## 🆕 Recent Changes

### 2025-11-09 - Web Search, Swagger Organization, Mobile Responsiveness
- 🔍 **Added**: Web search grounding to AI chat using Google Search tool → [web-search-grounding.md](./knowledge/features/web-search-grounding.md)
- 🔄 **Migrated**: From google-generativeai to google-genai library for better tool support → [google-genai-migration.md](./knowledge/patterns/google-genai-migration.md)
- 📊 **Added**: Sources display in chat UI with clickable links (9-15 sources per query)
- 📚 **Organized**: Swagger API documentation with 9 category tags → [swagger-api-organization.md](./knowledge/features/swagger-api-organization.md)
- 📱 **Implemented**: Mobile responsiveness for web app (Safari/Chrome) → [mobile-responsive-web-app.md](./knowledge/features/mobile-responsive-web-app.md)
- 🎨 **Created**: MobileNav component with shadcn/ui Sheet for drawer navigation → [mobile-nav.md](./knowledge/components/mobile-nav.md)
- 🔐 **Fixed**: Onboarding authentication (401 error) - token acquisition before API call
- 🐛 **Fixed**: Chat API 500 errors through library migration and correct Tool syntax
- 📝 **Updated**: Chat response format to `{"status": "success", "model": "...", "reply": "...", "sources": []}`
- ⚡ **Optimized**: Mobile performance (reduced blur effects, 44px touch targets)
- 📐 **Added**: Responsive headers, icons, and spacing across all pages (Dashboard, Feeds, Chat, Settings)

### 2025-11-09 - RSS Feed Enhancements & Function App Integration
- ✅ **Added**: LLM-powered RSS feed suggestions with Google Search grounding → [rss-feed-suggestions.md](./knowledge/features/rss-feed-suggestions.md)
- 📂 **Implemented**: Category standardization for RSS feeds (backend-driven) → [category-standardization.md](./knowledge/features/category-standardization.md)
- 🔄 **Integrated**: Function App to scrape articles from stored RSS feeds → [function-app-rss-scraping.md](./knowledge/features/function-app-rss-scraping.md)

### 2025-11-09 - User Preferences, AI Suggestions & Feed Enhancements
- ✅ **Added**: User preferences management with dialogs → [user-preferences-management.md](./knowledge/features/user-preferences-management.md)
- 🎨 **Created**: PreferencesDialog component (topics + newsletter format) → [settings-dialogs.md](./knowledge/components/settings-dialogs.md)
- 🔔 **Created**: NotificationsDialog component (email settings + frequency) → [settings-dialogs.md](./knowledge/components/settings-dialogs.md)
- 🤖 **Added**: AI-powered topic suggestions with Gemini 2.0 Flash Experimental → [ai-topic-suggestions.md](./knowledge/features/ai-topic-suggestions.md)
- ✨ **Integrated**: Topic suggestions directly into Preferences dialog with search
- 🔍 **Added**: Feed search by title or URL with real-time filtering → [feed-search-and-categorization.md](./knowledge/features/feed-search-and-categorization.md)
- 📂 **Implemented**: Feed categorization with grouping (Uncategorized fallback)
- 🔄 **Implemented**: Entra ID user migration pattern (email → user_id) → [entra-id-user-migration.md](./knowledge/patterns/entra-id-user-migration.md)
- 🔐 **Updated**: User API to use Entra ID tokens (get_current_user dependency)
- 📝 **Added**: Comprehensive backend tests for user migration scenarios
- ⚙️ **Replaced**: Settings placeholder toasts with functional dialogs
- 🛠️ **Updated**: Onboarding to create user with Entra ID authentication
- 🧪 **Improved**: Test coverage with pytest-mock, black, ruff added to requirements
- 📋 **Enhanced**: Settings page fetches user data and refreshes after dialog saves

### 2025-11-08 - Dashboard Overview & Data Transformation
- ✅ **Added**: Dashboard overview feature with stats and prioritized content → [dashboard-overview.md](./knowledge/features/dashboard-overview.md)
- 📊 **Implemented**: 4 stats cards (Total Articles, Active Feeds, New Today, Ask AI)
- 🎯 **Added**: Featured Stories section (top 3 articles) and Recent Articles section (latest 6)
- 🎨 **Created**: Enhanced empty state with CTA to add feeds
- 🔧 **Fixed**: API response format - standardized `{data: [...]}` wrapper
- 🏗️ **Implemented**: API data transformation pattern → [api-data-transformation.md](./knowledge/patterns/api-data-transformation.md)
- 🔄 **Added**: Field mapping (link → url, summary → description, published → published_at)
- 🌐 **Implemented**: Source extraction from URL domain (e.g., techcrunch.com → "Techcrunch")
- 🆔 **Fixed**: Generated UUIDs for articles missing id field
- 📱 **Added**: Responsive grid layouts (4 cols → 2 cols → 1 col)
- 🔗 **Integrated**: Stats card links to Chat page for AI interaction
- 📝 **Documented**: 4 key decisions, performance considerations, future ideas

### 2025-11-08 - AI Chat Integration
- ✅ **Added**: AI chat feature with Google Gemini integration → [ai-chat-integration.md](./knowledge/features/ai-chat-integration.md)
- 🤖 **Integrated**: Google Gemini 2.5 Flash model for chat responses
- 🎨 **Implemented**: Typing indicator with bouncing dots animation
- ⏸️ **Added**: Loading states (disabled input, pulsing send button, placeholder change)
- 🔧 **Fixed**: Vite proxy configuration for /api routing to backend (port 8000)
- 🔄 **Updated**: Backend from deprecated gemini-pro to gemini-2.5-flash
- 🔐 **Secured**: Azure AD Bearer token authentication for chat endpoint
- 🎯 **Optimized**: Optimistic UI updates with error rollback
- 📝 **Documented**: 4 key decisions, common issues, future ideas

### 2025-11-08 - Azure Functions Local Development
- ✅ **Added**: Azure Functions local dev setup pattern → [azure-functions-local-dev.md](./knowledge/patterns/azure-functions-local-dev.md)
- ✅ **Added**: Azure Functions architecture component → [azure-functions-architecture.md](./knowledge/components/azure-functions-architecture.md)
- 🐍 **Configured**: Python 3.11 virtual environment (.venv) for compatibility
- 🗄️ **Set up**: Azurite local storage emulator for development
- ⚙️ **Created**: local.settings.json with proper storage connection strings
- 📦 **Documented**: 6 serverless functions (NewsletterGenerator, CrawlerOrchestrator, CrawlerWorker, DataArchival, HealthMonitor, ManualTrigger)
- 🔧 **Documented**: Shared services (email_service, backend_client, key_vault_client, logger_config, orchestration_logic)
- 📝 **Captured**: Python version mismatch issue and resolution (3.11 vs 3.14)
- 🎯 **Explained**: Timer triggers, queue triggers, HTTP triggers, and durable functions patterns

### 2025-11-08 - Web App & Authentication
- ✅ **Added**: Web app frontend (React + Vite SPA) → [web-app-structure.md](./knowledge/frontend/web-app-structure.md)
- ✅ **Added**: Entra ID authentication feature → [entra-id-authentication.md](./knowledge/features/entra-id-authentication.md)
- 🎨 **Built**: 6 pages (Dashboard, Feeds, Chat, Settings, Onboarding, 404)
- 🧩 **Integrated**: shadcn/ui component library (49 components)
- 🔐 **Implemented**: Frontend MSAL integration (React) with popup/silent token flow
- 🔒 **Implemented**: Backend JWT validation (FastAPI) with fastapi-azure-auth
- 🎯 **Configured**: Single app registration approach for frontend + backend
- 📦 **Added**: Complete tech stack (React 18, TypeScript, Vite, Tailwind, TanStack Query)
- 📝 **Documented**: Comprehensive setup guide (AUTH_SETUP.md) and summary
- 🔧 **Created**: Custom components, hooks, API client, auth system
- 📋 **Recorded**: ADR 003 - Single App Registration decision

### 2025-11-08 - Monorepo Migration
- 🏗️ **Migrated**: Transformed up2d8-frontend into full-stack monorepo
- 📦 **Added**: Backend API (FastAPI) → `packages/backend-api/`
- ⚡ **Added**: Azure Functions (serverless) → `packages/functions/`
- 📱 **Moved**: React Native app → `packages/mobile-app/`
- 🔧 **Created**: Shared package structure → `packages/shared/`
- 📚 **Tagged**: All source repos with `archive-pre-monorepo-2025-01-08`
- ⚙️ **Configured**: Root package.json (npm workspaces) + pyproject.toml
- 🎯 **Organized**: Monorepo structure with docs/, scripts/, infrastructure/

### 2025-11-08 - Pre-Migration
- 🧹 **Cleaned**: Removed all React desktop web app files
- 📱 **Focused**: Repository was mobile-only before monorepo migration
- 🎉 **Initialized** AI knowledge management system
- 🔧 **Added** `/capture` command for automatic knowledge capture

---

## 📍 Quick Navigation

**New to this project?** → Read [GUIDE.md](./GUIDE.md) to learn where to find things

### Project Context
- [Overview](./context/overview.md) - What this project does and why
- [Architecture](./context/architecture.md) - How the system is structured
- [Decisions](./context/decisions/) - Architecture Decision Records (ADRs) - **3 recorded**

### 🎨 Personal Preferences (Cross-Project Standards)
*These apply to all your projects and are referenced, not modified.*

- [Coding Standards](./preferences/coding-standards.md) - Naming, organization, quality principles
- [Error Handling](./preferences/error-handling.md) - Error patterns, logging, retry strategies
- [Testing Strategy](./preferences/testing-strategy.md) - Test philosophy, coverage, patterns
- [Documentation Style](./preferences/documentation-style.md) - Docs philosophy, formats, examples

### Knowledge Base (Grows over time)
- [Features](./knowledge/features/) - **12 documented** - Cross-cutting features
- [Frontend](./knowledge/frontend/) - **1 documented** - Web app components
- [Backend Features](./knowledge/backend/) - **0 documented** - Backend API features
- [Functions](./knowledge/functions/) - **0 documented** - Azure Functions features
- [Mobile Features](./knowledge/mobile/) - **0 documented** - Mobile app features
- [Components](./knowledge/components/) - **4 documented** - Shared components
- [Patterns](./knowledge/patterns/) - **4 documented** - Coding patterns

---

## 📊 Project Stats

- **Monorepo structure**: 4 packages (backend-api, functions, mobile-app, web-app) + shared
- **Total knowledge files**: 28 (overview, architecture, 4 preferences, 3 decisions, 12 features, 4 components, 4 patterns)
- **Features documented**: 12
- **Components documented**: 4
- **Patterns captured**: 4
- **Decisions recorded**: 3
- **Personal preferences**: 4 (coding, errors, testing, docs)
- **Tech Stack**:
  - Backend: FastAPI, MongoDB, Azure Key Vault, Entra ID Auth
  - Functions: Azure Functions (Python), LangChain, Playwright
  - Mobile: React Native 0.82.1, TypeScript, React Navigation 7.x
  - Web: React, Vite, TypeScript, MSAL, shadcn/ui
- **Last migration**: Monorepo consolidation from 3 repositories

---

## 🎯 Current Focus

**Phase**: Monorepo Setup Complete - Ready for integrated development

**Architecture**:
- Backend API provides REST endpoints for articles, chat, users, analytics
- Azure Functions handle background tasks (RSS scraping, newsletters, crawling)
- Mobile app consumes backend API with offline fallback
- Shared package for common types/schemas/utilities

**Next Steps**:
1. Consolidate documentation from all packages
2. Create development scripts for local workflow
3. Set up unified environment configuration
4. Test all packages build and run successfully
5. Use `/capture` to document the monorepo structure

**Active Work**: Monorepo migration and setup

---

## 🗺️ Knowledge Map

### Features (12)
- [Web Search Grounding](./knowledge/features/web-search-grounding.md) - Google Search integration in AI chat with source citations (9-15 per query)
- [Swagger API Organization](./knowledge/features/swagger-api-organization.md) - API documentation organized with 9 category tags for 24 endpoints
- [Mobile Responsive Web App](./knowledge/features/mobile-responsive-web-app.md) - Safari/Chrome mobile support with responsive layouts and performance optimizations
- [RSS Feed Suggestions with AI](./knowledge/features/rss-feed-suggestions.md) - Discover and add new RSS feeds using AI-powered suggestions
- [Category Standardization for RSS Feeds](./knowledge/features/category-standardization.md) - Standardize categories for RSS feeds to ensure consistency
- [Function App RSS Scraping Integration](./knowledge/features/function-app-rss-scraping.md) - Integrate RSS feed scraping into the Azure Function App's article discovery process
- [Dashboard Overview](./knowledge/features/dashboard-overview.md) - Main landing page with stats cards, featured stories, and recent articles
- [AI Chat Integration](./knowledge/features/ai-chat-integration.md) - Interactive chat with Google Gemini AI (2.5-flash) via web app
- [Entra ID Authentication](./knowledge/features/entra-id-authentication.md) - Single sign-on with Microsoft Entra ID for web and API
- [User Preferences Management](./knowledge/features/user-preferences-management.md) - Topics, newsletter format, email notifications with modal dialogs
- [AI Topic Suggestions](./knowledge/features/ai-topic-suggestions.md) - Gemini-powered topic discovery integrated into preferences
- [Feed Search and Categorization](./knowledge/features/feed-search-and-categorization.md) - Real-time feed search and category grouping

### Components (4)
- [MobileNav Component](./knowledge/components/mobile-nav.md) - Drawer navigation for mobile with shadcn/ui Sheet (hamburger menu)
- [Azure Functions Architecture](./knowledge/components/azure-functions-architecture.md) - Serverless background tasks (6 functions: newsletters, crawling, health monitoring)
- [Web App Frontend](./knowledge/frontend/web-app-structure.md) - React SPA with Vite, TypeScript, shadcn/ui (6 pages, 49 UI components)
- [Settings Dialogs](./knowledge/components/settings-dialogs.md) - PreferencesDialog and NotificationsDialog with AI suggestions

### Patterns (4)
- [Google Genai Library Migration](./knowledge/patterns/google-genai-migration.md) - Migrate from google-generativeai to google-genai for tool support
- [API Data Transformation Layer](./knowledge/patterns/api-data-transformation.md) - Transform database schema to frontend contract in API layer
- [Azure Functions Local Development](./knowledge/patterns/azure-functions-local-dev.md) - Python 3.11 virtual environment + Azurite setup for local testing
- [Entra ID User Migration](./knowledge/patterns/entra-id-user-migration.md) - Seamless migration from email-based to user_id-based authentication

### Decisions (3)
- ✅ [003: Single App Registration](./context/decisions/003-single-app-registration.md) - Use one Entra ID app for frontend and backend
- ✅ [002: Focus on React Native](./context/decisions/002-focus-on-react-native.md) - Repository restructure to mobile-only
- ✅ [001: Personal Preferences System](./context/decisions/001-personal-preferences-system.md) - Cross-project standards approach

---

## 💡 How to Use This Index

**Every session, start here:**

1. **Check Recent Changes** (above) - See what's new since your last session
2. **Review Current Focus** - Understand what we're working on
3. **Use Quick Navigation** - Jump to relevant knowledge
4. **Read GUIDE.md** if you need help finding something specific

**After building something:**

1. Run `/capture` to automatically update this index
2. New knowledge files will be created/updated
3. Recent Changes section will be updated
4. Knowledge counts will increment

**This file is your dashboard** - it tells you everything that's happened and where to find what you need.

---

## 🔍 Quick Search Guide

| I need to... | Look in... |
|--------------|------------|
| See what's new | Recent Changes section above |
| Understand the project | [context/overview.md](./context/overview.md) |
| Learn the architecture | [context/architecture.md](./context/architecture.md) |
| Find a feature | [knowledge/features/](./knowledge/features/) (empty for now) |
| Find a component | [knowledge/components/](./knowledge/components/) (empty for now) |
| Learn patterns | [knowledge/patterns/](./knowledge/patterns/) (empty for now) |
| Understand decisions | [context/decisions/](./context/decisions/) (empty for now) |
| Navigate efficiently | [GUIDE.md](./GUIDE.md) |

---

## 📈 System Growth

This knowledge base will grow with every feature you build:

- **Week 1**: Foundation + 1-2 features documented
- **Month 1**: 10+ features, emerging patterns documented
- **Month 3**: Comprehensive knowledge base, AI rarely needs to search codebase

**The system learns as you build.**

---

## ⚡ Pro Tips

- **Check this file first** every session to see what's new
- **Run `/capture` regularly** to keep knowledge current
- **Use GUIDE.md** when you don't know where to look
- **Follow existing patterns** once they're documented
- **Update Recent Changes** whenever significant work is done

---

*This index is automatically updated by the `/capture` command and maintained by AI assistants working on this project.*
