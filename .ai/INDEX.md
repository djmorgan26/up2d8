# AI Knowledge Base Index - UP2D8 Monorepo

**Last Updated**: 2025-11-08
**Project Type**: Monorepo (Backend API + Azure Functions + Mobile App)
**Knowledge Items**: 0 features • 0 components • 0 patterns • 2 decisions

---

## 🆕 Recent Changes

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
- [Decisions](./context/decisions/) - Architecture Decision Records (ADRs) - **2 recorded**

### 🎨 Personal Preferences (Cross-Project Standards)
*These apply to all your projects and are referenced, not modified.*

- [Coding Standards](./preferences/coding-standards.md) - Naming, organization, quality principles
- [Error Handling](./preferences/error-handling.md) - Error patterns, logging, retry strategies
- [Testing Strategy](./preferences/testing-strategy.md) - Test philosophy, coverage, patterns
- [Documentation Style](./preferences/documentation-style.md) - Docs philosophy, formats, examples

### Knowledge Base (Grows over time)
- [Backend Features](./knowledge/backend/) - **0 documented** - Backend API features
- [Functions](./knowledge/functions/) - **0 documented** - Azure Functions features
- [Mobile Features](./knowledge/mobile/) - **0 documented** - Mobile app features
- [Components](./knowledge/components/) - **0 documented** - Shared components
- [Patterns](./knowledge/patterns/) - **0 documented** - Coding patterns

---

## 📊 Project Stats

- **Monorepo structure**: 3 packages (backend-api, functions, mobile-app) + shared
- **Total knowledge files**: 8 (overview, architecture, 4 preferences, 2 decisions)
- **Features documented**: 0
- **Components documented**: 0
- **Patterns captured**: 0
- **Decisions recorded**: 2
- **Personal preferences**: 4 (coding, errors, testing, docs)
- **Tech Stack**:
  - Backend: FastAPI, MongoDB, Azure Key Vault
  - Functions: Azure Functions (Python), LangChain, Playwright
  - Mobile: React Native 0.82.1, TypeScript, React Navigation 7.x
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

### Features (0)
*No features documented yet. Use `/capture` after building features to document them.*

### Components (0)
*No components documented yet. Components will be captured as you build.*

### Patterns (0)
*No patterns documented yet. Patterns will emerge as you build features.*

### Decisions (2)
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
