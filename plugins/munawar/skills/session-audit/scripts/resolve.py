#!/usr/bin/env python3
"""Resolve a session ID to its JSONL file path(s).

Usage:
    python3 resolve.py <session-id> [--project-dir /path/to/project]

Outputs JSON with:
  - main: path to the main session JSONL
  - subagents: list of subagent JSONL paths
  - project_dir: the resolved project directory under ~/.claude/projects/
"""
import argparse
import json
import sys
from pathlib import Path


def find_session(session_id: str, project_dir: str | None = None) -> dict:
    claude_dir = Path.home() / ".claude" / "projects"

    # If project_dir given, encode it; otherwise search all project dirs
    candidates = []
    if project_dir:
        encoded = project_dir.replace("/", "-")
        candidates.append(claude_dir / encoded)
    else:
        if claude_dir.exists():
            candidates = sorted(claude_dir.iterdir())

    for proj in candidates:
        main_file = proj / f"{session_id}.jsonl"
        if main_file.exists():
            subagent_dir = proj / session_id / "subagents"
            subagents = []
            if subagent_dir.exists():
                subagents = sorted(str(p) for p in subagent_dir.glob("*.jsonl"))
            return {
                "main": str(main_file),
                "subagents": subagents,
                "project_dir": str(proj),
            }

    return {"main": None, "subagents": [], "project_dir": None}


def main():
    parser = argparse.ArgumentParser(description="Resolve session ID to file paths")
    parser.add_argument("session_id", help="Session UUID")
    parser.add_argument("--project-dir", help="Project root path (optional)")
    args = parser.parse_args()

    result = find_session(args.session_id, args.project_dir)
    print(json.dumps(result, indent=2))
    if not result["main"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
