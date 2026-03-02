#!/usr/bin/env python3
"""Extract the conversation flow from a session JSONL.

Usage:
    python3 conversation.py <session.jsonl> [--no-thinking] [--no-tools] [--max-len 300]

Outputs a readable transcript of the session: user messages, assistant text,
thinking blocks, and tool calls with their results.
"""
import argparse
import json
import textwrap
from pathlib import Path


def truncate(text: str, max_len: int) -> str:
    if max_len <= 0 or len(text) <= max_len:
        return text
    return text[:max_len] + f"... ({len(text)} chars)"


def parse_session(path: str, show_thinking: bool, show_tools: bool, max_len: int):
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            t = r.get("type")

            if t == "user":
                msg = r.get("message", {})
                content = msg.get("content")
                ts = r.get("timestamp", "")[:19]

                if isinstance(content, str):
                    print(f"\n{'='*70}")
                    print(f"USER [{ts}]:")
                    print(textwrap.indent(truncate(content, max_len), "  "))

                elif isinstance(content, list) and show_tools:
                    for block in content:
                        if block.get("type") == "tool_result":
                            tid = block.get("tool_use_id", "?")[:20]
                            result_content = block.get("content", "")
                            if isinstance(result_content, list):
                                texts = [
                                    c.get("text", "")
                                    for c in result_content
                                    if c.get("type") == "text"
                                ]
                                result_content = "\n".join(texts)
                            is_err = block.get("is_error", False)
                            prefix = "TOOL ERROR" if is_err else "TOOL RESULT"
                            print(f"  {prefix} [{tid}]:")
                            print(
                                textwrap.indent(
                                    truncate(str(result_content), max_len), "    "
                                )
                            )

            elif t == "assistant":
                msg = r.get("message", {})
                content = msg.get("content", [])
                if not isinstance(content, list):
                    continue

                for block in content:
                    bt = block.get("type")

                    if bt == "thinking" and show_thinking:
                        thinking = block.get("thinking", "")
                        print(f"  THINKING:")
                        print(
                            textwrap.indent(truncate(thinking, max_len), "    ")
                        )

                    elif bt == "text":
                        text = block.get("text", "")
                        print(f"  ASSISTANT:")
                        print(textwrap.indent(truncate(text, max_len), "    "))

                    elif bt == "tool_use" and show_tools:
                        name = block.get("name", "?")
                        inp = block.get("input", {})
                        # Show key params compactly
                        if name == "Bash":
                            detail = inp.get("command", "")
                        elif name == "Read":
                            detail = inp.get("file_path", "")
                        elif name == "Write":
                            detail = inp.get("file_path", "")
                        elif name == "Edit":
                            detail = inp.get("file_path", "")
                        elif name == "Grep":
                            detail = f'pattern={inp.get("pattern","")} path={inp.get("path",".")}'
                        elif name == "Glob":
                            detail = f'pattern={inp.get("pattern","")} path={inp.get("path",".")}'
                        elif name == "Agent":
                            detail = f'type={inp.get("subagent_type","")} desc={inp.get("description","")}'
                        else:
                            detail = json.dumps(inp, separators=(",", ":"))

                        print(f"  TOOL: {name}")
                        print(
                            textwrap.indent(truncate(detail, max_len), "    ")
                        )


def main():
    parser = argparse.ArgumentParser(description="Session conversation transcript")
    parser.add_argument("session_file", help="Path to session JSONL")
    parser.add_argument(
        "--no-thinking", action="store_true", help="Hide thinking blocks"
    )
    parser.add_argument("--no-tools", action="store_true", help="Hide tool calls")
    parser.add_argument(
        "--max-len",
        type=int,
        default=500,
        help="Max chars per block (0=unlimited)",
    )
    args = parser.parse_args()
    parse_session(args.session_file, not args.no_thinking, not args.no_tools, args.max_len)
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
