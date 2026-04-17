# MCP Server

Source: https://support.read.ai/hc/en-us/articles/49381158409491

The Read AI MCP server is a **remote MCP (Model Context Protocol) server** allowing AI assistants to access Read AI capabilities through a standardized interface. Currently in open beta.

## Server Details

| Property | Value |
|----------|-------|
| Server URI | `https://api.read.ai/mcp` |
| Authentication | OAuth 2.1 (sign in with Read AI account) |
| Type | Remote MCP Server |
| Transport | Streamable HTTP |

## Compatible MCP Clients

- ChatGPT
- Claude Desktop and Web
- Claude Code
- Other MCP-compatible clients

## Connecting in ChatGPT

Requires developer mode enabled.

1. Go to ChatGPT Settings
2. Navigate to Apps → Advanced settings → Developer Mode
3. Enable Developer Mode
4. Click Create App
5. Enter server URI: `https://api.read.ai/mcp`
6. Select OAuth as authentication method
7. Sign in to Read AI account

## Connecting in Claude

### Team and Enterprise Plans

Admin setup (Primary Owners/Owners only):
1. Admin settings → Connectors
2. Add custom connector
3. Server URL: `https://api.read.ai/mcp`
4. Optional: Advanced settings for OAuth Client ID and Secret
5. Click Add

Individual users then connect and authenticate separately.

### Pro and Max Plans

1. Settings → Connectors
2. Add custom connector
3. Server URL: `https://api.read.ai/mcp`
4. Optional: OAuth Client ID and Secret in Advanced settings
5. Sign in to Read AI
6. Click Add

## Available Tools

### 1. Get Meeting by ID

Retrieve comprehensive info about a specific meeting using the meeting ULID.

**What you can retrieve:**
- Basic metadata (title, start/end times, platform, report URL)
- Participants with attendance status
- Summary
- Chapter summaries
- Action items
- Key questions
- Topics
- Full transcript with speaker identification
- Metrics
- URL to download meeting recording as MP4

### 2. List Meetings

Browse and filter meeting history with date-range filtering and pagination.

**What you can do:**
- Browse recent meetings (up to 10 per page)
- Filter meetings by date range
- Paginate through large collections
- Includes same detailed information as Get Meeting by ID for each meeting
