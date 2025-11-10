# GitHub Actions Workflow Triggers

This document explains when each deployment workflow runs automatically.

---

## Overview

All three workflows now support:
- ✅ **Automatic deployment** on push to `main`
- ✅ **Automatic deployment** on pull requests to `main`
- ✅ **Path filtering** - only runs when relevant code changes
- ✅ **Manual triggers** - can be run manually via GitHub Actions UI

---

## Backend API Workflow

**File:** `.github/workflows/up2d8-backend.yml`

### Triggers

#### Automatic on Push to Main
Runs when code is **merged** to main branch and changes include:
- `packages/backend-api/**` - Any backend API code
- `packages/shared/**` - Shared code/types
- `.github/workflows/up2d8-backend.yml` - The workflow itself

#### Automatic on Pull Request
Runs when a PR is **opened or updated** targeting main branch with changes to:
- `packages/backend-api/**`
- `packages/shared/**`
- `.github/workflows/up2d8-backend.yml`

**Purpose:** Test the deployment before merging to catch issues early.

#### Manual Trigger
Can be run manually from GitHub Actions UI with environment selection.

### Examples

**Will Trigger:**
```bash
# Editing backend code
git commit -m "Update API endpoint" packages/backend-api/routes/articles.py
git push origin main

# Editing shared types
git commit -m "Update models" packages/shared/models.py
git push origin main

# Updating workflow
git commit -m "Update CI" .github/workflows/up2d8-backend.yml
git push origin main
```

**Won't Trigger:**
```bash
# Editing frontend only
git commit -m "Update UI" packages/web-app/src/App.tsx
git push origin main

# Editing functions only
git commit -m "Update scraper" packages/functions/daily_scraper.py
git push origin main

# Editing docs only
git commit -m "Update README" README.md
git push origin main
```

---

## Azure Functions Workflow

**File:** `.github/workflows/up2d8-functions.yml`

### Triggers

#### Automatic on Push to Main
Runs when code is **merged** to main branch and changes include:
- `packages/functions/**` - Any function code
- `packages/shared/**` - Shared code/types
- `.github/workflows/up2d8-functions.yml` - The workflow itself

#### Automatic on Pull Request
Runs when a PR is **opened or updated** targeting main branch with changes to:
- `packages/functions/**`
- `packages/shared/**`
- `.github/workflows/up2d8-functions.yml`

#### Manual Trigger
Can be run manually from GitHub Actions UI with environment selection.

### Examples

**Will Trigger:**
```bash
# Editing function code
git commit -m "Update RSS scraper" packages/functions/rss_scraper.py
git push origin main

# Editing shared utilities
git commit -m "Add helper" packages/shared/utils.py
git push origin main
```

**Won't Trigger:**
```bash
# Editing backend only
git commit -m "Update API" packages/backend-api/main.py
git push origin main

# Editing mobile app only
git commit -m "Update app" packages/mobile-app/App.tsx
git push origin main
```

---

## Static Web App Workflow

**File:** `.github/workflows/up2d8-web.yml`

### Triggers

#### Automatic on Push to Main
Runs when code is **merged** to main branch and changes include:
- `packages/web-app/**` - Any web app code
- `packages/shared/**` - Shared code/types
- `.github/workflows/up2d8-web.yml` - The workflow itself

#### Automatic on Pull Request
Runs when a PR is **opened or updated** targeting main branch with changes to:
- `packages/web-app/**`
- `packages/shared/**`
- `.github/workflows/up2d8-web.yml`

**Note:** Azure Static Web Apps automatically create preview URLs for PRs.

#### Manual Trigger
Can be run manually from GitHub Actions UI with environment selection.

### Examples

**Will Trigger:**
```bash
# Editing web app code
git commit -m "Update dashboard" packages/web-app/src/pages/Dashboard.tsx
git push origin main

# Editing shared types
git commit -m "Update API types" packages/shared/types.ts
git push origin main
```

**Won't Trigger:**
```bash
# Editing backend only
git commit -m "Update API" packages/backend-api/routes/users.py
git push origin main

# Editing tests only
git commit -m "Add tests" tests/production/test_api.py
git push origin main
```

---

## Shared Code Changes

**Special Case:** Changes to `packages/shared/**` trigger **ALL THREE** workflows because:
- Backend API imports shared models
- Functions use shared utilities
- Web app uses shared types

### Example
```bash
git commit -m "Update Article model" packages/shared/models.py
git push origin main
```

**Result:** All 3 workflows run in parallel:
- ✅ Backend API deploys
- ✅ Functions deploy
- ✅ Web app deploys

---

## Pull Request Workflow

When you create a PR to `main`:

### 1. Open PR
```bash
git checkout -b feature/new-article-view
# Make changes to packages/web-app/
git commit -m "Add article detail view"
git push origin feature/new-article-view
# Open PR on GitHub
```

### 2. Workflow Runs
- GitHub Actions automatically runs the Web App workflow
- Build and deployment steps execute
- Azure creates a preview environment (for Static Web Apps)

### 3. Review & Test
- Check the workflow results in the PR
- Test the preview deployment
- Request reviews

### 4. Merge PR
```bash
# After approval, merge PR
```

### 5. Production Deployment
- Workflow runs again on `main` branch
- Deploys to production
- Verifies deployment health

---

## Optimizing Workflow Runs

### Path Filtering Benefits

**Saves Time & Resources:**
- Only relevant workflows run
- Faster CI/CD pipeline
- Lower GitHub Actions minutes usage

**Example Scenario:**
```bash
# You only edit the frontend
git commit -m "Update UI" packages/web-app/src/App.tsx
git push origin main

# Result: Only web-app workflow runs
# Backend and Functions workflows skip (no code changes)
```

### Multiple Package Changes

If you change multiple packages in one commit:

```bash
git commit -m "Add feature across stack" \
  packages/backend-api/routes/articles.py \
  packages/web-app/src/pages/Articles.tsx

git push origin main
```

**Result:** Both backend and web workflows run in **parallel**.

---

## Workflow Run Matrix

| Changed Files | Backend Workflow | Functions Workflow | Web Workflow |
|--------------|------------------|-------------------|--------------|
| `packages/backend-api/**` | ✅ Runs | ❌ Skips | ❌ Skips |
| `packages/functions/**` | ❌ Skips | ✅ Runs | ❌ Skips |
| `packages/web-app/**` | ❌ Skips | ❌ Skips | ✅ Runs |
| `packages/shared/**` | ✅ Runs | ✅ Runs | ✅ Runs |
| `docs/**` | ❌ Skips | ❌ Skips | ❌ Skips |
| `tests/**` | ❌ Skips | ❌ Skips | ❌ Skips |
| Workflow files | ✅ Respective | ✅ Respective | ✅ Respective |

---

## Manual Deployments

All workflows can still be triggered manually:

### Via GitHub UI
1. Go to **Actions** tab
2. Select workflow (e.g., "Deploy Backend API")
3. Click **Run workflow**
4. Choose branch and environment
5. Click **Run workflow**

### Via GitHub CLI
```bash
# Deploy backend
gh workflow run up2d8-backend.yml

# Deploy functions
gh workflow run up2d8-functions.yml

# Deploy web app
gh workflow run up2d8-web.yml
```

---

## Monitoring Workflow Runs

### View All Runs
```bash
gh run list
```

### View Specific Workflow
```bash
gh run list --workflow=up2d8-backend.yml
```

### View Run Details
```bash
gh run view <run-id>
```

### Watch Live Run
```bash
gh run watch <run-id>
```

---

## Troubleshooting

### Workflow Not Triggering

**Check:**
1. Did you push to `main` branch?
2. Did you change files in the correct paths?
3. Is the workflow file syntax correct?

**Debug:**
```bash
# View workflow configuration
gh workflow view up2d8-backend.yml

# Check recent runs
gh run list --workflow=up2d8-backend.yml
```

### Workflow Running When Not Expected

**Check:**
- Did you change files in `packages/shared/**`?
- Did you modify the workflow file itself?

**These trigger all workflows:**
```bash
# This triggers ALL workflows
git commit -m "Update model" packages/shared/models.py

# This only triggers backend workflow
git commit -m "Update route" packages/backend-api/routes/users.py
```

### Multiple Workflows Running

This is **normal** when:
- You change `packages/shared/**`
- You change multiple packages in one commit
- You modify workflow files

Workflows run in **parallel** so they don't delay each other.

---

## Best Practices

### 1. Commit Related Changes Together
```bash
# Good: Backend + shared changes in one commit
git commit -m "Add article tags feature" \
  packages/backend-api/routes/articles.py \
  packages/shared/models.py
```

### 2. Use Feature Branches
```bash
# Create feature branch
git checkout -b feature/article-tags

# Make changes
git commit -m "Add article tags"

# Open PR (triggers PR workflow)
git push origin feature/article-tags
```

### 3. Test Before Merging
- Let PR workflows run
- Review deployment results
- Test in preview environment
- Only merge when green

### 4. Keep Commits Focused
```bash
# Good: One package at a time
git commit -m "Update web UI" packages/web-app/

# Better: Logically related across packages
git commit -m "Add article tags" \
  packages/backend-api/ \
  packages/web-app/ \
  packages/shared/
```

---

## Summary

✅ **All workflows now auto-deploy:**
- On push to `main`
- On pull requests to `main`
- Only when relevant code changes

✅ **Smart path filtering:**
- Saves CI/CD minutes
- Faster deployment pipeline
- No unnecessary runs

✅ **Manual override:**
- Can still trigger manually
- Useful for hotfixes
- Environment selection

---

## Quick Reference

```bash
# Check what will trigger
git diff --name-only main...HEAD

# Triggers backend workflow
packages/backend-api/
packages/shared/

# Triggers functions workflow
packages/functions/
packages/shared/

# Triggers web workflow
packages/web-app/
packages/shared/

# Triggers respective workflow
.github/workflows/*.yml
```

---

**Last Updated:** 2025-11-10
**Workflows Updated:** All 3 (backend, functions, web)
