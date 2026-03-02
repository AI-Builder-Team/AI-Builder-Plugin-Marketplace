#!/usr/bin/env python3
"""Filter a session transcript to show only one category of record.

Usage:
    python3 only.py <session.jsonl> <mode> [--max-len 500]

Modes:
    user        — human text messages only
    assistant   — assistant text responses only
    thinking    — chain-of-thought blocks only
    tools       — tool calls only (name + input summary)
    results     — tool results only
    errors      — tool errors only (is_error=true or error keywords)
    bash        — bash commands and their outputs paired together
    edits       — Edit/Write tool calls with file paths
    agents      — Agent tool calls (subagent spawns)

Each record shows turn number, line, timestamp, and content.
"""
import argparse
import json
import textwrap
from pathlib import Path


def truncate(text: str, max_len: int) -> str:
    if max_len <= 0 or len(text) <= max_len:
        return text
    return text[:max_len] + f"... ({len(text)} chars)"


def summarize_tool_input(name: str, inp: dict) -> str:
    if name == "Bash":
        return inp.get("command", "")
    elif name in ("Read", "Write"):
        return inp.get("file_path", "")
    elif name == "Edit":
        fp = inp.get("file_path", "")
        old = inp.get("old_string", "")[:120]
        new = inp.get("new_string", "")[:120]
        return f"{fp}\n  old: {old!r}\n  new: {new!r}"
    elif name == "Grep":
        return f'pattern={inp.get("pattern","")} path={inp.get("path",".")}'
    elif name == "Glob":
        return f'pattern={inp.get("pattern","")} path={inp.get("path",".")}'
    elif name == "Agent":
        desc = inp.get("description", "")
        stype = inp.get("subagent_type", "")
        prompt = inp.get("prompt", "")[:300]
        bg = " [background]" if inp.get("run_in_background") else ""
        return f"type={stype} desc={desc}{bg}\n  prompt: {prompt}"
    else:
        return json.dumps(inp, separators=(",", ":"))


def extract_tool_result_text(block: dict) -> str:
    result = block.get("content", "")
    if isinstance(result, list):
        result = "\n".join(
            c.get("text", "") for c in result if c.get("type") == "text"
        )
    return str(result)


def main():
    parser = argparse.ArgumentParser(description="Filter session to one record category")
    parser.add_argument("session_file", help="Path to session JSONL")
    parser.add_argument(
        "mode",
        choices=["user", "assistant", "thinking", "tools", "results", "errors", "bash", "edits", "agents"],
        help="What to show",
    )
    parser.add_argument("--max-len", type=int, default=500, help="Max content length (0=unlimited)")
    args = parser.parse_args()

    mode = args.mode
    ml = args.max_len
    turn = 0
    count = 0

    # For bash mode, we need to pair calls with results
    # tool_use_id -> {name, input, line, turn, ts}
    pending_bash = {}

    with open(args.session_file) as f:
        for line_num, line in enumerate(f, 1):
            r = json.loads(line)
            t = r.get("type")
            ts = r.get("timestamp", "")[:19]

            if t == "user":
                msg = r.get("message", {})
                content = msg.get("content")

                if isinstance(content, str):
                    turn += 1
                    if mode == "user":
                        count += 1
                        print(f"[{count}] Turn {turn} | Line {line_num} | {ts}")
                        print(textwrap.indent(truncate(content, ml), "  "))
                        print()

                if isinstance(content, list):
                    for block in content:
                        if block.get("type") != "tool_result":
                            continue
                        tid = block.get("tool_use_id", "?")
                        is_err = block.get("is_error", False)
                        result_text = extract_tool_result_text(block)

                        if mode == "results":
                            count += 1
                            label = "ERROR" if is_err else "OK"
                            print(f"[{count}] Turn {turn} | Line {line_num} | {ts} | {label} [{tid[:25]}]")
                            print(textwrap.indent(truncate(result_text, ml), "  "))
                            print()

                        elif mode == "errors" and is_err:
                            count += 1
                            print(f"[{count}] Turn {turn} | Line {line_num} | {ts} | [{tid[:25]}]")
                            print(textwrap.indent(truncate(result_text, ml), "  "))
                            print()

                        elif mode == "bash" and tid in pending_bash:
                            call = pending_bash.pop(tid)
                            count += 1
                            label = "ERROR" if is_err else "OK"
                            print(f"[{count}] Turn {turn} | Line {call['line']}->{line_num} | {call['ts']} | {label}")
                            print(f"  $ {truncate(call['command'], ml)}")
                            if result_text.strip():
                                print(f"  => {truncate(result_text, ml)}")
                            print()

                # Also check toolUseResult for error keywords
                tool_result = r.get("toolUseResult")
                if tool_result and mode == "errors":
                    result_str = str(tool_result)
                    if any(kw in result_str for kw in ["Error", "error", "FAILED", "failed", "Exception", "Traceback"]):
                        count += 1
                        print(f"[{count}] Turn {turn} | Line {line_num} | {ts} | via toolUseResult")
                        print(textwrap.indent(truncate(result_str, ml), "  "))
                        print()

                # bash mode: also pair with toolUseResult
                if mode == "bash" and tool_result:
                    # Check pending bash by iterating (toolUseResult doesn't carry tool_use_id directly)
                    # We match by checking if there's exactly one pending bash call
                    result_str = str(tool_result)
                    for tid, call in list(pending_bash.items()):
                        if call.get("source_uuid") == r.get("parentUuid"):
                            count += 1
                            has_err = any(kw in result_str for kw in ["Error", "error", "FAILED", "Traceback"])
                            label = "ERROR" if has_err else "OK"
                            print(f"[{count}] Turn {turn} | Line {call['line']}->{line_num} | {call['ts']} | {label}")
                            print(f"  $ {truncate(call['command'], ml)}")
                            if result_str.strip():
                                print(f"  => {truncate(result_str, ml)}")
                            print()
                            del pending_bash[tid]
                            break

            elif t == "assistant":
                msg = r.get("message", {})
                content = msg.get("content", [])
                if not isinstance(content, list):
                    continue
                assistant_uuid = r.get("uuid", "")

                for block in content:
                    bt = block.get("type")

                    if bt == "text" and mode == "assistant":
                        text = block.get("text", "")
                        if text.strip():
                            count += 1
                            print(f"[{count}] Turn {turn} | Line {line_num} | {ts}")
                            print(textwrap.indent(truncate(text, ml), "  "))
                            print()

                    elif bt == "thinking" and mode == "thinking":
                        thinking = block.get("thinking", "")
                        if thinking.strip():
                            count += 1
                            print(f"[{count}] Turn {turn} | Line {line_num} | {ts}")
                            print(textwrap.indent(truncate(thinking, ml), "  "))
                            print()

                    elif bt == "tool_use":
                        name = block.get("name", "?")
                        tid = block.get("id", "")
                        inp = block.get("input", {})

                        if mode == "tools":
                            summary = summarize_tool_input(name, inp)
                            count += 1
                            print(f"[{count}] Turn {turn} | Line {line_num} | {ts} | {name} [{tid[:25]}]")
                            print(textwrap.indent(truncate(summary, ml), "  "))
                            print()

                        elif mode == "bash" and name == "Bash":
                            pending_bash[tid] = {
                                "command": inp.get("command", ""),
                                "line": line_num,
                                "ts": ts,
                                "source_uuid": assistant_uuid,
                            }

                        elif mode == "edits" and name in ("Edit", "Write"):
                            summary = summarize_tool_input(name, inp)
                            count += 1
                            print(f"[{count}] Turn {turn} | Line {line_num} | {ts} | {name}")
                            print(textwrap.indent(truncate(summary, ml), "  "))
                            print()

                        elif mode == "agents" and name == "Agent":
                            summary = summarize_tool_input(name, inp)
                            count += 1
                            print(f"[{count}] Turn {turn} | Line {line_num} | {ts}")
                            print(textwrap.indent(truncate(summary, ml), "  "))
                            print()

    print("=" * 60)
    print(f"Mode: {mode} | Total: {count}")
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
