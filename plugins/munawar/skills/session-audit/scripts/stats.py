#!/usr/bin/env python3
"""Compute session statistics from a JSONL file.

Usage:
    python3 stats.py <session.jsonl>

Shows: turn counts, token usage, tool call breakdown, timing, errors.
"""
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def parse_ts(ts_str: str) -> datetime | None:
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        print("Usage: stats.py <session.jsonl>", file=sys.stderr)
        sys.exit(1)

    type_counts = Counter()
    tool_calls = Counter()
    content_block_types = Counter()
    total_input_tokens = 0
    total_output_tokens = 0
    total_cache_read = 0
    total_cache_create = 0
    user_messages = 0
    assistant_text_blocks = 0
    thinking_blocks = 0
    errors = 0
    timestamps = []

    with open(path) as f:
        for line in f:
            r = json.loads(line)
            t = r.get("type", "?")
            type_counts[t] += 1

            ts = parse_ts(r.get("timestamp", ""))
            if ts:
                timestamps.append(ts)

            if t == "user":
                msg = r.get("message", {})
                content = msg.get("content")
                if isinstance(content, str):
                    user_messages += 1
                elif isinstance(content, list):
                    for block in content:
                        if block.get("is_error"):
                            errors += 1

            elif t == "assistant":
                msg = r.get("message", {})
                usage = msg.get("usage", {})
                total_input_tokens += usage.get("input_tokens", 0)
                total_output_tokens += usage.get("output_tokens", 0)
                total_cache_read += usage.get("cache_read_input_tokens", 0)
                total_cache_create += usage.get("cache_creation_input_tokens", 0)

                for block in msg.get("content", []):
                    bt = block.get("type", "?")
                    content_block_types[bt] += 1

                    if bt == "tool_use":
                        tool_calls[block.get("name", "?")] += 1
                    elif bt == "text":
                        assistant_text_blocks += 1
                    elif bt == "thinking":
                        thinking_blocks += 1

    # Timing
    duration = ""
    if len(timestamps) >= 2:
        span = max(timestamps) - min(timestamps)
        mins = int(span.total_seconds() // 60)
        secs = int(span.total_seconds() % 60)
        duration = f"{mins}m {secs}s"
        start = min(timestamps).strftime("%H:%M:%S")
        end = max(timestamps).strftime("%H:%M:%S")
        duration = f"{start} -> {end} ({duration})"

    print("SESSION STATS")
    print("=" * 50)
    print(f"Duration:          {duration or 'N/A'}")
    print(f"User messages:     {user_messages}")
    print(f"Assistant turns:   {type_counts.get('assistant', 0)}")
    print(f"  Text blocks:     {assistant_text_blocks}")
    print(f"  Thinking blocks: {thinking_blocks}")
    print(f"Tool errors:       {errors}")
    print()

    print("RECORD TYPES")
    print("-" * 30)
    for t, count in type_counts.most_common():
        print(f"  {t:30s} {count}")
    print()

    print("TOKEN USAGE")
    print("-" * 30)
    print(f"  Input tokens:    {total_input_tokens:,}")
    print(f"  Output tokens:   {total_output_tokens:,}")
    print(f"  Cache read:      {total_cache_read:,}")
    print(f"  Cache created:   {total_cache_create:,}")
    print()

    if tool_calls:
        print("TOOL CALLS")
        print("-" * 30)
        total = sum(tool_calls.values())
        for name, count in tool_calls.most_common():
            print(f"  {name:25s} {count:3d}  ({count*100//total}%)")
        print(f"  {'TOTAL':25s} {total:3d}")

    print_session_location(path)


def print_session_location(path: str):
    p = Path(path).resolve()
    session_dir = p.parent / p.stem  # e.g. .../projects/<proj>/<session-id>/
    print()
    print("SESSION FILES")
    print("-" * 50)
    print(f"  Transcript: {p}")
    if session_dir.is_dir():
        print(f"  Session dir: {session_dir}/")
        for item in sorted(session_dir.rglob("*")):
            rel = item.relative_to(session_dir)
            prefix = "    " if item.is_file() else "    "
            suffix = "/" if item.is_dir() else f"  ({item.stat().st_size:,} bytes)"
            print(f"{prefix}{rel}{suffix}")
    else:
        print("  Session dir: (none — no subagents or artifacts)")


if __name__ == "__main__":
    main()
