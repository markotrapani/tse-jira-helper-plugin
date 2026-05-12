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
| **Bug Jira** (`/tse-jira bug`) | ≥1 Zendesk PDF (multiple OK) | Related Jira PDFs (any number — linked via `Relates`) | Bug ticket in RED / MOD / DOC / RDSC with TSE-judged severity, default priority, impact score, mapped fields. Impact-score breakdown posted as a comment. For Azure: post-save RCA-template field populated. |
| **RCA Jira** (`/tse-jira rca`) | ≥1 Jira PDF (multiple OK) | Zendesk PDFs (any number) | RCA ticket created by cloning RCA-41 defaults: title `<Customer> - RCA <mm/dd/yyyy>`, Initial Root Cause from Jira PDF content, action items pre-filled with placeholders, all related bugs linked via `Relates`. Status starts at `Data Collection`. |
| **Impact Score** (`/tse-jira score`) | ≥1 Jira (PDF or live key) (multiple OK) | Zendesk PDFs (any number, supplement context) | 8-130 score + 6-component breakdown with reasoning. **No ticket creation.** Score is a recommendation; team leader confirms before applying. |

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

**Never auto-create.** Always preview the fields and ask for confirmation before any `createJiraIssue` / `createIssueLink` / `editJiraIssue` call.

---

## ⚠️ Mode: Dry-Run (Default) vs Publish

**Default mode is DRY-RUN.** The Bug and RCA workflows write a local markdown preview file and stop there — they NEVER call MCP write tools unless the user has explicitly requested publish mode.

### When publish mode is active

The skill enters publish mode **only** when one of these is true:

1. User invoked `/tse-jira bug ... --publish` or `/tse-jira rca ... --publish`
2. User has run a dry-run, reviewed the preview file, and said something like "publish it now", "go ahead and create", "publish to Jira" — referencing the preview file the skill produced
3. User is running the Impact Score workflow with the explicit "apply this score to ticket X" follow-up (since score-only is read-only by default)

**Implicit phrases like "yes", "go", "looks good" after a preview are AMBIGUOUS — clarify before publishing.** Per the user's documented preference (memory: `feedback_destructive_operations.md`), pause for an explicit `publish` keyword before any MCP write call. A top-level "go" earlier in the conversation does NOT cover later destructive steps — re-confirm each one.

### Two-layer protection

1. **Skill-level (this document):** dry-run by default, explicit publish keyword required
2. **Harness-level (`~/.claude/settings.json`):** the user should have `mcp__claude_ai_Atlassian__createJiraIssue` (and 9 other write tools) listed under `permissions.ask`. Even if this skill is misread, Claude Code will prompt the user before any write call fires. See [SECURITY.md](../../../../SECURITY.md) for the install snippet.

### Dry-run output: preview file

Default location: `~/tse-jira-previews/<project>-<workflow>-<timestamp>.md`

Example: `~/tse-jira-previews/RED-bug-20260511T153000Z.md`

If `~/tse-jira-previews/` doesn't exist, create it (`mkdir -p`). User can override the directory by saying "preview to `<path>`".

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

`/tse-jira score` is **inherently read-only** — it just computes the impact score. It doesn't have a "publish" mode in the same sense. The follow-up "apply this score to RED-NNN" is a separate small workflow that does count as publish (it sets `customfield_10585` and posts a breakdown comment) — that follow-up uses the same explicit-confirmation rules.

---

## Workflow A — Bug Jira from Zendesk

### Input Contract

- **Required:** ≥1 Zendesk PDF (path or text in conversation). Multiple Zendesk PDFs OK — they may all link to the same Bug if the issue is shared across customer tickets.
- **Optional:** Any number of related Jira PDFs (to be linked via `Relates` after creation).

### Steps

1. **Read all Zendesk PDFs** with the Read tool. PDFs are first-class — Read returns text and reads up to 20 pages.
2. **Extract per PDF**:
   - Zendesk ticket ID (filename pattern: `redislabs.zendesk.com_tickets_<ID>_print.pdf`)
   - Customer name / organization
   - Summary (one-line subject)
   - Description / problem statement
   - Comments thread (first few relevant exchanges)
   - Frequency indicators ("multiple times", "intermittent")
   - Cluster name, region, product version
   - Cloud (Azure / AWS / GCP), product (Redis Software / Cloud / RDI)
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
   - **RCA template (`customfield_10063`)**: ADF with the 6-section template populated. **NOT Azure-only — populate on EVERY bug.** Section 0 filled with one-line customer-readable description, sections 1-5 left as placeholders. ⭐ FIXED classification in v0.7
   - Workaround (`customfield_10374`): if a WA exists, multi-paragraph + code-block ADF. See [`references/zendesk-bug-mapping.md` → Workaround section](references/zendesk-bug-mapping.md).
   - Data loss / Data unavailable / Downtime (`customfield_10371` / `_10372` / `_10369`): Yes/No each — ask TSE.
   - Event Status (`customfield_10373`): set to `workaround implemented` if WA in place.
   - Major Prod Channel (`customfield_10370`): Slack link if Major prod event.
   - Metrics (`customfield_10375`): Grafana link if available.
   - Impact Score (`customfield_10585`): numeric final score.
   - ICM ID/s (`customfield_14258`): for AMR — Azure IcM incident IDs.
   - **Labels**: 2-3 max. Required: one of `CS` or `Support`. Add 1-2 domain tags. For Azure: `Azure-Integration` + (`AMR` or `ACRE`); add `Azure_RCA_req` if an RCA is needed. ⭐ Tightened in v0.7 — see [`references/zendesk-bug-mapping.md` → Labels section](references/zendesk-bug-mapping.md).
6. **Construct Description** — **Anchor to a canonical Jira first.** ⭐ MAJOR CHANGE in v0.7
   - Scan [`references/canonical-jiras/`](references/canonical-jiras/) for the closest match by issue type + domain (encryption, modules, Azure, A-A, support tooling, cm_server, auth, etc.)
   - **Mirror the H2 section structure** from the chosen canonical example. Use H2 sections like Summary / Root Cause / Customer Impact / Steps to Reproduce / Expected / Actual / Evidence from Support Case / Workaround (heading only) / Suggested Fix / Related Code Paths / Support Package Reference — exactly which sections depend on the canonical pick.
   - **Do NOT** add a flat "**Label:** value" prefix block at the top. Customer / cluster / subscription / BDB / product data lives ONLY in fields.
   - For Active-Active incidents: include the A-A mapping table inside `## Evidence from Support Case`.
   - Log references in `cluster_name, node_id, shard_id` format inside `## Evidence from Support Case`.
   - Related Jira links inside `## Related Jiras` (if any).
   - **If no canonical example fits**: pick the closest one and flag low confidence in the preview's pre-flight checks: `"Anchor: RED-XXXXX (closest match for {issue shape}) — review carefully"`. Suggest the user save the resulting Jira as a new canonical example after filing.
   - See [`references/zendesk-bug-mapping.md` → Description Body Template](references/zendesk-bug-mapping.md) for the full template and anti-patterns.
7. **Preview** — Ask the user for severity confirmation if not provided. Resolve Affected Organizations via paginated search. Build the full payload structures (createJiraIssue, addCommentToJiraIssue, createIssueLink calls).
8. **Dry-run by default** — Write the preview file to `~/tse-jira-previews/RED-bug-<timestamp>.md` (per the format in the "Mode" section above). Report the path to the user. **DO NOT call any MCP write tool yet.**
9. **Wait for explicit publish keyword.** Acceptable: `--publish` flag in the original invocation, or a follow-up message containing the word "publish" referring to this preview. Implicit confirmations ("yes", "go", "looks good") are **NOT sufficient** — clarify.
10. **On publish (and only on publish):**
    1. **Create** via `mcp__claude_ai_Atlassian__createJiraIssue` with `cloudId` + the mapped fields. Capture the new key.
    2. **Add a comment** with the impact-score 6-component breakdown table via `mcp__claude_ai_Atlassian__addCommentToJiraIssue` (markdown content format is fine for comments).
    3. **Link related Jiras** (if any related Jira PDFs/keys were provided): call `mcp__claude_ai_Atlassian__createIssueLink` with type `Relates` (id 10003) for each.
    4. **RCA template is populated on initial create** (not post-save) — see step 5's RCA template bullet. Azure ACRE/AMR tickets get the same 6-section template; section 0 is the only TSE-filled section at file time, and the customer-facing automation reads it for Azure tickets specifically.
    5. **Append to the preview file** an "Actual API responses" section showing the new key, comment id, and link statuses — so the preview becomes the post-create audit record.
11. **Output**: new Jira key + browse URL (`https://redislabs.atlassian.net/browse/<KEY>`) + path to the (now post-create) preview file + checklist of what still needs human input. Always include:
    - Attachments: "Attach the Zendesk PDF and any logs in the browser — MCP `createJiraIssue` doesn't accept attachments."
    - **If `customfield_10595` (Affected Organizations) was skipped** because no autocomplete match was found: "Open the ticket in the browser and select `<customer>` from the Affected Organizations dropdown."
    - Reporter / Assignee: verify the auto-assignment looks correct.
    - For Active-Active tickets: confirm the A-A mapping table in the description is accurate.

---

## Workflow B — RCA Jira (Multi-cluster)

### Input Contract

- **Required:** ≥1 Jira PDF (or live Jira key). Multiple Jiras OK — these are the related bug Jiras that feed the root cause analysis.
- **Optional:** Any number of Zendesk PDFs (customer-facing context for impact statement and timeline).
- **Required from user (ask once, batched):**
  - Customer name (e.g., "Azure", "monday.com") — or `ClusterID` / `Major Service` for multi-customer incidents
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

- `/tse-jira bug <zendesk-pdfs>+ [-- <jira-pdfs>+]` — Bug workflow shortcut
- `/tse-jira rca <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]` — RCA workflow shortcut
- `/tse-jira score <jira-pdfs-or-keys>+ [-- <zendesk-pdfs>+]` — Impact score only
- ECC `jira-integration` skill — complementary; read/comment/transition/search on existing tickets
- `redislabsdev/agent-skills/ticket-to-pr` — converts a Jira into a PR (after creation)
