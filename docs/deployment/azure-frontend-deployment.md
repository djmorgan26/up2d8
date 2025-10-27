# Deploying Frontend to Azure Static Web Apps (Free Tier)

This guide shows you how to host your React frontend on Azure Static Web Apps using the **free tier**.

## What is Azure Static Web Apps?

Azure Static Web Apps is a service that:
- ✅ **FREE hosting** for static sites
- ✅ **Free SSL/HTTPS** certificates
- ✅ Global CDN for fast loading
- ✅ **Automatic deployments** from GitHub
- ✅ Supports React, Vue, Angular, and other static frameworks

### Free Tier Limits
- 100GB bandwidth per month
- Unlimited requests
- Automatic HTTPS
- Custom domains supported
- Suitable for most small-to-medium applications

## Setup Instructions

### Step 1: Create Azure Static Web Apps Resource

1. Go to [Azure Portal](https://portal.azure.com)

2. Click "Create a resource"

3. Search for "Static Web Apps" and select it

4. Click "Create"

5. Fill in the details:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Create new or use existing
   - **Name**: `up2d8-frontend` (or your preferred name)
   - **Plan type**: **Free** (this is the free tier!)
   - **Region**: Choose closest to you
   - **Deployment source**: GitHub
   - **GitHub sign in**: Sign in with your GitHub account
   - **Organization**: Your GitHub username/organization
   - **Repository**: `up2d8` (or your repo name)
   - **Branch**: `main`
   - **Build Presets**: Custom
   - **App location**: `frontend`
   - **Output location**: `dist` (Vite build output)
   - **API location**: Leave empty

6. Click "Review + create" then "Create"

### Step 2: Wait for Initial Deployment

Azure will automatically:
- Create a GitHub Actions workflow
- Generate a deployment token
- Trigger the first deployment

This takes 5-10 minutes.

### Step 3: Get Your App URL

After deployment completes:

1. Go to your Static Web App in Azure Portal
2. Find the **URL** field (e.g., `https://your-app-name.azurestaticapps.net`)
3. This is your live frontend URL!

### Step 4: Update API Endpoint (Important)

Update your frontend API configuration to point to your deployed backend.

Edit `frontend/src/lib/api.ts` and update the API URL:

```typescript
const API_URL = import.meta.env.PROD 
  ? 'https://your-backend-function-app.azurewebsites.net'  // Production
  : 'http://localhost:8000';  // Development
```

### Step 5: Configure Custom Domain (Optional)

1. In Azure Portal, go to your Static Web App
2. Click "Custom domains" in the left menu
3. Click "Add" and follow the prompts

## Environment Variables

If your frontend needs environment variables:

1. In Azure Portal, go to your Static Web App
2. Click "Configuration" in the left menu
3. Add application settings under "Application settings"
4. Reference them in your code with `import.meta.env.VITE_YOUR_VARIABLE`

## Automatic Deployments

Every push to `main` branch that changes files in the `frontend/` directory will automatically trigger a new deployment.

To manually trigger:
1. Go to Actions tab in GitHub
2. Select "Deploy Frontend to Azure Static Web Apps"
3. Click "Run workflow"

## Monitoring & Costs

**Free Tier Monitoring:**
- Go to Azure Portal → Your Static Web App → "Usage"
- Track bandwidth usage
- Monitor requests

**Costs:**
- Free tier includes 100GB bandwidth per month
- Over limit: $0.15 per GB
- Most small apps won't exceed this

## Troubleshooting

### Build Fails
- Check GitHub Actions logs in the Actions tab
- Ensure `frontend/package.json` has correct build script
- Verify Node.js version (should be 18+)

### Page Not Found on Refresh
- Ensure `staticwebapp.config.json` exists (already created)
- This handles React Router routing

### API Calls Fail
- Update CORS settings on backend
- Check API URL in frontend configuration
- Ensure backend is deployed and accessible

## Resources

- [Azure Static Web Apps Documentation](https://docs.microsoft.com/azure/static-web-apps/)
- [Pricing](https://azure.microsoft.com/pricing/details/app-service/static/) (Scroll to Static Web Apps)
- [Free Tier Details](https://azure.microsoft.com/free/)
