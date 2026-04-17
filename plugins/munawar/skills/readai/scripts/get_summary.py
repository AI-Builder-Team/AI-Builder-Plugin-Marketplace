#!/usr/bin/env python3
"""Get the summary for a meeting.
Usage: get_summary.py <meeting_id> [--raw]
"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import _client as api

if len(sys.argv) < 2:
    print("Usage: get_summary.py <meeting_id> [--raw]", file=sys.stderr)
    sys.exit(1)

meeting_id = sys.argv[1]
raw = "--raw" in sys.argv

data = api.get(f"/v1/meetings/{meeting_id}", **{"expand[]": ["summary", "chapter_summaries"]})

if not data:
    print("Meeting not found.", file=sys.stderr)
    sys.exit(1)

if raw:
    api.pp({"summary": data.get("summary"), "chapter_summaries": data.get("chapter_summaries")})
else:
    print(api.fmt_meeting(data))
    print()
    if data.get("summary"):
        print("SUMMARY:")
        print(data["summary"])
        print()
    if data.get("chapter_summaries"):
        print("CHAPTERS:")
        for ch in data["chapter_summaries"]:
            print(f"  - {ch}")
