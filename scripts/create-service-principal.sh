#!/bin/bash
#
# Create Azure Service Principal for GitHub Actions Deployment
# This script creates a service principal with contributor access to your resource group
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

RESOURCE_GROUP="personal-rg"
SP_NAME="up2d8-github-deploy"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Azure Service Principal Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get subscription ID
echo "Getting subscription information..."
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)

echo -e "${GREEN}✅ Subscription: ${SUBSCRIPTION_NAME}${NC}"
echo -e "${GREEN}✅ Subscription ID: ${SUBSCRIPTION_ID}${NC}"
echo ""

# Get resource group ID
echo "Getting resource group information..."
RG_ID="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}"
echo -e "${GREEN}✅ Resource Group: ${RESOURCE_GROUP}${NC}"
echo ""

# Create service principal
echo -e "${YELLOW}Creating service principal: ${SP_NAME}${NC}"
echo "This will have Contributor access to resource group: ${RESOURCE_GROUP}"
echo ""

# Check if service principal already exists
EXISTING_SP=$(az ad sp list --display-name "$SP_NAME" --query "[0].appId" -o tsv 2>/dev/null || echo "")

if [ -n "$EXISTING_SP" ]; then
    echo -e "${YELLOW}⚠️  Service principal '${SP_NAME}' already exists${NC}"
    echo -e "${YELLOW}   App ID: ${EXISTING_SP}${NC}"
    echo ""
    read -p "Do you want to reset its credentials? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting without changes"
        exit 0
    fi

    # Reset credentials for existing SP
    echo "Resetting credentials..."
    CREDENTIALS=$(az ad sp credential reset \
        --id "$EXISTING_SP" \
        --query "{clientId: appId, clientSecret: password, tenantId: tenant, subscriptionId: \"$SUBSCRIPTION_ID\"}" \
        -o json)
else
    # Create new service principal
    CREDENTIALS=$(az ad sp create-for-rbac \
        --name "$SP_NAME" \
        --role contributor \
        --scopes "$RG_ID" \
        --query "{clientId: appId, clientSecret: password, tenantId: tenant, subscriptionId: \"$SUBSCRIPTION_ID\"}" \
        -o json)
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Service principal created/updated successfully!${NC}"
    echo ""
else
    echo -e "${RED}❌ Failed to create service principal${NC}"
    exit 1
fi

# Display the credentials in GitHub Actions format
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}GitHub Secret Configuration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Copy the JSON below and add it as a GitHub secret:${NC}"
echo ""
echo -e "${GREEN}Secret Name: ${BLUE}AZURE_CREDENTIALS${NC}"
echo ""
echo -e "${GREEN}Secret Value (copy everything between the lines):${NC}"
echo "----------------------------------------"
echo "$CREDENTIALS" | jq .
echo "----------------------------------------"
echo ""

# Save to file for easy copying
CREDS_FILE="/tmp/azure-credentials.json"
echo "$CREDENTIALS" | jq . > "$CREDS_FILE"
echo -e "${BLUE}💾 Credentials also saved to: ${CREDS_FILE}${NC}"
echo ""

# Instructions
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Copy the JSON above"
echo "2. Go to: GitHub → Repository → Settings → Secrets and variables → Actions"
echo "3. Click 'New repository secret'"
echo "4. Name: AZURE_CREDENTIALS"
echo "5. Value: Paste the JSON"
echo ""

# Verify permissions
echo -e "${BLUE}Verifying permissions...${NC}"
CLIENT_ID=$(echo "$CREDENTIALS" | jq -r .clientId)

# Wait a moment for Azure AD to propagate
sleep 5

ROLE_ASSIGNMENT=$(az role assignment list \
    --assignee "$CLIENT_ID" \
    --scope "$RG_ID" \
    --query "[?roleDefinitionName=='Contributor'].{Role:roleDefinitionName, Scope:scope}" \
    -o table)

if [ -n "$ROLE_ASSIGNMENT" ]; then
    echo -e "${GREEN}✅ Contributor role verified${NC}"
    echo "$ROLE_ASSIGNMENT"
else
    echo -e "${YELLOW}⚠️  Role assignment may take a moment to propagate${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Service Principal Details:"
echo "  Name: $SP_NAME"
echo "  Client ID: $CLIENT_ID"
echo "  Scope: $RESOURCE_GROUP (Contributor)"
echo ""
echo "Remember to add the AZURE_CREDENTIALS secret to GitHub!"
