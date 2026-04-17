---
name: readai
description: Access Read AI meeting transcripts, summaries, and action items via REST API
---

## How to Execute — Scripts, Not MCP

**All Read AI operations go through Python scripts in `scripts/`.**
Scripts require OAuth credentials stored at `~/.readai/` and use stdlib only (no pip).

### Script Reference

| Script | Purpose | Example |
|--------|---------|---------|
| `setup_auth.py` | Interactive OAuth setup (one-time) | `python3 scripts/setup_auth.py` |
| `token_status.py` | Check token expiration and credentials | `python3 scripts/token_status.py` |
| `list_meetings.py` | List meetings (paginated, filterable) | `python3 scripts/list_meetings.py --limit 5` |
| `get_meeting.py` | Get full meeting detail | `python3 scripts/get_meeting.py MEETING_ID --expand summary --expand transcript` |
| `get_transcript.py` | Get transcript only | `python3 scripts/get_transcript.py MEETING_ID` |
| `get_summary.py` | Get summary + chapter summaries | `python3 scripts/get_summary.py MEETING_ID` |
| `get_action_items.py` | Get action items | `python3 scripts/get_action_items.py MEETING_ID` |
| `get_live.py` | Get live meeting data (ongoing) | `python3 scripts/get_live.py MEETING_ID` |

### Script Details

All scripts accept `--raw` for full JSON output instead of compact lines.

**`list_meetings.py` options:** `--limit N` (max 10), `--after TIMESTAMP_MS`, `--before TIMESTAMP_MS`, `--cursor ID` (pagination), `--expand FIELD` (repeatable)

**`get_meeting.py` options:** `--expand FIELD` (repeatable — see expandable fields below)

**`get_live.py` options:** `--after TIMESTAMP_MS` (only data after this time)

### Expandable Fields

Pass `--expand FIELD` (repeatable) to include enriched data in responses. These fields are not returned by default and increase response time.

| Field | Description |
|-------|-------------|
| `summary` | Meeting summary text |
| `chapter_summaries` | Chapter-by-chapter summaries |
| `action_items` | Extracted action items with owners |
| `key_questions` | Key questions raised |
| `topics` | Topics discussed |
| `transcript` | Full transcript with speaker identification |
| `metrics` | read_score, sentiment, engagement |
| `recording_download` | URL to download MP4 recording |

### API Response Schemas

**Meeting object** (returned by all meeting endpoints):
```json
{
  "id": "ULID string",
  "start_time_ms": 1733800000000,
  "end_time_ms": 1733803600000,
  "scheduled_start_time_ms": 1733799800000,
  "scheduled_end_time_ms": 1733803400000,
  "participants": [
    {"name": "string", "email": "string", "invited": true, "attended": true}
  ],
  "owner": {"name": "string", "email": "string"},
  "title": "string",
  "report_url": "https://app.read.ai/analytics/meetings/...",
  "platform": "zoom|google_meet|teams",
  "platform_id": "string",
  "folders": ["string"],
  "live_enabled": false
}
```

**Transcript structure** (when expanded):
```json
{
  "speakers": [{"name": "Alice"}],
  "turns": [
    {
      "speaker": {"name": "Alice"},
      "text": "Let's start.",
      "start_time_ms": 1733800000000,
      "end_time_ms": 1733800005000
    }
  ],
  "text": "[Alice]: Let's start."
}
```

**Paginated list response:**
```json
{
  "object": "list",
  "url": "/v1/meetings",
  "has_more": true,
  "data": [ ...meeting objects... ]
}
```

Use the `id` of the last meeting in `data` as the `--cursor` value for the next page. Continue until `has_more` is `false`.

### Authentication

Read AI uses OAuth 2.1 with rotating refresh tokens. Run `setup_auth.py` once to set up:

1. Registers an OAuth client (credentials saved to `~/.readai/credentials.json`)
2. Guides through browser-based authorization flow
3. Exchanges auth code for access + refresh tokens (saved to `~/.readai/tokens.json`)

Access tokens expire after **10 minutes** — the client auto-refreshes using the refresh token. Refresh tokens are **single-use** and rotate on each refresh.

If token chain breaks: re-run `python3 scripts/setup_auth.py`

### Rate Limits

100 requests per minute per user. HTTP 429 on exceeding.

### Execution Patterns

**Quick transcript grab:**
```bash
# List recent meetings, find the one you want, grab its transcript
python3 scripts/list_meetings.py
python3 scripts/get_transcript.py 01HFYH0A6JM4R7MZ2E6X5T9BNP
```

**Full meeting dump:**
```bash
python3 scripts/get_meeting.py 01HFYH0A6JM4R7MZ2E6X5T9BNP \
  --expand summary --expand transcript --expand action_items --expand topics --raw
```

**Save transcript to file:**
```bash
python3 scripts/get_transcript.py 01HFYH0A6JM4R7MZ2E6X5T9BNP > /tmp/meeting_transcript.txt
```

**Iterate through all meetings:**
```bash
# Page 1
python3 scripts/list_meetings.py --raw > /tmp/meetings_p1.json
# Check has_more, get cursor from last item, page 2
python3 scripts/list_meetings.py --cursor LAST_ID --raw > /tmp/meetings_p2.json
```

## Supporting Files
- [scripts/_client.py](scripts/_client.py) — shared API client (OAuth token management, stdlib only)
- [scripts/setup_auth.py](scripts/setup_auth.py) — interactive OAuth setup wizard
- [docs/INDEX.md](docs/INDEX.md) — API reference documentation index
