---
description: Create a Documentation (DOC) Jira from a finding — no Zendesk PDF required. Defaults to DRY-RUN (writes .md + Jira-styled .html previews, no MCP writes). Use --publish to actually file. For docs gaps surfaced by Support audits, Slack discussions, internal observations, or anywhere a Zendesk-PDF-derived /bug flow doesn't fit.
argument-hint: [<title>] [--description-file <path>] [--from-slack <url>] [--related <key>+] [--assignee <email>] [--type bug|task] [--publish]
---

# /tse-jira:doc

Shortcut for the `tse-jira-ticket-creation` skill — **Workflow D (Doc Bug filing)**. Targets the **DOC** project (Documentation, id `10037`). Unlike `/tse-jira:bug`, this command does **not** require a Zendesk PDF — it's designed for documentation issues surfaced by:

- Support audits ("the public deploy doc is missing X")
- Internal Slack discussions (the canonical pattern of DOC-6659: "Issue created in Slack from a [message](URL)")
- Field observations during deployments / customer demos
- Anywhere the finding originated internally, not from a customer ticket

**Defaults to dry-run** — generates local markdown + Jira-styled HTML preview files, never calls MCP write tools. Use `--publish` (or say "publish this preview" after a dry-run) to actually file.

## Usage

```
# Default: dry-run (writes preview files, never writes to Jira)
/tse-jira:doc "FF: Publish helm chart OCI URL in deploy documentation" \
  --description-file ./bug-description.md \
  --from-slack https://redis.slack.com/archives/C09SL3B8VMM/p1779378791013709

# With related Jiras for cross-linking
/tse-jira:doc "FF: Document license key requirement in deploy guide" \
  --description-file ./desc.md \
  --related DOC-6659

# Publish — only after reviewing a dry-run
/tse-jira:doc "FF: ..." --description-file ./desc.md --publish
```

**Input contract** — the title (first positional arg or `--title`) is **required**. Everything else is optional:

| Arg | Purpose |
|---|---|
| `<title>` or `--title <text>` | **Required.** Short imperative summary, conventionally prefixed with the affected product (e.g., `"FF: <action>"`, `"RS: <action>"`, `"RC: <action>"`). |
| `--description-file <path>` | Markdown file with the description body. If omitted, interactive mode asks for the description text inline. |
| `--from-slack <url>` | Slack permalink. Appended to the description as `_Issue created in Slack from a [message](URL)._` (matches DOC-6659 convention). |
| `--related <KEY>` | Related Jira key (e.g., `RED-176559`). Repeatable. Linked via `Relates` (id 10003) on publish. |
| `--assignee <email>` | Override the default. For FF docs the conventional assignee is `kaitlyn.michael@redis.com` — the skill will suggest this when the title contains "FF" or "Feature Form". |
| `--type bug\|task` | Issue type. Defaults to `bug` (id `10074`). Use `task` (id `10023`) for "update docs to clarify X" style work (DOC-6659 was a Task). |
| `--publish` | Actually file the ticket via MCP. Without this, dry-run only. |

### Invoking without arguments — interactive mode

`/tse-jira:doc` with no arguments drops into **interactive mode**: the skill asks for title, description, optional Slack link, optional related Jiras, confirms project + assignee + type, then drafts the preview. Same explicit-confirm gate before any publish.

## Mode: Dry-Run (default) vs Publish

### Dry-run (default)

What it does:
1. Reads description-file (or prompts for description text in interactive mode)
2. Verifies related Jira keys (regex + `getJiraIssue` lookup) if provided
3. Auto-detects suggested assignee from title content (FF → Kaitlyn Michael, etc.)
4. **Writes BOTH a markdown preview AND a Jira-styled HTML preview** to `~/tse-jira-previews/DOC-doc-<ISO timestamp>.{md,html}`
5. **Auto-opens the HTML preview in your default browser** (`open <file.html>` on macOS)
6. Reports the paths. Stops. **No MCP writes happen.**

What it does NOT do (in dry-run):
- Call `createJiraIssue`, `createIssueLink`, `editJiraIssue`. Ever. In dry-run.

To convert a dry-run into a publish:
- Review the HTML preview in your browser
- If everything looks right, say `publish this preview` (referencing the file path is optional)
- The skill loads the preview, asks one final explicit confirmation, fires the writes

### Publish

What it does:
1. Same as dry-run (still produces the preview files as an audit record)
2. **PLUS** asks for one explicit final confirmation before any write tool fires
3. **PLUS** calls the MCP write tools in the right order:
   - `createJiraIssue` against project `DOC` (id `10037`) with issuetype id `10074` (Bug) or `10023` (Task)
   - For each `--related` key: `createIssueLink` with type `Relates` (id `10003`)
4. **PLUS** appends actual API responses to the preview file (key, link statuses)

Even in publish mode, the harness-level safety net should still prompt you — see [`bug.md` § Prerequisites](./bug.md#prerequisites).

## Behavior

Invokes the `tse-jira-ticket-creation` skill, **Workflow D**:

1. Reads / collects:
   - Title (required)
   - Description body (from file or interactive prompt)
   - Slack reference URL (optional)
   - Related Jira keys (optional, verified)
   - Assignee suggestion (auto-detected from product prefix in title)
   - Issue type (bug default; task if title is imperative "Update docs to..." style)

2. Constructs the Jira payload using the **minimal DOC schema** per [`references/jira-schema.md` → DOC section](../skills/tse-jira-ticket-creation/references/jira-schema.md):
   - `project: {id: "10037"}`
   - `issuetype: {id: "10074"}` (Bug) or `{id: "10023"}` (Task)
   - `summary: <title>`
   - `description`: ADF doc with the description body + Slack reference appended (if `--from-slack`)
   - `assignee: {accountId: "<resolved>"}` (if provided or auto-detected)
   - **NOT populated** (DOC project doesn't have them): `Severity`, `Component`, `Environment`, `Product`, `Seen by Customer/s`, `Found By`, `Issue source`, `RCA template`, `Workaround`, `Impact Score`, `Action Items`. The skill **must not** attempt to set RED-style fields on DOC tickets — verify the available fields via `getJiraIssueTypeMetaWithFields` if uncertain.

3. **Writes preview files** at `~/tse-jira-previews/DOC-doc-<timestamp>.{md,html}` — done in dry-run.

4. **On `--publish` or "publish this" follow-up**: asks for explicit final yes, then:
   - Creates the DOC ticket via MCP
   - Links related Jiras via `Relates` (id 10003)
   - Appends actual API responses to the preview file

## Examples

```bash
# Real-world example: file a doc bug surfaced by Support audit
/tse-jira:doc "FF: Publish helm chart OCI URL in deploy documentation" \
  --description-file ~/findings/oci-url-gap.md \
  --from-slack https://redis.slack.com/archives/C09SL3B8VMM/p1779378791013709

# Bulk-file backlog (one at a time — review each preview before publishing)
for f in ~/findings/ff-doc-bugs/*.md; do
  title=$(head -1 "$f" | sed 's/^# //')
  /tse-jira:doc "$title" --description-file "$f"
done
# Then for each preview, after review:
# > publish ~/tse-jira-previews/DOC-doc-<timestamp>.md

# Task-style update request
/tse-jira:doc "FF: Document Redis Cloud Essentials auto-delete behavior in deploy guide" \
  --description-file ./desc.md \
  --type task
```

## When to use /tse-jira:doc vs /tse-jira:bug

| Situation | Use |
|---|---|
| Documentation issue surfaced from internal audit / Slack / observation | `/tse-jira:doc` |
| Customer-reported issue with a Zendesk ticket | `/tse-jira:bug` (even if it ends up routed to DOC) |
| Need impact score, severity, customer info | `/tse-jira:bug` |
| Simple "update docs to clarify X" | `/tse-jira:doc --type task` |
| Documentation bug found via internal testing of a shipped feature | `/tse-jira:doc` |

If a Zendesk PDF exists, `/tse-jira:bug` will auto-route to DOC if the content matches DOC project detection rules — use that path. `/tse-jira:doc` is for the cases where there's no Zendesk origin.

## Prerequisites

Same as [`/tse-jira:bug`](./bug.md#prerequisites):
1. Claude.ai Atlassian MCP authenticated (`/mcp` → Atlassian → Authenticate with Redis Labs account)
2. (Strongly recommended) Harness-level safety net in `~/.claude/settings.json` — see [SECURITY.md](../../../SECURITY.md)

## Safety

- **Dry-run is the default** — no MCP writes happen unless `--publish` flag is set or you say "publish this preview" referring to a generated preview file.
- **Implicit confirmations don't count.** "Yes", "go", "looks good" are NOT publish keywords. You must say something containing "publish".
- **DOC schema is minimal** — the skill explicitly does NOT populate RED-style customfields (Severity, Component, Environment, etc.). If you find yourself wanting those, you probably want `/tse-jira:bug` instead.
- **No PII auto-redaction** — DOC bugs typically don't carry customer PII the way Zendesk-derived bugs do, but if your description contains customer names / emails / phone numbers, review the preview before publishing.

## Related

- **Skill:** [`../skills/tse-jira-ticket-creation/SKILL.md`](../skills/tse-jira-ticket-creation/SKILL.md) — Workflow D
- **Sibling commands:** [`/tse-jira:bug`](./bug.md), [`/tse-jira:rca`](./rca.md), [`/tse-jira:score`](./score.md)
- **Schema reference:** [`../skills/tse-jira-ticket-creation/references/jira-schema.md`](../skills/tse-jira-ticket-creation/references/jira-schema.md) — see "DOC (Documentation) — sparse schema, don't apply RED-style"
- **Canonical examples:** DOC-6659 (Task — "Update docs regarding Docker image accessibility"), DOC-6506 (Bug — Go-redis Smart Client Handoff endpoint type)
