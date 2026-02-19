# Version History

## v2.2 (2025-10-22): Documentation improvements and progressive disclosure
- Enhanced `count_tokens.py` documentation to explicitly note EVALUATION_REPORT.md exclusion
- Added inline comments clarifying why evaluation reports are excluded from token counts
- Moved version history to separate file (VERSION_HISTORY.md) for better progressive disclosure
- Reduced main SKILL.md body from 2,591 tokens to 2,330 tokens (261 token reduction, ~10% improvement)
- Total skill remains moderate at 6,791 tokens (within guidelines)

## v2.1 (2025-10-22): Added utility script following best practices
- Created `count_tokens.py` script for accurate token counting (Step 9)
- Updated Step 9 to reference the bundled script instead of manual estimation
- Script uses tiktoken for precise token counts with fallback to character-based estimation
- Follows skill's own prescription: "Use executable scripts instead of generating code"
- Self-measured with new script: 6,449 total tokens (moderate, well within guidelines)

## v2.0 (2025-10-21): Refactored based on self-evaluation findings
- Added table of contents for navigation
- Extracted report template to bundled file (report-template.md)
- Removed redundant final checklist section
- Condensed verbose sections (freedom levels, best practices, observational analysis)
- Renamed directory from running-skill-qc to evaluating-skills for consistency
- Created test scenarios file (test-scenarios.md) with 3 evaluation examples
- Reduced from 11,401 characters (~2,850 tokens) to 9,117 characters (~2,280 tokens) - 20% reduction

## v1.0 (2025-10-21): Initial framework
- Initial framework based on Anthropic best practices and Claude Cookbooks
- 12-step systematic evaluation workflow
- Comprehensive checklist-based approach
- Basic token estimation guidance
