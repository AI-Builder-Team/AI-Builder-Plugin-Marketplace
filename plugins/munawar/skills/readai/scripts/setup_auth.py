#!/usr/bin/env python3
"""Interactive OAuth setup for Read AI API.

Step 1: Register OAuth client (if no credentials file exists)
Step 2: Guide user through browser-based auth flow
Step 3: Exchange auth code for tokens and save

Usage: python3 scripts/setup_auth.py [--register]
  --register   Force re-registration of OAuth client
"""
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import base64

API = "https://api.read.ai"
TOKEN_ENDPOINT = "https://authn.read.ai/oauth2/token"
CREDS_FILE = os.path.expanduser("~/.readai/credentials.json")
TOKEN_FILE = os.path.expanduser("~/.readai/tokens.json")


def register_client():
    """Register a new OAuth client."""
    print("=== Step 1: Registering OAuth Client ===\n")
    data = json.dumps({
        "client_name": "ReadAI CLI Tool",
        "redirect_uris": ["https://api.read.ai/oauth/ui"],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "scope": "openid email offline_access profile meeting:read mcp:execute",
        "token_endpoint_auth_method": "client_secret_basic",
    }).encode()
    req = urllib.request.Request(
        f"{API}/oauth/register",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Registration failed — HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

    creds = {
        "client_id": result["client_id"],
        "client_secret": result["client_secret"],
    }
    os.makedirs(os.path.dirname(CREDS_FILE), exist_ok=True)
    with open(CREDS_FILE, "w") as f:
        json.dump(creds, f, indent=2)
    os.chmod(CREDS_FILE, 0o600)
    print(f"Client registered. Credentials saved to {CREDS_FILE}")
    print(f"  client_id: {creds['client_id']}")
    print()
    return creds


def load_credentials():
    if os.path.exists(CREDS_FILE):
        with open(CREDS_FILE) as f:
            return json.load(f)
    return None


def exchange_code(creds: dict, code: str, code_verifier: str = ""):
    """Exchange authorization code for tokens."""
    auth = base64.b64encode(f"{creds['client_id']}:{creds['client_secret']}".encode()).decode()
    params = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "https://api.read.ai/oauth/ui",
    }
    if code_verifier:
        params["code_verifier"] = code_verifier
    data = urllib.parse.urlencode(params).encode()
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
        print(f"Token exchange failed — HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def main():
    force_register = "--register" in sys.argv

    # Step 1: Get or register credentials
    creds = load_credentials()
    if not creds or force_register:
        creds = register_client()
    else:
        print(f"Using existing credentials from {CREDS_FILE}")
        print(f"  client_id: {creds['client_id']}")
        print()

    # Step 2: Guide through browser auth
    print("=== Step 2: Browser Authorization ===\n")
    print("1. Open this URL in your browser:")
    print(f"   https://api.read.ai/oauth/ui\n")
    print(f"2. Enter your client_id: {creds['client_id']}")
    print(f"3. Enter your client_secret: {creds['client_secret']}")
    print("4. Click 'Start OAuth Flow'")
    print("5. Sign in to Read AI and click 'Allow Access'")
    print("6. Copy the authorization code shown on screen\n")

    code = input("Paste authorization code here: ").strip()
    if not code:
        print("No code provided.", file=sys.stderr)
        sys.exit(1)

    code_verifier = input("Paste code_verifier (or press Enter to skip): ").strip()

    # Step 3: Exchange for tokens
    print("\n=== Step 3: Exchanging Code for Tokens ===\n")
    import time
    tokens = exchange_code(creds, code, code_verifier)

    saved = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_at": time.time() + tokens.get("expires_in", 599),
    }
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(saved, f, indent=2)
    os.chmod(TOKEN_FILE, 0o600)

    print(f"Tokens saved to {TOKEN_FILE}")
    print("Setup complete. You can now use the Read AI scripts.\n")

    # Quick test
    print("=== Testing API Access ===\n")
    req = urllib.request.Request(
        f"{API}/oauth/test-token-with-scopes",
        headers={"Authorization": f"Bearer {saved['access_token']}"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Token test: OK")
            print(json.dumps(json.loads(resp.read().decode()), indent=2))
    except urllib.error.HTTPError as e:
        print(f"Token test failed: HTTP {e.code}", file=sys.stderr)


if __name__ == "__main__":
    main()
