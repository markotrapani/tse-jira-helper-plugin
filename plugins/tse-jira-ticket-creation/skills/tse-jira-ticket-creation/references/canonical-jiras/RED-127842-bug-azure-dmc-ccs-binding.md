# RED-127842 — Node did not send completion update to CCS during SMBindEndpoint task

> **Link:** https://redislabs.atlassian.net/browse/RED-127842
> **Issue Type:** Bug (id 10004)
> **Project:** RED (Redislabs)
> **Domain:** Azure / ACRE / DMC / CCS / endpoint binding / race condition / multi-occurrence customer report
> **When to use this anchor:** **Azure-specific Bug** with race-condition root cause. Strong reference when an Azure customer reports a recurring issue across multiple Zendesk tickets and the bug spans an Epic (refactoring). Shows the **Azure-Integration label pattern** and the **multi-ZD aggregation** when one underlying bug surfaces in many tickets over time.
> **Added:** 2026-05-12

## Header fields used

| Field            | Value                                                                       |
|------------------|-----------------------------------------------------------------------------|
| Project          | Redislabs (RED)                                                             |
| Type             | Bug                                                                         |
| Priority         | Highest (escalated from Medium)                                             |
| Severity         | `1 - High`                                                                  |
| Status           | Closed                                                                      |
| Components       | None (set via `customfield_10181` Component instead → DMC)                  |
| Affects versions | `7.6 RCP preview`, `7.8.x - PubPreview_1`                                   |
| Labels           | `Azure-Integration`, `CS`, `CS-Support-PM-Followup`, `Support`, `azure_releasenotes`  ← 5 labels |
| Sprint           | Sprint 165 - DMC                                                            |
| Story Points     | 5                                                                           |
| Parent / Epic    | Refactoring of the DMC management operations and configuration updates (RED-112334) |

## Custom fields populated

| fieldId               | Name                   | Value                                                          |
|-----------------------|------------------------|----------------------------------------------------------------|
| `customfield_10180`   | Severity               | `1 - High`                                                     |
| `customfield_10181`   | Component              | `DMC` (single-select)                                          |
| `customfield_10025`   | Environment/s          | `[Production]`                                                 |
| `customfield_10026`   | Product/s              | `[RS (Redis Software)]`                                        |
| `customfield_10056`   | Reported Version/Build | `7.4.2-156`                                                    |
| `customfield_10595`   | Affected Organizations | `[Azure]`                                                      |
| `customfield_10027`   | Seen by Customer/s     | `Azure Engineering`                                            |
| `customfield_10036`   | Zendesk ID/s           | **`121011, 121074, 121079, 121248, 124442, 129828, 130654, 132249, 124589, 127278, 132310, 135857, 135951, 135782, 135813, 136347`** (16 IDs aggregated) |
| `customfield_10585`   | Impact Score           | `80`                                                           |
| `customfield_10115`   | Found By               | `Prod/Customer`                                                |
| `customfield_10371`   | Data loss              | `No`                                                           |
| `customfield_10373`   | Event Status           | `workaround implemented`                                       |
| `customfield_10374`   | Workaround             | "Try restarting the dmcproxy service on the node with a pending SM task. If that does not resolve the issue, manually complete the task via similar commands `ccs-cli hset bdb:1 _changestate:dmc:30 done` and `ccs-cli publish config-change:cnm_exec:master dmc:30@bdb:1`" |
| `customfield_10063`   | RCA                    | 6-section template with sections 1-4 filled in (post-resolution) — see below |
| —                     | Fixed in Build         | `7.8.0-43,7.6.0-100,7.12.0-1,7.11.0-1,7.4.6-223` (multi-version cherrypick) |

## RCA template (post-resolution example)

When a bug has been investigated and fixed, the RCA template gets filled in. This Jira's RCA field at close:

```
------------------------------
1. Bug Description:
See https://redislabs.atlassian.net/browse/RED-127842?focusedCommentId=1823252

2. Which components impacted by this bug?
DMC.

3. What was fixed?
Since we could not reproduce the issue, a theoretical fix was merged where the workers start right
after mgmt initializes its memory, making sure they're up before anything else happens in the mgmt's flow.
As mentioned, this is a theoretical fix, so based on its behavior we might leave it or revert it.

4. Reproduction steps?
N/A
------------------------------
```

Pattern observation: section 1 can link to a specific comment in the same Jira via `focusedCommentId`. Section 0 ("Incident short description") was not used in this older bug — but is now expected per Azure-specific Support guidance.

## Description body structure

This bug uses a **flatter narrative** style than RED-194253. Common for older / pre-template-standard bugs.

```markdown
## {Customer / Cluster}: {one-line symptom}

Azure experienced what appears to be another instance of {related-bug-link}. However, this time,
the issue was on a {context}. The initial symptoms were a prolonged running SM for rebinding endpoints:

    <log excerpt: indented code block showing the symptom>

DATABASES:
DB:ID NAME TYPE ...
db:1 db redis ... (the rladmin output showing the stuck state)

Investigating further, the completion message to CCS was never sent, although the dmcproxy seemed to apply the rebind successfully:

    <log excerpt>

CCS BDB:1 change states:

    <log/data excerpt>

Of possible interest, {customer} confirmed {context}, and node X indicated bootstrap activities in cluster_wd.log around the time of the SM:

    <log excerpt>

We resolved the issue by manually marking the state change as done via ccs-cli:

    <command excerpt>

With the issue now resolved, {customer} would like to understand the root cause and methods for avoiding it in the future.
```

### Section observations

- **No H2 section headers** in the description body — flat narrative with embedded log excerpts.
- **Cross-Jira references** at the top — "another instance of {RED-NNNNNN}" — establishes pattern.
- **Customer ask at the end** — "would like to understand the root cause and methods for avoiding it" — frames the request.
- **Log excerpts are indented/fenced** code blocks throughout.
- **The customer's product/cluster context** is embedded inline ("a 7.4 cluster", "Azure confirmed OS patching") rather than in fields.

## Multi-ZD aggregation pattern

This bug aggregates **16 separate Zendesk tickets** in `customfield_10036` because the same underlying bug surfaced repeatedly. As new occurrences came in, the TSE added the new ZD ID to the field rather than filing a new Jira each time.

When the skill encounters a customer mentioning a recurring issue across multiple tickets, it should:

1. Search Jira for an existing bug with similar symptoms first (`searchJiraIssuesUsingJql`)
2. If found, add the new ZD ID to that bug's `customfield_10036` and add a comment with the new occurrence details
3. Only file a new Jira if no existing match

## Notes / nuances

- **5 labels** including `Azure-Integration`, `CS`, `CS-Support-PM-Followup`, `Support`, `azure_releasenotes`. More labels than RED-194253's 2 — but justified because:
  - `Azure-Integration` + `azure_releasenotes` = Azure-specific routing tags
  - `CS` + `Support` are the TSE-team tags (duplicative — pick one normally; this bug has both because it was reopened multiple times)
  - `CS-Support-PM-Followup` is a specific PM-tracking tag
  - **For TSE-filed new bugs**: stick to `CS` or `Support` + 1-2 domain tags. Add Azure-specific labels for Azure tickets.
- **Component=DMC** + **Affected Organizations=Azure** is the standard ACRE/AMR pattern.
- **Priority Highest, Severity 1 - High** — was escalated from Medium because the bug duplicated a critical Azure release blocker.
- **Workaround field has rich content** — short paragraph + inline code commands. ADF should support mixed paragraph + code-block content.
- **Event Status = workaround implemented** — sets the field when a WA is documented and applied.
- **Description ends with the customer ask, not a "Customer Expectations: Fix" line** — pattern matches RED-194253. The ask is conveyed by the closing sentence, not a separate prefix line.
- **Bug discovery via repeated Azure ZD tickets** — Azure submitted 16 separate Zendesk tickets over ~9 months for what turned out to be the same race condition. The skill should be alert for this pattern.
- **Engineering investigation in comments** — the Initial investigation by Vladislav Morozov is a comment (not the Initial Root Cause field), with detailed log analysis. Comments often carry as much investigation depth as the description body for Azure-recurring bugs.
