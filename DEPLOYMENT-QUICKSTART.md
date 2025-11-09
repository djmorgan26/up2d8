# UP2D8 Deployment Quick Start

**Time Required**: ~15 minutes
**Prerequisites**: Azure CLI installed and logged in (`az login`)

---

## ✅ Current Status

Your Azure resources exist and some environment variables are already configured:
- Backend API has environment variables ✅
- Backend startup command needs update ⚠️ (currently set to wrong path)
- CORS needs production URLs ⚠️
- Managed Identities need to be enabled ⚠️
- Key Vault access needs to be granted ⚠️

---

## 🚀 Quick Deployment Steps

### Step 1: Run Automated Setup (2 minutes)

```bash
cd /Users/davidmorgan/Documents/Repositories/up2d8
./scripts/setup-azure-config.sh
```

**What this does**:
- ✅ Fixes backend startup command (from wrong path to correct: `main:app`)
- ✅ Configures all environment variables (Backend, Functions, Static Web App)
- ✅ Enables Managed Identities
- ✅ Grants Key Vault access
- ✅ Sets up CORS with production URLs

**Expected output**: Green checkmarks for each step

---

### Step 2: Add GitHub Secrets (5 minutes)

Navigate to: **GitHub → Repository → Settings → Secrets and variables → Actions**

**Create 3 secrets**:

1. **`AZURE_WEBAPP_PUBLISH_PROFILE`**
   - Azure Portal → App Services → `up2d8` → Deployment Center
   - Click "Manage publish profile" → Download → Copy entire XML content → Paste

2. **`AZURE_FUNCTIONAPP_PUBLISH_PROFILE`**
   - Azure Portal → Function App → `up2d8-function-app` → Deployment Center
   - Click "Manage publish profile" → Download → Copy entire XML content → Paste

3. **`AZURE_STATIC_WEB_APPS_API_TOKEN`**
   - Azure Portal → Static Web Apps → `up2d8-web` → Overview
   - Click "Manage deployment token" → Copy token → Paste

---

### Step 3: Update App Registration (2 minutes)

1. Navigate to: **Azure Portal → Entra ID → App registrations → up2d8**
2. Left menu → **Authentication**
3. Under "Single-page application" → **+ Add URI**
4. Add: `https://gray-wave-00bdfc60f.3.azurestaticapps.net`
5. Click **Save**

---

### Step 4: Deploy Services (6 minutes)

**Deploy in this order** (GitHub → Actions → Run workflow):

1. **Deploy Backend API** (3 min)
   - Workflow: "Deploy Backend API"
   - Wait for green checkmark
   - Verify: `https://up2d8.azurewebsites.net/api/health` returns `{"status": "healthy"}`

2. **Deploy Function App** (2 min)
   - Workflow: "Deploy Function App"
   - Wait for green checkmark
   - Check Azure Portal → Functions (should see 7 functions)

3. **Deploy Static Web App** (1 min)
   - Workflow: "Deploy Static Web App"
   - Wait for green checkmark
   - Open: `https://gray-wave-00bdfc60f.3.azurestaticapps.net`

---

## ✅ Verification

1. **Backend Health**: https://up2d8.azurewebsites.net/api/health → `{"status": "healthy"}`
2. **Swagger Docs**: https://up2d8.azurewebsites.net/docs → Interactive API documentation
3. **Web App**: https://gray-wave-00bdfc60f.3.azurestaticapps.net → Login and test features
4. **Functions**: Azure Portal → Function App → Functions → See 7 functions listed

---

## 🎯 Test Your Deployment

1. Open web app: https://gray-wave-00bdfc60f.3.azurestaticapps.net
2. Click **Login** → Sign in with Microsoft
3. Complete onboarding (select topics)
4. Test features:
   - **Dashboard**: Should load (empty initially)
   - **Feeds**: Add RSS feed (e.g., `https://feeds.bbci.co.uk/news/rss.xml`)
   - **Chat**: Ask "What's happening in tech?" → Should get AI response with sources
   - **Settings**: View preferences

---

## 🔧 If Something Goes Wrong

### Backend API issues
```bash
# View logs
az webapp log tail --name up2d8 --resource-group personal-rg

# Check startup command
az webapp config show --name up2d8 --resource-group personal-rg --query "appCommandLine"

# Expected: "python -m uvicorn main:app --host 0.0.0.0 --port 8000"
```

### Function App issues
```bash
# View logs
az functionapp log tail --name up2d8-function-app --resource-group personal-rg

# Check settings
az functionapp config appsettings list --name up2d8-function-app --resource-group personal-rg
```

### CORS errors in browser
- Check browser console for specific error
- Verify backend CORS includes: `https://gray-wave-00bdfc60f.3.azurestaticapps.net`
- Redeploy backend if CORS was changed

### Login not working
- Verify redirect URI was added to App Registration
- Check browser console for MSAL errors
- Ensure Static Web App environment variables are set

---

## 📊 What Each Service Does

**Backend API** (`up2d8.azurewebsites.net`):
- REST API for all data operations
- JWT authentication with Entra ID
- Connects to Cosmos DB and Key Vault
- Provides Swagger documentation

**Function App** (`up2d8-function-app`):
- DailyArticleScraper: Fetches RSS feeds at 08:00 UTC
- NewsletterGenerator: Sends email digests at 09:00 UTC
- CrawlerWorker: Web page content extraction
- Other background tasks

**Static Web App** (`gray-wave-00bdfc60f.3.azurestaticapps.net`):
- React frontend (Dashboard, Feeds, Chat, Settings)
- Proxies `/api/*` requests to Backend API
- Handles user authentication with MSAL

---

## 🎉 Success Criteria

- ✅ Backend health check returns 200
- ✅ Swagger docs accessible
- ✅ Web app loads and login works
- ✅ Can add RSS feed successfully
- ✅ Chat returns AI responses with web search sources
- ✅ No CORS errors in browser console
- ✅ Function App shows 7 functions in Azure Portal

---

## 📚 Full Documentation

See **DEPLOYMENT.md** for:
- Detailed troubleshooting
- Manual setup instructions (if script fails)
- Rollback procedures
- Monitoring and maintenance
- Common issues and solutions

---

**Need Help?** Check logs in Azure Portal → Application Insights or use the Azure CLI commands above.
