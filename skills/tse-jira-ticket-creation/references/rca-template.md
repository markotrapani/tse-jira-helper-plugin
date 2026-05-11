# RCA Jira Template

Adapted from `jira-helper/src/generate_rca_form.py` and `jira_creator.create_rca_ticket`.

## Project

**Project key**: Look up via `mcp__claude_ai_Atlassian__getVisibleJiraProjects` with `searchString: "Root Cause Analysis"`. The display name is "Root Cause Analysis" but the project key may be shorter (e.g., `RCA`). Cache the resolved key once discovered.

**Issue type**: `RCA` (verify via `getJiraProjectIssueTypesMetadata` on first run).

## Required Fields

Ask the user for these once, batched:

1. **Customer name** — e.g., "Azure", "monday.com", "Salesforce"
2. **Incident date** — MM/DD/YY format (e.g., "10/24/25")
3. **Cluster names** — list (one or many): `rediscluster-ktcsproda11.eastus2`, `csie-fnp-linx01-redis03.northeurope`, etc.
4. **Regions** — list: `eastus2`, `northeurope`, `uksouth`, ...
5. **Affected component** — typically `DMC` for ACRE incidents. Default: detect from Jira PDFs.

## Basic Fields

| Field | Value |
|---|---|
| Project | Root Cause Analysis |
| Issue Type | RCA |
| Summary | `{customer_name} - RCA {date}` (e.g., "Azure - RCA 10/24/25") |
| Status | `Data Collection` (initial; user transitions to "Root Cause and Action Items" after filling final RCA) |
| Priority | `Medium` (RCAs don't carry P1 urgency — the underlying bug Jiras do) |
| Reporter | Current user |
| Assignee | Unassigned — user assigns to a Support DRI |
| Labels | Combine: `customer_name_underscored`, incident-specific keywords (`ACRE`, `dmc`, `high_cpu`, `azure`, `audit_logging`, ...) |
| Components | `{affected_component}` |
| Affects versions | None (typically) |
| Fix versions | None (filled later by Engineering) |

## Custom Fields (RCA-specific)

These appear on the RCA issue create screen. Field IDs to be confirmed per tenant via `getJiraIssueTypeMetaWithFields`.

| Field | Default Value |
|---|---|
| Is Customer RCA needed? | `Yes` |
| Slack channel | `#prod-{date_compact}-{customer_lower}` — e.g., `#prod-102425-azure`. Mark "No prod channel (yet)" if none exists |
| Cluster ID | Comma-separated list from input |
| Account name | Customer name |
| Account ID | (Leave blank unless found in PDFs) |
| Product | `Redis Software` for ACRE/Enterprise; `Redis Cloud` for Redis Cloud incidents |
| Affected component | From input |
| Is the Customer RCA delivered? | `None` initially |

## Description Body Structure

Render in this exact order. Use the markdown form (the MCP can take markdown for descriptions). The description should mirror what a TSE would expect to see in a Jira RCA — the user shouldn't have to reorganize it.

### Section 1: Summary

A 2–4 sentence narrative. Pattern:

```
{Impact statement: what broke, where, when}. {Affected count of clusters and regions}.
{How it was resolved per cluster — manual restart vs. automatic VM freeze}.
{Initial hypothesis from Jira PDFs — e.g., "Initial analysis indicates potential correlation with audit logging configuration issues and BDB state machine updates."}
```

### Section 2: Key Details

```
**Start time (UTC):** {earliest_event}
**End time (UTC):** {latest_event}

**Zendesk:**
- #{zendesk_id_1}
- #{zendesk_id_2}
- ...

**Slack:** {channel_or_"No prod channel (yet)"}
```

### Section 3: Timeline Table

```
| Date and Time (UTC)  | Activity                                                                |
|----------------------|-------------------------------------------------------------------------|
| {MMM-DD-YYYY, HH:MM} | {Event description tied to specific cluster}                             |
| ...                  | ...                                                                       |
```

**Event ordering**: chronological, oldest first.
**Event content**: one event per row. Tie each row to a specific cluster name when possible.
**Resolution rows**: mark how each cluster recovered — `Manual DMC restart - Issue resolved` or `Automatic VM freeze event - Issue resolved`.

### Section 4: Logs Section

```
**Logs Section:**
Key log patterns identified across incidents:
1. {Log pattern or placeholder if not yet extracted}
2. {...}
3. {...}
```

If logs aren't yet extracted, use placeholders the TSE can fill in later:
- `[Key log entries to be added manually]`
- `[Include timestamps, error messages, and relevant system logs]`
- `[Focus on logs that indicate the root cause of the incident]`

### Section 5: Relevant Links

```
**Relevant Links:**

**Zendesk Tickets:**
- [#{zendesk_id_1}](https://redislabs.zendesk.com/agent/tickets/{zendesk_id_1})
- ...

**Jira Bug Tickets:**
- [{RED-NNNNNN}](https://redislabs.atlassian.net/browse/{RED-NNNNNN}) - {bug_summary}
- ...

**Related RCA Tickets:**
- {related RCA key or "[No related RCA tickets]"}
```

### Section 6: Logs and Files (Support Packages + Cache Links)

```
**Logs and Files:**

**Ticket #{zendesk_id_1} Support Packages:**
- s3://gt-logs/exa-to-gt/ZD-{zendesk_id_1}-{related_bug}/...

**ACRE Cache Links:** (only for Azure incidents)
- {jarvis-west.dc.ad.msft.net dgrep URL}
- ...
```

Extract `s3://gt-logs/...` URLs from the Zendesk PDFs. ACRE Jarvis URLs typically come from the Jira PDFs or are added manually.

### Section 7: Initial Root Cause

```
**Initial Root Cause:**
{1-3 paragraph hypothesis based on Jira PDF content. Should reference specific symptoms (high CPU, audit disconnects, state machine updates) without committing to a definitive cause — Engineering will refine this.}
```

### Section 8: Final Root Cause & Conclusions

```
**Final Root Cause & Conclusions:**
[To be completed by Engineering team]
```

### Section 9: Action Items

```
**Action Items:**
After updating the table below, ensure the tickets are linked with the `relates to` type.

| Description                          | Type                    | Owner   | Ticket           |
|--------------------------------------|-------------------------|---------|------------------|
| {Action description}                 | Investigate/Prevent/Mitigate | @name   | <jira-ticket>    |
| ...                                  | ...                     | ...     | ...              |
```

**Action item Type taxonomy** (pick one):
- **Investigate** — research / analysis tasks ("Investigate CPU utilization patterns")
- **Prevent** — preventative engineering changes ("Implement automatic recovery for X")
- **Mitigate** — short-term mitigations ("Document manual restart procedure for support")

Generate suggested action items from Jira PDF content keywords:

| Keyword in Jira PDF | Suggested Action |
|---|---|
| `cpu` | Investigate CPU utilization patterns |
| `audit` | Review audit logging configuration |
| `restart` | Implement automatic recovery mechanisms |
| (default) | Investigate root cause of reported issue |

Owner / Ticket are placeholders (`@name`, `<jira-ticket>`) for Engineering to fill in.

## Issue Links (Created Separately)

After `createJiraIssue` returns, call `mcp__claude_ai_Atlassian__createIssueLink` for each:

| Linked Issue | Link Type | Direction |
|---|---|---|
| Each related bug Jira (from Jira PDFs) | `Relates` | outward |
| (Future) Each Zendesk ticket if Zendesk integration is wired | Custom integration link | n/a |

Confirm link type names via `getIssueLinkTypes` on first run.

## Multi-Cluster Considerations

When an incident spans multiple clusters (common for Azure ACRE):

- **Cluster ID custom field**: pass a comma-separated list
- **Timeline**: each event references its cluster by name
- **Summary**: enumerate clusters and regions ("affecting 4 Azure clusters across 3 regions")
- **Resolution method per cluster**: distinguish in timeline ("Manual DMC restart" vs "Automatic VM freeze event")

## Worked Example (Skeleton)

For an incident with:
- Customer: Azure
- Date: 10/24/25
- Clusters: `prod110-europe-hdc-europe-cp102-titan2.northeurope`, `rediscluster-ktcsproda11.eastus2`
- Regions: northeurope, eastus2
- Component: DMC

Generated summary:

> "DMC high-CPU utilization incident affecting 2 Azure clusters across 2 regions, leading to CPU exhaustion on ACRE nodes. The incident was resolved for one cluster/node with a manual DMC restart, while the other was resolved automatically by VM freeze. Initial analysis indicates potential correlation with audit logging configuration issues and BDB state machine updates."

Generated labels: `Azure`, `ACRE`, `dmc`, `high_cpu`, `azure`

Generated Slack channel: `#prod-102425-azure`

## Anti-patterns

- **Don't write the Final Root Cause yourself.** That's Engineering's job after investigation. Use the `[To be completed by Engineering team]` placeholder.
- **Don't link the RCA to itself.** Sanity-check issue link calls.
- **Don't auto-transition** from "Data Collection" — leave the user in control of workflow state.
- **Don't fabricate timestamps.** If the PDFs don't have specific times, use placeholder `MMM-DD-YYYY, HH:MM` and mark the row clearly so the TSE can fill in.
- **Don't dump entire PDF contents** into the description. Extract relevant facts.
