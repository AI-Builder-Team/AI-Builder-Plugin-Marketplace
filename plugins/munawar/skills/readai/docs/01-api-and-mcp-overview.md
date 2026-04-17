# Read AI API and MCP Overview

Source: https://support.read.ai/hc/en-us/articles/49379985941523

Read AI now offers both a REST API and an MCP (Model Context Protocol) server, enabling programmatic access to meeting data such as transcripts, summaries, and action items. Users can connect third-party AI applications and platforms (ChatGPT, Claude, other LLM-powered tools) as MCP clients.

These capabilities are currently available as part of an **open beta**.

## Current State

- **Open Beta**: Both the API and MCP server are in open beta, accessible to all users who meet the prerequisites.
- **Core Capabilities**: Retrieve meeting reports, live transcripts, summaries, and more. Both API and MCP provide access to the same data through different means.

## Prerequisites

- If you belong to a workspace, it must have the **Downloads** option enabled in Workspace Settings > Reports & Sharing.
- Otherwise available to all users regardless of plan or workspace.

## Known Issues and Limitations

- **Authentication Complexity**: OAuth 2.1 flow requires browser-based login. No static API keys or client credentials yet. Access tokens expire after 10 minutes. Refresh tokens are single-use and rotate on each refresh (with a short grace period). Manual intervention needed if token chains break.
- **SSO Redirect**: Some users not redirected properly after SSO login. Workaround: restart OAuth process after signing in.
- **Rate Limits**: 100 requests per minute per user. HTTP 429 on exceeding.
- **Feature Gaps**: Search Copilot, Coaching, and other integration features not yet exposed via API/MCP. No audio/video upload for transcription via API.
- **Live Transcript**: Not enabled by default unless someone accesses the live dashboard. Account-level setting planned.
- **Cross-Platform Interoperability**: Some MCP clients (VS Code, Notion) have authentication issues. Compatibility testing ongoing.
- **Permissions**: Users can only retrieve data for meetings they have access to. Admins must enable global report access for workspace-wide access.

## Planned Enhancements (GA)

- Static API keys / personal access tokens
- More options for token lifetimes and refresh token grace period
- Setting to enable live transcription for all meetings
- Additional endpoints, tools, and webhook/event support
- Expanded documentation and self-serve UI
