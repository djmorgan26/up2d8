#!/bin/bash
#
# Azure Configuration Setup Script for UP2D8
# This script verifies and configures all Azure resources with required environment variables
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Azure Resource Names
RESOURCE_GROUP="personal-rg"
BACKEND_APP_NAME="up2d8"
FUNCTION_APP_NAME="up2d8-function-app"
STATIC_WEB_APP_NAME="up2d8-web"
KEY_VAULT_NAME="personal-key-vault1"

# Configuration Values
ENTRA_TENANT_ID="6f69caf6-bea0-4a54-a20c-7469005eadf4"
ENTRA_CLIENT_ID="2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97"
ENTRA_AUDIENCE="api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97"
KEY_VAULT_URI="https://personal-key-vault1.vault.azure.net/"
MONGODB_DATABASE="up2d8"
STATIC_WEB_APP_URL="https://gray-wave-00bdfc60f.3.azurestaticapps.net"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}UP2D8 Azure Configuration Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if command succeeded
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1 - FAILED${NC}"
        exit 1
    fi
}

# Function to set app setting
set_app_setting() {
    local app_name=$1
    local setting_name=$2
    local setting_value=$3
    local app_type=$4  # "webapp" or "functionapp"

    if [ "$app_type" = "webapp" ]; then
        az webapp config appsettings set \
            --name "$app_name" \
            --resource-group "$RESOURCE_GROUP" \
            --settings "$setting_name=$setting_value" \
            --output none
    else
        az functionapp config appsettings set \
            --name "$app_name" \
            --resource-group "$RESOURCE_GROUP" \
            --settings "$setting_name=$setting_value" \
            --output none
    fi
}

#
# 1. Configure Backend API (App Service)
#
echo -e "${YELLOW}[1/4] Configuring Backend API: ${BACKEND_APP_NAME}${NC}"

echo "Setting environment variables..."
set_app_setting "$BACKEND_APP_NAME" "ENTRA_TENANT_ID" "$ENTRA_TENANT_ID" "webapp"
set_app_setting "$BACKEND_APP_NAME" "ENTRA_CLIENT_ID" "$ENTRA_CLIENT_ID" "webapp"
set_app_setting "$BACKEND_APP_NAME" "ENTRA_AUDIENCE" "$ENTRA_AUDIENCE" "webapp"
set_app_setting "$BACKEND_APP_NAME" "KEY_VAULT_URI" "$KEY_VAULT_URI" "webapp"
set_app_setting "$BACKEND_APP_NAME" "MONGODB_DATABASE" "$MONGODB_DATABASE" "webapp"
set_app_setting "$BACKEND_APP_NAME" "SCM_DO_BUILD_DURING_DEPLOYMENT" "true" "webapp"
check_status "Backend environment variables configured"

echo "Setting startup command..."
az webapp config set \
    --name "$BACKEND_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --startup-file "python -m uvicorn main:app --host 0.0.0.0 --port 8000" \
    --output none
check_status "Backend startup command configured"

echo "Configuring CORS..."
az webapp cors add \
    --name "$BACKEND_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --allowed-origins "http://localhost:5173" "http://localhost:8080" "$STATIC_WEB_APP_URL" \
    --output none 2>/dev/null || echo "CORS already configured"

az webapp cors remove \
    --name "$BACKEND_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --allowed-origins "*" \
    --output none 2>/dev/null || echo "Wildcard CORS not present"

check_status "Backend CORS configured"

echo "Enabling Managed Identity..."
az webapp identity assign \
    --name "$BACKEND_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --output none 2>/dev/null || echo "Already enabled"
BACKEND_IDENTITY=$(az webapp identity show \
    --name "$BACKEND_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query principalId -o tsv)
check_status "Backend Managed Identity enabled (Object ID: $BACKEND_IDENTITY)"

#
# 2. Configure Function App
#
echo ""
echo -e "${YELLOW}[2/4] Configuring Function App: ${FUNCTION_APP_NAME}${NC}"

echo "Setting environment variables..."
set_app_setting "$FUNCTION_APP_NAME" "KEY_VAULT_URI" "$KEY_VAULT_URI" "functionapp"
set_app_setting "$FUNCTION_APP_NAME" "BACKEND_API_URL" "https://${BACKEND_APP_NAME}.azurewebsites.net" "functionapp"
set_app_setting "$FUNCTION_APP_NAME" "MONGODB_DATABASE" "$MONGODB_DATABASE" "functionapp"
set_app_setting "$FUNCTION_APP_NAME" "BREVO_SMTP_HOST" "smtp-relay.brevo.com" "functionapp"
set_app_setting "$FUNCTION_APP_NAME" "BREVO_SMTP_PORT" "587" "functionapp"
set_app_setting "$FUNCTION_APP_NAME" "BREVO_SMTP_USER" "9a9964001@smtp-brevo.com" "functionapp"
set_app_setting "$FUNCTION_APP_NAME" "SENDER_EMAIL" "davidjmorgan26@gmail.com" "functionapp"
check_status "Function App environment variables configured"

echo "Enabling Managed Identity..."
az functionapp identity assign \
    --name "$FUNCTION_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --output none 2>/dev/null || echo "Already enabled"
FUNCTION_IDENTITY=$(az functionapp identity show \
    --name "$FUNCTION_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query principalId -o tsv)
check_status "Function App Managed Identity enabled (Object ID: $FUNCTION_IDENTITY)"

#
# 3. Grant Key Vault Access (RBAC-based)
#
echo ""
echo -e "${YELLOW}[3/4] Configuring Key Vault Access (RBAC)${NC}"

# Get Key Vault resource ID
KEY_VAULT_ID=$(az keyvault show \
    --name "$KEY_VAULT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query id -o tsv)

echo "Granting Backend API access to Key Vault..."
az role assignment create \
    --assignee "$BACKEND_IDENTITY" \
    --role "Key Vault Secrets User" \
    --scope "$KEY_VAULT_ID" \
    --output none 2>/dev/null || echo "Role already assigned"
check_status "Backend has Key Vault Secrets User role"

echo "Granting Function App access to Key Vault..."
az role assignment create \
    --assignee "$FUNCTION_IDENTITY" \
    --role "Key Vault Secrets User" \
    --scope "$KEY_VAULT_ID" \
    --output none 2>/dev/null || echo "Role already assigned"
check_status "Function App has Key Vault Secrets User role"

#
# 4. Configure Static Web App
#
echo ""
echo -e "${YELLOW}[4/4] Configuring Static Web App: ${STATIC_WEB_APP_NAME}${NC}"

echo "Setting environment variables..."
az staticwebapp appsettings set \
    --name "$STATIC_WEB_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --setting-names \
        VITE_APP_ENTRA_CLIENT_ID="$ENTRA_CLIENT_ID" \
        VITE_APP_ENTRA_TENANT_ID="$ENTRA_TENANT_ID" \
        VITE_APP_ENTRA_REDIRECT_URI="$STATIC_WEB_APP_URL" \
        VITE_APP_ENTRA_API_SCOPE="$ENTRA_AUDIENCE/access_as_user" \
    --output none
check_status "Static Web App environment variables configured"

#
# Summary
#
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Configuration Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Set up GitHub Secrets (if not already done):"
echo "   - AZURE_WEBAPP_PUBLISH_PROFILE"
echo "   - AZURE_FUNCTIONAPP_PUBLISH_PROFILE"
echo "   - AZURE_STATIC_WEB_APPS_API_TOKEN"
echo ""
echo "2. Update App Registration redirect URI:"
echo "   - Go to: Entra ID → App registrations → up2d8"
echo "   - Add SPA redirect: $STATIC_WEB_APP_URL"
echo ""
echo "3. Run deployments in order:"
echo "   a. GitHub Actions → Deploy Backend API"
echo "   b. GitHub Actions → Deploy Function App"
echo "   c. GitHub Actions → Deploy Static Web App"
echo ""
echo -e "${BLUE}Verification URLs:${NC}"
echo "   Backend:  https://${BACKEND_APP_NAME}.azurewebsites.net/api/health"
echo "   Functions: https://${FUNCTION_APP_NAME}.azurewebsites.net"
echo "   Web App:   ${STATIC_WEB_APP_URL}"
echo ""
