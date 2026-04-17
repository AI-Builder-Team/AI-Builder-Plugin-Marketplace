# API Reference

Source: https://support.read.ai/hc/en-us/articles/49381161088659

Read AI REST API — open beta. Base URL: `https://api.read.ai/`

## Authentication

All endpoints require Bearer token authentication.

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Meeting States

- **Active Meeting**: In progress. `end_time_ms` is null.
- **Ended Meeting**: Completed. `end_time_ms` has a value.
- **Live-Enabled Meeting**: Real-time data capture enabled. `live_enabled: true`.

## Endpoints

### 1. List Meetings

`GET /v1/meetings`

Returns paginated list of meetings in reverse chronological order (newest first).

**Query Parameters:**

| Name | Type | Description |
|------|------|-------------|
| limit | int | Number of results. Default 10, max 10 |
| start_time_ms.gt | int | Meetings where start_time_ms > value |
| start_time_ms.gte | int | Meetings where start_time_ms >= value |
| start_time_ms.lt | int | Meetings where start_time_ms < value |
| start_time_ms.lte | int | Meetings where start_time_ms <= value |
| cursor | str | Cursor for pagination (ID of last object from previous page) |
| expand[] | array | Fields to expand |

**Example:**
```bash
curl "https://api.read.ai/v1/meetings?limit=5&start_time_ms.gte=1733700000000" \
  -H "Authorization: Bearer sk_test_123" \
  -H "Accept: application/json"
```

**Response:**
```json
{
  "object": "list",
  "url": "/v1/meetings",
  "has_more": false,
  "data": [
    {
      "id": "01HFYH0A6JM4R7MZ2E6X5T9BNP",
      "start_time_ms": 1733800000000,
      "end_time_ms": 1733803600000,
      "scheduled_start_time_ms": 1733799800000,
      "scheduled_end_time_ms": 1733803400000,
      "participants": [
        {
          "name": "Alice Example",
          "email": "alice@example.com",
          "invited": true,
          "attended": true
        }
      ],
      "owner": {
        "name": "Alice Example",
        "email": "alice@example.com"
      },
      "title": "Weekly status sync",
      "report_url": "https://app.read.ai/analytics/meetings/01HFYH0A6JM4R7MZ2E6X5T9BNP",
      "platform": "zoom",
      "platform_id": "987654321",
      "folders": ["Weekly Sync"],
      "live_enabled": false
    }
  ]
}
```

### 2. Retrieve a Meeting

`GET /v1/meetings/{id}`

Fetch a specific meeting by ULID.

**Path Parameters:** `id` (string) — Meeting ULID

**Query Parameters:** `expand[]` (array) — Fields to expand

**Example:**
```bash
curl "https://api.read.ai/v1/meetings/01HFYH0A6JM4R7MZ2E6X5T9BNP?expand[]=summary&expand[]=metrics" \
  -H "Authorization: Bearer sk_test_123" \
  -H "Accept: application/json"
```

**Response (with expansions):**
```json
{
  "id": "01HFYH0A6JM4R7MZ2E6X5T9BNP",
  "start_time_ms": 1733800000000,
  "end_time_ms": 1733803600000,
  "participants": [...],
  "owner": {...},
  "title": "Weekly status sync",
  "report_url": "...",
  "platform": "zoom",
  "platform_id": "987654321",
  "folders": ["Weekly Sync"],
  "live_enabled": false,
  "summary": "We reviewed project timelines and assigned new action items.",
  "metrics": {
    "read_score": 0.9,
    "sentiment": 0.3,
    "engagement": 0.75
  }
}
```

### 3. Retrieve a Live Meeting

`GET /v1/meetings/{id}/live`

Real-time transcript and chapter summaries for ongoing meetings.

**Important:** Live data only available if the live dashboard is open during the meeting.

**Query Parameters:**

| Name | Type | Description |
|------|------|-------------|
| start_time_ms.gt | int | Live data where start_time_ms > value |
| start_time_ms.gte | int | Live data where start_time_ms >= value |
| expand[] | array | Only `transcript` and `chapter_summaries` available for live |

**Transcript Response Structure:**
```json
{
  "transcript": {
    "speakers": [{"name": "Alice Example"}],
    "turns": [
      {
        "speaker": {"name": "Alice Example"},
        "text": "Let's start with the project updates.",
        "start_time_ms": 1733800000000,
        "end_time_ms": 1733800005000
      }
    ],
    "text": "[Alice Example]: Let's start with the project updates."
  }
}
```

## Expandable Fields

Use `expand[]` parameter to fetch additional enriched fields (not included by default). Multiple expansions increase response time.

| Field | Description |
|-------|-------------|
| summary | Meeting summary text |
| chapter_summaries | Chapter-by-chapter summaries |
| action_items | Action items extracted |
| key_questions | Key questions raised |
| topics | Topics discussed |
| transcript | Full transcript with speakers |
| metrics | read_score, sentiment, engagement |
| recording_download | URL to download MP4 recording |

**Example:**
```bash
curl "https://api.read.ai/v1/meetings?expand[]=metrics&expand[]=transcript" \
  -H "Authorization: Bearer sk_test_123"
```

## Pagination

Cursor-based pagination. Use ID of last object from previous page as `cursor`.

| Parameter | Description |
|-----------|-------------|
| limit | Max objects to return. Default 10, max 10 |
| cursor | ID of last object from prior page |

**Response envelope:**

| Field | Type | Description |
|-------|------|-------------|
| object | str | "list" |
| url | str | Request URL |
| has_more | bool | More pages exist |
| data | array | Meeting objects |

Continue paginating until `has_more` is `false`.

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 400 | Bad Request — malformed parameters |
| 401 | Unauthorized — auth failed or missing |
| 403 | Forbidden — no permission |
| 404 | Not Found |
| 422 | Unprocessable Entity — validation failed |
| 429 | Too Many Requests — rate limited |
| 500 | Server Error |

## Rate Limits

100 requests per minute per user.
