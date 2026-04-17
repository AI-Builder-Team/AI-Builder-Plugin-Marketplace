"""Shared Read AI API client. All scripts import from here.

Auth: OAuth 2.1 with token refresh. Tokens stored in ~/.readai/tokens.json.
Requires READAI_CLIENT_ID and READAI_CLIENT_SECRET env vars (or in ~/.readai/credentials.json).
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

API = "https://api.read.ai"
TOKEN_ENDPOINT = "https://authn.read.ai/oauth2/token"
TOKEN_FILE = os.path.expanduser("~/.readai/tokens.json")
CREDS_FILE = os.path.expanduser("~/.readai/credentials.json")


def _load_credentials() -> tuple[str, str]:
    """Load client_id and client_secret from env or credentials file."""
    cid = os.environ.get("READAI_CLIENT_ID", "")
    secret = os.environ.get("READAI_CLIENT_SECRET", "")
    if cid and secret:
        return cid, secret
    if os.path.exists(CREDS_FILE):
        with open(CREDS_FILE) as f:
            creds = json.load(f)
        return creds["client_id"], creds["client_secret"]
    print(
        "Error: Set READAI_CLIENT_ID and READAI_CLIENT_SECRET env vars, "
        f"or create {CREDS_FILE} with client_id and client_secret.",
        file=sys.stderr,
    )
    sys.exit(1)


def _load_tokens() -> dict | None:
    """Load saved tokens from disk."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return None


def _save_tokens(tokens: dict):
    """Persist tokens to disk."""
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)


def _refresh_access_token(refresh_token: str) -> dict:
    """Exchange refresh token for new access + refresh tokens."""
    cid, secret = _load_credentials()
    import base64
    auth = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }).encode()
    req = urllib.request.Request(
        TOKEN_ENDPOINT,
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"Token refresh failed — HTTP {e.code}: {body}", file=sys.stderr)
        print(f"Re-run: python3 scripts/setup_auth.py", file=sys.stderr)
        sys.exit(1)


def _get_access_token() -> str:
    """Get a valid access token, refreshing if needed."""
    tokens = _load_tokens()
    if not tokens:
        print(
            f"Error: No tokens found at {TOKEN_FILE}. Run: python3 scripts/setup_auth.py",
            file=sys.stderr,
        )
        sys.exit(1)

    # Check if token is expired (refresh proactively with 60s buffer)
    expires_at = tokens.get("expires_at", 0)
    if time.time() < expires_at - 60:
        return tokens["access_token"]

    # Refresh
    refresh = tokens.get("refresh_token")
    if not refresh:
        print("Error: No refresh_token. Re-run: python3 scripts/setup_auth.py", file=sys.stderr)
        sys.exit(1)

    new_tokens = _refresh_access_token(refresh)
    saved = {
        "access_token": new_tokens["access_token"],
        "refresh_token": new_tokens["refresh_token"],
        "expires_at": time.time() + new_tokens.get("expires_in", 599),
    }
    _save_tokens(saved)
    return saved["access_token"]


def _request(method: str, path: str, params: dict | None = None) -> dict | list | None:
    """Make an authenticated API request."""
    token = _get_access_token()
    url = f"{API}{path}"
    if params:
        filtered = {k: v for k, v in params.items() if v is not None}
        if filtered:
            url += "?" + urllib.parse.urlencode(filtered, doseq=True)

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode()
            if not content or content.strip() == "null":
                return None
            return json.loads(content)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 401:
            print(f"HTTP 401: Token expired or invalid. Re-run: python3 scripts/setup_auth.py", file=sys.stderr)
        elif e.code == 429:
            print(f"HTTP 429: Rate limited. Wait and retry.", file=sys.stderr)
        else:
            print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def get(path: str, **params):
    return _request("GET", path, params=params if params else None)


def pp(obj):
    """Pretty-print a JSON object."""
    if obj is None:
        return
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def fmt_meeting(m: dict) -> str:
    """Format a meeting as a single compact line."""
    parts = [f"[{m['id']}] {m.get('title', 'Untitled')}"]
    if m.get("start_time_ms"):
        from datetime import datetime
        dt = datetime.fromtimestamp(m["start_time_ms"] / 1000)
        parts.append(dt.strftime("%Y-%m-%d %H:%M"))
    if m.get("platform"):
        parts.append(m["platform"])
    participants = m.get("participants", [])
    attended = [p["name"] for p in participants if p.get("attended")]
    if attended:
        parts.append(f"{len(attended)} attendees")
    if m.get("live_enabled"):
        parts.append("LIVE")
    return " | ".join(parts)


def print_meetings(data, raw=False):
    """Print meeting list in compact or raw JSON format."""
    if raw:
        pp(data)
        return
    items = data.get("data", []) if isinstance(data, dict) else [data]
    for m in items:
        print(fmt_meeting(m))
    if isinstance(data, dict) and data.get("has_more"):
        last_id = items[-1]["id"] if items else "?"
        print(f"\n... more results available (cursor: {last_id})")
