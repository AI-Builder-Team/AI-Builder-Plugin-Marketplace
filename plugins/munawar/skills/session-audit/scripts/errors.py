#!/usr/bin/env python3
"""Find errors, retries, and self-corrections in a session.

Usage:
    python3 errors.py <session.jsonl>

For each error shows: turn number, what tool was called, what input was given,
and the error message returned.
"""
import json
import sys
from pathlib import Path


CORRECTION_PHRASES = [
    "let me try",
    "that didn't work",
    "that did not work",
    "instead,",
    "actually,",
    "sorry,",
    "my mistake",
    "let me fix",
    "i made an error",
    "wrong approach",
    "let me correct",
]


def summarize_tool_input(name: str, inp: dict) -> str:
    """One-line summary of what a tool call attempted."""
    if name == "Bash":
        return inp.get("command", "")[:200]
    elif name == "Read":
        return inp.get("file_path", "")
    elif name == "Write":
        return inp.get("file_path", "")
    elif name == "Edit":
        fp = inp.get("file_path", "")
        old = inp.get("old_string", "")[:80]
        return f"{fp}  old_string={old!r}"
    elif name == "Grep":
        return f'pattern={inp.get("pattern","")} path={inp.get("path",".")}'
    elif name == "Glob":
        return f'pattern={inp.get("pattern","")} path={inp.get("path",".")}'
    elif name == "Agent":
        return f'type={inp.get("subagent_type","")} desc={inp.get("description","")}'
    else:
        return json.dumps(inp, separators=(",", ":"))[:200]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        print("Usage: errors.py <session.jsonl>", file=sys.stderr)
        sys.exit(1)

    # First pass: index all tool calls by their tool_use_id
    # and build a turn counter (each user text message = new turn)
    tool_calls_by_id = {}  # tool_use_id -> {name, input, line, turn}
    tool_errors = []
    corrections = []
    tool_call_sequence = []  # (name, sig, line, turn) for retry detection
    turn = 0

    lines = []
    with open(path) as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        r = json.loads(line)
        t = r.get("type")

        if t == "user":
            msg = r.get("message", {})
            content = msg.get("content")

            # Count turns by human text messages
            if isinstance(content, str):
                turn += 1

            # Collect tool errors from tool_result blocks
            if isinstance(content, list):
                for block in content:
                    if block.get("is_error"):
                        tid = block.get("tool_use_id", "?")
                        result = block.get("content", "")
                        if isinstance(result, list):
                            result = " ".join(
                                c.get("text", "") for c in result if c.get("type") == "text"
                            )
                        # Look up the originating tool call
                        call = tool_calls_by_id.get(tid, {})
                        tool_errors.append({
                            "line": line_num,
                            "turn": turn,
                            "tool_use_id": tid,
                            "tool_name": call.get("name", "?"),
                            "tool_input": call.get("input_summary", "?"),
                            "call_line": call.get("line"),
                            "error": str(result)[:400],
                        })

            # toolUseResult records don't carry is_error — real errors
            # surface through content blocks with is_error=true (handled above).
            # Keyword-matching toolUseResult.stdout causes false positives when
            # output merely *discusses* errors (e.g. auditing another session).

        elif t == "assistant":
            msg = r.get("message", {})
            for block in msg.get("content", []):
                bt = block.get("type")

                if bt == "text":
                    text_lower = block.get("text", "").lower()
                    for phrase in CORRECTION_PHRASES:
                        if phrase in text_lower:
                            corrections.append({
                                "line": line_num,
                                "turn": turn,
                                "phrase": phrase,
                                "context": block["text"][:200],
                            })
                            break

                elif bt == "tool_use":
                    name = block.get("name", "?")
                    inp = block.get("input", {})
                    tid = block.get("id", "")
                    input_summary = summarize_tool_input(name, inp)

                    tool_calls_by_id[tid] = {
                        "name": name,
                        "input_summary": input_summary,
                        "line": line_num,
                        "turn": turn,
                    }

                    # For retry detection
                    if name == "Bash":
                        sig = inp.get("command", "")[:100]
                    else:
                        sig = json.dumps(inp, sort_keys=True, separators=(",", ":"))[:100]
                    tool_call_sequence.append((name, sig, line_num, turn))

    # Detect retries: same tool+similar input called consecutively
    retries = []
    for i in range(1, len(tool_call_sequence)):
        prev_name, prev_sig, _, _ = tool_call_sequence[i - 1]
        curr_name, curr_sig, curr_line, curr_turn = tool_call_sequence[i]
        if curr_name == prev_name and curr_sig == prev_sig:
            retries.append({
                "line": curr_line,
                "turn": curr_turn,
                "tool": curr_name,
                "input": curr_sig[:150],
            })

    # Report
    print("ERROR & RETRY REPORT")
    print("=" * 70)

    print(f"\nTool Errors: {len(tool_errors)}")
    print("-" * 70)
    for i, e in enumerate(tool_errors, 1):
        call_line_str = f" (call at line {e['call_line']})" if e["call_line"] else ""
        print(f"\n  [{i}] Turn {e['turn']} | Line {e['line']}{call_line_str}")
        print(f"      Tool:  {e['tool_name']}")
        if e["tool_input"]:
            print(f"      Input: {e['tool_input'][:200]}")
        print(f"      Error: {e['error'][:300]}")

    print(f"\nExact Retries (same tool+input back-to-back): {len(retries)}")
    print("-" * 70)
    for r in retries:
        print(f"  Turn {r['turn']} | Line {r['line']}: {r['tool']} -> {r['input'][:120]}")

    print(f"\nSelf-Corrections: {len(corrections)}")
    print("-" * 70)
    for c in corrections:
        print(f"  Turn {c['turn']} | Line {c['line']}: \"{c['phrase']}\" in: {c['context'][:150]}")

    total_issues = len(tool_errors) + len(retries) + len(corrections)
    print(f"\n{'='*70}")
    if total_issues == 0:
        print("Clean session - no errors, retries, or corrections detected.")
    else:
        print(f"Total issues found: {total_issues}")
        print(f"\nTo inspect context around an error, run:")
        scripts_dir = Path(__file__).resolve().parent
        print(f"  python3 {scripts_dir}/context.py {path} <LINE_NUM> [radius]")

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
