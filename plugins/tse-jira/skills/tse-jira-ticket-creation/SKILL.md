---
name: tse-jira-ticket-creation
description: Create Redis Jira tickets for Technical Support Engineers — Bug Jiras from Zendesk PDFs (+ optional related Jira PDFs), multi-cluster RCA Jiras by cloning RCA-41 (Zendesk + Jira PDFs), and impact score estimation using the 8-130 model. Grounded in Redis Customer Support team standards (Confluence pages 3785981958, 4267671553, 4575690753) and the canonical RCA-41 template. Multi-project (RED/MOD/DOC/RDSC + RCA), sprint-blank, uses the claude.ai Atlassian MCP. Activate when the user mentions creating a Jira from a Zendesk ticket, drafting an RCA, scoring a ticket's impact, or filing against redislabs.atlassian.net.
---

# TSE Jira Ticket Creation

A Redis Technical Support Engineer workflow for creating Jira tickets in `redislabs.atlassian.net` through the claude.ai Atlassian MCP. **All workflows must align with the Support team's documented standards** — when in doubt, the Confluence docs win.

## Authoritative Sources (Re-read on Doubt)

1. [**Jira creation for Support**](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958) — CS team's Bug-filing guide
2. [**Jira - Impact Score**](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553) — 6-component scoring model
3. [**RCA Initiation and Data Collection Procedure**](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4575690753) — RCA creation procedure (clone RCA-41)
4. [**Internal R&D RCA Process**](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4571660292) — overall RCA process and KPIs
5. [**RCA-41**](https://redislabs.atlassian.net/browse/RCA-41) — canonical RCA template ticket

## Three Workflows

| Workflow | Required Input | Optional Input | Result |
|---|---|---|---|
| **Bug Jira** (`/tse-jira:bug`) | ≥1 Zendesk PDF (multiple OK) | Related Jira PDFs (any number — linked via `Relates`) | Bug ticket in RED / MOD / DOC / RDSC with TSE-judged severity, default priority, impact score, mapped fields. Impact-score breakdown posted as a comment. For Azure: post-save RCA-template field populated. |
| **RCA Jira** (`/tse-jira:rca`) | ≥1 Jira PDF (multiple OK) | Zendesk PDFs (any number) | RCA ticket created by cloning RCA-41 defaults: title `<Customer> - RCA <mm/dd/yyyy>`, Initial Root Cause from Jira PDF content, action items pre-filled with placeholders, all related bugs linked via `Relates`. Status starts at `Data Collection`. |
| **Impact Score** (`/tse-jira:score`) | ≥1 Jira (PDF or live key) (multiple OK) | Zendesk PDFs (any number, supplement context) | 8-130 score + 6-component breakdown with reasoning. **No ticket creation.** Score is a recommendation; team leader confirms before applying. |

This skill is the spiritual successor to `~/Downloads/marko-projects/jira-helper` — same impact scoring model and conceptual field mapping, but actually creates tickets via MCP instead of generating markdown.

## Cloud ID

For all `mcp__claude_ai_Atlassian__*` calls against Redis Labs Jira:

```
cloudId: 06f73ca7-8f2c-4392-b40a-08288e9d0ba3
```

(Confirm with `getAccessibleAtlassianResources` if a call fails.)

## Reference Files

Read the matching reference file as the workflow demands — don't load all upfront:

- [`references/jira-schema.md`](references/jira-schema.md) — **Source of truth for real field IDs, projects, issue types, link types.** Verified against the live tenant. Read for any field-level decisions.
- [`references/impact-score-model.md`](references/impact-score-model.md) — Full 6-component scoring model (P1-P5 definitions, ARR tiers, SLA thresholds, multiplier rules) per [DevOps page 4267671553](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553). Read for any score-related work.
- [`references/zendesk-bug-mapping.md`](references/zendesk-bug-mapping.md) — Bug filing field-by-field rules per [CS page 3785981958](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958). Read for the Bug workflow.
- [`references/rca-template.md`](references/rca-template.md) — RCA filing per [DevOps page 4575690753](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4575690753) and RCA-41. Read for the RCA workflow.
- [`references/canonical-jiras/`](references/canonical-jiras/) — **⭐ STRUCTURED EXTRACTS OF REAL JIRAS.** Before drafting any new ticket description, scan this directory for the closest matching example (by issue type + domain) and **mirror its H2 section structure**. The Confluence docs describe field rules; canonical-jiras describe description style. Both are needed. See the directory's `README.md` for the current index.

## When to Activate

- User says "create a Jira for this Zendesk ticket / PDF"
- User mentions filing an RCA / drafting a root cause / multi-cluster incident
- User asks for an impact score / priority assessment for a Jira ticket
- User wants to file a bug against RED, MOD, DOC, or RDSC
- User attaches or references a Zendesk PDF or Jira PDF/key
- User invokes `/tse-jira:new` (router — asks which type) or any of the three workflow commands without args

**Never auto-create.** Always preview the fields and ask for confirmation before any `createJiraIssue` / `createIssueLink` / `editJiraIssue` call.

---

## ✨ Interactive Mode

The plugin runs in **interactive mode** whenever the user invokes it without sufficient information. Three trigger conditions:

1. **Top-level router** — `/tse-jira:new` is the entry point for "I want to file a Jira but I don't remember which command." Use `AskUserQuestion` with three options (`Bug Jira` / `RCA Jira` / `Impact Score`), then chain into the matching interactive flow.
2. **Command with no args** — `/tse-jira:bug`, `/tse-jira:rca`, `/tse-jira:score` invoked without arguments → fall back to the flow's interactive script below.
3. **Command with partial / ambiguous args** — glob matched 0 files, project auto-detection has multiple candidates, Jira key looks malformed, etc. Pause and ask instead of guessing.

### Per-flow interactive scripts

**bug flow:**
1. Ask: *"Path or glob to the Zendesk PDF(s)? You can give one path, a glob like `~/Downloads/packages/162249/*.pdf`, or comma-separated paths."* — validate with `ls`/glob; if 0 matches, re-prompt.
2. Optionally scan the same directory for sibling screenshots (PNG/JPG/GIF/WEBP) and confirm: *"Found N image files alongside the PDF — should I embed these in the description? [yes / no / list which ones]"*.
3. Ask: *"Any related Jiras? Give me keys (e.g., `RED-176559 RED-184754`) or PDF paths, or say `none`."* — for each key, regex-check `^[A-Z]+-\d+$` and verify via `getJiraIssue`. Re-prompt on validation failure.
4. After project auto-detection: if confidence is medium/low, confirm: *"I'm detecting project = RED based on `<signal>`. Override?"*.
5. Ask for **Severity** (required TSE judgment): `AskUserQuestion` with `0 - Very High / 1 - High / 2 - Medium / 3 - Low` — default highlight `2 - Medium`.
6. Ask: *"Should I run a codebase investigation against the customer's reported version to ground the Suggested Fix in real file:line refs? Looks like you have `<repo>` locally — I'll `git fetch --tags` first."* See [[feedback-check-local-codebase]].
7. Draft the preview. Show paths. Stop.

**rca flow:**
1. Ask: *"Path(s) to the Zendesk PDF(s)? Comma-separated or glob. **At least one required.**"* — validate; re-prompt if 0.
2. Ask: *"Related Jira(s)? Keys or PDF paths, comma-separated. **At least one required.**"* — validate each.
3. Batched RCA prerequisites via `AskUserQuestion` (where structured) and plain Q&A (where free-text):
   - Customer name (or `ClusterID` for cluster-incident shape) — free-text
   - Incident date (`mm/dd/yyyy`) — free-text, parse-check
   - Cluster names (list) — free-text
   - Start time / End time (UTC) — free-text, parse-check
   - Product: `Redis Cloud / Redis Software / AMR` — AskUserQuestion
   - Affected components — multi-select if multiple plausible
   - Contributors — free-text
4. Detect cluster-incident shape (automation-initiated, no customer ZD). If detected, skip step 1's "Zendesk required" — see [[feedback-rca-zendesk-required]].
5. Draft preview, show paths, stop.

**score flow:**
1. Ask: *"Jira key(s) or PDF path(s) you want scored? Comma-separated."* — validate each.
2. Ask: *"Any Zendesk PDFs that add customer/frequency context? Optional."*
3. Compute. Show breakdown. Stop. No publish step unless user says *"apply this score to RED-NNN"*.

### Validation policy: validate as we go

- **File paths**: check existence with `ls` or `test -f` before accepting. If glob returns 0 files, re-prompt.
- **Jira keys**: regex `^[A-Z]+-\d+$` first, then verify live via `getJiraIssue` (read-only — no MCP write).
- **Dates**: parse to `mm/dd/yyyy` and check sanity (year ≥ 2025, etc.).
- **Customer names**: light check — non-empty. Resolve against `customfield_10595` (Affected Organizations) when filing.
- **Re-prompt on failure** rather than coasting forward.

### Avoid asking what you can infer

- If the user has already typed paths/keys in the same message that invoked the command, don't re-ask — use what they gave.
- If project auto-detection from PDF content is high-confidence, don't ask "which project?" — state the detection and let the user override.
- If only one customer is named in the PDF, don't ask "who's the customer?" — state it and let the user correct.

### Confirm-as-you-go

After each major question, echo back what was captured: *"OK — bug from `ticket_162249.pdf` (Aetna), related Jiras RED-176559 + RED-184754, severity 2-Medium. Proceeding to project detection..."*. Reduces error and gives the user opportunity to course-correct early.

---

## ⚠️ Mode: Dry-Run (Default) vs Publish

**Default mode is DRY-RUN.** The Bug and RCA workflows write a local markdown preview file and stop there — they NEVER call MCP write tools unless the user has explicitly requested publish mode.

### When publish mode is active

The skill enters publish mode **only** when one of these is true:

1. User invoked `/tse-jira:bug ... --publish` or `/tse-jira:rca ... --publish`
2. User has run a dry-run, reviewed the preview file, and said something like "publish it now", "go ahead and create", "publish to Jira" — referencing the preview file the skill produced
3. User is running the Impact Score workflow with the explicit "apply this score to ticket X" follow-up (since score-only is read-only by default)

**Implicit phrases like "yes", "go", "looks good" after a preview are AMBIGUOUS — clarify before publishing.** Per the user's documented preference (memory: `feedback_destructive_operations.md`), pause for an explicit `publish` keyword before any MCP write call. A top-level "go" earlier in the conversation does NOT cover later destructive steps — re-confirm each one.

### Two-layer protection

1. **Skill-level (this document):** dry-run by default, explicit publish keyword required
2. **Harness-level (`~/.claude/settings.json`):** the user should have `mcp__claude_ai_Atlassian__createJiraIssue` (and 9 other write tools) listed under `permissions.ask`. Even if this skill is misread, Claude Code will prompt the user before any write call fires. See [SECURITY.md](../../../../SECURITY.md) for the install snippet.

### Dry-run output: dual preview files (.md + .html) — v0.9+

**Dry-run produces TWO files** alongside each other in `~/tse-jira-previews/`:

| File | Purpose |
|---|---|
| `<project>-<workflow>-<timestamp>.md` | Markdown — for editing, diffing, version control, terminal review |
| `<project>-<workflow>-<timestamp>.html` | **Jira-mimicking HTML preview** — opens in browser for visual review |

Example pair:
- `~/tse-jira-previews/RED-bug-20260511T153000Z.md`
- `~/tse-jira-previews/RED-bug-20260511T153000Z.html`

If `~/tse-jira-previews/` doesn't exist, create it (`mkdir -p`). User can override the directory by saying "preview to `<path>`".

### Auto-open the HTML preview in the browser

After writing both files, the skill should run:

```bash
open ~/tse-jira-previews/<...>.html
```

This launches the user's default browser to the rendered preview. Also print both file paths as clickable `file://` URLs in the terminal output:

```
✅ Preview written:
   md  →  file:///Users/marko.trapani/tse-jira-previews/RED-bug-<ts>.md
   html → file:///Users/marko.trapani/tse-jira-previews/RED-bug-<ts>.html  (auto-opened in browser)
```

If `open` fails (non-macOS or no default browser), just print the paths and let the user click them.

### HTML template

The skill renders the HTML using the structure in [`references/preview-template.html`](references/preview-template.html). That file is a complete self-contained Jira-mimicking template with:

- A `## DRY-RUN PREVIEW` banner at the top with timestamp and skill version
- A ticket-header section with the ticket-key placeholder (`RED-XXXXX [PREVIEW]`), summary, type, status, project, and canonical-jiras anchor
- A two-column layout:
  - **Main column**: Description body (full H2-sectioned content rendered as HTML), Comment to be posted, Issue Links to create, Pre-flight Checks panel, Publish CTA, Raw API Payloads in a `<details>` collapsible
  - **Sidebar**: field rows grouped by section (Details / Component & Environment / Customer / Impact & Classification / Workaround / RCA Template Section 0 / Labels)
- Embedded CSS (no external deps), dark-mode aware via `prefers-color-scheme`
- Footer with source markdown path

**The skill builds the .html by template-substituting the field values from its in-memory field map into the placeholder tokens in `preview-template.html`** (`{SUMMARY}`, `{DESCRIPTION_HTML}`, `{PRIORITY}`, etc.). Markdown body content (description, comment, workaround) must be converted to HTML inline (handle ## headings → `<h2>`, fenced code blocks → `<pre><code>`, tables → `<table>`, bulleted lists → `<ul><li>`, numbered lists → `<ol><li>`, inline code → `<code>`).

### Preview file structure (.md)

The .md file mimics what the Jira issue would look like, plus an appendix with the raw API payloads:

```markdown
# RED Bug Preview — <ISO timestamp>


### Preview file structure

The preview mimics what the Jira issue would look like, plus an appendix with the raw API payloads:

```markdown
# RED Bug Preview — <ISO timestamp>

> Generated by tse-jira-ticket-creation skill (dry-run). No MCP writes have occurred.
> Source: <input PDFs / Jira keys>

## Header

| Field          | Value                                       |
|----------------|---------------------------------------------|
| Project        | RED (Redislabs, id 10020)                   |
| Issue Type     | Bug (id 10004)                              |
| Summary        | <one-line title>                            |
| Priority       | Medium (default; PM bumps later)            |
| Severity       | 2 - Medium (id 10329)                       |
| Status         | To Do (default)                             |
| Assignee       | Automatic                                   |

## Description (rendered preview)

<the markdown description, exactly as it will render in Jira>

## Custom Fields

| Field                  | fieldId             | Value                              |
|------------------------|---------------------|------------------------------------|
| Zendesk ID/s           | customfield_10036   | "162249"                           |
| Seen by Customer/s     | customfield_10027   | "Aetna"                            |
| Affected Organizations | customfield_10595   | [{id:23311} = "Aetna"]             |
| Component              | customfield_10181   | {id:10552} = "Cloud API"           |
| Environment/s          | customfield_10025   | [{id:10007} = "Production"]        |
| Product/s              | customfield_10026   | [{id:10010} = "RCP(RV/Pro/Flex)"]  |
| Reported Version/Build | customfield_10056   | "Terraform 1.9.8, redis-cloud..."  |
| Workaround             | customfield_10374   | [ADF doc] "Manual config via..."   |
| Data loss / Unavail/Downtime | _10371/_10372/_10369 | No / No / No                |
| Event Status           | customfield_10373   | (blank)                            |
| Major Prod Channel     | customfield_10370   | (blank)                            |
| Metrics                | customfield_10375   | (blank)                            |
| Impact Score           | customfield_10585   | 58.3                               |
| Impact Score details   | customfield_10681   | [ADF doc] "Base 53..."             |

## Labels

`CS`, `terraform`, `terraform-provider`, `active-active`, `remote-backup`, `e2e_ta_coverage`

## Comment to be posted (after create)

> ## Impact Score Breakdown
> Final Score: 58.3 (MEDIUM)
> ...full rendered comment...

## Issue Links to create (after create)

- new-bug `Relates` → RED-176559
- new-bug `Relates` → RED-184754

## Azure post-save step

❌ Not applicable (this is a GCP ticket, not Azure ACRE/AMR)

---

## Pre-flight Checks Result

- [x] Project RED resolved to id 10020
- [x] Bug issue type resolved to id 10004
- [x] Component "Cloud API" resolved to id 10552
- [x] Severity "2 - Medium" resolved to id 10329
- [x] Affected Organizations "Aetna" resolved to id 23311 (via paginated search)
- [x] Related Jira RED-176559 verified (Status: To Do, type: Bug)
- [x] Related Jira RED-184754 verified (Status: To Do, type: Bug)
- [x] No PII detected in description
- [x] Seen by Customer/s populated (validation rule satisfied for Environment=Production)

---

## Raw API Payloads (Appendix)

### createJiraIssue
\`\`\`jsonc
{
  "cloudId": "06f73ca7-...",
  "projectKey": "RED",
  "issueTypeName": "Bug",
  ...
}
\`\`\`

### addCommentToJiraIssue (post-create)
\`\`\`jsonc
{...}
\`\`\`

### createIssueLink × 2 (post-create)
\`\`\`jsonc
[{...}, {...}]
\`\`\`

---

## To Publish This

After reviewing the preview, say one of:
- "publish this" (the skill loads the payloads from this preview and fires)
- "publish this with these changes: <list>" (the skill regenerates the preview with edits, then waits for another publish confirmation)
- "cancel" or "scrap this" (the skill discards the preview)

The skill will not call any `mcp__claude_ai_Atlassian__create*` / `edit*` / `transition*` tool until it sees the word **publish** referencing this preview.
```

### Dry-run vs publish at a glance

| Step                          | Dry-run (default) | Publish (--publish or "publish this") |
|-------------------------------|-------------------|---------------------------------------|
| Read inputs (PDFs, Jira keys) | ✅ Yes            | ✅ Yes                                |
| Compute impact score          | ✅ Yes            | ✅ Yes                                |
| Auto-detect project / fields  | ✅ Yes            | ✅ Yes                                |
| Resolve Affected Orgs lookup  | ✅ Yes            | ✅ Yes                                |
| Verify related Jiras exist    | ✅ Yes            | ✅ Yes                                |
| Generate preview file         | ✅ Yes            | ✅ Yes (also writes the preview for audit) |
| Call `createJiraIssue`        | ❌ NEVER          | ✅ After explicit user yes            |
| Post comment                  | ❌ NEVER          | ✅ After createJiraIssue succeeds     |
| Create issue links            | ❌ NEVER          | ✅ After createJiraIssue succeeds     |
| Azure post-save edit          | ❌ NEVER          | ✅ After createJiraIssue succeeds     |

### Score workflow is special

`/tse-jira:score` is **inherently read-only** — it just computes the impact score. It doesn't have a "publish" mode in the same sense. The follow-up "apply this score to RED-NNN" is a separate small workflow that does count as publish (it sets `customfield_10585` and posts a breakdown comment) — that follow-up uses the same explicit-confirmation rules.

---

## Workflow A — Bug Jira from Zendesk

### Input Contract

- **Required:** ≥1 Zendesk PDF (path or text in conversation). Multiple Zendesk PDFs OK — they may all link to the same Bug if the issue is shared across customer tickets.
- **Optional:** Any number of related Jira PDFs (to be linked via `Relates` after creation).

### Steps

1. **Read all Zendesk PDFs** with the Read tool. PDFs are first-class — Read returns text and reads up to 20 pages.

   ⭐ **NEW in v0.10**: **ALSO scan the same directory for sibling image files** (PNG / JPG / JPEG / GIF / WEBP) and other supplementary artifacts (TXT logs, ZIP). Customers commonly attach screenshots to Zendesk that should carry over to the Jira. Use `ls <PDF-directory>` to enumerate. For each image, Read it to understand what it shows, then plan the embed spot in the description body per [`references/zendesk-bug-mapping.md` → "Screenshots & Other Customer-Provided Files"](references/zendesk-bug-mapping.md).
2. **Extract per PDF**:
   - Zendesk ticket ID (filename pattern: `redislabs.zendesk.com_tickets_<ID>_print.pdf`)
   - Customer name / organization
   - Summary (one-line subject)
   - Description / problem statement
   - Comments thread (first few relevant exchanges)
   - Frequency indicators ("multiple times", "intermittent")
   - Cluster name, region, product version
   - Cloud (Azure / AWS / GCP), product (Redis Software / Cloud / RDI)
   - ⭐ **Auto-infer related Jiras** (v0.13+) — scan the PDF text for Jira-key patterns (`\b[A-Z]+-\d+\b`) and Atlassian browse URLs (`redislabs\.atlassian\.net/browse/<KEY>`). De-duplicate by key. Verify each detected key via `getJiraIssue` (read-only).
   - ⭐ **NEW in v0.14**: **Also run Glean Search for semantically-related Jiras** — Glean often surfaces relevant tickets the customer didn't explicitly cite in the thread (e.g., tickets from other customers with the same symptom, internal OPCR/IR tickets discussing the underlying issue). Procedure:
     1. Construct a SHORT query: `<customer-name> <key-technical-signal>` — e.g., `Aetna terraform`, `monday.com dmc CPU`, `Walmart CRDB replication`. Single high-signal noun pair. Don't query-stuff per Glean MCP guidelines.
     2. Call `mcp__claude_ai_Glean__search` with `query` + `app: "jira"` + `num_results: 10`.
     3. ⚠️ **Glean responses are verbose (often >25KB)** and may overflow the agent token budget. The MCP automatically saves overflow responses to a file and returns the path. **Use `grep` on that file** rather than reading the full response:
        ```bash
        grep -oE 'browse/[A-Z]+-[0-9]+' /path/to/saved/glean-response.txt | sort -u
        ```
        This extracts every Jira key Glean surfaced, one per line, deduplicated.
     4. **Filter results**: keep only keys whose project is plausible for this bug (RED / MOD / DOC / RDSC / FR / OPCR for cross-team-related). Drop keys that are obviously the wrong project (e.g., HR-, MKTG- tickets).
     5. **De-duplicate against PDF-text inference** (Step 2's first bullet). Keys appearing in both PDF and Glean are STRONG candidates.
     6. **Present in the interactive prompt** as a layered question:
        > "Two sources of candidate Related Jiras:
        > - From the Zendesk PDF text: `RED-176559`, `RED-184754` (these two were explicitly cited)
        > - Additional candidates from Glean Search (`<customer> <signal>`): `RED-147548`, `RED-190334`, `RED-195595` (related but not cited in the thread)
        >
        > Use which? [PDF-only / PDF + select Glean / all / custom list / none]"
     7. **Verify each candidate** with `getJiraIssue` (read-only) before adding to the createIssueLink calls. Drop any that return 404 or are obviously closed/duplicated to something else.
     8. **If the Glean MCP is not available** (e.g., user's session doesn't have it connected): skip Glean and proceed with PDF-text inference only. Log "Glean unavailable — using PDF-text inference only" in the preview's pre-flight checks.
     The TSE shouldn't have to remember which Jiras were cited OR which other Jiras might be related — the skill does both inferences automatically and asks for selection.
3. **Compute impact score** — apply [`references/impact-score-model.md`](references/impact-score-model.md). Show 6-component breakdown with reasoning. **Flag that the score is a recommendation pending team leader confirmation.**
4. **Auto-detect project** — apply rules in [`references/zendesk-bug-mapping.md`](references/zendesk-bug-mapping.md) (RDSC → MOD → DOC → RED). State the detected project; let the user override.

   ⭐ **NEW in v0.8**: After project detection, **read the matching "Project-Shape Schema" section in [`references/jira-schema.md`](references/jira-schema.md)** before doing any field mapping. Each project has a different field schema:
   - **DOC**: sparse — no Severity/Component/Environment/Product/Found By/RCA template. Don't apply RED-style fields.
   - **RDSC**: dedicated `Steps to Reproduce` / `Expected Result` / `Actual Result` custom fields (NOT description H2 sections). Has special `RDI Customer Issue` type. Different label set.
   - **MOD**: Components is multi-select. `Found by` includes `Community` for AMR-routed bugs. Has `BugScore` field.
   - **RCA**: two distinct shapes — customer-RCA (TSE-initiated) vs cluster-incident-RCA (automation-initiated). Detect which shape applies.
   - **RED**: full TSE schema (default assumption).

   Pick the matching canonical-jiras example for that project + shape and use it as the description structure anchor.
5. **Map fields** per [`references/zendesk-bug-mapping.md`](references/zendesk-bug-mapping.md):
   - Issue type: `Bug` (id from [`references/jira-schema.md`](references/jira-schema.md))
   - **Severity** (`customfield_10180`): **TSE-judged Jira severity** based on customer impact (`0 - Very High` / `1 - High` / `2 - Medium` / `3 - Low`). See [`references/zendesk-bug-mapping.md`](references/zendesk-bug-mapping.md) for the exact criteria per level.
     - ⚠️ **DO NOT copy the Zendesk Severity field value.** Zendesk's Severity uses different categories (typically `Normal` / `High` / `Urgent`) that do **not** map 1:1 to Jira's `0/1/2/3` scale. Treat the Zendesk Severity as advisory at best — always ask the TSE for the Jira severity based on customer-impact assessment.
     - **DO NOT derive severity from the impact score.** Impact score is for prioritization across tickets; Jira Severity is for describing customer impact of this ticket. Independent fields.
     - Default `2 - Medium` (id `10329`), but always confirm with the TSE before creation.
   - **Priority** (system): `Medium` (default, id 3). PM sets later.
   - Status: leave default (To Do).
   - Assignee: leave default (Automatic).
   - Sprint: leave blank.
   - Component (`customfield_10181`): single-select, detect from content (DMC / Cluster / Azure integration / Cloud API / Security / etc.). Show pick and let user override.
   - Environment (`customfield_10025`): **`Production`** (id 10007) — always for customer-originated tickets.
   - Product (`customfield_10026`): multi-select — pick `RS (Redis Software)` for ACRE/Software, `RCP(RV/Pro/Flexible)` for Cloud.
   - Reported Version/Build (`customfield_10056`): always add; comma-separated for multiple.
   - **Seen by Customer/s (`customfield_10027`): ALWAYS REQUIRED when Environment=Production** — set to the customer name as a plain string. The Support docs call this "deprecated" but a project validation rule still requires it. Set this in *addition to* Affected Organizations, never instead of.
   - Affected Organizations (`customfield_10595`): customer name dropdown with **9,253+ options**. Resolution procedure:
     1. **Try exact match first.** Call `getJiraIssueTypeMetaWithFields` with `projectIdOrKey=RED`, `issueTypeId=10004`, and `maxResults=50`, `startAt=0`. Search the returned `customfield_10595.allowedValues` list for a case-insensitive substring match on the customer name.
     2. **If not in first page**, page through using `startAt` increments. **Cap at 5 pages (250 options total)** to avoid burning tokens — exact customer names usually surface in early pages alphabetically.
     3. **If found**: set `customfield_10595` to `[{"id":"<resolved_id>"}]`.
     4. **If NOT found**: skip `customfield_10595` entirely. Set the free-text fallback `customfield_10027` (Seen by Customer/s) to the customer name. Add the customer name as a label too. **Then in the post-create output, explicitly tell the TSE: "Affected Organizations was not auto-resolved — please pick `<customer>` from the dropdown in the browser before saving."**
     5. **Never invent an ID.** If the search doesn't find an exact substring match, do not guess.
   - Zendesk ID/s (`customfield_10036`): numbers only, comma-separated.
   - **Found By (`customfield_10115`)**: single-select. TSE default `Prod/Customer` (id 10149). ⭐ NEW in v0.7
   - **Issue source (`customfield_10177`)**: single-select. TSE default `Product Bug` (id 10322). ⭐ NEW in v0.7
   - **RCA template (`customfield_10063`)**: ⭐ **CORRECTED in v0.13** — **TSE leaves blank.** R&D fills this during triage; it is not the TSE's territory at file-time. Narrow exception: Azure ACRE/AMR tickets where Microsoft's customer-facing automation reads section 0 — populate section 0 only, sections 1-5 stay blank. See [`references/jira-schema.md` → RCA Template Block](references/jira-schema.md).
   - **Workaround (`customfield_10374`)**: ⭐ **DEDICATED FIELD, NOT BODY H2** (v0.13). If a workaround exists, populate as ADF doc with multi-paragraph + code-block content. If none, populate with `"None known. <one-line reason>"` (ADF). Do NOT duplicate as a body H2 section — the Jira UI renders this field as its own section below the description.
   - **Data loss / Data unavailable / Downtime** (`customfield_10371` / `_10372` / `_10369`): Yes/No each — ask TSE.
   - **Event Status (`customfield_10373`)**: set to `workaround implemented` if WA in place. If no workaround, leave blank.
   - **Major Prod Channel (`customfield_10370`)**: Slack link if Major prod event.
   - **Metrics (`customfield_10375`)**: Grafana link if available.
   - **Impact Score (`customfield_10585`)**: ⭐ **INTEGER ONLY** (v0.12). Round and lean lower per "if in doubt, lean towards the lower score". E.g., raw 59.4 → integer 59.
   - **Impact Score details (`customfield_10681`)**: ⭐ **DEDICATED FIELD, NOT BODY H2** (v0.13). Populate as ADF doc with the 6-component breakdown table + sheet link. The TSE pastes a Google Sheet row screenshot into this field post-create. Do NOT add a `## Impact Score` H2 to the description body — this corrects earlier guidance. See [`references/impact-score-model.md` → "Posting on the Ticket"](references/impact-score-model.md).
   - **Action Items (`customfield_10672`)**: ⭐ **NEW destination in v0.13** — if the TSE has hypotheses or questions for R&D (formerly "Asks for R&D" in the body), put them here as ADF doc. Frame as questions ("Please verify X", "Could you check Y", "Test gap: Z"). Do NOT add an `## Asks for R&D` H2 to the description body.
   - **ICM ID/s (`customfield_14258`)**: for AMR — Azure IcM incident IDs.
   - **Labels**: 2-3 max. Required: one of `CS` or `Support`. Add 1-2 domain tags. For Azure: `Azure-Integration` + (`AMR` or `ACRE`); add `Azure_RCA_req` if an RCA is needed. ⭐ Tightened in v0.7 — see [`references/zendesk-bug-mapping.md` → Labels section](references/zendesk-bug-mapping.md).
6. **Construct Description** — **Anchor to a canonical Jira first; body holds narrative only (v0.13).**
   - Scan [`references/canonical-jiras/`](references/canonical-jiras/) for the closest match by issue type + domain (encryption, modules, Azure, A-A, support tooling, cm_server, auth, etc.).
   - **Mirror the H2 section structure** from the chosen canonical example, but the body now holds NARRATIVE ONLY:
     - Summary, Possible Root Cause *(optional, with one-line italicized AI-ack)*, Customer Impact *(optional)*, Steps to Reproduce, Expected, Actual, Evidence from Support Case, Related Code Paths *(optional)*, Pending Information *(optional)*, Zendesk Reference.
     - Separate major H2 sections with `---` horizontal rules.
   - ⭐ **CORRECTED in v0.13**: Do NOT add `## Workaround`, `## Impact Score`, or `## Asks for R&D` H2 sections in the body. That content goes in the dedicated **fields** (`customfield_10374`, `customfield_10681`, `customfield_10672`) — see Step 5. The Jira UI renders these fields as section-like blocks below the description.
   - ⭐ **`## Customer Impact` is optional** (v0.13). Include only when the customer-visible behavior is concrete and non-obvious from the rest of the body. Skip when impact is implied through Customer ARR / Affected Organizations / Workaround field / the symptom narrative in Summary.
   - **Do NOT** add a flat "**Label:** value" prefix block at the top. Customer / cluster / subscription / BDB / product data lives ONLY in fields.
   - For Active-Active incidents: include the A-A mapping table inside `## Evidence from Support Case`.
   - Log references in `cluster_name, node_id, shard_id` format inside `## Evidence from Support Case`.
   - **Zendesk-is-not-Jira relevance filter** ⭐ NEW in v0.13: every candidate Evidence subsection / piece of context has to pass the test "Does this directly support understanding or fixing the bug?" If R&D would skim past it, drop it. Padding from Zendesk trivia (internal-team observations, name discrepancies that don't bear on the bug mechanism, routing chatter) distracts from triage signal.
   - **Embed customer-provided screenshots using image-paste markers** ⭐ REFINED in v0.13. For each PNG / JPG found in the source directory, insert an explicit paste-here marker at the paragraph that best matches the image's content:

     ```markdown
     📸 _Paste `<filename>.png` here._
     ```

     The TSE filing the Jira will drag-and-drop the image into the browser post-create at exactly that spot — abstract "see attached X.png" prose in unrelated paragraphs doesn't tell them WHERE to drop the image. Markers should sit at the exact paragraph the image renders best, name the file basename, and become self-deleting (or repurposed as caption) once pasted.
   - **AI-acknowledgment** ⭐ REFINED in v0.13: if "Possible Root Cause" includes AI-assisted code review, open the section with a single italicized one-liner — e.g., `*Support-side hypothesis (AI-assisted code review of <repo> @ <tag>) — please verify before acting.*` Do NOT include a verbose "Analysis Note" callout in the publish-bound body; that lives in preview-only metadata. The heading framing ("Possible Root Cause — please verify") + the one-liner are enough.
   - **If no canonical example fits**: pick the closest one and flag low confidence in the preview's pre-flight checks: `"Anchor: RED-XXXXX (closest match for {issue shape}) — review carefully"`. Suggest the user save the resulting Jira as a new canonical example after filing.
   - See [`references/zendesk-bug-mapping.md` → Description Body Template](references/zendesk-bug-mapping.md) for the full template, field-destination map, and anti-patterns.
7. **Preview** — Ask the user for severity confirmation if not provided. Resolve Affected Organizations via paginated search. Build the full payload structures (createJiraIssue, addCommentToJiraIssue, createIssueLink calls).
8. **Dry-run by default** — Write **BOTH** preview files (v0.9+):
   1. `~/tse-jira-previews/RED-bug-<timestamp>.md` — markdown per the "Mode" section above. Write directly with the `Write` tool.
   2. ⭐ **CRITICAL CHANGE in v0.14**: `~/tse-jira-previews/RED-bug-<timestamp>.html` — **DO NOT write the HTML preview from scratch with the `Write` tool.** The template is ~530 lines of CSS + layout boilerplate that's identical across filings; re-writing it from scratch is slow (~30+ seconds of agent tokens per filing) and prone to drift.
      - **Instead, use the helper script** [`plugins/tse-jira/scripts/render-html-preview.py`](../../../scripts/render-html-preview.py):
        1. Write the field values to a temporary fields.json (use `Write` tool; format documented in [`plugins/tse-jira/scripts/fields.schema.md`](../../../scripts/fields.schema.md)).
        2. Convert the description body's markdown to HTML inline (handle `## H2 → <h2>`, fenced code → `<pre><code>`, tables → `<table>`, lists → `<ul>/<ol>`, links, inline code) — this becomes the `DESCRIPTION_HTML` scalar value.
        3. Construct the JSON payload strings (CREATE_PAYLOAD_JSON, LINK_PAYLOADS_JSON, etc.) as the values you'd pass to MCP at publish time.
        4. Invoke the script via `Bash` tool:
           ```bash
           python3 <plugin-cache-dir>/scripts/render-html-preview.py \
             --template <plugin-cache-dir>/skills/tse-jira-ticket-creation/references/preview-template.html \
             --input /tmp/<ts>.fields.json \
             --output ~/tse-jira-previews/RED-bug-<ts>.html
           ```
        5. The script substitutes all 45 placeholders + 4 loop expansions in one pass. Output is byte-identical across runs given the same input. No agent-token cost beyond writing the JSON inputs.
        6. (Optional) delete the fields.json after success.
   3. Run `open ~/tse-jira-previews/RED-bug-<timestamp>.html` to launch the user's default browser (skip silently if `open` is unavailable / non-macOS).
   4. Report **both** file paths as clickable `file://` URLs in the terminal output. **DO NOT call any MCP write tool yet.**
9. **Wait for explicit publish keyword.** Acceptable: `--publish` flag in the original invocation, or a follow-up message containing the word "publish" referring to this preview. Implicit confirmations ("yes", "go", "looks good") are **NOT sufficient** — clarify.
10. **On publish (and only on publish):**
    1. **Create** via `mcp__claude_ai_Atlassian__createJiraIssue` with `cloudId` + the mapped fields. Capture the new key.
    2. **Link related Jiras** (if any related Jira PDFs/keys were provided): call `mcp__claude_ai_Atlassian__createIssueLink` with type `Relates` (id 10003) for each.
    3. ⭐ **NO post-create comment for Impact Score breakdown** (v0.13). The breakdown goes in `customfield_10681` (Impact Score details) at create time — the dedicated field replaces the old "add a comment with breakdown" step. `addCommentToJiraIssue` is not called as part of the publish flow.
    4. **Azure-only:** if this is an Azure ACRE/AMR ticket, the `customfield_10063` (RCA) section 0 was populated at create time per Step 5. For non-Azure tickets, the RCA template field is left blank — R&D fills during triage.
    5. **Append to the preview file** an "Actual API responses" section showing the new key + link statuses — so the preview becomes the post-create audit record.
11. **Output**: new Jira key + browse URL (`https://redislabs.atlassian.net/browse/<KEY>`) + path to the (now post-create) preview file + checklist of what still needs human input. Always include:
    - Attachments: "Attach the Zendesk PDF and any logs in the browser — MCP `createJiraIssue` doesn't accept attachments."
    - **If `customfield_10595` (Affected Organizations) was skipped** because no autocomplete match was found: "Open the ticket in the browser and select `<customer>` from the Affected Organizations dropdown."
    - Reporter / Assignee: verify the auto-assignment looks correct.
    - For Active-Active tickets: confirm the A-A mapping table in the description is accurate.

---

## Workflow B — RCA Jira (Multi-cluster)

### Input Contract

- **Required:** ≥1 Zendesk PDF (customer-facing context for impact statement and timeline).
- **Required:** ≥1 Jira PDF (or live Jira key). Multiple Jiras OK — these are the related bug Jiras that feed the root cause analysis.
- **Exception:** Cluster-incident-shape RCAs (automation-initiated, e.g. RCA-563) may not have a customer Zendesk. The skill should detect this case via cluster ID / automation reporter signals and skip the Zendesk requirement, instead asking for cluster context. Default for customer-facing RCAs: Zendesk required. See [memory: feedback-rca-zendesk-required].
- **Required from user (ask once, batched):**
  - Customer name (e.g., "Azure", "monday.com") — or `ClusterID` / `Major Service` for multi-customer / cluster-incident
  - Incident date (`mm/dd/yyyy`)
  - Cluster names (list — TSE incidents often span multiple clusters)
  - Start time and End time (UTC)
  - Product: Redis Cloud / Redis Software / AMR
  - Affected components (multi-select from the 44-option list)
  - Contributors (incident participants — emails / account IDs)

### Steps

1. **Read all Jira and Zendesk PDFs** in parallel with the Read tool. For live Jira keys provided as input (not PDFs), fetch via `mcp__claude_ai_Atlassian__getJiraIssue` (cloudId, key, `responseContentFormat: "markdown"`).
2. **Azure prerequisite check**: If the user is creating an Azure RCA (label or content indicates Azure / ACRE / AMR), verify at least one related Jira is in RED or MOD project. If not, flag and refuse to proceed — per Support docs, Azure RCAs always need a RED/MOD ticket associated.
3. **Extract from Zendesk PDFs**:
   - Ticket IDs, customer-reported start times, impact descriptions
   - Support-package S3 paths (`s3://gt-logs/...`)
4. **Extract from Jira PDFs / live issues**:
   - Bug keys (filenames: `[#RED-NNNNNN]...pdf`)
   - Summaries, "Initial Root Cause" candidates, action items drafts, log patterns
5. **Build timeline** — chronologically sorted events tied to specific cluster names per [`references/rca-template.md`](references/rca-template.md). Format:
   ```
   | Date and Time (UTC)  | Activity                                              |
   |----------------------|-------------------------------------------------------|
   | MMM-DD-YYYY, HH:MM   | <event tied to cluster>                              |
   ```
6. **Compose summary** (must include per procedure): incident summary, customer impact, critical event timestamps, impact assessment, mitigation actions, escalations.
7. **Build payload** modeling RCA-41 defaults (full template in [`references/rca-template.md`](references/rca-template.md)):
   - Project: `RCA` (10245), Issue Type: `RCA` (10590) — NOT Support RCA
   - Summary: `<Customer> - RCA <mm/dd/yyyy>` (or `<ClusterID> - RCA <mm/dd/yyyy>` for multi-customer)
   - Description: Summary paragraph + Timeline table (the only content in description body)
   - Custom fields populated:
     - `customfield_10469` (Start time UTC) — datetime
     - `customfield_10470` (End time UTC) — datetime
     - `customfield_10475` (Zendesk) — bullet list with links
     - `customfield_10476` (Slack) — channel name with link
     - `customfield_10490` (Initial Root Cause) — hypothesis from Jira PDFs
     - `customfield_10467` (Final Root Cause & Conclusions) — keep 5-bullet placeholder
     - `customfield_10478` (Action item(s)) — ADF table with action items + red instruction line
     - `customfield_10495` (Affected component) — multi-checkbox
     - `customfield_10516` (Cluster ID) — labels array
     - `customfield_10520` (Account name) — `[customer_underscored]`
     - `customfield_10521` (Account ID) — if known
     - `customfield_10519` (Product) — `Redis Cloud` / `Redis Software` / `AMR`
     - `customfield_10619` (Is Customer RCA needed?) — `Yes` (23171)
     - `customfield_10472` (Contributors) — incident participants
   - Reporter: current user (the TSE creating the ticket)
   - Status (initial): `Data Collection` (id 10732) — leave as default
   - Labels: customer underscored + incident keywords (`ACRE`, `dmc`, `high_cpu`, etc.)
8. **Dry-run by default** — Write the preview file to `~/tse-jira-previews/RCA-rca-<timestamp>.md` (per the format in the "Mode" section above) showing the full RCA payload, action items table, custom field values, related bug links. Report path. **DO NOT call any MCP write tool yet.**
9. **Wait for explicit publish keyword.** Acceptable: `--publish` flag in the original invocation, or a follow-up message containing the word "publish". Implicit confirmations are NOT sufficient.
10. **On publish (and only on publish):**
    1. **Create** via `createJiraIssue` with project=RCA, issuetype=10590, all custom fields populated.
    2. **Link each related bug Jira** via `createIssueLink` with type `Relates` (id 10003): `inwardIssueKey` = new RCA, `outwardIssueKey` = each related bug key.
    3. **Append actual responses** to the preview file (new RCA key + link statuses).
11. **Output**:
    - RCA key + browse URL
    - Path to the (now post-create) preview file
    - Checklist of placeholders still needing human input:
      - Final Root Cause (Engineering)
      - Action item owners and Jira ticket keys
      - Customer RCA URL when generated
      - Contributors verification
    - **Reminder**: "When data entry is complete, transition the ticket from `Data Collection` to `Root Cause and Action Items`. Slack notifications post automatically to #root-cause-analysis."

---

## Workflow C — Impact Score Estimation

### Input Contract

- **Required:** ≥1 Jira (multiple OK):
  - Live Jira key (e.g. `RED-172734`) — fetched via `getJiraIssue`
  - OR Jira PDF path — Read tool
- **Optional:** Any number of Zendesk PDFs (supplement context for ARR / customer impact / frequency).

### Steps

1. **Source the content** for each Jira input:
   - Live key → `mcp__claude_ai_Atlassian__getJiraIssue` (cloudId, key, `responseContentFormat: "markdown"`)
   - PDF → Read tool
2. **For each Zendesk PDF** (if provided): Read; extract customer / frequency / SLA / workaround signals.
3. **Apply the model** in [`references/impact-score-model.md`](references/impact-score-model.md). For each of the 6 components, output:
   - Score (e.g., "16/16")
   - Reasoning (e.g., "found 'multiple occurrences' across 3 Zendesk threads")
4. **Compute base + final** (`base × (1 + CloudOps_mult + Customer_mult)`).
5. **Output** structured breakdown:
   ```
   IMPACT SCORE: 78.0 (HIGH)
   Base: 78  Multipliers: CloudOps=0, Customer=0

   | Component         | Score | Max | Reasoning                          |
   |-------------------|-------|-----|------------------------------------|
   | Impact & Severity | 30    | 38  | P2 — service degraded              |
   | Customer ARR      | 15    | 15  | Azure (>$1M)                       |
   | SLA Breach        | 8     | 8   | Breach claim in ticket             |
   | Frequency         | 16    | 16  | >4 occurrences over 2 weeks        |
   | Workaround        | 5     | 15  | Simple restart workaround          |
   | RCA Action Item   | 8     | 8   | Linked to existing RCA             |

   Per Support standard, the team leader should confirm this score before applying to the ticket(s).
   ```
6. **Do NOT create or modify any ticket** in this workflow. Score-only is a triage / discussion tool.
7. **Offer**: "Want me to apply this score to <Jira-key>? I'll set `customfield_10585` and post a breakdown comment." (Only on explicit yes.)

---

## Multi-Project Handling

The skill supports filing into any project the user has access to. Rules:

- **Auto-detect** project from content for the Bug workflow per [`references/zendesk-bug-mapping.md`](references/zendesk-bug-mapping.md). Show the choice; let user override.
- **For unknown projects** (user says "file in PROJ-XYZ"): call `getJiraProjectIssueTypesMetadata` first, then `getJiraIssueTypeMetaWithFields` for the chosen type. Filter the field list to TSE-relevant fields before previewing.
- **Component lists are project-specific.** Don't hardcode beyond what's in [`references/jira-schema.md`](references/jira-schema.md). For new projects, fetch components dynamically.
- **Custom field IDs are tenant-specific** but stable for redislabs.atlassian.net per [`references/jira-schema.md`](references/jira-schema.md). If `createJiraIssue` fails with "field cannot be set", drop the offending field and retry.

## Description Formatting (ADF vs Markdown)

Two distinct rules — these are not the same thing:

### System `description` field — markdown is fine

For the top-level `description` argument to `createJiraIssue` (or the system `description` field in `editJiraIssue`), pass markdown and set `contentFormat: "markdown"`. The MCP handles the conversion. Tables, headings, code blocks, links — all work.

### Custom textarea fields — ADF required, strings rejected

For any **custom textarea field** (`customfield_10374` Workaround, `customfield_10681` Impact Score details, `customfield_10063` RCA, and all the RCA narrative fields — `_10467`, `_10475`, `_10476`, `_10478`, `_10490`, `_11853`), the API requires Atlassian Document Format (ADF). A raw string returns:

```
"customfield_NNNNN": "Operation value must be an Atlassian Document (see the Atlassian Document Format)"
```

**Minimum viable ADF** for a one-line text value:

```jsonc
"customfield_10374": {
  "type": "doc",
  "version": 1,
  "content": [
    { "type": "paragraph",
      "content": [ { "type": "text", "text": "Your text here." } ] }
  ]
}
```

For multi-line content, add more paragraph blocks. For tables/lists, use ADF table / orderedList / bulletList nodes. See [`references/jira-schema.md`](references/jira-schema.md) for the full list of textarea fields requiring ADF.

### Comments — markdown is fine

`addCommentToJiraIssue` accepts markdown via `contentFormat: "markdown"`. Use that for the impact-score breakdown comment.

## Safety Rules

1. **Always preview + confirm** before any `createJiraIssue`, `createIssueLink`, or `editJiraIssue` call.
2. **Never silently overwrite an existing ticket's fields** with `editJiraIssue` — show the diff first.
3. **Never assume a Jira key exists** without verifying via `getJiraIssue` — typos are common.
4. **Refuse to file tickets exposing PII / secrets** in source PDFs without redaction. Flag and ask.
5. **Never auto-transition tickets** as part of creation. That's a separate user action.
6. **Azure RCA prerequisite**: refuse to create an Azure RCA if no RED/MOD bug is in the related links — per Support docs.
7. **Impact score is a recommendation**: always flag that the team leader should confirm the score before applying.

## Failure Modes & Recovery

| Symptom | Likely cause | Fix |
|---|---|---|
| `createJiraIssue` returns 400 "field cannot be set" | Custom field not on the create screen for that issue type | Fetch `getJiraIssueTypeMetaWithFields` for project + issue type; drop fields not in the response |
| 401/403 on any MCP call | Atlassian auth expired | Run `mcp__claude_ai_Atlassian__authenticate` (claude.ai surfaces login) |
| Project name typo (e.g., "Root Cause Analysis" key) | Need actual project key | `getVisibleJiraProjects` with `searchString` to discover real key |
| Issue type `RCA` rejected on non-RCA project | Issue type only exists in RCA project | `getJiraProjectIssueTypesMetadata` to confirm valid types per project |
| Affected Organizations dropdown — customer not found | Customer not in the 9,253-option list | Set `Seen by Customer/s` (free text) as fallback and note |
| Severity field rejects value | Wrong format — values need numeric prefix | Use `0 - Very High`, `1 - High`, `2 - Medium`, `3 - Low` exactly |
| RCA-related fields rejected on Bug ticket | Some RCA fields only exist on RCA issue type | Drop and warn |

## Related Tools

- `/tse-jira:bug <zendesk-pdfs>+ [-- <jira-pdfs>+]` — Bug workflow shortcut
- `/tse-jira:rca <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]` — RCA workflow shortcut
- `/tse-jira:score <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]` — Impact score only
- ECC `jira-integration` skill — complementary; read/comment/transition/search on existing tickets
- `redislabsdev/agent-skills/ticket-to-pr` — converts a Jira into a PR (after creation)
