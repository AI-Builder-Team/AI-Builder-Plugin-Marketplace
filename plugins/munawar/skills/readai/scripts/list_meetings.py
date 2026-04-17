#!/usr/bin/env python3
"""List meetings in reverse chronological order.
Usage: list_meetings.py [--limit N] [--after TIMESTAMP_MS] [--before TIMESTAMP_MS] [--cursor ID] [--expand FIELD] [--raw]

Examples:
  list_meetings.py                              # Latest 10 meetings
  list_meetings.py --limit 5                    # Latest 5
  list_meetings.py --after 1733700000000        # After timestamp
  list_meetings.py --expand transcript          # Include transcripts
  list_meetings.py --expand summary --expand action_items --raw
"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import _client as api

args = sys.argv[1:]
raw = "--raw" in args
if raw:
    args.remove("--raw")

params = {}
expands = []
i = 0
while i < len(args):
    if args[i] == "--limit":
        params["limit"] = args[i + 1]; i += 2
    elif args[i] == "--after":
        params["start_time_ms.gte"] = args[i + 1]; i += 2
    elif args[i] == "--before":
        params["start_time_ms.lte"] = args[i + 1]; i += 2
    elif args[i] == "--cursor":
        params["cursor"] = args[i + 1]; i += 2
    elif args[i] == "--expand":
        expands.append(args[i + 1]); i += 2
    else:
        print(f"Unknown option: {args[i]}", file=sys.stderr); sys.exit(1)

if expands:
    params["expand[]"] = expands

data = api.get("/v1/meetings", **params)
api.print_meetings(data, raw=raw)
