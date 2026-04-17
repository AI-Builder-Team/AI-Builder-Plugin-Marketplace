# Read AI API Reference Documents

Fetched: 2026-04-01 from Read AI support center and web research.

## Documents

| File | Topic | Source |
|------|-------|--------|
| [01-api-and-mcp-overview.md](01-api-and-mcp-overview.md) | Overview, beta status, prerequisites, known limitations | support.read.ai/articles/49379985941523 |
| [02-authentication.md](02-authentication.md) | OAuth 2.1 flow, client registration, token management | support.read.ai/articles/49380809380371 |
| [03-api-reference.md](03-api-reference.md) | REST API endpoints, request/response schemas, pagination | support.read.ai/articles/49381161088659 |
| [04-mcp-server.md](04-mcp-server.md) | MCP server setup, compatible clients, available tools | support.read.ai/articles/49381158409491 |
| [05-webhooks.md](05-webhooks.md) | Webhook setup, triggers, payload, verification | Various support docs |

## Key URLs

| Purpose | URL |
|---------|-----|
| API Base | `https://api.read.ai/v1/` |
| MCP Server | `https://api.read.ai/mcp` |
| OAuth Registration | `https://api.read.ai/oauth/register` |
| OAuth UI | `https://api.read.ai/oauth/ui` |
| Token Endpoint | `https://authn.read.ai/oauth2/token` |
| Webhooks UI | `https://app.read.ai/analytics/integrations/webhooks` |

## API Summary

- **3 REST endpoints**: List Meetings, Get Meeting, Get Live Meeting
- **2 MCP tools**: List Meetings, Get Meeting by ID
- **1 webhook trigger**: meeting_end
- **Auth**: OAuth 2.1 (tokens expire in 10 min, refresh tokens rotate)
- **Rate limit**: 100 req/min/user
- **Status**: Open Beta (as of April 2026)
