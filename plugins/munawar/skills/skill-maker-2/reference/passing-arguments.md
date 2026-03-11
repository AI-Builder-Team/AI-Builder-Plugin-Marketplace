# Passing Arguments to Skills

## Invocation

```bash
/skill-name arg1 arg2 arg3
```

## Accessing Arguments in SKILL.md

- `$ARGUMENTS` - All arguments as single string
- `$ARGUMENTS[0]` or `$0` - First argument
- `$ARGUMENTS[1]` or `$1` - Second argument
- `$ARGUMENTS[N]` or `$N` - Nth argument (0-indexed)

## How It Works

`$ARGUMENTS` is **text substitution**, not a shell variable. Claude Code replaces it with the literal argument text in the markdown *before* Claude sees the prompt. So just write `$ARGUMENTS` directly in your skill content — no `echo`, no backticks needed. If `$ARGUMENTS` is not referenced anywhere in the SKILL.md, Claude Code auto-appends `ARGUMENTS: <value>` at the end.

## Example

```yaml
---
name: migrate-component
argument-hint: "[component] [from-framework] [to-framework]"
---

Migrate the $0 component from $1 to $2.

Steps:
1. Read the component at: $0
2. Analyze $1 patterns
3. Convert to $2 syntax
4. Preserve all behavior and tests
```

Running `/migrate-component SearchBar React Vue` gives:
- `$0` = SearchBar
- `$1` = React
- `$2` = Vue

## Limitation — No "Rest of Args" Syntax

`$N` always resolves to a single word. There is no built-in way to get "everything after the first argument" as one string. If your skill takes an ID plus a free-form instruction (e.g. `/audit abc123 show me all the errors`), use `$0` for the ID where you need it (like in a script call), and `$ARGUMENTS` where you need the full string. Claude will see both and naturally understand the structure from context — no parsing instructions needed.

## Arguments in the Frontmatter

Use `argument-hint` to show users what to pass:

```yaml
argument-hint: "[component-name] [component-type]"
```

This appears in autocomplete when the user types `/skill-name`.
