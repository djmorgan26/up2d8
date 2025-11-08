# UP2D8 - Full-Stack Monorepo

**Project Type**: Full-Stack Monorepo (Backend API + Azure Functions + Mobile App)
**Purpose**: Personal news digest and information management platform
**Tech Stack**: FastAPI (Python), Azure Functions, React Native, MongoDB
**Status**: Monorepo Migration Complete - Active Development
**Last Updated**: 2025-11-08

---

## For AI Assistants 🤖

> **READ THIS FIRST** every time you start working on this project.

### Your First 3 Steps (Every Session)

1. **Read `.ai/INDEX.md`** - Your dashboard with recent changes and knowledge map
2. **Check `.ai/GUIDE.md`** - Learn where to find specific types of information
3. **Review recent changes** - See what's new in INDEX.md before starting

### Knowledge Base Structure

```
.ai/
├── INDEX.md              ← Start here: dashboard with recent changes
├── GUIDE.md              ← Where to look for common questions
│
├── context/              ← Project architecture and key decisions
│   ├── overview.md       ← What this project does
│   ├── architecture.md   ← How it's structured
│   └── decisions/        ← Important decisions (ADRs)
│
└── knowledge/            ← Captured knowledge (grows over time)
    ├── backend/          ← Backend API features
    ├── functions/        ← Azure Functions features
    ├── mobile/           ← Mobile app features
    ├── components/       ← Component documentation
    └── patterns/         ← Coding patterns used
```

### How This System Works

**The Core Concept:**
- Instead of searching the entire repository, you know exactly where to look
- Knowledge is captured incrementally as features are built
- Every session starts with INDEX.md to see what's new
- GUIDE.md tells you where to find specific types of information

**The Flow:**
```
Read claude.md → Read INDEX.md → Read GUIDE.md → Find specific knowledge → Build → Capture
```

### Personal Preferences (Cross-Project Standards)

**Before coding**, review `.ai/preferences/` for general standards:

- **[Coding Standards](./.ai/preferences/coding-standards.md)** - Naming, organization, code quality principles
- **[Error Handling](./.ai/preferences/error-handling.md)** - Error patterns, logging strategies
- **[Testing Strategy](./.ai/preferences/testing-strategy.md)** - Test philosophy, coverage targets
- **[Documentation Style](./.ai/preferences/documentation-style.md)** - How to document code

**These preferences apply to all projects** - follow them unless project-specific needs dictate otherwise. Document project-specific implementations in `.ai/knowledge/patterns/`.

### Before Making Changes

1. **Check `.ai/INDEX.md`** for recent updates that might affect your work
2. **Review `.ai/preferences/`** for applicable coding standards
3. **Look for related features** in `.ai/knowledge/features/` to understand existing patterns
4. **Review relevant patterns** in `.ai/knowledge/patterns/` to maintain consistency
5. **Check architecture** in `.ai/context/` if making structural changes

### After Making Changes

1. **Run `/capture`** to document what you built (knowledge capture workflow)
2. **Ensure tests pass** (if tests exist)
3. **Commit with clear messages** explaining what and why

### Available Commands

- **`/capture`** - Automatically document recent work (run after building features)
- **`/init`** - Initialize AI knowledge system in a new project (one-time setup)

### Navigation Quick Reference

| Need to know... | Look in... |
|----------------|------------|
| What's new? | `.ai/INDEX.md` → Recent Changes |
| My coding preferences? | `.ai/preferences/` (cross-project standards) |
| How does X work? | `.ai/knowledge/features/[feature].md` |
| Why was Y decided? | `.ai/context/decisions/` |
| What patterns to use? | `.ai/knowledge/patterns/` (project-specific) |
| Project architecture? | `.ai/context/architecture.md` |
| What components exist? | `.ai/knowledge/components/` |

### Working Principles

1. **Discovery over Search**: Use INDEX.md and GUIDE.md to find what you need
2. **Context First**: Always read relevant knowledge before building
3. **Capture After**: Run `/capture` after completing work to document it
4. **Incremental Growth**: The knowledge base grows with each feature
5. **Consistency**: Follow existing patterns found in `.ai/knowledge/patterns/`

### Tool Agnostic Design

This knowledge base works with **any AI assistant**:
- **Claude Code**: Full integration with `/capture` command
- **Gemini/Cursor/Other**: Read `claude.md` → `INDEX.md` → `GUIDE.md`, same flow
- **Human Developers**: All files are human-readable markdown

---

## Project Overview

### What This Is

A full-stack personal news digest and information management platform consisting of:

**Backend API** (`packages/backend-api/`)
- FastAPI REST API serving mobile and web clients
- MongoDB database for articles, users, feeds, analytics
- Google Gemini AI integration for chat features
- Azure Key Vault for secrets management

**Azure Functions** (`packages/functions/`)
- Serverless background tasks and automation
- RSS feed scraping (daily schedule)
- Newsletter generation (personalized digests)
- Web crawling orchestration (durable functions)
- Email delivery via SendGrid

**Mobile App** (`packages/mobile-app/`)
- React Native app for iOS and Android
- News browsing with AI-powered chat
- Offline mode with mock data fallback
- Custom theming with dark mode support

**Shared** (`packages/shared/`)
- Common types, schemas, and utilities
- Single source of truth for data models

### Architecture

```
Mobile App → Backend API → Cosmos DB (MongoDB)
                ↑
         Azure Functions (background tasks)
```

### Tech Stack

**Backend**:
- FastAPI (Python), MongoDB, Azure Key Vault, Google Gemini

**Functions**:
- Azure Functions (Python), LangChain, Playwright, BeautifulSoup4

**Mobile**:
- React Native 0.82.1, TypeScript, React Navigation 7.x, Zustand

### Current Status

**Phase**: Monorepo Migration Complete - Ready for Integrated Development
**Packages**: 3 (backend-api, functions, mobile-app) + shared
**Features**: 0 documented (use `/capture` to document as you build)
**Components**: 0 documented
**Patterns**: 0 documented

See `.ai/context/overview.md` and `.ai/INDEX.md` for full details.

---

## For Human Developers

### Quick Start

1. Read this file to understand the system
2. Read `README.md` for human-readable documentation
3. Browse `.ai/` directory to see knowledge structure
4. After building features, run `/capture` to document them

### Maintaining This System

- **Weekly**: Review Recent Changes in INDEX.md
- **After Features**: Always run `/capture`
- **Keep Current**: Update INDEX.md, GUIDE.md as the project grows

### Philosophy

> "AI should know where to look, not search everything."

This system is designed to:
- Start simple and grow organically
- Capture knowledge with minimal overhead
- Work with any AI assistant
- Stay maintainable as projects scale

For more details, see `README.md` and `.ai/context/architecture.md`.
