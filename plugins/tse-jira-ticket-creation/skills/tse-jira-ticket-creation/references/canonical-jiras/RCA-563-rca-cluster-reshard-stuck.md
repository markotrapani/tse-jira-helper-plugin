# RCA-563 — #prod__2026-03-24_mc1716-autumn_reshard-stuck

> **Link:** https://redislabs.atlassian.net/browse/RCA-563
> **Issue Type:** RCA (id 10590)
> **Project:** RCA (Root Cause Analysis)
> **Domain:** Redis Cloud / CRDB CRDT assertion / scaling manager stuck / reshard / active-active / JSON heavy workload / CPU pressure
> **When to use this anchor:** **Cluster-incident-style** RCA — title takes the `#prod__<YYYY-MM-DD>_<cluster>-<account>_<short-symptom>` format (NOT `<Customer> - RCA <date>`). This is the canonical shape for Redis Cloud incidents triggered by automated incident detection (`Reporter: Incident`). Use as anchor for: short well-scoped Redis Cloud incidents with bridge call, milestone-style timeline, cluster ID in dedicated field, and minimal R&D-driven RCA writeup.
> **Added:** 2026-05-12

## Header fields used

| Field            | Value                                                          |
|------------------|----------------------------------------------------------------|
| Project          | Root Cause Analysis (RCA, id 10245)                            |
| Type             | RCA (id 10590) — NOT Support RCA                               |
| Priority         | Medium (default)                                               |
| Reporter         | **`Incident`** (automation user — not a TSE handle)            |
| Assignee         | Engineer assigned by R&D leadership (Eran Hadad)               |
| Labels           | `rca_FRRT_automation`, `rca_r&d`     ← 2 labels (no `Escalations_RCA`) |
| Components       | None                                                           |
| Affects versions | None                                                           |
| Fix versions     | None                                                           |
| Status           | Final Review                                                   |

## Custom fields populated

| fieldId               | Name                                | Value                                                     |
|-----------------------|-------------------------------------|-----------------------------------------------------------|
| `customfield_10469`   | Start time (UTC)                    | `24/Mar/26 9:06 PM`                                       |
| `customfield_10470`   | End time (UTC)                      | `24/Mar/26 10:15 PM` (≈1h 9min incident)                  |
| `customfield_10475`   | Zendesk                             | `https://redislabs.zendesk.com/agent/tickets/158673` (single URL, not Zendesk ID list) |
| `customfield_10476`   | Slack                               | `https://app.slack.com/client/T041Q0WL9/C0ANJ4Q5UVB` (full URL) |
| `customfield_10490`   | Initial Root Cause                  | 1-2 sentences (short — automation-style, not the long TSE writeup) |
| `customfield_10467`   | Final Root Cause & Conclusions      | Short paragraph + linked RED-NNNNNN follow-up bug         |
| `customfield_10478`   | Action item(s)                      | Bulleted list (NOT a table): each item ends with status `– IN PROGRESS` |
| `customfield_10472`   | Contributors                        | Comma-separated user names (Alex Valverde, Amol Gadgayya Swami, Aric Adiego, Eran Hadad, Jamaica Noriel, Joe Danford, Louis Scheffer) |
| `customfield_10516`   | Cluster ID                          | `mc1716`              ← **populated as a dedicated field** |
| `customfield_10520`   | Account name                        | `autumn`                                                  |
| —                     | Account ID                          | `2665284`                                                 |
| `customfield_10519`   | Product                             | `Redis Cloud`                                             |
| `customfield_10495`   | Affected component                  | `CRDB`         ← populated (vs RCA-583 where it's blank)  |
| `customfield_10487`   | Timestamp of TIMELINE               | `24/Mar/26 10:34 PM`                                      |
| `customfield_10526`   | Delivery of Timeline (KPI)          | `0.3` hours          ← very fast turnaround               |
| `customfield_10488`   | Timestamp of ROOT CAUSE and ACTION ITEMS | `30/Mar/26 1:05 PM`                                   |
| `customfield_10529`   | Delivery of Root Cause and Action Items | `134.5` hours                                          |
| `customfield_10492`   | Timestamp of RCA APPROVAL by R&D    | `30/Mar/26 1:05 PM`                                       |
| `customfield_10619`   | Is Customer RCA needed?             | (not shown — likely No for internal/automation-triggered) |

## Title format and Reporter — distinguishes from customer-RCA shape

| Aspect                | RCA-583 (customer-shape) | **RCA-563 (cluster-incident-shape)** |
|-----------------------|--------------------------|--------------------------------------|
| Title                 | `American Express - RCA 04/02/2026` | `#prod__2026-03-24_mc1716-autumn_reshard-stuck` |
| Reporter              | TSE (Marko Trapani)      | `Incident` (automation user)         |
| Labels                | `Escalations_RCA`, `rca_RTTI_automation`, `rca_r&d` | `rca_FRRT_automation`, `rca_r&d` |
| Issue links           | `Relates` to bugs        | `causes` CINC-NNNN + PRB-NN, plus `Relates` to bugs |
| Bridge link           | usually not in body      | Google Meet URL in `Bridge:` field of description |

## Issue links pattern

```
Problem/Incident:
  causes  CINC-1220 mc1716-autumn_reshard-stuck (Completed)
  causes  PRB-14    Redis Cloud database configuration ch... (Identifying Solution)
Relates:
  relates to  RED-191649 A/A - StuckSM after DB config changes... (Closed)
  relates to  RED-193919 [Quality RCA] Autumn - CRDT assertion... (To Do)
```

- **`causes` CINC-NNNN** — Cloud Incident ticket (the actual incident response Jira). RCA always traces back to a CINC.
- **`causes` PRB-NN** — Problem ticket (ITIL-style umbrella for repeat issue patterns).
- **`relates to` RED-NNNNNN** — bug tickets for engineering follow-up.
- **`relates to` RED-NNNNNN [Quality RCA]** — separate Quality-RCA ticket that engineering opens for deeper investigation.

## Description body structure (cluster-incident shape)

This is **single-section** (`## Summary`) with emoji-prefixed bullet labels and a date-stamped milestone timeline. Different from RCA-583 which uses `## Incident Summary` + `## Timeline` as separate H2s.

```markdown
## Summary

🏷 Incident name: <cluster>-<account>_<short-symptom>
👥 Customer(s): Account <ACCOUNT_ID> - <Account name>
📋 Status: Resolved
📄 Tickets: ZD-<zendesk-id>
☎️ Bridge: <google-meet-url>
💥 Customer Impact: <1-2 sentences describing observable customer-side impact>
📚 Incident Summary: <2-3 sentence narrative of what happened at a database/cluster level>
🕵️‍♂️ What happened (in detail): <multi-sentence technical narrative covering trigger event, cascading
failures, recovery steps. Reference specific shard numbers, code paths (e.g., hdt_effect.c:375), versions
(e.g., cluster version 80225). One paragraph.>
🔧 Mitigation: <multi-sentence: recovery actions taken, by whom, monitoring follow-up>
⏰ Timeline:
HH:MM:SS UTC – <event 1>
HH:MM:SS UTC – <event 2>
...
HH:MM:SS UTC – Milestone: Investigating
...
HH:MM:SS UTC – Milestone: Identified
...
HH:MM:SS UTC – Milestone: Pending Customer
...
HH:MM:SS UTC – Milestone: Resolved
```

### Section observations

- **Emoji-prefixed labels** are part of the canonical template:
  - 🏷 Incident name
  - 👥 Customer(s)
  - 📋 Status
  - 📄 Tickets
  - ☎️ Bridge
  - 💥 Customer Impact
  - 📚 Incident Summary
  - 🕵️‍♂️ What happened (in detail)
  - 🔧 Mitigation
  - ⏰ Timeline
- **Timeline format**: `HH:MM:SS UTC – <event>` (one line each, NOT a table). Includes named milestones (`Milestone: Investigating`, `Milestone: Identified`, `Milestone: Pending Customer`, `Milestone: Resolved`).
- **Account ID and Customer name BOTH shown** in 👥 Customer(s) line — `Account 2665284 - Autumn`.
- **Bridge URL** preserved (Google Meet) so post-incident reviewers can find the recording.
- **Specific code path / version references** in narrative: `CRDB CRDT module (hdt_effect.c:375)`, `cluster version 80225`. Even though this is an RCA (not a bug), the TSE/incident writeup preserves code-level detail.

## Initial Root Cause field (`customfield_10490`) — short form

In cluster-incident RCAs, this field is **1-2 sentences** (automation/incident-template style), NOT the multi-paragraph TSE writeup seen in customer-shape RCAs.

```
CRDB assertion failure in CRDT module (active-active code) triggered during reshard operation.
Customer's intensive JSON operations with large keys contributed to the initial CPU pressure
that prompted the reshard attempt.
```

The detailed narrative lives in the description body's `🕵️‍♂️ What happened (in detail):` line, not in this field.

## Final Root Cause field (`customfield_10467`) — engineer-filled, links to RED bug

```
HDT assertion failure in CRDT module triggered during reshard operation.
we can't say why it failed now, we have to investigate https://redislabs.atlassian.net/browse/RED-191649,
schedule for sprint 205.
```

- Short, engineering-voice.
- **Embeds the follow-up RED bug link** inline.
- May acknowledge "we can't say why it failed now" — incomplete final RCA is acceptable when engineering has triaged but not deep-investigated.

## Action items field (`customfield_10478`) — bullet list, NOT a table

For cluster-incident RCAs, this is rendered as bullets (not the 3-column table seen in customer-shape RCAs):

```
- JIRA ticket created to investigate CRDB assertion failure – IN PROGRESS
- R&D team engaged requesting additional diagnostics (JSON examples, debug objects) – IN PROGRESS (Eran Hadad from R&D)
```

Each bullet ends with a status suffix (`– IN PROGRESS`, `– COMPLETED`, etc.).

## Multi-customer awareness

Account-based: `Account 2665284 - Autumn` is one customer. For multi-customer incidents (shared infrastructure), the 👥 Customer(s) line can list multiple accounts. This RCA is single-customer.

## Notes / nuances

- **Reporter is the `Incident` user**, not a TSE handle. Indicates an automation-created RCA tied to a CINC ticket from PagerDuty/incident-response.
- **`rca_FRRT_automation` label** (not `rca_RTTI_automation` like RCA-583) — FRRT = Final RC Report Time, RTTI = different SLA metric. Automation chooses based on which KPI is in play.
- **`Delivery of Timeline = 0.3 hours`** — extraordinarily fast (within 20 minutes of incident close). Cluster-incident RCAs often have timeline auto-populated from CINC, hence the fast delivery.
- **`Delivery of Root Cause and Action Items = 134.5 hours`** — engineering's investigation took ~5.6 days. Normal for an issue requiring R&D deep-dive.
- **FRRT breach comment by `Automation for Jira` at 48 hours** — same pattern as RCA-583's RTTI breach. TSE/engineer should not write these.
- **Cluster ID (`mc1716`) populated as a dedicated `customfield_10516`** — distinguishes cluster-incident RCAs from customer-shape RCAs (where this field is often blank and the cluster ID only appears in description prose).
- **Account ID is a separate field** from Account name (`Account ID: 2665284` and `Account name: autumn`). Both populated.
- **`Affected component = CRDB`** populated by TSE/engineer at file time (not left to engineering as in RCA-583).
- **Two `causes` links** (CINC + PRB) are standard for Redis Cloud incident-triggered RCAs.
- **Compare to `RCA-583-rca-amex-ccs-quorum-loss.md`** for the customer-RCA shape — different title format, different reporter, different label set, table-based action items, multi-paragraph Initial RC.
