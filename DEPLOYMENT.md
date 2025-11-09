# UP2D8 Azure Deployment Guide

Complete guide to deploy the UP2D8 monorepo to Azure with all resources correctly configured and communicating.

---

## Prerequisites

You already have these Azure resources created:
- ✅ Backend API: `up2d8` (App Service)
- ✅ Function App: `up2d8-function-app` (Azure Functions)
- ✅ Static Web App: `up2d8-web` (Static Web Apps)
- ✅ Cosmos DB: `up2d8cluster` (MongoDB API)
- ✅ Key Vault: `personal-key-vault1`
- ✅ App Registration: `up2d8` (Entra ID)
- ✅ Storage Account: `personalrg8fab`

---

## Phase 1: Azure Portal Configuration

### 1.1 Enable Managed Identities & Key Vault Access

#### Backend API Managed Identity
1. Navigate to: Azure Portal → App Services → `up2d8`
2. Left menu → **Identity** → System assigned tab
3. Status: **On** → Save
4. Copy the **Object (principal) ID** (you'll need this)

#### Function App Managed Identity
1. Navigate to: Azure Portal → Function App → `up2d8-function-app`
2. Left menu → **Identity** → System assigned tab
3. Status: **On** → Save
4. Copy the **Object (principal) ID**

#### Grant Key Vault Access
1. Navigate to: Azure Portal → Key Vaults → `personal-key-vault1`
2. Left menu → **Access policies** → **+ Create**
3. Permissions tab:
   - Secret permissions: ☑️ **Get**, ☑️ **List**
   - Click **Next**
4. Principal tab:
   - Search for: `up2d8` (your App Service)
   - Select it → **Next** → **Next** → **Create**
5. **Repeat steps 2-4** for `up2d8-function-app` (Function App)

**Result**: Both services can now read secrets from Key Vault using Managed Identity.

---

### 1.2 Configure Backend API (App Service)

Navigate to: Azure Portal → App Services → `up2d8` → Configuration

#### Application Settings
Click **+ New application setting** for each:

| Name | Value |
|------|-------|
| `ENTRA_TENANT_ID` | `6f69caf6-bea0-4a54-a20c-7469005eadf4` |
| `ENTRA_CLIENT_ID` | `2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97` |
| `ENTRA_AUDIENCE` | `api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97` |
| `KEY_VAULT_URI` | `https://personal-key-vault1.vault.azure.net/` |
| `MONGODB_DATABASE` | `up2d8` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |

Click **Save** → **Continue**

#### CORS Settings
1. Same page → Left menu → **CORS**
2. **Allowed Origins** → Add each:
   - `http://localhost:5173` (for local development)
   - `http://localhost:8080`
   - `https://gray-wave-00bdfc60f.3.azurestaticapps.net` (production)
3. **Enable Access-Control-Allow-Credentials**: ☑️ **Yes**
4. Click **Save**

#### Startup Command (Optional - improves performance)
1. Same page → **General settings** tab
2. **Startup Command**:
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```
3. Click **Save**

---

### 1.3 Configure Function App

Navigate to: Azure Portal → Function App → `up2d8-function-app` → Configuration

#### Application Settings
Click **+ New application setting** for each:

| Name | Value |
|------|-------|
| `FUNCTIONS_WORKER_RUNTIME` | `python` |
| `KEY_VAULT_URI` | `https://personal-key-vault1.vault.azure.net/` |
| `BACKEND_API_URL` | `https://up2d8.azurewebsites.net` |
| `BREVO_SMTP_HOST` | `smtp-relay.brevo.com` |
| `BREVO_SMTP_PORT` | `587` |
| `BREVO_SMTP_USER` | `9a9964001@smtp-brevo.com` |
| `SENDER_EMAIL` | `davidjmorgan26@gmail.com` |
| `MONGODB_DATABASE` | `up2d8` |

Click **Save** → **Continue**

**Note**: `AzureWebJobsStorage` should already be configured automatically by Azure.

---

### 1.4 Configure Static Web App

Navigate to: Azure Portal → Static Web Apps → `up2d8-web` → Configuration

#### Application Settings
Click **Add** for each:

| Name | Value |
|------|-------|
| `VITE_APP_ENTRA_CLIENT_ID` | `2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97` |
| `VITE_APP_ENTRA_TENANT_ID` | `6f69caf6-bea0-4a54-a20c-7469005eadf4` |
| `VITE_APP_ENTRA_REDIRECT_URI` | `https://gray-wave-00bdfc60f.3.azurestaticapps.net` |
| `VITE_APP_ENTRA_API_SCOPE` | `api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97/access_as_user` |

Click **Save**

---

### 1.5 Update App Registration (Entra ID)

Navigate to: Azure Portal → Microsoft Entra ID → App registrations → `up2d8` (or search for Client ID: `2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97`)

#### Add Production Redirect URI
1. Left menu → **Authentication**
2. Platform configurations → **Single-page application** section
3. **+ Add URI**: `https://gray-wave-00bdfc60f.3.azurestaticapps.net`
4. Click **Save**

#### Verify API Exposure
1. Left menu → **Expose an API**
2. Verify Application ID URI: `api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97`
3. Verify Scope exists: `access_as_user` (Enabled)

**Result**: Production web app can now authenticate users.

---

## Phase 2: GitHub Repository Secrets

Navigate to: GitHub → Your Repository → **Settings** → **Secrets and variables** → **Actions**

### Required Secrets

#### 1. Backend API Deployment Secret
1. In Azure Portal → App Services → `up2d8` → **Deployment Center**
2. Top menu → **Manage publish profile** → Download file
3. Open the XML file and copy **entire contents**
4. In GitHub → **New repository secret**:
   - Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
   - Value: [Paste entire XML content]

#### 2. Function App Deployment Secret
1. In Azure Portal → Function App → `up2d8-function-app` → **Deployment Center**
2. Top menu → **Manage publish profile** → Download file
3. Open the XML file and copy **entire contents**
4. In GitHub → **New repository secret**:
   - Name: `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
   - Value: [Paste entire XML content]

#### 3. Static Web App Deployment Secret
1. In Azure Portal → Static Web Apps → `up2d8-web` → **Overview** page
2. Click **Manage deployment token** → Copy the token
3. In GitHub → **New repository secret**:
   - Name: `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - Value: [Paste token]

#### 4. Email Notification Secrets (Optional but recommended)
1. In GitHub → **New repository secret**:
   - Name: `NOTIFICATION_EMAIL`
   - Value: `your-email@gmail.com` (where you want deployment notifications)

2. **If using Gmail**:
   - Go to: Google Account → Security → 2-Step Verification → App passwords
   - Generate new app password for "GitHub Actions"
   - In GitHub → **New repository secret**:
     - Name: `GMAIL_APP_PASSWORD`
     - Value: [16-character app password]

**Alternative email providers**: Update the SMTP settings in workflow files if not using Gmail.

---

## Phase 3: Verify GitHub Actions Workflows

The following workflows have been created in `.github/workflows/`:

1. ✅ **`up2d8-backend.yml`** - Deploy Backend API
2. ✅ **`up2d8-functions.yml`** - Deploy Function App
3. ✅ **`up2d8-web.yml`** - Deploy Static Web App

### Verify Workflows Are Available
1. Navigate to: GitHub → Your Repository → **Actions** tab
2. You should see 3 workflows listed on the left sidebar:
   - Deploy Backend API
   - Deploy Function App
   - Deploy Static Web App

**If you don't see them**: Commit and push the `.github/workflows/*.yml` files to your repository.

---

## Phase 4: First Deployment

### Deployment Order (Important!)
Deploy in this specific order to ensure dependencies are met:

#### Step 1: Deploy Backend API
1. GitHub → Repository → **Actions** tab
2. Left sidebar → **Deploy Backend API**
3. Click **Run workflow** button (right side)
4. Select branch: `main`
5. Environment: `production`
6. Click **Run workflow**
7. **Wait for completion** (~3-5 minutes)
8. Verify success: Open `https://up2d8.azurewebsites.net/api/health` (should return 200)

#### Step 2: Deploy Function App
1. GitHub → Repository → **Actions** tab
2. Left sidebar → **Deploy Function App**
3. Click **Run workflow** button
4. Select branch: `main`
5. Environment: `production`
6. Click **Run workflow**
7. **Wait for completion** (~5-8 minutes)
8. Verify: Check Azure Portal → Function App → Functions (should list 7 functions)

#### Step 3: Deploy Static Web App
1. GitHub → Repository → **Actions** tab
2. Left sidebar → **Deploy Static Web App**
3. Click **Run workflow** button
4. Select branch: `main`
5. Environment: `production`
6. Click **Run workflow**
7. **Wait for completion** (~3-5 minutes)
8. Verify: Open `https://gray-wave-00bdfc60f.3.azurestaticapps.net` (web app loads)

---

## Phase 5: Post-Deployment Verification

### 5.1 Backend API Health Check
```bash
curl https://up2d8.azurewebsites.net/api/health
```
**Expected**: `{"status": "healthy"}`

### 5.2 Backend API Swagger Docs
Open: `https://up2d8.azurewebsites.net/docs`
**Expected**: Interactive API documentation with 9 categories

### 5.3 Function App Verification
1. Azure Portal → Function App → `up2d8-function-app` → **Functions**
2. Verify these functions are listed:
   - ✅ DailyArticleScraper
   - ✅ NewsletterGenerator
   - ✅ CrawlerOrchestrator
   - ✅ CrawlerWorker
   - ✅ HealthMonitor
   - ✅ ManualTrigger
   - ✅ DataArchival

### 5.4 Web App End-to-End Test
1. Open: `https://gray-wave-00bdfc60f.3.azurestaticapps.net`
2. Click **Login** → Authenticate with Microsoft account
3. Complete onboarding (select topics)
4. Navigate through pages:
   - **Dashboard**: Should load (may be empty initially)
   - **Feeds**: Add a test RSS feed (e.g., `https://feeds.bbci.co.uk/news/rss.xml`)
   - **Chat**: Ask a question (e.g., "What's happening in tech today?")
   - **Settings**: Verify preferences load

### 5.5 API Proxy Test
```bash
curl https://gray-wave-00bdfc60f.3.azurestaticapps.net/api/health
```
**Expected**: Same response as backend health check (proves proxy works)

---

## Common Issues & Troubleshooting

### Issue 1: Backend API Returns 500 Error
**Symptoms**: `/api/health` returns 500 Internal Server Error

**Likely Causes**:
1. Managed Identity not configured → Go to Phase 1.1
2. Key Vault access not granted → Verify access policies in Key Vault
3. MongoDB connection string missing in Key Vault → Check secret `COSMOS-DB-CONNECTION-STRING-UP2D8` exists

**Debug**:
- Azure Portal → App Service → Log stream (watch for errors)
- Check Application Insights logs

### Issue 2: Function App Functions Not Running
**Symptoms**: Scheduled functions don't trigger at expected times

**Likely Causes**:
1. `AzureWebJobsStorage` not configured → Should be auto-configured, check Configuration
2. Timer triggers disabled → Azure Portal → Function → Integration → Check "Enabled" box
3. Python version mismatch → Ensure using Python 3.11

**Debug**:
- Azure Portal → Function App → Monitor → Check Invocations
- Check Application Insights for errors

### Issue 3: CORS Errors in Browser Console
**Symptoms**: Browser console shows "CORS policy: No 'Access-Control-Allow-Origin' header"

**Likely Causes**:
1. CORS not configured on backend → Revisit Phase 1.2 CORS settings
2. Static Web App URL not in allowed origins → Check `main.py` CORS configuration
3. Credentials not enabled → Ensure `Access-Control-Allow-Credentials` is **Yes**

**Fix**:
- Backend code already updated with correct CORS (redeploy if needed)
- Verify Azure Portal CORS settings match

### Issue 4: Login Fails / Infinite Redirect
**Symptoms**: Clicking login doesn't work or redirects in a loop

**Likely Causes**:
1. Production redirect URI not added to App Registration → Revisit Phase 1.5
2. MSAL configuration incorrect → Check `VITE_APP_ENTRA_*` variables in Static Web App config
3. Scopes mismatch → Verify API scope in App Registration matches frontend config

**Debug**:
- Browser console → Look for MSAL errors
- Network tab → Check token requests (should return 200)

### Issue 5: API Proxy Not Working
**Symptoms**: `/api/*` calls from web app return 404 or don't reach backend

**Likely Causes**:
1. `staticwebapp.config.json` not deployed → Ensure file exists in web app package
2. Backend URL typo in config → Verify `https://up2d8.azurewebsites.net` is correct
3. Backend not responding → Test backend health directly first

**Fix**:
- Redeploy Static Web App workflow
- Check `staticwebapp.config.json` is in `packages/web-app/` directory

### Issue 6: Email Notifications Not Received
**Symptoms**: Workflows complete but no email arrives

**Likely Causes**:
1. GitHub secrets not configured → Revisit Phase 2 (step 4)
2. Gmail app password incorrect → Regenerate and update secret
3. Email in spam → Check spam folder
4. SMTP rate limiting → Gmail limits sending rate

**Fix**:
- Test with manual workflow run
- Check GitHub Actions logs for email step errors
- Use alternative SMTP provider if Gmail doesn't work

---

## Rollback Procedures

### Backend API Rollback
1. Azure Portal → App Services → `up2d8` → **Deployment Center**
2. **Logs** tab → Find previous successful deployment
3. Click **Redeploy** on that deployment

### Function App Rollback
1. Azure Portal → Function App → `up2d8-function-app` → **Deployment Center**
2. **Logs** tab → Find previous successful deployment
3. Click **Redeploy**

### Static Web App Rollback
1. GitHub → Repository → **Actions** → **Deploy Static Web App**
2. Find previous successful workflow run
3. Click **Re-run all jobs**

### Code Rollback (Git)
```bash
# Find the commit to revert to
git log --oneline

# Revert to previous commit
git revert <commit-hash>

# Push changes
git push origin main

# Re-run appropriate workflow
```

---

## Monitoring & Maintenance

### Daily Health Checks
- Backend API: `https://up2d8.azurewebsites.net/api/health`
- Function App: Azure Portal → Monitor → Invocations
- Web App: Open homepage, test login

### Azure Portal Quick Links
- **Application Insights**: View logs, performance metrics, errors
- **Log Stream**: Real-time log viewing for debugging
- **Metrics**: CPU, Memory, Request counts
- **Alerts**: Configure alerts for failures, high CPU, etc.

### Scheduled Function Verification
Check these run as expected:
- **08:00 UTC Daily**: DailyArticleScraper (RSS feeds)
- **09:00 UTC Daily**: NewsletterGenerator (Email digests)
- **00:00 UTC Sundays**: DataArchival (Old data cleanup)

### Cost Monitoring
Navigate to: Azure Portal → Cost Management + Billing → Cost analysis
- Expected monthly cost: ~$50-100 (depends on usage)
- Main costs: App Service Plans, Cosmos DB, Functions execution

---

## Next Steps

### Optional Enhancements
1. **Custom Domain**: Add custom domain to Static Web App
2. **Staging Environments**: Create staging slots for App Service and Functions
3. **CI/CD on Push**: Change workflows to trigger on push to `main` (instead of manual)
4. **Monitoring Alerts**: Set up Azure Monitor alerts for failures
5. **Application Insights**: Configure structured logging and distributed tracing
6. **CDN**: Add Azure Front Door for better performance
7. **Backup Strategy**: Configure automated backups for Cosmos DB

### Development Workflow
1. Make code changes locally
2. Test locally (backend + frontend)
3. Commit and push to GitHub
4. Manually trigger appropriate workflow(s)
5. Wait for deployment confirmation email
6. Test production deployment
7. Monitor for issues

---

## Support Resources

### Documentation
- Azure App Service: https://learn.microsoft.com/en-us/azure/app-service/
- Azure Functions: https://learn.microsoft.com/en-us/azure/azure-functions/
- Static Web Apps: https://learn.microsoft.com/en-us/azure/static-web-apps/
- GitHub Actions: https://docs.github.com/en/actions

### Troubleshooting Tools
- **Azure CLI**: `az webapp log tail --name up2d8 --resource-group personal-rg`
- **Function Logs**: `az functionapp log tail --name up2d8-function-app --resource-group personal-rg`
- **Application Insights Query**: Azure Portal → Application Insights → Logs

---

## Deployment Checklist

Use this checklist for each deployment:

### Pre-Deployment
- [ ] Code changes committed and pushed
- [ ] Local tests pass
- [ ] GitHub secrets verified (if first time)
- [ ] Azure Portal configurations verified (if changed)

### Deployment
- [ ] Run Backend API workflow (if backend changed)
- [ ] Wait for Backend completion and verify health
- [ ] Run Function App workflow (if functions changed)
- [ ] Wait for Functions completion and verify
- [ ] Run Static Web App workflow (if frontend changed)
- [ ] Wait for Web App completion and verify

### Post-Deployment
- [ ] Test backend health endpoint
- [ ] Test web app homepage loads
- [ ] Test login flow
- [ ] Test one feature from each page (Dashboard, Feeds, Chat, Settings)
- [ ] Check Application Insights for errors
- [ ] Monitor email for deployment notification

### Issues Encountered
- [ ] Document any issues and resolutions
- [ ] Update this guide if new patterns discovered

---

**Deployment Guide Version**: 1.0.0
**Last Updated**: 2025-11-09
**Maintained By**: UP2D8 Development Team
