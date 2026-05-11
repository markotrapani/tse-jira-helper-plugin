---
name: tse-jira-ticket-creation
description: Create Redis Jira tickets for Technical Support Engineers — Bug Jiras from Zendesk PDFs (with optional related Jira PDFs), multi-cluster RCA Jiras from Zendesk+Jira PDFs, and impact score estimation using the 8-130 TSE model. Multi-project (RED/MOD/DOC/RDSC/Root Cause Analysis), sprint-optional, uses the claude.ai Atlassian MCP. Activate when the user mentions creating a Jira from a Zendesk ticket, drafting an RCA, scoring a ticket's impact, or filing against any redislabs.atlassian.net project.
---

# TSE Jira Ticket Creation

A Redis Technical Support Engineer workflow for creating Jira tickets in `redislabs.atlassian.net` through the claude.ai Atlassian MCP. Supports three workflows:

| Workflow | Input | Output |
|---|---|---|
| **Bug Jira** | Zendesk PDF(s) (required) + related Jira PDFs (optional) | Bug ticket in RED / MOD / DOC / RDSC with impact score, mapped fields, optional linked issues |
| **RCA Jira** | Zendesk PDF(s) **and** Jira PDF(s) (both required) | RCA ticket in "Root Cause Analysis" project with timeline, bug links, action items table |
| **Impact Score** | Zendesk PDF, Jira PDF, plain text, or existing Jira key | 8-130 score + 6-component breakdown with reasoning |

This skill is the spiritual successor to `~/Downloads/marko-projects/jira-helper` — same impact scoring, same Zendesk→Jira field mapping, but actually creates tickets via MCP instead of generating markdown for copy/paste.

## Cloud ID

For all `mcp__claude_ai_Atlassian__*` calls against Redis Labs Jira:

```
cloudId: 06f73ca7-8f2c-4392-b40a-08288e9d0ba3
```

(Confirm with `mcp__claude_ai_Atlassian__getAccessibleAtlassianResources` if the call fails.)

## Reference Files

Read the matching reference file as the workflow demands — don't load all of them upfront:

- `references/impact-score-model.md` — full 6-component scoring model with point values, keyword indicators, priority bands. Read for any score-related work.
- `references/zendesk-bug-mapping.md` — Zendesk PDF → Jira field mapping, project auto-detection rules, component/severity/priority maps. Read for the Bug workflow.
- `references/rca-template.md` — RCA Jira form structure, timeline table format, action item taxonomy. Read for the RCA workflow.

## When to Activate

- User says "create a Jira for this Zendesk ticket / PDF"
- User mentions filing an RCA / drafting a root cause / multi-cluster incident
- User asks for an impact score / priority assessment for a ticket
- User wants to file a bug against RED, MOD, DOC, or RDSC
- User attaches or references a Zendesk PDF or Jira PDF

Do NOT auto-create. **Always preview the fields and ask for confirmation before calling `createJiraIssue`.**

## Workflow A — Bug Jira from Zendesk

### Inputs

- **Required:** one or more Zendesk PDF paths (or full ticket text in the conversation)
- **Optional:** related Jira PDF paths (used to add `Relates to` issue links, not to override scoring)

### Steps

1. **Read the Zendesk PDF(s)** with the Read tool. PDFs are first-class — Read returns text + can read up to 20 pages.
2. **Extract**:
   - Zendesk ticket ID (filename pattern: `redislabs.zendesk.com_tickets_<ID>_print.pdf`)
   - Customer name (from account/organization field)
   - Summary (one-line subject)
   - Description (problem statement + first relevant comment thread)
   - Priority / severity if stated
   - Frequency indicators ("multiple times", "intermittent", recurrence dates)
   - Cluster name, region, product (Redis Cloud / Redis Software / Azure Cache for Redis / RDI)
3. **Compute impact score** — apply the model in `references/impact-score-model.md`. Show each component's score + reasoning to the user.
4. **Auto-detect project** — apply rules in `references/zendesk-bug-mapping.md` (RDSC > MOD > RED). State the detected project; let the user override.
5. **Map fields** — using `references/zendesk-bug-mapping.md`:
   - Issue type: `Bug`
   - Priority (Highest/High/Medium/Low/Lowest from score → priority text)
   - Severity (Very High / High / Medium / Low from score thresholds)
   - Components (DMC / Redis / Cluster / module-specific)
   - Labels (extracted keywords + customer name + `Customer-Reported`)
   - Custom fields: Zendesk ID, impact score, cache name, region, affected organization (Azure/AWS/GCP)
6. **Preview** the ticket as a structured block:
   ```
   Project: <key>
   Type: Bug
   Summary: <one line>
   Priority: <P-level>  Severity: <text>
   Labels: <list>
   Components: <list>
   Custom fields:
     Zendesk ID: <id>
     Impact Score: <n> (<priority band>)
     ...
   Description preview: <first 200 chars>...
   Related Jiras (issue links): <list, if any>
   ```
7. **Ask for confirmation.** "Ready to create this in <project>? (yes/edit/cancel)"
8. **Create** via `mcp__claude_ai_Atlassian__createJiraIssue` with `cloudId` + the mapped fields.
9. **Link related Jiras** (if optional Jira PDFs were provided): extract their issue keys from filenames or content, then call `mcp__claude_ai_Atlassian__createIssueLink` with type `Relates`.
10. **Output**: the new Jira key + browse URL (`https://redislabs.atlassian.net/browse/<KEY>`).

### Sprint handling

**Do not** ask about sprint by default. TSE bugs typically land in the backlog. If the user explicitly says "add to current sprint" or names a sprint, fetch sprint ID via `mcp__claude_ai_Atlassian__searchJiraIssuesUsingJql` (`project = X AND sprint in openSprints()`) and add it to the create call.

## Workflow B — RCA Jira (Multi-cluster)

### Inputs

- **Required:** Zendesk PDF(s) — the customer-facing incident tickets
- **Required:** Jira PDF(s) — the related bug Jiras that feed the root cause analysis
- **Required from user (ask once, batch the questions):**
  - Customer name (e.g. "Azure", "monday.com")
  - Incident date (MM/DD/YY)
  - Cluster names (list — TSE incidents often span multiple clusters)
  - Regions (list)
  - Affected component (default: detect from PDFs — typically DMC, Redis, or Cluster)

> **Rationale for both PDF types:** Zendesk PDFs give the customer-facing timeline and impact. Jira PDFs give the root-cause hypotheses, action items, and engineering details. The RCA description weaves both.

### Steps

1. **Read all PDFs** in parallel with the Read tool.
2. **Extract from Zendesk PDFs**:
   - Ticket IDs, customer-reported start times, customer impact descriptions, support-package S3 paths (look for `s3://gt-logs/...`)
3. **Extract from Jira PDFs**:
   - Bug keys (filenames: `[#RED-NNNNNN]...pdf`), bug summaries, "Initial Root Cause" candidates, action item drafts, log patterns
4. **Build timeline table** — chronologically sort events per cluster. Use `references/rca-template.md` format:
   ```
   | Date and Time (UTC) | Activity |
   | Oct-01-2025, 21:22  | DMC high CPU on <cluster> |
   | Oct-03-2025, 04:26  | Manual DMC restart — resolved |
   ```
5. **Determine start/end times**: earliest "started"/"detected" event, latest "resolved"/"completed" event.
6. **Compose RCA fields** (full template in `references/rca-template.md`):
   - Project: `Root Cause Analysis` (look up actual project key with `mcp__claude_ai_Atlassian__getVisibleJiraProjects` if first run)
   - Issue type: `RCA`
   - Summary: `{customer} - RCA {date}`
   - Priority: Medium (RCAs are not P1 — the underlying bug Jiras own urgency)
   - Status: Data Collection (initial)
   - Labels: ACRE / cluster / dmc / azure / customer_name — pulled from incident content
   - Custom fields: Cluster ID list, Account name, Affected component, Is Customer RCA needed? (Yes), Slack channel, Product
   - Description body: Summary paragraph + Timeline table + Logs section + Relevant Links (Zendesk + Jira + ACRE cache links) + Initial Root Cause + (placeholders for) Final Root Cause + Action Items table
7. **Preview** the full description rendered as the user will see it in Jira. Include the timeline table.
8. **Ask for confirmation** explicitly — RCAs are high-visibility tickets.
9. **Create** via `createJiraIssue`.
10. **Link every related ticket**:
    - For each Zendesk ticket: add a remote issue link via `mcp__claude_ai_Atlassian__createIssueLink` if Jira has the Zendesk integration, otherwise embed the URL in the description's "Relevant Links" section
    - For each bug Jira: `createIssueLink` with type `Relates`
11. **Output**: RCA key + browse URL + a checklist of what still needs human input (Final Root Cause, Action Item assignees/tickets).

## Workflow C — Impact Score Estimation Only

### Inputs (any one of)

- Path to a Zendesk PDF
- Path to a Jira PDF
- Existing Jira key (e.g., `RED-172734`)
- Pasted ticket text (summary + description)

### Steps

1. **Source the content**:
   - PDF → Read tool
   - Jira key → `mcp__claude_ai_Atlassian__getJiraIssue` with cloudId + key, expand `renderedFields` so the description is plain text
   - Pasted text → use as-is
2. **Apply the model** in `references/impact-score-model.md`. For each of the 6 components, output:
   - Score (e.g. "16/16")
   - Reasoning ("found 'multiple occurrences' keyword in comments")
3. **Compute base + final** (base × (1 + support_mult + account_mult)).
4. **Output** structured breakdown:
   ```
   IMPACT SCORE: 78.0 (HIGH)
   Base: 78  Multipliers: Support=0, Account=0

   | Component        | Score | Max | Reasoning |
   |------------------|-------|-----|-----------|
   | Impact & Severity | 30   | 38  | P2 — service degraded |
   | Customer ARR      | 15   | 15  | ARR > $1M (Azure) |
   | SLA Breach        | 8    | 8   | Breach mentioned in ticket |
   | Frequency         | 16   | 16  | >4 occurrences over 2 weeks |
   | Workaround        | 5    | 15  | Simple restart workaround |
   | RCA Action Item   | 8    | 8   | Linked to existing RCA |
   ```
5. **Do NOT create a ticket** in this workflow. Score-only is a triage tool.

## Multi-Project Handling

The skill should support filing into any project the user has access to, not just RED. Rules:

- **Auto-detect** the project from PDF content for Bug workflow (see `references/zendesk-bug-mapping.md`). Show the choice and let the user override.
- **For unknown projects** (user says "file in PROJ-XYZ"), call `mcp__claude_ai_Atlassian__getJiraProjectIssueTypesMetadata` first to discover allowed issue types, then `getJiraIssueTypeMetaWithFields` for required fields.
- **Component lists are project-specific.** Do not hardcode. For projects beyond RED/MOD/DOC/RDSC, fetch components dynamically and ask the user to pick.
- **Custom field IDs are tenant-specific.** Field IDs in `references/zendesk-bug-mapping.md` are the known ones for redislabs.atlassian.net (e.g. `customfield_10010` Sprint). If a `createJiraIssue` call fails with "field not on screen for issue type X", fetch the issue type meta to learn which fields are valid for that combination.

## Description Formatting (ADF)

`mcp__claude_ai_Atlassian__createJiraIssue` and `editJiraIssue` accept descriptions as Atlassian Document Format (ADF). For TSE workflows, lean on the simplest ADF nodes:

- `paragraph` with `text` runs
- `bulletList` / `orderedList` with `listItem`
- `table` for timeline + action items (RCA)
- `codeBlock` for log snippets
- `inlineCard` or plain link for Zendesk/Jira URLs

The MCP tool will accept either ADF objects or plain markdown strings depending on its current implementation — try markdown first; if rendering is off, convert to ADF. Keep the description structure mirroring `references/rca-template.md` for RCAs and the bug template for Bugs.

## Safety Rules

1. **Never** create a ticket without explicit user confirmation of the preview.
2. **Never** silently overwrite an existing ticket's fields with `editJiraIssue` — show the diff and ask first.
3. **Never** assume a Jira key exists without verifying via `getJiraIssue` — typos are common.
4. **Refuse** to file tickets that would expose PII or secrets present in the source PDFs without redaction. Flag and ask the user to confirm.
5. **Never** auto-transition tickets (e.g., to "In Progress") as part of creation. That's a separate user action.

## Failure Modes & Recovery

| Symptom | Likely cause | Fix |
|---|---|---|
| `createJiraIssue` returns 400 "field cannot be set" | Custom field not on the create screen for that issue type | Fetch `getJiraIssueTypeMetaWithFields` for project + issue type; drop fields not in the response |
| 401/403 on any MCP call | Atlassian auth expired | Run `mcp__claude_ai_Atlassian__authenticate` (claude.ai will surface a login prompt) |
| Project name typo (e.g., "Root Cause Analysis" doesn't resolve) | Need the actual project key | `getVisibleJiraProjects` with `searchString` to discover the real key |
| Issue type `RCA` rejected | Issue type ID/name varies per project | `getJiraProjectIssueTypesMetadata` to list valid types |
| Description renders as raw markdown | MCP expected ADF | Re-encode description as ADF document |

## Related Tools

- `/tse-jira bug <zendesk-pdf>` — Bug workflow shortcut (see `commands/tse-jira.md`)
- `/tse-jira rca` — RCA workflow shortcut
- `/tse-jira score <input>` — Impact score only
- ECC `jira-integration` skill — complementary; handles read/comment/transition/search on existing tickets
- `redislabsdev/agent-skills` `ticket-to-pr` — converts a Jira ticket into a PR (after creation)
