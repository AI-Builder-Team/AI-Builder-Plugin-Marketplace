#!/usr/bin/env python3
"""Get a single meeting by ID with optional expanded fields.
Usage: get_meeting.py <meeting_id> [--expand FIELD]... [--raw]

Examples:
  get_meeting.py 01HFYH0A6JM4R7MZ2E6X5T9BNP
  get_meeting.py 01HFYH0A6JM4R7MZ2E6X5T9BNP --expand transcript
  get_meeting.py 01HFYH0A6JM4R7MZ2E6X5T9BNP --expand summary --expand action_items --expand transcript --raw
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

params = {}
expands = []
i = 0
while i < len(args):
    if args[i] == "--expand":
        expands.append(args[i + 1]); i += 2
    else:
        print(f"Unknown option: {args[i]}", file=sys.stderr); sys.exit(1)

if expands:
    params["expand[]"] = expands

data = api.get(f"/v1/meetings/{meeting_id}", **params)

if raw:
    api.pp(data)
elif data:
    print(api.fmt_meeting(data))
    print()
    if data.get("summary"):
        print("SUMMARY:")
        print(data["summary"])
        print()
    if data.get("action_items"):
        print("ACTION ITEMS:")
        for item in data["action_items"]:
            owner = item.get("owner", {}).get("name", "Unassigned")
            print(f"  - [{owner}] {item.get('text', item.get('description', '?'))}")
        print()
    if data.get("key_questions"):
        print("KEY QUESTIONS:")
        for q in data["key_questions"]:
            print(f"  - {q.get('text', q.get('question', '?'))}")
        print()
    if data.get("topics"):
        print("TOPICS:")
        for t in data["topics"]:
            print(f"  - {t.get('name', t.get('text', '?'))}")
        print()
    if data.get("transcript"):
        tx = data["transcript"]
        if isinstance(tx, dict) and tx.get("text"):
            print("TRANSCRIPT:")
            print(tx["text"][:2000])
            if len(tx["text"]) > 2000:
                print(f"\n... truncated ({len(tx['text'])} chars total)")
        print()
    if data.get("metrics"):
        print("METRICS:")
        for k, v in data["metrics"].items():
            print(f"  {k}: {v}")
        print()
    if data.get("recording_download"):
        print(f"RECORDING: {data['recording_download']}")
else:
    print("Meeting not found.")
