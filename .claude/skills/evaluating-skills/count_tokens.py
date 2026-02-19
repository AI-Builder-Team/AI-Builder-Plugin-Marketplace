#!/usr/bin/env python3
"""
Token Counter for Agent Skills

Counts tokens in skill files using tiktoken (Claude's tokenizer).
Provides accurate token counts for skill evaluation (Step 9).

Excludes EVALUATION_REPORT.md from counts as it's generated output,
not part of the skill content itself.

Usage:
    python count_tokens.py <skill_directory>
    python count_tokens.py ~/.claude/skills/my-skill
    python count_tokens.py .claude/skills/evaluating-skills

Output:
    - Token count per file (metadata, main body, bundled files)
    - Total token count
    - Character count for comparison
    - Efficiency guidance
"""

import sys
import os
from pathlib import Path
from typing import Dict, Tuple


def count_tokens_tiktoken(text: str) -> int:
    """
    Count tokens using tiktoken (OpenAI's tokenizer, close approximation to Claude).
    Falls back to character-based estimation if tiktoken not available.

    Args:
        text: Text content to tokenize

    Returns:
        Token count
    """
    try:
        import tiktoken
        # Use cl100k_base encoding (GPT-4/Claude approximation)
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except ImportError:
        # Fallback: rough estimation (chars / 4)
        return len(text) // 4


def extract_frontmatter(content: str) -> Tuple[str, str]:
    """
    Extract YAML frontmatter from skill file.

    Args:
        content: Full file content

    Returns:
        Tuple of (frontmatter, body)
    """
    if not content.startswith("---"):
        return "", content

    lines = content.split("\n")
    end_idx = -1

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return "", content

    frontmatter = "\n".join(lines[:end_idx + 1])
    body = "\n".join(lines[end_idx + 1:])

    return frontmatter, body


def analyze_skill_tokens(skill_path: str) -> Dict[str, any]:
    """
    Analyze token counts for all files in a skill directory.

    Args:
        skill_path: Path to skill directory

    Returns:
        Dictionary with token analysis results
    """
    skill_dir = Path(skill_path).resolve()

    if not skill_dir.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

    if not skill_dir.is_dir():
        raise ValueError(f"Path is not a directory: {skill_dir}")

    results = {
        "skill_name": skill_dir.name,
        "skill_path": str(skill_dir),
        "files": {},
        "metadata_tokens": 0,
        "main_body_tokens": 0,
        "bundled_files_tokens": 0,
        "total_tokens": 0,
        "total_chars": 0
    }

    # Find SKILL.md
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_dir}")

    # Analyze SKILL.md
    with open(skill_file, "r", encoding="utf-8") as f:
        content = f.read()

    frontmatter, body = extract_frontmatter(content)

    metadata_tokens = count_tokens_tiktoken(frontmatter)
    body_tokens = count_tokens_tiktoken(body)

    results["metadata_tokens"] = metadata_tokens
    results["main_body_tokens"] = body_tokens
    results["files"]["SKILL.md"] = {
        "metadata_tokens": metadata_tokens,
        "body_tokens": body_tokens,
        "total_tokens": metadata_tokens + body_tokens,
        "chars": len(content)
    }
    results["total_chars"] += len(content)

    # Analyze bundled files (any .md files except SKILL.md and EVALUATION_REPORT.md)
    # EVALUATION_REPORT.md is excluded as it's generated output, not skill content
    for md_file in skill_dir.glob("*.md"):
        if md_file.name in ["SKILL.md", "EVALUATION_REPORT.md"]:
            continue

        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        file_tokens = count_tokens_tiktoken(content)
        results["bundled_files_tokens"] += file_tokens
        results["files"][md_file.name] = {
            "tokens": file_tokens,
            "chars": len(content)
        }
        results["total_chars"] += len(content)

    # Analyze any script files (.py, .sh, .js, etc.)
    for script_file in skill_dir.glob("*"):
        if script_file.suffix in [".py", ".sh", ".js", ".ts", ".bash"]:
            with open(script_file, "r", encoding="utf-8") as f:
                content = f.read()

            file_tokens = count_tokens_tiktoken(content)
            results["bundled_files_tokens"] += file_tokens
            results["files"][script_file.name] = {
                "tokens": file_tokens,
                "chars": len(content)
            }
            results["total_chars"] += len(content)

    results["total_tokens"] = (
        results["metadata_tokens"] +
        results["main_body_tokens"] +
        results["bundled_files_tokens"]
    )

    return results


def format_output(results: Dict[str, any]) -> str:
    """
    Format token analysis results for display.

    Args:
        results: Token analysis dictionary

    Returns:
        Formatted string output
    """
    output = []
    output.append("=" * 60)
    output.append(f"Token Analysis: {results['skill_name']}")
    output.append("=" * 60)
    output.append("")

    # SKILL.md breakdown
    skill_md = results["files"]["SKILL.md"]
    output.append("SKILL.md:")
    output.append(f"  Metadata (frontmatter): {skill_md['metadata_tokens']:>6} tokens")
    output.append(f"  Main body:              {skill_md['body_tokens']:>6} tokens")
    output.append(f"  Subtotal:               {skill_md['total_tokens']:>6} tokens ({skill_md['chars']:>6} chars)")
    output.append("")

    # Bundled files
    if results["bundled_files_tokens"] > 0:
        output.append("Bundled Files:")
        for filename, stats in results["files"].items():
            if filename == "SKILL.md":
                continue
            output.append(f"  {filename:30} {stats['tokens']:>6} tokens ({stats['chars']:>6} chars)")
        output.append(f"  Bundled files subtotal: {results['bundled_files_tokens']:>6} tokens")
        output.append("")

    # Total
    output.append("=" * 60)
    output.append(f"TOTAL:                    {results['total_tokens']:>6} tokens ({results['total_chars']:>6} chars)")
    output.append("=" * 60)
    output.append("")

    # Efficiency guidance
    output.append("Token Efficiency Guidance:")
    output.append("  • Main body <5,000 tokens: Recommended")
    output.append("  • Metadata <100 tokens: Recommended")

    if results["main_body_tokens"] > 5000:
        output.append(f"  ⚠ Main body ({results['main_body_tokens']} tokens) exceeds 5,000 token recommendation")

    if results["metadata_tokens"] > 100:
        output.append(f"  ⚠ Metadata ({results['metadata_tokens']} tokens) exceeds 100 token recommendation")

    if results["total_tokens"] < 5000:
        output.append(f"  ✓ Total skill is lean ({results['total_tokens']} tokens)")
    elif results["total_tokens"] < 10000:
        output.append(f"  ℹ Total skill is moderate ({results['total_tokens']} tokens)")
    else:
        output.append(f"  ⚠ Total skill is large ({results['total_tokens']} tokens) - consider splitting content")

    return "\n".join(output)


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python count_tokens.py <skill_directory>")
        print("Example: python count_tokens.py ~/.claude/skills/my-skill")
        sys.exit(1)

    skill_path = sys.argv[1]

    try:
        results = analyze_skill_tokens(skill_path)
        print(format_output(results))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
