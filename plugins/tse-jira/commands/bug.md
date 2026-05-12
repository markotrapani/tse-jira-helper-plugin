---
description: Create a Redis Bug Jira from one or more Zendesk PDFs. Defaults to DRY-RUN (writes .md + Jira-styled .html previews, no MCP writes). Use --publish to actually file. Aligned with Redis CS Support team Confluence standards.
argument-hint: <zendesk-pdf>+ [-- <jira-pdfs-or-keys>+] [--publish]
---

# /tse-jira:bug

Shortcut for the `tse-jira-ticket-creation` skill — Workflow A (Bug filing). **Defaults to dry-run** — generates local markdown + Jira-styled HTML preview files, never calls MCP write tools. Use `--publish` (or say "publish this preview" after a dry-run) to actually file. Aligned with Redis Customer Support team standards documented in [Confluence](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958).

## Usage

```
# Default: dry-run (writes preview files, never writes to Jira)
/tse-jira:bug <zendesk-pdf>+ [-- <jira-pdfs-or-keys>+]

# Publish: actually fires MCP writes (still asks for explicit confirmation per safety rules)
/tse-jira:bug <zendesk-pdf>+ [-- <jira-pdfs-or-keys>+] --publish
```

**Input contract** — one or more Zendesk PDFs are **required**; the optional second set after `--` provides supporting context (related Jira PDFs or live keys). The `--publish` flag enables publish mode.

## Mode: Dry-Run (default) vs Publish

### Dry-run (default)

What it does:
1. Reads PDFs / fetches live Jiras
2. Scans the PDF's directory for sibling screenshots and supplementary artifacts (PNG/JPG/GIF/WEBP/TXT/ZIP) — v0.10+
3. Computes impact score, auto-detects fields, resolves dropdowns
4. **Writes BOTH a markdown preview AND a Jira-styled HTML preview** to `~/tse-jira-previews/<project>-bug-<ISO timestamp>.{md,html}` (v0.9+)
5. **Auto-opens the HTML preview in your default browser** (`open <file.html>` on macOS)
6. Reports the paths. Stops. **No MCP writes happen.**

What it does NOT do:
- Call `createJiraIssue`, `addCommentToJiraIssue`, `createIssueLink`, `editJiraIssue`, or `transitionJiraIssue`. Ever. In dry-run.

To convert a dry-run into a publish:
- Review the HTML preview in your browser
- If everything looks right, say something like "publish this preview" or "publish /Users/.../tse-jira-previews/RED-bug-...md"
- The skill will then load the preview, ask one final explicit confirmation, and fire the writes

### Publish

What it does:
1. Same as dry-run (still produces the preview files as an audit record)
2. **PLUS** asks for one explicit final confirmation before any write tool fires
3. **PLUS** calls the MCP write tools in the right order
4. **PLUS** appends actual API responses to the preview file (key, comment id, link statuses)

Even in publish mode, the harness-level safety net should still prompt you — see the Prerequisites section below.

## Behavior

Invokes the `tse-jira-ticket-creation` skill, Workflow A:
1. Reads the Zendesk PDF(s)
2. Extracts customer, summary, description, ticket ID, etc.
3. Computes the 8-130 impact score (recommendation, team leader confirms)
4. Auto-detects project: RED (default), MOD (modules), DOC (docs), RDSC (RDI)
5. Asks the TSE to confirm Severity (TSE-judged, not impact-derived)
6. Maps all Support-standard fields (labels include `CS` / `Support`; Azure tickets get `Azure-Integration` + `ACRE`/`AMR`)
7. Leaves Priority at default `Medium` (PM sets later)
8. Resolves Affected Organizations via paginated dropdown search
9. Sets Seen by Customer/s (required for Environment=Production validation rule)
10. Builds H2-sectioned description body anchored to canonical Jira examples (see `references/canonical-jiras/`)
11. Embeds customer screenshots at meaningful spots in the description (v0.10+) — manual upload reminder included
12. **Writes preview files** at `~/tse-jira-previews/<project>-bug-<timestamp>.{md,html}` — done in dry-run
13. **On `--publish` or "publish this" follow-up**: asks for explicit final yes, then:
    - Creates the Bug via MCP
    - Posts the impact-score breakdown as a comment
    - Links related Jiras via `Relates` (id 10003)
    - For Azure tickets: populates `customfield_10063` with `0. Incident short description:` template
    - Appends actual API responses to the preview file

## Examples

```
# Dry-run (default)
/tse-jira:bug ~/Downloads/redislabs.zendesk.com_tickets_162249_print.pdf
/tse-jira:bug ~/Downloads/packages/162249/#162249*.pdf -- RED-176559 RED-184754

# Publish — only after reviewing a dry-run
/tse-jira:bug ticket_162249.pdf -- RED-176559 RED-184754 --publish
```

## Prerequisites

### 1. Claude.ai Atlassian MCP authenticated

```
/mcp
# Find Atlassian → Authenticate → sign in with your Redis Labs Atlassian account
```

Confirm with `mcp__claude_ai_Atlassian__getAccessibleAtlassianResources` — should return id `06f73ca7-8f2c-4392-b40a-08288e9d0ba3` for `redislabs.atlassian.net`.

### 2. (Strongly recommended) Harness-level safety net in `~/.claude/settings.json`

Add the 10 Atlassian write tools to your `permissions.ask` list. Even if the skill ever misreads "publish" intent, Claude Code will prompt you per call. See [SECURITY.md](../../../SECURITY.md) for the exact JSON snippet.

## Safety

- **Dry-run is the default** — no MCP writes happen unless `--publish` flag is set or you say "publish this preview" referring to a generated preview file.
- **Implicit confirmations don't count.** "Yes", "go", "looks good" are NOT publish keywords. You must say something containing "publish".
- **Top-level go doesn't cover later steps.** Each destructive write call re-confirms.
- **PII guard.** If PDFs contain phone numbers / internal customer emails, the skill flags it before writing the preview.
- **Score is a recommendation.** Per Support docs, impact scores should be confirmed by the team leader.

## Related

- **Skill:** [`../skills/tse-jira-ticket-creation/SKILL.md`](../skills/tse-jira-ticket-creation/SKILL.md) — full reference docs in `references/`
- **Sibling commands:** `/tse-jira:rca`, `/tse-jira:score`
- **Harness safety:** [`SECURITY.md`](../../../SECURITY.md) — settings.json permission rule (at marketplace root)
- **Inspired by:** [`markotrapani/jira-helper`](https://github.com/markotrapani/jira-helper) (Python CLI version that generates markdown rather than creating tickets directly)
