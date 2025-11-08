---
type: decision
name: Focus Repository on React Native Mobile App
status: implemented
created: 2025-11-08
updated: 2025-11-08
decision_date: 2025-11-08
tags: [architecture, repository-structure, react-native, cleanup]
---

# ADR 002: Focus Repository on React Native Mobile App

## Status

**Implemented** - 2025-11-08

## Context

The repository originally contained both a React web application (desktop UI) and a React Native mobile application. This created several issues:

1. **Confusion**: Two separate applications in one repository with unclear focus
2. **Complexity**: Multiple build systems (Vite for web, Metro for React Native)
3. **Dependency conflicts**: Different versions of React and conflicting dependencies
4. **Maintenance overhead**: Two codebases to maintain and keep in sync
5. **Unclear primary application**: Documentation and focus split between platforms

The React Native mobile app is the primary focus and future direction of this project.

## Decision

**Remove all React desktop web app files and focus the repository exclusively on the React Native mobile application.**

### What Was Removed

**React Web App Files:**
- All source code: `components/`, `pages/`, `hooks/`, `context/`, `services/`
- Entry points: `App.tsx`, `index.tsx`, `index.html`, `index.css`
- Build configuration: `vite.config.ts`, `package.json`, `tsconfig.json`
- Styling: `tailwind.config.js`
- Documentation: `AIGeneratorPrompt.md`, `gemini.md`, `metadata.json`
- Backend docs: `docs/handoff/` (backend and function deployment guides)
- Assets: `public/logo.png`
- Dependencies: `node_modules/`, `.env`

**Total removal**: 36 files, ~2,073 lines deleted

### What Was Preserved

**React Native App:**
- Complete `up2d8ReactNative/` directory with all mobile app code
- Mobile app configuration and dependencies
- iOS and Android build configurations

**Supporting Infrastructure:**
- `.ai/` knowledge management system
- `.claude/` command configuration
- `.git/` version control
- `.gitignore`

### What Was Updated

**Documentation:**
- `README.md`: Rewritten to focus on React Native setup and structure
- `claude.md`: Updated project type, tech stack, and features to reflect mobile focus

## Consequences

### Positive

1. **Clear Focus**: Repository now has a single, clear purpose
2. **Simplified Structure**: One application, one build system, one set of dependencies
3. **Better Documentation**: All docs now accurately describe what exists
4. **Reduced Confusion**: New developers immediately understand this is a mobile app
5. **Easier Maintenance**: Only one codebase to maintain and update
6. **Clean Git History**: Old web app code removed but preserved in git history if needed

### Negative

1. **Lost Web Application**: The desktop React app is no longer available in this repository
2. **Git History Size**: Deleted files remain in git history (can be cleaned with git filter-branch if needed)
3. **Potential Recovery Needed**: If web app is needed later, must recover from git history

### Neutral

1. **Migration Path**: If web and mobile need to coexist, proper approach would be:
   - Monorepo structure (e.g., using Turborepo or Nx)
   - Separate repositories for web and mobile
   - Shared component library in separate package

## Implementation

```bash
# Removed directories
rm -rf components pages hooks context services public dist docs node_modules

# Removed configuration files
rm -f App.tsx index.tsx index.html index.css vite.config.ts
rm -f tailwind.config.js types.ts metadata.json tsconfig.json
rm -f AIGeneratorPrompt.md gemini.md package.json package-lock.json .env

# Updated documentation
# - README.md: Rewrote to focus on React Native
# - claude.md: Updated project metadata

# Committed changes
git add -A
git commit -m "Clean up project to focus on React Native mobile app"
```

## Current Repository Structure

```
up2d8-frontend/
├── .ai/                    # AI knowledge management
├── .claude/                # Claude Code commands
├── .git/                   # Version control
├── claude.md               # AI assistant instructions (updated)
├── README.md               # Project documentation (updated)
└── up2d8ReactNative/       # React Native mobile app (primary)
    ├── android/            # Android configuration
    ├── ios/                # iOS configuration
    ├── src/                # Mobile app source code
    ├── App.tsx             # Mobile app entry point
    ├── package.json        # Mobile dependencies
    └── ...                 # Other React Native configs
```

## Notes

- The web application code still exists in git history (commit `a5ac47f` and earlier)
- React Native app was already at version 0.82.1 before cleanup
- The mobile app uses React Navigation 7.x for routing
- Decision documented as part of knowledge management best practices

## Related Decisions

- [001: Personal Preferences System](./001-personal-preferences-system.md) - Cross-project standards approach

## Future Considerations

If the project needs both web and mobile in the future:

1. **Option A: Monorepo**
   - Use Turborepo, Nx, or Lerna
   - Structure: `apps/web/`, `apps/mobile/`, `packages/shared/`
   - Shared code in common packages

2. **Option B: Separate Repositories**
   - `up2d8-web` for React web app
   - `up2d8-mobile` for React Native app
   - `up2d8-shared` for shared utilities/types

3. **Option C: React Native Web**
   - Use single React Native codebase
   - Compile to web using React Native Web
   - Share maximum code between platforms
