# RCA Jira — TSE Workflow

**Authoritative sources:**
- [RCA Initiation and Data Collection Procedure (DevOps space, page 4575690753)](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4575690753) — the procedure
- [Internal R&D RCA and Continuous Improvement Process (DevOps space, page 4571660292)](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4571660292) — the overall process
- [RCA-41](https://redislabs.atlassian.net/browse/RCA-41) — the canonical template ticket
- [Jira creation for Support](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958) — Support team's Jira guide (mentions Azure RCA → RED/MOD link requirement)

## TLDR

**Per Support procedure**: clone RCA-41 (in the UI: three-dots → Clone). For programmatic creation via MCP, we replicate that effect by calling `createJiraIssue` with the same field defaults as RCA-41, then overriding incident-specific values.

## Project + Type

```
project: { "key": "RCA" }    // id 10245, name "Root Cause Analysis"
issuetype: { "id": "10590" } // RCA — same type as RCA-41
```

> **Don't use `Support RCA` (16251)**. RCA-41 (the canonical template) uses plain `RCA` (10590). Field schemas are nearly identical, but RCA-41 = RCA, so we use RCA.

## TSE Role

Per the R&D RCA process doc, the TSE is the **Initiator** (along with CloudOps / SRE). The Initiator's responsibilities:

- Identify incidents requiring an RCA
- **Create the RCA ticket within 6 hours after incident resolution** (RTTI KPI)
- Provide collected data, initial root cause, context
- Set the right status

## Input Contract (v0.12+ — Zendesk now required)

For the **customer-facing RCA shape** (default, e.g. RCA-583):

- **Required:** ≥1 Zendesk PDF — customer-facing context for impact statement and timeline.
- **Required:** ≥1 Jira PDF or live Jira key — related bug Jiras that feed the root cause analysis.

For the **cluster-incident-shape RCA** (automation-initiated, e.g. RCA-563): Zendesk is **not** required. Detect via cluster ID prefix in summary + `Reporter: Incident` (automation) on the source Jira. In that case, ask for cluster context instead.

This is a tightening from earlier versions where Zendesk was optional. See memory: `feedback-rca-zendesk-required`.

## Required Fields

- `project` — `{"key":"RCA"}`
- `issuetype` — `{"id":"10590"}`
- `summary` — see Title Format below

## Title Format

From the procedure doc and RCA-41:

```
<Customer Name> - RCA <mm/dd/yyyy>
```

- Example: `"Azure - RCA 10/24/2025"`, `"LTK - RCA 11/02/2025 - db:13038666 latency"`
- The RCA-41 raw template literally says `<mm/dd/yyy>` (3 y's). Most real production clones use `mm/dd/yyyy` (4 y's) — both are accepted. The skill should use `mm/dd/yyyy` for clarity.

**Multi-customer / multi-tenant incidents**: replace `<Customer Name>` with:
- `ClusterID` (when affecting a specific cluster shared by multiple customers)
- `Major Service Affected` like `DNS`, `Control Plane`, `Cloud API`

Examples from production: `"Multiple GCP - RCA <11/16/2015>"`, `"AMR - RCA 03/13/2026"`.

## Initial Status

Set or leave as **`Data Collection`** (status id 10732). Transition to `Root Cause and Action Items` (id 10856) only when data entry is complete (Step 5 of procedure).

Full workflow: `Data Collection` → `Root Cause and Action Items` → `Pending Action Items` → `Final Review` → `RCA Completed`.

**TSE rule**: Don't auto-transition past `Root Cause and Action Items`. Engineering and Leadership control later transitions.

## Custom Fields — Populated Directly

**Critical**: RCA content lives in dedicated custom fields, NOT mixed into description body. RCA-41 demonstrates the canonical placement.

### Right Panel Fields (per procedure)

| Field                  | fieldId             | Type             | Per RCA-41 default / TSE notes |
|------------------------|---------------------|------------------|-------|
| **Reporter**           | `reporter`          | user             | **Assign yourself** — the TSE creating the ticket |
| **Contributors**       | `customfield_10472` | array of user    | All active participants of the incident |
| **Cluster ID**         | `customfield_10516` | array (labels)   | Cluster names from incident |
| **Account name**       | `customfield_10520` | array (labels)   | Customer name. **Replace spaces with underscores** (e.g., `"monday.com"` → `["monday_com"]`) |
| **Account ID**         | `customfield_10521` | array (labels)   | If known |
| **Product**            | `customfield_10519` | option (select)  | "Cloud or Software" per docs. Options: `Redis Cloud` (11122), `Redis Software` (11123), `AMR` (11209). Default: Redis Cloud |
| **Affected component** | `customfield_10495` | multi-checkbox   | One or more from the 44-option list (see jira-schema.md) |

### Main Section Fields (per procedure)

| Field                              | fieldId             | Type             | Per RCA-41 default / TSE notes |
|------------------------------------|---------------------|------------------|-------|
| **Start time (UTC)**               | `customfield_10469` | datetime         | Incident start time |
| **End time (UTC)**                 | `customfield_10470` | datetime         | Incident end time |
| **Zendesk**                        | `customfield_10475` | textarea (ADF)   | Bullet list with linked Zendesk IDs. RCA-41 default: `#XXXXXX` linked to `https://redislabs.zendesk.com/agent/tickets/XXXXXX` |
| **Slack**                          | `customfield_10476` | textarea (ADF)   | Hyperlinked Slack channel — see Slack Channel Convention below |
| **Initial Root Cause**             | `customfield_10490` | textarea (ADF)   | High-level understanding from production event or preliminary investigation. RCA-41 default placeholder: `<Add your initial RCA here>` |
| **Final Root Cause & Conclusions** | `customfield_10467` | textarea (ADF)   | **Leave with 5 bullet placeholders** `<Add your final RCA and Conclusions here>` — Engineering fills later |
| **Action item(s)**                 | `customfield_10478` | textarea (ADF table) | RCA-41 default: 3-row ADF table. See Action Items Template below |
| **Is Customer RCA needed?**        | `customfield_10619` | option (select)  | `Yes` (23171) — TSE default |
| Is the Customer RCA delivered?     | `customfield_14159` | multi-checkbox   | Leave empty initially |
| Customer RCA                       | `customfield_10496` | URL              | Link to customer-facing RCA doc (filled later) |

## Description Body (Summary + Timeline)

Per RCA-41, the description is minimal:

```markdown
**Summary:** {Incident summary: what broke, where, when, customer impact, mitigation actions, escalations}

---

| **Date and Time _(UTC)_** | **Activity** |
| --- | --- |
| {MMM-DD-YYYY, HH:MM}      | {What happened / what was done} |
| {MMM-DD-YYYY, HH:MM}      | {...}                            |
```

### Summary Must Include (per procedure)

- Incident summary
- Customer impact statement
- Timestamps of critical events
- Impact assessment
- Mitigation actions
- Escalation details (e.g., notifications sent to on-call engineers)

### Summary May Include (when available)

- Extra system logs or monitoring data
- Non-critical commands
- Supporting screenshots / supplementary details

## Slack Channel Convention

RCA-41 default: `#prod-YEARMONTHDATE-cXXXXXX` (compact, cluster-based).

Procedure example: `#prod_incident-20250127-biocatch_prod37_zd131142` (descriptive, single-incident).

The skill should suggest the more descriptive form when single-customer/single-cluster, fall back to compact form otherwise:

- Descriptive: `#prod_incident-{YYYYMMDD}-{customer_lower}_{cluster_short}_zd{zendesk_id}`
- Compact: `#prod-{YYYYMMDD}-c{cluster_id_short}`

If no Slack channel exists yet, populate with the text `"No prod channel (yet)"`.

## Action Items Template (`customfield_10478` ADF)

RCA-41's default. **Keep the red instruction line; replace placeholders with actual action items**:

```markdown
[red text] After updating the table below, ensure the tickets are linked with the `relates to` type.

| Description           | Type                                       | Owner  | Ticket                              |
|-----------------------|--------------------------------------------|--------|-------------------------------------|
| <What is the AI about?> | **Investigate** or **Prevent** or **Mitigate** | @name | <jira-ticket> e.g: RED-999999      |
| <What is the AI about?> | **Investigate** or **Prevent** or **Mitigate** | @name | <jira-ticket> e.g: RED-999999      |
| <What is the AI about?> | **Investigate** or **Prevent** or **Mitigate** | @name | <jira-ticket> e.g: RED-999999      |
```

**Type values** — pick one per row:
- **Investigate** — research / analysis
- **Prevent** — preventative engineering change
- **Mitigate** — short-term mitigation

When the skill has Jira PDFs of related bugs, it can pre-fill some action items derived from bug content (e.g., keyword "cpu" → "Investigate CPU utilization patterns").

## Linking Related Tickets

Per Step 4 of the procedure:

```
mcp__claude_ai_Atlassian__createIssueLink:
  cloudId: 06f73ca7-8f2c-4392-b40a-08288e9d0ba3
  inwardIssueKey: RCA-NNNN       // the new RCA
  outwardIssueKey: RED-NNNNNN     // related bug Jira
  typeName: "Relates"             // id 10003 — "relates to" both directions
```

Link **every** related ticket — those created during incident resolution OR afterward. Include external URLs (files, logs, procedures, Jira tickets) in the description / Slack field as relevant.

## Multi-Cluster Considerations

When an incident spans multiple clusters (typical for Azure ACRE incidents):

- `customfield_10516` (Cluster ID): all cluster names as separate labels
- Description Timeline references each cluster by name in each row
- Description Summary enumerates clusters and regions
- Distinguish resolution method per cluster in Timeline rows ("Manual DMC restart" vs "Automatic VM freeze event")
- Title can use ClusterID instead of customer name if multi-customer

## Azure-Specific Rule

Per the Support team Jira creation doc: **for Azure (ACRE or AMR) RCAs, you always need a RED or MOD Bug Jira associated**. The skill should:

1. Check the input Jira PDFs — if all are RCA Jiras and no Bug exists, flag this and refuse to create
2. If a RED/MOD Bug is among the inputs, link it via `Relates`

## Worked Example — `createJiraIssue` Payload

For an incident with:
- Customer: Azure
- Date: 10/24/2025
- Clusters: `prod110-europe-hdc-europe-cp102-titan2.northeurope`, `rediscluster-ktcsproda11.eastus2`
- Affected components: DMC, Azure integration
- Product: Redis Software
- Zendesk tickets: 146983, 146173
- Related bugs: RED-172012, RED-172734

```json
{
  "fields": {
    "project":     { "key": "RCA" },
    "issuetype":   { "id": "10590" },
    "summary":     "Azure - RCA 10/24/2025",
    "description": "**Summary:** DMC high-CPU utilization incident affecting 2 Azure clusters across 2 regions, leading to CPU exhaustion on ACRE nodes. One cluster resolved via manual DMC restart; the other via automatic VM freeze event. Initial analysis indicates potential correlation with audit logging configuration issues and BDB state machine updates. On-call engineers notified via #prod_incident Slack channel.\n\n---\n\n| **Date and Time _(UTC)_** | **Activity** |\n| --- | --- |\n| Oct-01-2025, 21:22 | DMC high CPU started on rediscluster-ktcsproda11.eastus2 |\n| Oct-03-2025, 04:26 | Manual DMC restart - Issue resolved |\n| Oct-08-2025, 01:03 | High CPU on csie-fnp-linx01-redis03.northeurope |\n| Oct-08-2025, 01:05 | Automatic VM freeze - Issue resolved |\n",
    "labels": ["Azure", "ACRE", "dmc", "high_cpu", "Azure-Integration"],
    "customfield_10469": "2025-10-01T21:22:00.000+0000",
    "customfield_10470": "2025-10-17T22:35:00.000+0000",
    "customfield_10475": "- [#146983](https://redislabs.zendesk.com/agent/tickets/146983)\n- [#146173](https://redislabs.zendesk.com/agent/tickets/146173)",
    "customfield_10476": "[#prod_incident-20251024-azure_titan2_zd146983](https://app.slack.com/)",
    "customfield_10490": "DMC high-CPU utilization with simultaneous BDB state machine updates and audit logging anomalies. Hypothesis: audit logging contention under load triggers state machine churn that the DMC cannot keep up with.",
    "customfield_10467": "- <Add your final RCA and Conclusions here>\n- <Add your final RCA and Conclusions here>\n- <Add your final RCA and Conclusions here>\n- <Add your final RCA and Conclusions here>\n- <Add your final RCA and Conclusions here>",
    "customfield_10478": "After updating the table below, ensure the tickets are linked with the `relates to` type.\n\n| Description | Type | Owner | Ticket |\n|---|---|---|---|\n| Investigate CPU utilization patterns | **Investigate** | @name | <jira-ticket> e.g: RED-999999 |\n| Review audit logging configuration | **Investigate** | @name | <jira-ticket> e.g: RED-999999 |\n| Implement automatic recovery for high-CPU events | **Prevent** | @name | <jira-ticket> e.g: RED-999999 |",
    "customfield_10495": [{ "id": "11147" }, { "id": "11154" }],
    "customfield_10516": ["prod110-europe-hdc-europe-cp102-titan2.northeurope", "rediscluster-ktcsproda11.eastus2"],
    "customfield_10520": ["Azure"],
    "customfield_10519": { "id": "11123" },
    "customfield_10619": { "id": "23171" }
  }
}
```

After `createJiraIssue` returns the new key (e.g., `RCA-NNN`):
1. `createIssueLink` × N for each related bug (RED-172012, RED-172734) with type `Relates`
2. Set Reporter to current user if not already
3. Set Contributors to incident participants (ask user for emails/account IDs)
4. Verify status is `Data Collection` (default)
5. Notify user: "RCA-NNN created. Transition to `Root Cause and Action Items` after data entry confirmed complete."

## Slack Notification

Per the R&D RCA process doc: changing RCA ticket status automatically posts to Slack [#root-cause-analysis](https://redis.slack.com/archives/C07U49XETM1). The skill doesn't need to post separately.

## Anti-patterns

- **Don't write the Final Root Cause** — Engineering owns it. Use the 5-bullet placeholder.
- **Don't put structured content (root cause, action items, timeline) in the description body alone** — use the dedicated custom fields. Description is for narrative summary + timeline table only.
- **Don't auto-transition past `Root Cause and Action Items`.** Engineering / Leadership control later states.
- **Don't use `Support RCA` (16251)**. RCA-41 uses `RCA` (10590). Stay consistent.
- **Don't fabricate timestamps.** If PDFs don't have specific times, use clear placeholders.
- **Don't skip Azure prerequisite check.** If an Azure RCA is being created and no RED/MOD bug is in the input/related links, flag this and ask.
- **Don't take over Reporter / Contributors from the template defaults.** Set Reporter to yourself (current user) and Contributors to the actual incident participants.
