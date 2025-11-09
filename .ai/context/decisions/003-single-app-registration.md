---
type: decision
status: accepted
date: 2025-11-08
deciders: djmorgan26, Claude
---

# ADR 003: Single Entra ID App Registration for Frontend and Backend

## Context

When implementing Entra ID (Azure AD) authentication for a web application with a separate backend API, there are two primary architectural approaches:

1. **Single App Registration:** Frontend and backend share one app registration
2. **Separate Registrations:** Frontend has its own registration, backend has its own

The UP2D8 monorepo has:
- Web frontend (`packages/web-app`) - React SPA
- Backend API (`packages/backend-api`) - FastAPI REST API
- Future mobile app (`packages/mobile-app`) - React Native

## Decision

Use a **single Entra ID app registration** for both web frontend and backend API.

**App Registration Details:**
- Name: `up2d8-app-registration`
- Client ID: `2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97`
- Tenant ID: `6f69caf6-bea0-4a54-a20c-7469005eadf4`
- API Scope: `api://2b5f5cca-a081-43bc-9ac9-8fdfd5ca0d97/access_as_user`

**Configuration:**
- **Platform:** Single-page application (SPA) for web frontend
- **Expose API:** API scope `access_as_user` for backend validation
- **Token Issuance:** Access tokens and ID tokens enabled

## Rationale

### Advantages of Single Registration

1. **Simplicity:**
   - One set of credentials to manage
   - Single configuration in Azure Portal
   - Easier to understand for personal project

2. **Token Flow:**
   - Frontend requests token with scope `api://{CLIENT_ID}/access_as_user`
   - Backend validates token was issued for its API (same CLIENT_ID)
   - Clean, straightforward flow

3. **Maintenance:**
   - Fewer secrets to rotate
   - Single source of truth for configuration
   - Less complexity in deployment

4. **Standard Pattern:**
   - Common approach for SPAs with dedicated backend
   - Well-documented in Microsoft docs
   - Aligns with OAuth 2.0 public client + resource server pattern

### Why Not Separate Registrations?

**Separate registrations would require:**
- Frontend registration (public client)
- Backend registration (web API)
- Frontend requesting permission to backend API
- More complex configuration in Azure Portal
- Additional maintenance overhead

**When to use separate:**
- Backend API is shared by multiple frontends (not our case)
- Different teams manage frontend vs backend (not our case)
- Strict security boundary needed (overkill for personal project)
- Multiple backend services with different scopes (not yet needed)

## Consequences

### Positive

- ✅ Simple configuration and deployment
- ✅ Easy to understand and debug
- ✅ Single set of environment variables
- ✅ Fast to implement and iterate
- ✅ Consistent user experience

### Negative

- ⚠️ Harder to migrate if we need separate registrations later
- ⚠️ All frontends (web, mobile) share same client ID
- ⚠️ Cannot have different token lifetimes for different clients

### Neutral

- 🔄 If we add more backend services, we can create new app registrations with separate scopes
- 🔄 Mobile app can use same registration with different platform config (mobile redirect URI)

## Implementation Notes

**Frontend uses:**
- MSAL.js library (@azure/msal-browser, @azure/msal-react)
- Requests scope: `api://{CLIENT_ID}/access_as_user`
- Stores tokens in localStorage

**Backend uses:**
- fastapi-azure-auth library
- Validates tokens using same CLIENT_ID as audience
- Extracts user claims (sub, email, name, oid)

**Configuration files:**
- `packages/web-app/.env` - Frontend config
- `packages/backend-api/.env` - Backend config
- `AUTH_SETUP.md` - Setup documentation

## Alternatives Considered

### Alternative 1: Separate Registrations

**Config:**
- Frontend registration: `up2d8-frontend` (SPA)
- Backend registration: `up2d8-api` (Web API)
- Frontend requests permission to backend

**Rejected because:**
- Added complexity without clear benefit for personal project
- More configuration to maintain
- Harder to debug auth issues
- Overkill for current needs

**When to reconsider:**
- Backend API becomes shared by multiple external clients
- Need different security policies for different clients
- Compliance requirements demand separation

### Alternative 2: Backend Client Secret (Confidential Client)

**Config:**
- Backend has client secret
- Frontend authenticates, backend validates with secret

**Rejected because:**
- Backend doesn't need to authenticate itself (it validates user tokens)
- Adds secret management complexity
- Public client + resource server pattern is sufficient
- No on-behalf-of flow needed

## Verification

To verify this decision is working:

1. **Frontend can authenticate:**
   ```bash
   cd packages/web-app && npm run dev
   # Login should work, token should be in localStorage
   ```

2. **Backend validates tokens:**
   ```bash
   curl -H "Authorization: Bearer <token>" \
        http://localhost:8000/api/auth/me
   # Should return user profile
   ```

3. **Azure Portal shows:**
   - One app registration: `up2d8-app-registration`
   - SPA platform with redirect URI
   - API scope: `access_as_user`
   - Access tokens and ID tokens enabled

## Future Considerations

**If we need to change this:**

1. **Add mobile app** - Can use same registration with:
   - New platform: Mobile and desktop applications
   - Mobile redirect URI: `msauth.{bundle-id}://auth`

2. **Add separate backend services** - Can create new registrations:
   - Keep this registration for main API
   - Create separate registration for new service (e.g., up2d8-analytics-api)
   - Frontend requests both scopes as needed

3. **Migrate to separate registrations:**
   - Create new backend registration
   - Update backend configuration
   - Update frontend to request new API scope
   - Deprecate old configuration
   - Document migration in ADR

## References

- [Microsoft Docs: Single-page application scenario](https://learn.microsoft.com/en-us/entra/identity-platform/scenario-spa-overview)
- [OAuth 2.0 for Browser-Based Apps](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps)
- [Implementation: entra-id-authentication.md](.ai/knowledge/features/entra-id-authentication.md)
- [Setup Guide: AUTH_SETUP.md](../../../AUTH_SETUP.md)

## Status

**Accepted** - Implemented on 2025-11-08

This decision can be revisited if requirements change significantly (e.g., multiple backend services, external API consumers).
