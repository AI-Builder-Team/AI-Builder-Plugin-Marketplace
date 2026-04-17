#!/usr/bin/env python3
"""Get live meeting data (transcript + chapter summaries) for an ongoing meeting.
Usage: get_live.py <meeting_id> [--after TIMESTAMP_MS] [--raw]

Requires the live dashboard to be open during the meeting.
"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import _client as api

if len(sys.argv) < 2:
    print(__doc__, file=sys.stderr)
    sys.exit(1)

meeting_id = sys.argv[1]
args = sys.argv[2:]
raw = "--raw" in args
if raw:
    args.remove("--raw")

params = {"expand[]": ["transcript", "chapter_summaries"]}
i = 0
while i < len(args):
    if args[i] == "--after":
        params["start_time_ms.gt"] = args[i + 1]; i += 2
    else:
        print(f"Unknown option: {args[i]}", file=sys.stderr); sys.exit(1)

data = api.get(f"/v1/meetings/{meeting_id}/live", **params)
if raw:
    api.pp(data)
elif data:
    print(api.fmt_meeting(data))
    tx = data.get("transcript")
    if tx:
        print("\nLIVE TRANSCRIPT:")
        if isinstance(tx, dict) and tx.get("text"):
            print(tx["text"])
        elif isinstance(tx, dict) and tx.get("turns"):
            for turn in tx["turns"]:
                speaker = turn.get("speaker", {}).get("name", "Unknown")
                print(f"[{speaker}]: {turn.get('text', '')}")
    cs = data.get("chapter_summaries")
    if cs:
        print("\nCHAPTER SUMMARIES:")
        for ch in cs:
            print(f"  - {ch}")
else:
    print("No live data available.", file=sys.stderr)
