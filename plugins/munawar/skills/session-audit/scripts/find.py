#!/usr/bin/env python3
"""Search a session transcript for a keyword or regex pattern.

Usage:
    python3 find.py <session.jsonl> <pattern> [--scope user|both|all] [--max-len 300]

Scopes:
    user  — only human text messages
    both  — human text + assistant text (default)
    all   — human text + assistant text + thinking + tool calls + tool results

For each match, shows the turn number, line, timestamp, which field matched,
and a snippet with the match highlighted in ** markers.
"""
import argparse
import json
import re
import sys
import textwrap
from pathlib import Path


def excerpt(text: str, match: re.Match, context_chars: int = 80) -> str:
    """Return a snippet around the match with ** markers."""
    start = max(0, match.start() - context_chars)
    end = min(len(text), match.end() + context_chars)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    before = text[start:match.start()]
    matched = text[match.start():match.end()]
    after = text[match.end():end]
    # Collapse newlines for readability
    snippet = f"{prefix}{before}**{matched}**{after}{suffix}"
    return snippet.replace("\n", " ")


def summarize_tool_input(name: str, inp: dict) -> str:
    if name == "Bash":
        return inp.get("command", "")
    elif name in ("Read", "Write"):
        return inp.get("file_path", "")
    elif name == "Edit":
        fp = inp.get("file_path", "")
        old = inp.get("old_string", "")[:120]
        new = inp.get("new_string", "")[:120]
        return f"{fp} old={old!r} new={new!r}"
    elif name == "Grep":
        return f'pattern={inp.get("pattern","")} path={inp.get("path",".")}'
    elif name == "Glob":
        return f'pattern={inp.get("pattern","")} path={inp.get("path",".")}'
    elif name == "Agent":
        return f'type={inp.get("subagent_type","")} desc={inp.get("description","")} prompt={inp.get("prompt","")[:200]}'
    else:
        return json.dumps(inp, separators=(",", ":"))


def main():
    parser = argparse.ArgumentParser(description="Search session transcript for a pattern")
    parser.add_argument("session_file", help="Path to session JSONL")
    parser.add_argument("pattern", help="Regex pattern to search for (case-insensitive)")
    parser.add_argument(
        "--scope",
        choices=["user", "both", "all"],
        default="both",
        help="What to search: user (human text only), both (human + assistant text), all (everything including tools)",
    )
    parser.add_argument("--max-len", type=int, default=300, help="Max snippet length (0=unlimited)")
    parser.add_argument("--case-sensitive", action="store_true", help="Make search case-sensitive")
    args = parser.parse_args()

    flags = 0 if args.case_sensitive else re.IGNORECASE
    try:
        regex = re.compile(args.pattern, flags)
    except re.error as e:
        print(f"Invalid regex: {e}", file=sys.stderr)
        sys.exit(1)

    turn = 0
    matches = []

    with open(args.session_file) as f:
        for line_num, line in enumerate(f, 1):
            r = json.loads(line)
            t = r.get("type")
            ts = r.get("timestamp", "")[:19]

            if t == "user":
                msg = r.get("message", {})
                content = msg.get("content")

                # Human text message — new turn
                if isinstance(content, str):
                    turn += 1
                    m = regex.search(content)
                    if m:
                        matches.append({
                            "turn": turn,
                            "line": line_num,
                            "ts": ts,
                            "field": "USER",
                            "snippet": excerpt(content, m),
                        })

                # Tool results
                if args.scope == "all" and isinstance(content, list):
                    for block in content:
                        if block.get("type") == "tool_result":
                            result = block.get("content", "")
                            if isinstance(result, list):
                                result = " ".join(
                                    c.get("text", "") for c in result if c.get("type") == "text"
                                )
                            result = str(result)
                            m = regex.search(result)
                            if m:
                                tid = block.get("tool_use_id", "?")[:25]
                                is_err = block.get("is_error", False)
                                label = f"TOOL ERROR [{tid}]" if is_err else f"TOOL RESULT [{tid}]"
                                matches.append({
                                    "turn": turn,
                                    "line": line_num,
                                    "ts": ts,
                                    "field": label,
                                    "snippet": excerpt(result, m),
                                })

                # Also check toolUseResult
                if args.scope == "all":
                    tool_result = r.get("toolUseResult")
                    if tool_result:
                        result_str = str(tool_result)
                        m = regex.search(result_str)
                        if m:
                            matches.append({
                                "turn": turn,
                                "line": line_num,
                                "ts": ts,
                                "field": "TOOL RESULT (raw)",
                                "snippet": excerpt(result_str, m),
                            })

            elif t == "assistant":
                msg = r.get("message", {})
                content = msg.get("content", [])
                if not isinstance(content, list):
                    continue

                for block in content:
                    bt = block.get("type")

                    if bt == "text" and args.scope in ("both", "all"):
                        text = block.get("text", "")
                        m = regex.search(text)
                        if m:
                            matches.append({
                                "turn": turn,
                                "line": line_num,
                                "ts": ts,
                                "field": "ASSISTANT",
                                "snippet": excerpt(text, m),
                            })

                    elif bt == "thinking" and args.scope == "all":
                        thinking = block.get("thinking", "")
                        m = regex.search(thinking)
                        if m:
                            matches.append({
                                "turn": turn,
                                "line": line_num,
                                "ts": ts,
                                "field": "THINKING",
                                "snippet": excerpt(thinking, m),
                            })

                    elif bt == "tool_use" and args.scope == "all":
                        name = block.get("name", "?")
                        inp = block.get("input", {})
                        full_input = summarize_tool_input(name, inp)
                        m = regex.search(full_input)
                        if m:
                            matches.append({
                                "turn": turn,
                                "line": line_num,
                                "ts": ts,
                                "field": f"TOOL CALL ({name})",
                                "snippet": excerpt(full_input, m),
                            })

    # Report
    print(f"SEARCH: /{args.pattern}/ (scope={args.scope}, case_sensitive={args.case_sensitive})")
    print("=" * 70)
    print(f"Matches: {len(matches)}")
    print()

    for i, hit in enumerate(matches, 1):
        snippet = hit["snippet"]
        if args.max_len > 0 and len(snippet) > args.max_len:
            snippet = snippet[:args.max_len] + "..."
        print(f"  [{i}] Turn {hit['turn']} | Line {hit['line']} | {hit['ts']} | {hit['field']}")
        for sl in textwrap.wrap(snippet, 100):
            print(f"       {sl}")
        print()

    if matches:
        print("-" * 70)
        print("To drill into a specific match, run:")
        scripts_dir = Path(__file__).resolve().parent
        print(f"  python3 {scripts_dir}/context.py {args.session_file} <LINE> [radius]")

    print_session_location(args.session_file)


def print_session_location(path: str):
    p = Path(path).resolve()
    session_dir = p.parent / p.stem
    print()
    print("SESSION FILES")
    print("-" * 50)
    print(f"  Transcript: {p}")
    if session_dir.is_dir():
        print(f"  Session dir: {session_dir}/")
        for item in sorted(session_dir.rglob("*")):
            rel = item.relative_to(session_dir)
            suffix = "/" if item.is_dir() else f"  ({item.stat().st_size:,} bytes)"
            print(f"    {rel}{suffix}")
    else:
        print("  Session dir: (none — no subagents or artifacts)")


if __name__ == "__main__":
    main()
