---
description: Interactive entry point — asks what kind of Jira to file (Bug / RCA / Doc / Impact Score), then walks you through the inputs. Use when you don't remember the specific subcommand or want guided prompts.
argument-hint: (no arguments — interactive flow)
---

# /tse-jira:new

Interactive entry point for the `tse-jira` plugin. Use this when you want guided prompts rather than CLI-style invocation.

## What it does

1. Asks **"What kind of Jira do you want to file?"** via `AskUserQuestion` — four options:
   - **Bug Jira** (from Zendesk PDF + optional related Jiras)
   - **RCA Jira** (multi-cluster RCA from ≥1 Zendesk PDF + ≥1 related Jira)
   - **Doc Jira** (DOC project — internal finding / Slack-derived / audit-derived; no Zendesk PDF required)
   - **Impact Score** (read-only — score one or more existing Jiras)

2. Chains into the matching interactive flow:
   - Bug → asks for Zendesk PDF path/glob, sibling screenshots, related Jiras, severity, optional codebase investigation
   - RCA → asks for Zendesk PDF(s), related Jira(s), then batched RCA prerequisites (customer, date, clusters, start/end UTC, product, affected components, contributors)
   - Doc → asks for title, description (text or file), optional Slack link, optional related Jiras, confirms issue type (Bug/Task) and assignee
   - Score → asks for Jira key(s) or PDF path(s), optional Zendesk context

3. Validates each input as it's collected:
   - File paths checked via `ls` / `test -f`
   - Jira keys regex-checked, then verified via `getJiraIssue` (read-only — no MCP write)
   - Re-prompts on validation failure

4. Confirms-as-you-go: echoes back what was captured before moving to the next question.

5. Drafts the dry-run preview (both `.md` and Jira-styled `.html`) and stops. No MCP writes until you explicitly say `publish this preview`.

## Mode

Always **dry-run** by default. Even at the end of the interactive flow, the skill writes preview files and waits for explicit publish authorization — same safety rules as the direct commands (`/tse-jira:bug`, `/tse-jira:rca`, `/tse-jira:score`).

To publish: review the preview in your browser, then reply with something containing the word `publish` (e.g., `publish this preview`).

## When to use this vs the direct commands

- **`/tse-jira:new`** — you don't remember which subcommand you want, or you'd rather be walked through it.
- **`/tse-jira:bug ticket.pdf -- RED-NNN`** — you know the exact paths and keys; faster.
- **`/tse-jira:rca`** with partial args also drops into interactive mode to collect missing required inputs.

## Examples

```
# Pure interactive — answer questions as they come
/tse-jira:new

# CLI form (skip interactive) — works identically to direct commands
/tse-jira:bug ~/Downloads/packages/162249/#162249*.pdf -- RED-176559 RED-184754
```

## Safety

- Dry-run by default — no MCP writes during the interactive Q&A phase, ever.
- Validation as you go — bad inputs re-prompt; the skill never coasts forward with a malformed Jira key or missing file.
- Top-level `go` / `yes` does not authorize a `publish` later in the flow — the word `publish` must appear explicitly per the [feedback-destructive-operations](../../../../.claude/projects/-Users-marko-trapani-Downloads-marko-projects-agent-skills/memory/feedback_destructive_operations.md) rule.

## Related

- **Skill:** [`../skills/tse-jira-ticket-creation/SKILL.md`](../skills/tse-jira-ticket-creation/SKILL.md) → "Interactive Mode" section
- **Direct commands:** [`./bug.md`](./bug.md), [`./rca.md`](./rca.md), [`./doc.md`](./doc.md), [`./score.md`](./score.md)
- **Harness safety:** [`SECURITY.md`](../../../SECURITY.md)
