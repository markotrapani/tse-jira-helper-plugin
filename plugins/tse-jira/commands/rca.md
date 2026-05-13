---
description: Create a multi-cluster RCA Jira by cloning RCA-41 defaults. Requires at least one Zendesk PDF AND at least one related Jira (PDF or live key). Defaults to DRY-RUN — writes .md + Jira-styled .html previews, no MCP writes. Use --publish to actually file.
argument-hint: <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+] [--publish]
---

# /tse-jira:rca

Shortcut for the `tse-jira-ticket-creation` skill — Workflow B (RCA filing). **Defaults to dry-run** — generates local markdown + Jira-styled HTML preview files, never calls MCP write tools. Use `--publish` (or say "publish this preview" after a dry-run) to actually file. Aligned with the Redis [RCA Initiation and Data Collection Procedure](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4575690753) and [RCA-41 template](https://redislabs.atlassian.net/browse/RCA-41).

## Usage

```
# Default: dry-run (writes preview files, never writes to Jira)
/tse-jira:rca <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]

# Publish: actually fires MCP writes (still asks for explicit confirmation per safety rules)
/tse-jira:rca <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+] --publish
```

**Input contract** — **both** sides required (v0.12+ tightening, 2026-05-12):
- ≥1 Jira PDF (or live Jira key) — the bugs that feed the root cause analysis.
- ≥1 Zendesk PDF — customer-facing context for impact statement and timeline.

**Exception:** automation-initiated cluster-incident-shape RCAs (e.g. RCA-563) may have no customer Zendesk. The skill detects this case via cluster ID / automation reporter signals and waives the Zendesk requirement, asking for cluster context instead.

The `--publish` flag enables publish mode.

### Invoking without arguments — interactive mode (v0.12+)

`/tse-jira:rca` with no arguments drops into **interactive mode**: asks for the Zendesk PDF(s) (≥1), the related Jira(s) (≥1), then batches the RCA prerequisites (customer, incident date, clusters, start/end UTC, product, affected components, contributors). Validation runs as you go. See [SKILL.md → Interactive Mode](../skills/tse-jira-ticket-creation/SKILL.md).

If only the Jiras are provided on the CLI (`/tse-jira:rca RED-XXX RED-YYY`) with no Zendesk after `--`, the skill drops into interactive mode to collect the Zendesk side rather than erroring out.

## Mode: Dry-Run (default) vs Publish

### Dry-run (default)

1. Reads PDFs / fetches live Jiras
2. Auto-detects RCA shape: customer-RCA vs cluster-incident-RCA
3. **Writes BOTH a markdown preview AND a Jira-styled HTML preview** to `~/tse-jira-previews/RCA-rca-<ISO timestamp>.{md,html}`
4. **Auto-opens the HTML preview in your default browser** (`open <file.html>` on macOS)
5. Reports the paths. Stops. **No MCP writes happen.**

To convert into a publish: review the HTML preview, then say "publish this preview" or `--publish`. The skill will then ask one final explicit confirmation and fire the writes.

### Publish

1. Same as dry-run (still produces the preview files as an audit record)
2. **PLUS** asks for one explicit final confirmation before any write tool fires
3. **PLUS** calls the MCP write tools in the right order
4. **PLUS** appends actual API responses to the preview file (key, link statuses)

Even in publish mode, the harness-level safety net should still prompt you — see Prerequisites.

## Inputs the skill will ask for once

- Customer name (or ClusterID / Major Service for multi-customer)
- Incident date (`mm/dd/yyyy`)
- Cluster names
- Start time and End time (UTC)
- Product: `Redis Cloud` / `Redis Software` / `AMR`
- Affected components (multi-select from 44 options)
- Contributors

## Behavior

Invokes the `tse-jira-ticket-creation` skill, Workflow B:
1. Reads all Jira (PDF or live) and Zendesk PDFs
2. **Azure prerequisite check**: refuses if Azure RCA without a RED/MOD bug among the inputs
3. Extracts bug summaries, action items drafts, log patterns from Jira PDFs
4. Extracts customer impact, support-package paths from Zendesk PDFs
5. Builds RCA payload modeling RCA-41 defaults (project=RCA, type=10590, etc.)
6. Anchors structure to canonical RCAs in `references/canonical-jiras/` (RCA-583 customer-RCA shape; RCA-563 cluster-incident shape)
7. **Writes preview files** at `~/tse-jira-previews/RCA-rca-<timestamp>.{md,html}` — done in dry-run
8. **On `--publish` or "publish this" follow-up**: asks for explicit final yes, then:
    - Creates the RCA in the "Root Cause Analysis" project
    - Links each related bug via `createIssueLink` (type `Relates`)
    - Appends actual API responses to the preview file
9. Returns RCA key + browse URL + checklist of placeholders + transition reminder

## Examples

```
# Dry-run (default) — live Jira keys + Zendesk PDFs for context
/tse-jira:rca RED-172012 RED-172734 -- ZD-146983.pdf ZD-146173.pdf

# Dry-run (default) — Jira PDFs only
/tse-jira:rca jira_RED-172012.pdf jira_RED-172734.pdf

# Publish — only after reviewing a dry-run
/tse-jira:rca RED-172012 RED-172734 -- ZD-146983.pdf --publish
```

## Prerequisites

### 1. Claude.ai Atlassian MCP authenticated

```
/mcp
# Find Atlassian → Authenticate → sign in with your Redis Labs Atlassian account
```

Confirm with `mcp__claude_ai_Atlassian__getAccessibleAtlassianResources` — should return id `06f73ca7-8f2c-4392-b40a-08288e9d0ba3` for `redislabs.atlassian.net`.

### 2. (Strongly recommended) Harness-level safety net in `~/.claude/settings.json`

Add the 10 Atlassian write tools to your `permissions.ask` list. See [SECURITY.md](../../../SECURITY.md).

## Safety

- **Dry-run is the default** — no MCP writes happen unless `--publish` flag is set or you say "publish this preview".
- **Implicit confirmations don't count.** You must say something containing "publish".
- **Top-level go doesn't cover later steps.** Each destructive write call re-confirms.
- **Azure RCA gated.** Won't create an Azure RCA without a RED/MOD bug among the inputs.

## Related

- **Skill:** [`../skills/tse-jira-ticket-creation/SKILL.md`](../skills/tse-jira-ticket-creation/SKILL.md) — Workflow B + RCA template in `references/rca-template.md`
- **Sibling commands:** `/tse-jira:bug`, `/tse-jira:score`
- **Harness safety:** [`SECURITY.md`](../../../SECURITY.md)
