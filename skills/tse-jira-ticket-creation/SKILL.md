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

## When to Activate

- User says "create a Jira for this Zendesk ticket / PDF"
- User mentions filing an RCA / drafting a root cause / multi-cluster incident
- User asks for an impact score / priority assessment for a Jira ticket
- User wants to file a bug against RED, MOD, DOC, or RDSC
- User attaches or references a Zendesk PDF or Jira PDF/key

**Never auto-create.** Always preview the fields and ask for confirmation before any `createJiraIssue` / `createIssueLink` / `editJiraIssue` call.

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
   - Affected Organizations (`customfield_10595`): customer name dropdown with **9,253+ options**. Resolution procedure:
     1. **Try exact match first.** Call `getJiraIssueTypeMetaWithFields` with `projectIdOrKey=RED`, `issueTypeId=10004`, and `maxResults=50`, `startAt=0`. Search the returned `customfield_10595.allowedValues` list for a case-insensitive substring match on the customer name.
     2. **If not in first page**, page through using `startAt` increments. **Cap at 5 pages (250 options total)** to avoid burning tokens — exact customer names usually surface in early pages alphabetically.
     3. **If found**: set `customfield_10595` to `[{"id":"<resolved_id>"}]`.
     4. **If NOT found**: skip `customfield_10595` entirely. Set the free-text fallback `customfield_10027` (Seen by Customer/s) to the customer name. Add the customer name as a label too. **Then in the post-create output, explicitly tell the TSE: "Affected Organizations was not auto-resolved — please pick `<customer>` from the dropdown in the browser before saving."**
     5. **Never invent an ID.** If the search doesn't find an exact substring match, do not guess.
   - Zendesk ID/s (`customfield_10036`): numbers only, comma-separated.
   - Workaround (`customfield_10374`): if a WA exists, describe in a few words + complicated/simple.
   - Data loss / Data unavailable / Downtime (`customfield_10371` / `_10372` / `_10369`): Yes/No each — ask TSE.
   - Event Status (`customfield_10373`): set to `workaround implemented` if WA in place.
   - Major Prod Channel (`customfield_10370`): Slack link if Major prod event.
   - Metrics (`customfield_10375`): Grafana link if available.
   - Impact Score (`customfield_10585`): numeric final score.
   - ICM ID/s (`customfield_14258`): for AMR — Azure IcM incident IDs.
   - **Labels**: always include `CS` or `Support`. Add `e2e_ta_coverage` if e2e-testable. For Azure: `Azure-Integration` + (`AMR` or `ACRE`); add `Azure_RCA_req` if an RCA is needed.
6. **Construct Description** with the structure in [`references/zendesk-bug-mapping.md`](references/zendesk-bug-mapping.md):
   - Symptom statement
   - **Customer expectations (Fix / RCA / Information / Workaround)** — required per Support docs
   - Cluster, Region, Product
   - Reporter (Zendesk #)
   - Details (extracted from Zendesk thread; ≤ ~2000 chars)
   - For Active-Active incidents: A-A mapping table
   - Log references in `cluster_name, node_id, shard_id` format
   - Related Jira links (if any)
7. **Preview** the structured ticket data. Include severity confirmation question to the user.
8. **Ask for explicit confirmation**: "Ready to create this Bug in <project>? (yes / edit / cancel)"
9. **Create** via `mcp__claude_ai_Atlassian__createJiraIssue` with `cloudId` + the mapped fields.
10. **Post-create steps**:
    1. **Add a comment** with the impact-score 6-component breakdown table (per Support standard, the breakdown goes in a comment, not a field). Use `mcp__claude_ai_Atlassian__addCommentToJiraIssue`.
    2. **Link related Jiras** (if any related Jira PDFs were provided): extract issue keys from filenames/content, call `mcp__claude_ai_Atlassian__createIssueLink` with type `Relates` (id 10003) for each.
    3. **For Azure tickets** (labels include `ACRE` or `AMR`): `editJiraIssue` to populate `customfield_10063` (RCA) with the Azure Incident Short Description template:
       ```
       ------------------------------
       0. Incident short description:
       ```
11. **Output**: new Jira key + browse URL (`https://redislabs.atlassian.net/browse/<KEY>`) + checklist of what still needs human input. Always include:
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
8. **Preview** the full payload — render description, action items table, custom field values.
9. **Ask for explicit confirmation**: "Ready to create this RCA? (yes / edit / cancel)"
10. **Create** via `createJiraIssue`.
11. **Post-create steps**:
    1. **Link each related bug Jira** via `createIssueLink` with type `Relates` (id 10003): `inwardIssueKey` = new RCA, `outwardIssueKey` = each related bug key.
    2. **Output checklist of placeholders** still needing human input:
       - Final Root Cause (Engineering)
       - Action item owners and Jira ticket keys
       - Customer RCA URL when generated
       - Contributors verification
    3. **Reminder**: "When data entry is complete, transition the ticket from `Data Collection` to `Root Cause and Action Items`. Slack notifications post automatically to #root-cause-analysis."

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

`createJiraIssue` and `editJiraIssue` typically accept either ADF or markdown for description / textarea fields. **Try markdown first**; if rendering is off (e.g., tables don't render), convert to ADF.

For Action Item tables (`customfield_10478`), markdown tables usually work. ADF is more reliable for nested formatting (bold "Investigate" / "Prevent" / "Mitigate" cells, red instruction line).

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
