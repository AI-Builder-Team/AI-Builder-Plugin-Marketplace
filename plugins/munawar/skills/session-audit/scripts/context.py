#!/usr/bin/env python3
"""Extract context around a specific line in a session JSONL.

Usage:
    python3 context.py <session.jsonl> <line_number> [radius]

Shows the N records before and after the target line (default radius=3),
rendering each as a readable summary. Useful for investigating errors
found by errors.py.

The target line is highlighted with >>> markers.
"""
import json
import sys
import textwrap
from pathlib import Path


def summarize_tool_input(name: str, inp: dict) -> str:
    if name == "Bash":
        return inp.get("command", "")[:300]
    elif name == "Read":
        return inp.get("file_path", "")
    elif name == "Write":
        return inp.get("file_path", "")
    elif name == "Edit":
        fp = inp.get("file_path", "")
        old = inp.get("old_string", "")[:100]
        return f"{fp}  old_string={old!r}"
    elif name == "Grep":
        return f'pattern={inp.get("pattern","")} path={inp.get("path",".")}'
    elif name == "Glob":
        return f'pattern={inp.get("pattern","")} path={inp.get("path",".")}'
    elif name == "Agent":
        return f'type={inp.get("subagent_type","")} desc={inp.get("description","")}'
    else:
        return json.dumps(inp, separators=(",", ":"))[:300]


def render_record(line_num: int, r: dict, is_target: bool) -> list[str]:
    """Render a JSONL record into readable lines."""
    marker = ">>>" if is_target else "   "
    t = r.get("type", "?")
    ts = r.get("timestamp", "")[:19]
    out = []

    if t == "user":
        msg = r.get("message", {})
        content = msg.get("content")

        if isinstance(content, str):
            out.append(f"{marker} L{line_num} [{ts}] USER:")
            out.append(f"{marker}   {content[:300]}")

        elif isinstance(content, list):
            for block in content:
                bt = block.get("type")
                if bt == "tool_result":
                    tid = block.get("tool_use_id", "?")[:25]
                    is_err = block.get("is_error", False)
                    label = "TOOL ERROR" if is_err else "TOOL RESULT"
                    result = block.get("content", "")
                    if isinstance(result, list):
                        result = " ".join(
                            c.get("text", "") for c in result if c.get("type") == "text"
                        )
                    out.append(f"{marker} L{line_num} [{ts}] {label} [{tid}]:")
                    for rl in textwrap.wrap(str(result)[:400], 100):
                        out.append(f"{marker}   {rl}")

        # Also show toolUseResult if present
        tool_result = r.get("toolUseResult")
        if tool_result:
            result_str = str(tool_result)[:400]
            has_error = any(kw in result_str for kw in ["Error", "error", "FAILED", "Traceback"])
            label = "TOOL RESULT (error)" if has_error else "TOOL RESULT"
            out.append(f"{marker} L{line_num} [{ts}] {label}:")
            for rl in textwrap.wrap(result_str, 100):
                out.append(f"{marker}   {rl}")

    elif t == "assistant":
        msg = r.get("message", {})
        content = msg.get("content", [])
        if not isinstance(content, list):
            out.append(f"{marker} L{line_num} [{ts}] ASSISTANT: (non-list content)")
            return out

        for block in content:
            bt = block.get("type")
            if bt == "thinking":
                thinking = block.get("thinking", "")[:200]
                out.append(f"{marker} L{line_num} [{ts}] THINKING:")
                out.append(f"{marker}   {thinking}")

            elif bt == "text":
                text = block.get("text", "")[:400]
                out.append(f"{marker} L{line_num} [{ts}] ASSISTANT:")
                for tl in textwrap.wrap(text, 100):
                    out.append(f"{marker}   {tl}")

            elif bt == "tool_use":
                name = block.get("name", "?")
                tid = block.get("id", "?")[:25]
                inp = block.get("input", {})
                summary = summarize_tool_input(name, inp)
                out.append(f"{marker} L{line_num} [{ts}] TOOL CALL: {name} [{tid}]")
                for sl in textwrap.wrap(summary, 100):
                    out.append(f"{marker}   {sl}")

    elif t == "progress":
        # Skip progress records — they're noisy
        return []

    elif t == "file-history-snapshot":
        out.append(f"{marker} L{line_num} [{ts}] FILE SNAPSHOT")

    elif t == "system":
        subtype = r.get("subtype", "")
        out.append(f"{marker} L{line_num} [{ts}] SYSTEM: {subtype}")

    else:
        out.append(f"{marker} L{line_num} [{ts}] {t}")

    return out


def main():
    if len(sys.argv) < 3:
        print("Usage: context.py <session.jsonl> <line_number> [radius]", file=sys.stderr)
        print("  radius: number of non-progress records before/after to show (default: 3)", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    target_line = int(sys.argv[2])
    radius = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    # Load all records, skipping progress for context window purposes
    records = []  # (line_num, parsed_json)
    with open(path) as f:
        for line_num, line in enumerate(f, 1):
            r = json.loads(line)
            records.append((line_num, r))

    # Find target index (by line number)
    target_idx = None
    for i, (ln, _) in enumerate(records):
        if ln == target_line:
            target_idx = i
            break

    if target_idx is None:
        print(f"Line {target_line} not found in {path}", file=sys.stderr)
        sys.exit(1)

    # Filter out progress records for context, but keep target even if progress
    meaningful = [(i, ln, r) for i, (ln, r) in enumerate(records) if r.get("type") != "progress" or i == target_idx]

    # Find target in meaningful list
    target_mi = None
    for mi, (i, ln, r) in enumerate(meaningful):
        if i == target_idx:
            target_mi = mi
            break

    if target_mi is None:
        # Target was a progress record not in meaningful — add it
        meaningful.append((target_idx, target_line, records[target_idx][1]))
        meaningful.sort(key=lambda x: x[0])
        for mi, (i, ln, r) in enumerate(meaningful):
            if i == target_idx:
                target_mi = mi
                break

    assert target_mi is not None, f"Could not locate line {target_line} in meaningful records"

    # Extract window
    start = max(0, target_mi - radius)
    end = min(len(meaningful), target_mi + radius + 1)
    window = meaningful[start:end]

    print(f"CONTEXT AROUND LINE {target_line} (radius={radius}, skipping progress records)")
    print("=" * 70)
    print()

    for _, ln, r in window:
        is_target = (ln == target_line)
        lines = render_record(ln, r, is_target)
        if lines:
            for l in lines:
                print(l)
            print()

    print("=" * 70)
    print_session_location(path)


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
