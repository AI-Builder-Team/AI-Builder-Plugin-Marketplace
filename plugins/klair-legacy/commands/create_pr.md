---
description: Create feature branch, commit changes, and open PR
argument-hint: [optional-branch-name]
---

Create a pull request following this workflow:

1. **Check current branch**:
   - Use `git branch --show-current` to determine the current branch
   - If on `main`, proceed to create a feature branch
   - If already on a feature branch, skip to step 3

2. **Create feature branch** (only if on main):
   - If $ARGUMENTS is provided, use it as the branch name
   - If no arguments provided, ask the user for a branch name suggestion based on the changes
   - Create and checkout the new branch using `git checkout -b <branch-name>`

3. **Commit changes**:
   - Follow the standard git commit workflow from your instructions:
     - Run `git status` to see all untracked files
     - Run `git diff` to see staged and unstaged changes
     - Run `git log -5 --oneline` to see recent commit messages for style reference
   - Analyze the changes and draft an appropriate commit message
   - Stage relevant files with `git add .` (or specific files if needed)
   - Create commit with message ending with the standard footer:
     ```
     🤖 Generated with [Claude Code](https://claude.com/claude-code)

     Co-Authored-By: Claude <noreply@anthropic.com>
     ```

4. **Validate feature/spec documents** (if applicable):
   - Check if any files in `features/` directory were created or modified using `git diff main...HEAD --name-only | grep "^features/"`

   **For spec documents** (`specs/*/spec.md`):
   - Read the spec and check if `**Status:**` is set to "Completed" or similar
   - If status is not complete, prompt user: "The spec status is currently '[status]'. Should I update it to 'Completed'?"
   - Check if a `checklist.md` exists in the same spec folder
   - If checklist exists, launch a Task agent to verify all checklist items are marked complete (`- [x]` vs `- [ ]`)
   - If incomplete items found, list them and ask user how to proceed

   **For feature documents** (`FEATURE.md`):
   - Read the FEATURE.md and locate the "## Files Touched" section
   - Compare against actual files changed in the PR using `git diff main...HEAD --name-only`
   - If new files were touched that aren't listed, prompt user: "The following files were changed but not listed in Files Touched: [list]. Should I add them?"
   - Update the Files Touched section if user confirms

5. **Push to remote**:
   - Push the branch using `git push -u origin <branch-name>`

6. **Confirm Linear tickets**:
   - Ask user to provide the Linear ticket ID(s) related to this PR (e.g., KLAIR-1234)
   - If ticket IDs are unclear or not provided, prompt user to confirm
   - Ask for a brief description of each ticket if not obvious from context

7. **Create Pull Request**:
   - Use `gh pr create --draft` to create the PR as a draft
   - Analyze ALL commits in the branch (not just the latest) using `git log main..HEAD` and `git diff main...HEAD`
   - **PR Title format**: `[TICKET-ID1, TICKET-ID2] One sentence description of the change`
     - Example: `[KLAIR-1234, KLAIR-1235] Add validation for feature documents in PR workflow`
   - Generate a comprehensive PR description with:
     - **Linear Tickets**: List each ticket ID with its description
     - **Summary**: 1-3 bullet points covering all changes
     - **Test plan**: Bulleted markdown checklist of testing steps
     - Footer: "🤖 Generated with [Claude Code](https://claude.com/claude-code)"
   - Use HEREDOC format for the PR body
   - Return the PR URL to the user

**Important notes**:
- Never skip hooks or use --no-verify
- Check authorship before amending commits
- Do not push force to main/master
- Follow the project's commit message style from git log
