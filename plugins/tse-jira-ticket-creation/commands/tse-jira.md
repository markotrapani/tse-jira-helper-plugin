---
description: Create Redis Jira tickets as a TSE — Bug from Zendesk PDFs, RCA by cloning RCA-41, or impact score estimation. Defaults to DRY-RUN (writes .md + Jira-styled .html previews, no MCP writes). Use --publish to actually file. Aligned with Redis CS Support team Confluence standards.
argument-hint: <bug|rca|score> <required-inputs>+ [-- <optional-inputs>+] [--publish]
---

# /tse-jira

Shortcut for the `tse-jira-ticket-creation` skill. **Defaults to dry-run** — generates a local markdown preview file, never calls MCP write tools. Use `--publish` (or say "publish this preview" after a dry-run) to actually file. Aligned with Redis Customer Support team standards documented in [Confluence](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958).

## Usage

```
# Default: dry-run (writes preview file, never writes to Jira)
/tse-jira bug   <zendesk-pdf>+ [-- <jira-pdfs-or-keys>+]
/tse-jira rca   <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]
/tse-jira score <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]

# Publish: actually fires MCP writes (still asks for explicit confirmation per safety rules)
/tse-jira bug   <zendesk-pdf>+ [-- <jira-pdfs-or-keys>+] --publish
/tse-jira rca   <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+] --publish
```

**Input contract** — the first set of args is **required** (one or more), the optional second set after `--` provides supporting context. The `--publish` flag enables publish mode.

## Mode: Dry-Run (default) vs Publish

### Dry-run (default)

What it does:
1. Reads PDFs / fetches live Jiras
2. Computes impact score, auto-detects fields, resolves dropdowns
3. **Writes BOTH a markdown preview AND a Jira-styled HTML preview** to `~/tse-jira-previews/<project>-<workflow>-<ISO timestamp>.{md,html}` (v0.9+)
4. **Auto-opens the HTML preview in your default browser** (`open <file.html>` on macOS)
4. Reports the path. Stops. **No MCP writes happen.**

What it does NOT do:
- Call `createJiraIssue`, `addCommentToJiraIssue`, `createIssueLink`, `editJiraIssue`, or `transitionJiraIssue`. Ever. In dry-run.

To convert a dry-run into a publish:
- Review the preview file in your viewer of choice
- If everything looks right, say something like "publish this preview" or "publish /Users/.../tse-jira-previews/RED-bug-...md"
- The skill will then load the preview, ask one final explicit confirmation, and fire the writes

### Publish

What it does:
1. Same as dry-run (still produces the preview file as an audit record)
2. **PLUS** asks for one explicit final confirmation before any write tool fires
3. **PLUS** calls the MCP write tools in the right order
4. **PLUS** appends actual API responses to the preview file (key, comment id, link statuses)

Even in publish mode, the harness-level safety net should still prompt you — see the Prerequisites section below.

## Subcommands

### `/tse-jira bug <zendesk-pdf>+ [-- <jira-pdfs>+] [--publish]`

Create a Bug Jira from one or more Zendesk PDFs.

**Required:** one or more Zendesk PDF paths
**Optional:** related Jira PDFs or live Jira keys (after `--`)
**Optional flag:** `--publish` to actually file (default is dry-run)

**Behavior** — invokes `tse-jira-ticket-creation` skill, Workflow A:
1. Reads the Zendesk PDF(s)
2. Extracts customer, summary, description, ticket ID, etc.
3. Computes the 8-130 impact score (recommendation, team leader confirms)
4. Auto-detects project: RED (default), MOD (modules), DOC (docs), RDSC (RDI)
5. Asks the TSE to confirm Severity (TSE-judged, not impact-derived)
6. Maps all Support-standard fields (labels include `CS` / `Support`; Azure tickets get `Azure-Integration` + `ACRE`/`AMR`)
7. Leaves Priority at default `Medium` (PM sets later)
8. Resolves Affected Organizations via paginated dropdown search
9. Sets Seen by Customer/s (required for Environment=Production validation rule)
10. Builds description with Customer Expectations, A-A mapping (if applicable), log-ref format
11. **Writes preview file** at `~/tse-jira-previews/RED-bug-<timestamp>.md` — done in dry-run
12. **On `--publish` or "publish this" follow-up**: asks for explicit final yes, then:
    - Creates the Bug via MCP
    - Posts the impact-score breakdown as a comment
    - Links related Jiras via `Relates` (id 10003)
    - For Azure tickets: populates `customfield_10063` with `0. Incident short description:` template
    - Appends actual API responses to the preview file

**Examples:**
```
# Dry-run (default)
/tse-jira bug ~/Downloads/redislabs.zendesk.com_tickets_162249_print.pdf
/tse-jira bug ticket_162249.pdf -- RED-176559 RED-184754

# Publish — only after reviewing a dry-run
/tse-jira bug ticket_162249.pdf -- RED-176559 RED-184754 --publish
```

### `/tse-jira rca <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+] [--publish]`

Create a multi-cluster RCA by cloning RCA-41's defaults. Requires at least one Jira (the related bug Jira(s) that feed the root cause analysis).

**Required:** one or more Jira PDFs OR live Jira keys
**Optional:** Zendesk PDFs (after `--`) for customer-impact context
**Optional flag:** `--publish` to actually file (default is dry-run)

You'll also be asked once for:
- Customer name (or ClusterID / Major Service for multi-customer)
- Incident date (`mm/dd/yyyy`)
- Cluster names
- Start time and End time (UTC)
- Product: `Redis Cloud` / `Redis Software` / `AMR`
- Affected components (multi-select from 44 options)
- Contributors

**Behavior** — invokes `tse-jira-ticket-creation` skill, Workflow B:
1. Reads all Jira (PDF or live) and Zendesk PDFs
2. **Azure prerequisite check**: refuses if Azure RCA without a RED/MOD bug among the inputs
3. Extracts bug summaries, action items drafts, log patterns from Jira PDFs
4. Extracts customer impact, support-package paths from Zendesk PDFs
5. Builds RCA payload modeling RCA-41 defaults (project=RCA, type=10590, etc.)
6. **Writes preview file** at `~/tse-jira-previews/RCA-rca-<timestamp>.md` — done in dry-run
7. **On `--publish` or "publish this" follow-up**: asks for explicit final yes, then:
    - Creates the RCA in the "Root Cause Analysis" project
    - Links each related bug via `createIssueLink` (type `Relates`)
    - Appends actual API responses to the preview file
8. Returns RCA key + browse URL + checklist of placeholders + transition reminder

**Examples:**
```
# Dry-run (default)
/tse-jira rca RED-172012 RED-172734 -- ZD-146983.pdf ZD-146173.pdf

# Publish — only after reviewing a dry-run
/tse-jira rca RED-172012 RED-172734 -- ZD-146983.pdf --publish
```

### `/tse-jira score <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]`

Compute the impact score for one or more existing Jira tickets. **Inherently read-only — no `--publish` flag needed.** Triage / planning tool.

**Required:** one or more Jira inputs (PDF or live key)
**Optional:** Zendesk PDFs (after `--`) for supplemental customer/frequency context

**Behavior** — invokes `tse-jira-ticket-creation` skill, Workflow C:
1. Sources content (live Jira via `getJiraIssue`; PDFs via Read; Zendesk PDFs supplement)
2. Applies the 6-component model with multipliers (CloudOps / Customer)
3. Outputs structured breakdown
4. Does **not** create or modify any ticket
5. After scoring, offers (on explicit user "publish to RED-NNN"): apply the score to the Jira(s) by setting `customfield_10585` and posting a breakdown comment

**Examples:**
```
/tse-jira score RED-172734
/tse-jira score RED-172734 RED-172012
/tse-jira score RED-172734 -- ZD-146983.pdf ZD-146173.pdf
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
- **Azure RCA gated.** Won't create an Azure RCA without a RED/MOD bug among the inputs.
- **Score is a recommendation.** Per Support docs, impact scores should be confirmed by the team leader.

## Related

- **Skill:** [`../skills/tse-jira-ticket-creation/SKILL.md`](../skills/tse-jira-ticket-creation/SKILL.md) — full reference docs in `references/`
- **Harness safety:** [`SECURITY.md`](../../../SECURITY.md) — settings.json permission rule (at marketplace root)
- **Complementary:** `everything-claude-code/jira-integration` + `/jira` for retrieving / commenting on / transitioning existing tickets
- **Inspired by:** [`markotrapani/jira-helper`](https://github.com/markotrapani/jira-helper) (Python CLI version that generates markdown rather than creating tickets directly)
