#!/usr/bin/env python3
"""Get the full transcript for a meeting.
Usage: get_transcript.py <meeting_id> [--raw]

Outputs plain text transcript by default.
Use --raw for the full JSON structure with speaker/timing data.
"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import _client as api

if len(sys.argv) < 2:
    print(__doc__, file=sys.stderr)
    sys.exit(1)

meeting_id = sys.argv[1]
raw = "--raw" in sys.argv

data = api.get(f"/v1/meetings/{meeting_id}", **{"expand[]": ["transcript"]})

if not data:
    print("Meeting not found.", file=sys.stderr)
    sys.exit(1)

tx = data.get("transcript")
if not tx:
    print(f"No transcript available for meeting {meeting_id}.", file=sys.stderr)
    sys.exit(1)

if raw:
    api.pp(tx)
else:
    if isinstance(tx, dict):
        if tx.get("text"):
            print(tx["text"])
        elif tx.get("turns"):
            for turn in tx["turns"]:
                speaker = turn.get("speaker", {}).get("name", "Unknown")
                text = turn.get("text", "")
                print(f"[{speaker}]: {text}")
    elif isinstance(tx, str):
        print(tx)
