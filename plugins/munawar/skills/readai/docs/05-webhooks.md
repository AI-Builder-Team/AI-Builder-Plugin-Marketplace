# Webhooks

Source: Read AI support docs and search results (no single canonical URL — webhooks page was removed/moved)

## Overview

Read AI supports webhooks for meeting event notifications. Currently only the `meeting_end` trigger is supported, with more triggers planned.

## Setup

1. Go to app.read.ai → Account menu → Apps & Integrations → Webhooks
2. Click "Add Webhook"
3. Enter a name and HTTPS URL endpoint
4. Send a test request to verify connectivity
5. Click "Create webhook"
6. A signing key is provided — store securely for request verification

## Trigger

| Trigger | Description |
|---------|-------------|
| `meeting_end` | Fires when a meeting ends (only for meetings where you have at least "viewer" access) |

More triggers planned for future releases.

## Payload

HTTP POST with JSON body:

```json
{
  "session_id": "unique-meeting-session-id",
  "trigger": "meeting_end"
}
```

The payload includes the `session_id` which can be used with the REST API to fetch full meeting data (transcript, summary, action items, etc.).

## Webhook Status

| Status | Meaning |
|--------|---------|
| Pending | Created but no real meeting has triggered it yet |
| Active | Successfully received a meeting_end event |
| Stopped | 25+ consecutive delivery failures |

## Security

- A signing key is provided at creation for verifying request authenticity
- Use HTTPS endpoints only

## Troubleshooting

- If status shows "stopped": fix endpoint, then recreate the webhook
- Test requests can be sent from the UI to verify connectivity
- Webhooks only fire for meetings where you have "viewer" access or above

## Integration with REST API

Typical pattern:
1. Webhook fires with `session_id` on meeting end
2. Use `GET /v1/meetings/{session_id}?expand[]=transcript&expand[]=summary&expand[]=action_items` to fetch full meeting data
3. Process and store as needed
