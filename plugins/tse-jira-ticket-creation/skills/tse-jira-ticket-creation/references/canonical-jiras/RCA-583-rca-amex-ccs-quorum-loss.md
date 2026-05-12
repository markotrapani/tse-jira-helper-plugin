# RCA-583 — American Express - RCA 04/02/2026

> **Link:** https://redislabs.atlassian.net/browse/RCA-583
> **Issue Type:** RCA (id 10590)
> **Project:** RCA (Root Cause Analysis)
> **Domain:** CCS quorum loss / topology change overload / IP migration / node additions+removals / cluster recovery
> **When to use this anchor:** TSE-filed RCA where a major incident involves complex topology changes, multi-component cluster behavior, and engineering investigation. This is the **canonical real-world RCA shape** — strong reference for any RCA workflow.
> **Added:** 2026-05-12

## Header fields used

| Field          | Value                                                        |
|----------------|--------------------------------------------------------------|
| Project        | Root Cause Analysis (RCA, id 10245)                          |
| Type           | RCA (id 10590) — NOT Support RCA                             |
| Priority       | Medium (default)                                             |
| Reporter       | TSE who initiated (here: Marko Trapani)                      |
| Assignee       | Engineer who led investigation (here: Vladislav Morozov)     |
| Labels         | `Escalations_RCA`, `rca_RTTI_automation`, `rca_r&d`   ← 3 labels |
| Components     | None                                                         |
| Affects versions| None                                                        |
| Fix versions   | None                                                         |
| Status         | Final Review (initial state: Data Collection)                |

## Custom fields populated

| fieldId               | Name                                | Value                                                     |
|-----------------------|-------------------------------------|-----------------------------------------------------------|
| `customfield_10469`   | Start time (UTC)                    | `01/Apr/26 9:45 PM`                                       |
| `customfield_10470`   | End time (UTC)                      | `02/Apr/26 8:56 AM`                                       |
| `customfield_10475`   | Zendesk                             | List of Zendesk IDs with notes (primary, background)      |
| `customfield_10476`   | Slack                               | Channel ref OR "No prod channel" note                     |
| `customfield_10490`   | Initial Root Cause                  | Multi-paragraph narrative (the bulk of TSE's writeup)     |
| `customfield_10467`   | Final Root Cause & Conclusions      | Engineering-filled multi-paragraph after investigation    |
| `customfield_10478`   | Action item(s)                      | Table: Description / Owner / Ticket (3 rows default)      |
| `customfield_10472`   | Contributors                        | List of users involved (here: Prakash Selvaraj)           |
| `customfield_10519`   | Product                             | `Redis Software`                                          |
| `customfield_10619`   | Is Customer RCA needed?             | `Yes`                                                     |
| `customfield_10520`   | Account name                        | `Amex`                                                    |
| `customfield_10495`   | Affected component                  | (not populated here — left to engineering)                |
| `customfield_10516`   | Cluster ID                          | (mentioned in description body, not in field)             |
| `customfield_10487`   | Timestamp of TIMELINE               | `02/Apr/26 11:52 PM`                                      |
| `customfield_10526`   | Delivery of Timeline (KPI)          | `14.9` hours                                              |
| `customfield_10488`   | Timestamp of ROOT CAUSE and ACTION ITEMS | `19/Apr/26 7:17 AM`                                  |
| `customfield_10529`   | Delivery of Root Cause and Action Items | `391.4` hours                                         |
| `customfield_10492`   | Timestamp of RCA APPROVAL by R&D    | `19/Apr/26 7:17 AM`                                       |

## RCA-specific structural rules (verified against RCA-583)

1. **Title format**: `<Customer> - RCA <mm/dd/yyyy>` confirmed
2. **Initial Root Cause** (`customfield_10490`) is **substantial** — usually 4-6 paragraphs covering the incident narrative, contributing factors, log evidence cross-references. TSE writes this from incident timeline + Zendesk + initial Jira investigation.
3. **Description body** has its own structure separate from the Initial Root Cause field:
   - `## Incident Summary` (single H2 — multi-paragraph)
   - `## Timeline` (single H2 — a Date/Time + Activity table)
4. **Final Root Cause & Conclusions** (`customfield_10467`) is **engineering-filled later** — TSE leaves as placeholder bullets `<Add your final RCA and Conclusions here>`.
5. **Action items table** (`customfield_10478`) — default has 3 empty rows with "@name" + `<jira-ticket>` placeholders. Engineering fills in.
6. **Labels** are RCA-specific tags (`Escalations_RCA`, `rca_RTTI_automation`, `rca_r&d`), NOT `CS` / `Support` like Bug tickets.

## Description body structure (this RCA)

```markdown
## Incident Summary

{Opening paragraph: full quorum loss / outage on customer cluster, RS version, cluster size at time of incident.}

On {date}, the customer performed an infrastructure migration as part of their {context}:

1. {numbered action 1}
2. {numbered action 2}

{Causal paragraph: what triggered the incident — sequence of events leading to the failure state.}

{Recovery paragraph: who did what, when, how — including specific scripts/procedures used (BGSAVE, CCS RDB restore, etc.) and any data loss assessment.}

## Timeline

| Date and Time (UTC) | Activity |
|---|---|
| YYYY-MM-DD | {Initial ticket open / known prior bug context} |
| YYYY-MM-DD | {Each major operation: upgrade, migration, customer action} |
| YYYY-MM-DD, HH:MM | {Each incident-window event: rollback, restart, recovery step} |
```

## Initial Root Cause field structure (`customfield_10490`)

Multi-section narrative. Pattern observed in RCA-583:

```markdown
## Initial Root Cause

{Opening 1-2 paragraphs: what failed, why, sequence of events from a technical perspective. Reference
specific log signals, IDs, services, configurations. Specific timestamps.}

{Hypothesis paragraph: TSE's best guess at the deep cause, explicitly hedged ("a likely contributing
factor is..."), with reasoning.}

{What was attempted and why it didn't fully recover — restart sequences, supervisorctl operations, etc.}

## Contributing Factors

### 1. {Primary factor name} (PRIMARY)

{Paragraph explaining why this is the primary contributor. Reference cluster limits, R&D guidance, supporting evidence.}

Additional factors that may have contributed:
- {Bullet 1}
- {Bullet 2}

### 2. {Secondary factor} (CONTRIBUTING)

{Paragraph.}

### 3. {Tertiary factor} (CONTRIBUTING)

{Paragraph.}

### 4. {Background context factor} (BACKGROUND)

{Reference to prior known bug RED-NNNNNN with explanation of how it interacted.}

### 5. {Historical context factor} (CONTEXT)

{Reference to prior tickets that documented similar issues on the same cluster/customer.}

## Log Evidence

| Source | Key Finding |
|---|---|
| node:NN <log file> | {Specific behavior, timestamps, counts} |
| ... | ... |

## R&D to assess:

- {Open question 1 — what specifically TSE wants engineering to address}
- {Open question 2}

## Support package / Log data

- `s3://gt-logs/zendesk-tickets/ZD-NNNNNN/<file>.tar.gz`
- ... (every node, every relevant artifact)
```

## Action items table format (`customfield_10478`)

The ADF table has columns: Description, Owner, Ticket (NOT Type — the simpler 3-column variant). Initial state: 3 rows with placeholders `<What is the AI about?>`, `@name`, `<jira-ticket> e.g: RED-999999`.

Note: this Jira's table is simpler than the 4-column (Description / Type / Owner / Ticket) version we documented in `rca-template.md`. Both exist in practice — Engineering / Leadership chooses based on incident complexity.

## Notes / nuances

- **Engineering-driven RCA**: the bulk of "Initial Root Cause" was likely drafted by the TSE then expanded by the engineer (Vladislav Morozov). The TSE provides scaffolding + raw data; engineer adds technical depth.
- **Comments thread is extensive** — for a real RCA, expect 30+ comments showing investigation iterations (TSE → engineer back-and-forth, R&D involvement requests, automation alerts about RTTI breach, customer follow-up questions).
- **RTTI breach alert** — `Automation for Jira` posts comments when RTTI > 6 hours. TSE shouldn't write these; they're auto-generated. Plan to clear them by transitioning to "Root Cause and Action Items" within 6h of resolution.
- **Multiple related Jiras linked** via `Relates` — both bugs already known to the cluster (RED-111465, RED-174050, RED-173195) and ones discovered during investigation. The skill should add these as the TSE identifies them, not all at once on creation.
- **Customer name `Amex`** in `Account name` field, not full "American Express". Use the customer's short tag.
- **Slack channel "For Redis Software – No prod channel"** is a valid value when no incident-specific channel exists. Don't fabricate one.
- **No `Affected component` set** — engineering can fill later via multi-checkbox.
- **Initial state is Data Collection**, transitions to "Root Cause and Action Items" once TSE finishes data entry, then engineering moves to Final Review.
