# Project Overview

**Project Name**: up2d8 - React Native Mobile App
**Created**: 2025-11-08
**Status**: Early Development
**Repository**: up2d8-frontend

---

## What This Is

A **React Native mobile application** for personal news digests and information management. The app provides a native mobile experience with custom theming, smooth navigation, and cross-platform support for iOS and Android.

Think of it as your **personal mobile news companion** - bringing you relevant news and information in a beautiful, native mobile interface.

---

## The Problem It Solves

### Information Overload Challenges

In today's digital landscape, users typically face:

1. **News Fragmentation**: Information scattered across multiple sources and platforms
2. **Time Constraints**: No time to visit multiple news sites and aggregate information
3. **Relevance Issues**: Generic news feeds don't match personal interests
4. **No Interactive Help**: Can't ask questions or dive deeper into topics of interest
5. **Context Switching**: Moving between different apps and websites for news

### Real-World Impact

- ⏱️ **Time waste**: Visiting multiple news sites to stay informed
- 📱 **App fatigue**: Too many news apps with different interfaces
- 🔍 **Search friction**: Hard to find specific information or get quick answers
- 🧠 **Information overload**: Too much noise, not enough signal
- 💬 **No conversation**: Traditional news is one-way, can't ask follow-up questions

---

## The Solution

### Native Mobile News Experience

A React Native mobile application that provides:

1. **Personal News Digest**: Curated news feed accessible on mobile devices
2. **Native Performance**: Smooth, responsive mobile experience
3. **Cross-Platform**: Works on both iOS and Android
4. **Custom Theming**: Dark mode with beautiful gradients and animations
5. **Modern Navigation**: Bottom tab navigation with smooth transitions

### Key Innovation: Conversational News

The app leverages **Google's Gemini AI** to enable:
- Natural language questions about news and topics
- Context-aware responses
- Deep dives into subjects of interest
- Personalized news curation

### Streamlined Experience

Instead of:
```
User visits 5 news sites → Reads headlines → Googles for more info → Switches apps
[Takes 30+ minutes, fragmented experience]
```

We provide:
```
User opens up2d8 → Views digest → Chats with AI about topics → Gets personalized answers
[Takes 5-10 minutes, seamless experience]
```

---

## How It Works

### The Flow

```
┌─────────────┐
│ New Session │
└──────┬──────┘
       │
       ├─> Read claude.md (orientation)
       │
       ├─> Read .ai/INDEX.md (what's new?)
       │
       ├─> Read .ai/GUIDE.md (where to look?)
       │
       ├─> Find specific knowledge
       │
       ├─> Build feature/fix bug
       │
       ├─> Run /capture
       │
       └─> Knowledge base updated
```

### Knowledge Capture Process

1. **Build something** (feature, component, fix)
2. **Run `/capture`**
3. **AI analyzes** git diff and changed files
4. **AI generates** structured documentation
5. **INDEX.md updates** with recent changes
6. **Next session**: Knowledge is available

### Incremental Growth

- **Day 1**: Foundation with 0 documented features
- **Week 1**: 2-3 features documented, patterns emerging
- **Month 1**: 10+ features, comprehensive pattern library
- **Month 3**: Complete knowledge base, AI rarely searches codebase

---

## Core Design Principles

### 1. Discovery Over Search
AI knows where to look first, reducing time and token costs

### 2. Incremental Knowledge Capture
Every feature adds to the knowledge base automatically

### 3. Tool Agnostic
Works with Claude Code, Gemini, Cursor, or any AI assistant

### 4. Human Readable
All files are markdown + YAML, easy to read and edit

### 5. Structured Navigation
Hierarchical: claude.md → INDEX.md → GUIDE.md → specific knowledge → code

### 6. Low Overhead
Simple `/capture` command, no complex setup per task

### 7. Git-Friendly
Plain text files tracked in git, merges easily, diff-able

---

## Current Status

### Phase: Foundation

**What's Built**:
- ✅ Directory structure (`.ai/`, `.claude/`)
- ✅ Entry point (`claude.md`)
- ✅ Dashboard (`INDEX.md`)
- ✅ Navigation guide (`GUIDE.md`)
- ✅ Context files (`overview.md`, `architecture.md`)
- ✅ Knowledge capture (`/capture` command)

**What's Next**:
1. Test `/capture` with dummy feature
2. Validate knowledge capture workflow
3. Begin building real features
4. Watch knowledge base grow organically

### Metrics (Current)

- **Features**: 0 documented
- **Components**: 0 documented
- **Patterns**: 0 documented
- **Decisions**: 0 recorded
- **Total knowledge files**: 5 (foundation files)

---

## Use Cases

### For This Project (Meta-System)

This project IS the knowledge management system itself. It's self-documenting - as we build features for the system, we use `/capture` to document them.

### For Future Projects

Once established, this system can be:

1. **Copied to new projects** as a template
2. **Customized** for specific tech stacks
3. **Extended** with project-specific patterns
4. **Shared** across teams for consistency

### For Different AI Tools

- **Claude Code**: Full integration with `/capture` command and slash commands
- **Gemini/Bard**: Read `claude.md`, follow same file structure
- **Cursor**: Point to knowledge files, same navigation
- **GitHub Copilot**: Can reference knowledge files in prompts
- **Human Developers**: All files human-readable, serves as documentation

---

## Success Criteria

### Quantitative

- **Discovery time**: < 30 seconds to find relevant information
- **Search reduction**: 70%+ reduction in full-repo searches
- **Knowledge coverage**: 100% of features documented
- **Index hit rate**: 60%+ of questions answered from INDEX.md

### Qualitative

- AI provides context-aware answers without clarifying questions
- New features automatically follow established patterns
- Code reviews reference project-specific standards
- Knowledge base grows organically with minimal effort
- New developers (human or AI) get up to speed in minutes

---

## Technology Stack

### Current Stack

- **Frontend Framework**: React 19 with TypeScript
- **Build Tool**: Vite (fast, modern bundler)
- **AI Integration**: Google Generative AI SDK (@google/genai)
- **Routing**: React Router DOM v7
- **Styling**: CSS/Tokens-based design system

### Future Enhancements

As the project evolves, we may add:
- **Backend**: API server for news aggregation
- **Database**: User preferences and saved articles
- **Authentication**: User accounts and personalization
- **Real-time Updates**: WebSocket for live news feeds
- **Mobile**: React Native companion app

---

## Related Documentation

- [Architecture](./architecture.md) - How the system is structured
- [Decisions](./decisions/) - Major architectural decisions (empty for now)
- [INDEX.md](../INDEX.md) - Current state and recent changes
- [GUIDE.md](../GUIDE.md) - How to navigate the knowledge base
- [claude.md](../../claude.md) - AI entry point and orientation

---

## Philosophy

> "The best documentation is the one that's always up to date."

By capturing knowledge automatically as features are built, we eliminate the doc/code drift problem. Documentation is generated from reality (git changes) not aspirational intentions.

> "AI should know where to look, not search everything."

Structured navigation beats unstructured search. Like a well-organized library vs. a pile of books.

> "Start simple, grow organically."

Begin with minimal structure. Add complexity only when needed. Let the project guide its evolution.

---

**Last Updated**: 2025-11-08 (Foundation)
