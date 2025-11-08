# Azure Key Vault Integration Guide

This document explains how UP2D8 uses Azure Key Vault for secrets management.

## Architecture

### Production (Azure)
```
Backend/Functions → Managed Identity → Key Vault → Secrets
```

1. Application runs with System-Assigned Managed Identity
2. Identity has access policies on Key Vault
3. Application fetches secrets at runtime using Azure SDK
4. No secrets stored in environment variables or code

### Local Development
```
Developer → Azure CLI Auth → Key Vault → Secrets
```

1. Developer runs `az login` to authenticate
2. Application uses DefaultAzureCredential (falls back to Azure CLI)
3. Secrets fetched from Key Vault (same as production)
4. OR: Set secrets directly in `.env` for offline testing

## Key Vault Secrets

### Secret Names (in Key Vault)

| Secret Name | Purpose | Used By |
|-------------|---------|---------|
| `COSMOS-DB-CONNECTION-STRING-UP2D8` | MongoDB connection | Backend, Functions |
| `UP2D8-GEMINI-API-KEY` | Google Gemini API | Backend, Functions |
| `GOOGLE-CUSTOM-SEARCH-API` | Google Search API | Functions |
| `UP2D8-SMTP-KEY` | Brevo/SendGrid SMTP | Functions |
| `UP2D8-STORAGE-CONNECTION-STRING` | Azure Storage | Functions |
| `GOOGLE-CLIENT-ID` | Google OAuth | Backend |
| `GOOGLE-CLIENT-SECRET` | Google OAuth | Backend |

### Environment Variables (non-secret)

These are safe to commit and are in `.env.example`:

```bash
# Key Vault configuration
KEY_VAULT_URI=https://personal-key-vault1.vault.azure.net/
AZURE_KEY_VAULT_NAME=personal-key-vault1

# Azure resource IDs
AZURE_SUBSCRIPTION_ID=90d7fd42-6dc4-41e8-808e-b4a1e63b5a8e
AZURE_RESOURCE_GROUP_NAME=personal-rg

# Service endpoints
AZURE_BACKEND_APP_URL=https://up2d8.azurewebsites.net
AZURE_FUNCTION_APP_URL=https://up2d8-function-app.azurewebsites.net/

# Non-secret SMTP config
BREVO_SMTP_HOST=smtp-relay.brevo.com
BREVO_SMTP_PORT=587
SENDER_EMAIL=davidjmorgan26@gmail.com
```

## Backend API Key Vault Integration

The backend uses `packages/backend-api/shared/key_vault_client.py`:

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os

def get_key_vault_client():
    vault_uri = os.getenv("KEY_VAULT_URI")
    credential = DefaultAzureCredential()
    return SecretClient(vault_url=vault_uri, credential=credential)

def get_secret(secret_name: str) -> str:
    client = get_key_vault_client()
    return client.get_secret(secret_name).value
```

### Usage in Backend

```python
from shared.key_vault_client import get_secret

# Fetch MongoDB connection at runtime
mongodb_connection = get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8")

# Fetch Gemini API key
gemini_key = get_secret("UP2D8-GEMINI-API-KEY")
```

## Azure Functions Key Vault Integration

Functions use `packages/functions/shared/key_vault_client.py` (same pattern):

```python
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class KeyVaultClient:
    def __init__(self):
        vault_uri = os.getenv("KEY_VAULT_URI")
        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=vault_uri, credential=credential)
    
    def get_secret(self, secret_name: str) -> str:
        return self.client.get_secret(secret_name).value
```

### Usage in Functions

```python
from shared.key_vault_client import KeyVaultClient

kv = KeyVaultClient()

# Fetch secrets
mongodb_conn = kv.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8")
smtp_key = kv.get_secret("UP2D8-SMTP-KEY")
gemini_key = kv.get_secret("UP2D8-GEMINI-API-KEY")
```

## Local Development Setup

### Option 1: Use Key Vault (Recommended)

1. **Install Azure CLI**:
   ```bash
   # macOS
   brew install azure-cli
   
   # Windows
   winget install Microsoft.AzureCLI
   ```

2. **Login**:
   ```bash
   az login
   ```

3. **Set up .env**:
   ```bash
   cp .env.example .env
   # KEY_VAULT_URI is already set correctly
   ```

4. **Run application**:
   ```bash
   # Backend
   cd packages/backend-api
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   
   # Functions (local)
   cd packages/functions
   func start
   ```

The application will automatically use your Azure CLI credentials to fetch secrets from Key Vault.

### Option 2: Local Secrets (Offline Testing)

If you can't access Azure (offline, testing, etc.), set secrets directly in `.env`:

```bash
# .env (for local development only)
KEY_VAULT_URI=https://personal-key-vault1.vault.azure.net/

# Set secrets directly for local testing
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/
GEMINI_API_KEY=your-test-api-key
SENDGRID_API_KEY=your-test-smtp-key
```

Update code to fall back to environment variables:

```python
# Example fallback pattern
mongodb_conn = (
    get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8") 
    if is_production() 
    else os.getenv("MONGODB_CONNECTION_STRING")
)
```

## Managed Identity Setup (Production)

### Current Configuration

- **Identity ID**: `3be3ee73-9b0b-424c-848d-be1bfb4d6c2b`
- **Type**: System-Assigned Managed Identity
- **Scope**: Backend App Service + Function App

### Key Vault Access Policies

Both the Backend and Functions have "Get" and "List" permissions on Key Vault secrets.

### How It Works

1. Azure automatically injects Managed Identity credentials into the app
2. `DefaultAzureCredential()` detects Managed Identity and uses it
3. No credentials needed in code or config
4. Access controlled by Azure RBAC

### Verify Access

```bash
# Check if Function App has access
az webapp identity show \
  --name up2d8-function-app \
  --resource-group personal-rg

# Check Key Vault access policies
az keyvault show \
  --name personal-key-vault1 \
  --resource-group personal-rg
```

## Adding New Secrets

### 1. Add to Key Vault

```bash
az keyvault secret set \
  --vault-name personal-key-vault1 \
  --name NEW-SECRET-NAME \
  --value "secret-value"
```

### 2. Update .env.example

```bash
# Add reference (no value)
NEW_SECRET_NAME=
```

### 3. Update Code

```python
# Backend or Functions
new_secret = get_secret("NEW-SECRET-NAME")
```

### 4. Document in this file

Update the secrets table above.

## Troubleshooting

### Error: "Client does not have permission to get secrets"

**Solution**: Ensure Managed Identity has Key Vault access:

```bash
az keyvault set-policy \
  --name personal-key-vault1 \
  --object-id 3be3ee73-9b0b-424c-848d-be1bfb4d6c2b \
  --secret-permissions get list
```

### Error: "DefaultAzureCredential failed"

**Local Development**: Run `az login` first

**Production**: Check that Managed Identity is enabled:
```bash
az webapp identity assign \
  --name up2d8 \
  --resource-group personal-rg
```

### Error: "Secret not found"

**Check secret exists**:
```bash
az keyvault secret show \
  --vault-name personal-key-vault1 \
  --name COSMOS-DB-CONNECTION-STRING-UP2D8
```

### Local Development: Can't access Key Vault

**Fallback to environment variables**:
```python
import os
from shared.key_vault_client import get_secret

def get_mongodb_connection():
    try:
        return get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8")
    except Exception:
        # Fallback to .env for local dev
        return os.getenv("MONGODB_CONNECTION_STRING", "mongodb://localhost:27017/")
```

## Security Best Practices

1. ✅ **Never commit secrets** - Use `.gitignore` for `.env`
2. ✅ **Use Managed Identity** in production - No credentials in code
3. ✅ **Rotate secrets regularly** - Update in Key Vault only
4. ✅ **Principle of least privilege** - Only grant "Get" permission
5. ✅ **Audit access** - Monitor Key Vault logs in Azure
6. ✅ **Separate dev/prod** - Use different Key Vaults for each environment

## Key Vault URLs

- **Production**: https://personal-key-vault1.vault.azure.net/
- **Azure Portal**: https://portal.azure.com/#@/resource/subscriptions/90d7fd42-6dc4-41e8-808e-b4a1e63b5a8e/resourceGroups/personal-rg/providers/Microsoft.KeyVault/vaults/personal-key-vault1

## References

- [Azure Key Vault SDK for Python](https://docs.microsoft.com/en-us/python/api/overview/azure/keyvault-secrets-readme)
- [DefaultAzureCredential](https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential)
- [Managed Identity Overview](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview)
