# API Keys & Authentication

Source: https://support.read.ai/hc/en-us/articles/49380809380371

Read AI API uses **OAuth 2.1** with dynamic client registration. Supports the **Authorization Code** grant with refresh tokens.

## Flow Overview

1. Register an OAuth 2.1 client using dynamic client registration
2. Obtain an authorization code via the Authorization Code flow (browser)
3. Exchange the authorization code for access and refresh tokens
4. Use the access token to make API requests
5. Refresh the access token as needed using the refresh token

## Step 1: Register Your OAuth Client

```bash
curl -X POST https://api.read.ai/oauth/register \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "My App",
    "redirect_uris": ["https://api.read.ai/oauth/ui"],
    "grant_types": ["authorization_code", "refresh_token"],
    "response_types": ["code"],
    "scope": "openid email offline_access profile meeting:read mcp:execute",
    "token_endpoint_auth_method": "client_secret_basic"
  }'
```

Response includes `client_id` and `client_secret` — save immediately, cannot be retrieved later.

### Scopes

- `openid` — OpenID Connect
- `email` — Email access
- `offline_access` — Refresh tokens
- `profile` — Profile info
- `meeting:read` — Read meeting data
- `mcp:execute` — MCP server access

## Step 2: Obtain Authorization Code (Browser)

Navigate to https://api.read.ai/oauth/ui, enter client ID and secret, click Start OAuth Flow. Sign in to Read AI, consent to scopes, receive authorization code.

## Step 3: Exchange Code for Tokens

```bash
curl -X POST https://authn.read.ai/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Authorization: Basic $(echo -n 'CLIENT_ID:CLIENT_SECRET' | base64)" \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE" \
  -d "redirect_uri=https://api.read.ai/oauth/ui" \
  -d "code_verifier=VERIFIER"
```

Response:
```json
{
  "access_token": "...",
  "expires_in": 599,
  "id_token": "...",
  "refresh_token": "...",
  "scope": "openid profile email meeting:read mcp:execute offline_access",
  "token_type": "bearer"
}
```

## Step 4: Use Access Token

```bash
curl -X GET "https://api.read.ai/v1/meetings" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Accept: application/json"
```

Test endpoint: `GET https://api.read.ai/oauth/test-token-with-scopes`

## Step 5: Refresh Token

Access tokens expire after **10 minutes**. Refresh tokens are **single-use** and rotate on every use (with short grace period for concurrency).

```bash
curl -X POST https://authn.read.ai/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "CLIENT_ID:CLIENT_SECRET" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=YOUR_REFRESH_TOKEN"
```

**Important**: Persist the new refresh token returned; discard the old one.

## Key URLs

| Purpose | URL |
|---------|-----|
| Client Registration | `https://api.read.ai/oauth/register` |
| OAuth UI | `https://api.read.ai/oauth/ui` |
| Token Endpoint | `https://authn.read.ai/oauth2/token` |
| Token Test | `https://api.read.ai/oauth/test-token-with-scopes` |
| API Base | `https://api.read.ai/v1/` |
| MCP Server | `https://api.read.ai/mcp` |
