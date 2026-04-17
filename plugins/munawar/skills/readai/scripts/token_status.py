#!/usr/bin/env python3
"""Check token status and expiration.
Usage: token_status.py
"""
import json
import os
import sys
import time

TOKEN_FILE = os.path.expanduser("~/.readai/tokens.json")
CREDS_FILE = os.path.expanduser("~/.readai/credentials.json")

if not os.path.exists(TOKEN_FILE):
    print(f"No tokens found at {TOKEN_FILE}")
    print("Run: python3 scripts/setup_auth.py")
    sys.exit(1)

with open(TOKEN_FILE) as f:
    tokens = json.load(f)

expires_at = tokens.get("expires_at", 0)
remaining = expires_at - time.time()

print(f"Token file: {TOKEN_FILE}")
print(f"Has access_token: {'yes' if tokens.get('access_token') else 'no'}")
print(f"Has refresh_token: {'yes' if tokens.get('refresh_token') else 'no'}")
if remaining > 0:
    print(f"Access token expires in: {int(remaining)}s ({int(remaining/60)}m)")
else:
    print(f"Access token EXPIRED {int(-remaining)}s ago (will auto-refresh on next API call)")

if os.path.exists(CREDS_FILE):
    with open(CREDS_FILE) as f:
        creds = json.load(f)
    print(f"\nCredentials file: {CREDS_FILE}")
    print(f"Client ID: {creds.get('client_id', 'missing')}")
else:
    print(f"\nNo credentials file at {CREDS_FILE}")
