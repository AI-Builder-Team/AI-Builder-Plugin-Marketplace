#!/usr/bin/env python3
"""Get action items from a meeting.
Usage: get_action_items.py <meeting_id> [--raw]
"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import _client as api

if len(sys.argv) < 2:
    print("Usage: get_action_items.py <meeting_id> [--raw]", file=sys.stderr)
    sys.exit(1)

meeting_id = sys.argv[1]
raw = "--raw" in sys.argv

data = api.get(f"/v1/meetings/{meeting_id}", **{"expand[]": ["action_items"]})

if not data:
    print("Meeting not found.", file=sys.stderr)
    sys.exit(1)

items = data.get("action_items", [])
if raw:
    api.pp(items)
elif items:
    print(api.fmt_meeting(data))
    print()
    for item in items:
        owner = item.get("owner", {}).get("name", "Unassigned")
        text = item.get("text", item.get("description", "?"))
        print(f"  - [{owner}] {text}")
else:
    print("No action items for this meeting.")
