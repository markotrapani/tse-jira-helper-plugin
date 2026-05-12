# RDSC-4706 — AXIS - After one of the RAC instances of the Oracle database went down. This prevented Debezium from accessing the SCN files.

> **Link:** https://redislabs.atlassian.net/browse/RDSC-4706
> **Issue Type:** Bug (id 10004)
> **Project:** RDSC (Redis Data Integration)
> **Domain:** RDI / Debezium / Oracle RAC / source DB failover / SCN file access / CDC continuity / Oracle node-by-node maintenance
> **When to use this anchor:** TSE-filed Bug in **RDSC (Redis Data Integration)** project for a customer experiencing Debezium pipeline failure during Oracle RAC node maintenance. Strong reference for: (1) the **RDSC project field schema** (uses `Steps to Reproduce`, `Expected Result`, `Actual Result` as **dedicated custom fields**, not description sections); (2) bugs that **clone another customer's ticket** (`Cloners` link to RDSC-3919) when the same defect affects multiple customers; (3) RDI bugs with attached container logs and `application.properties` configuration files.
> **Added:** 2026-05-12

## Header fields used

| Field            | Value                                                          |
|------------------|----------------------------------------------------------------|
| Project          | Redis Data Integration (RDSC)                                  |
| Type             | Bug                                                            |
| Priority         | High                                                           |
| Status           | Closed (resolution: `Done`)                                    |
| Reporter         | TSE who filed (Jorge Ramos Sánchez)                            |
| Assignee         | Engineer (Ilian Iliev)                                         |
| Labels           | `Support-Attention`, `rca_related`     ← 2 labels (RDSC-specific values) |
| Components       | None                                                           |
| Affects versions | None                                                           |
| Fix versions     | None                                                           |
| Parent           | `Supporting Oracle RAC work loads` (RDSC-4015) ← Epic          |
| Sprint           | Sprint 201-206 - RDSC (multi-sprint)                           |
| Story Points     | `10`                                                            |

## RDSC-specific schema — dedicated reproduction fields

Unlike RED/MOD which put reproduction content **inside the description body**, RDSC uses dedicated custom fields:

| fieldId (TBD)        | Name                   | Value (verbatim from PDF)                                   |
|----------------------|------------------------|-------------------------------------------------------------|
| —                    | Steps to Reproduce     | Numbered list (5 steps) as a **field**, not description     |
| —                    | Expected Result        | "Debezium was expected to be able to continue ingestion uninterrupted." |
| —                    | Actual Result          | Multi-line: "Debezium was unable to locate the required SCN files... The second Oracle instance had to be brought back online..." |
| —                    | Component              | `RDI` (single value, free-text field on this project — distinct from the multi-select Components row above) |
| `customfield_10025`  | Environment/s          | `Production`                                                |
| `customfield_10595`  | Affected Organizations | `Axis Bank Ltd, ICICI Bank Ltd` (MULTIPLE customers in one ticket) |
| `customfield_10585`  | Impact Score           | `69`                                                         |
| `customfield_10036`  | Zendesk ID/s           | `141052, 142237, 153651` (comma-separated, 3 IDs)            |
| —                    | Story Points           | `10` (estimating work for the engineer)                      |

## RDSC-specific observations

- **`Steps to Reproduce`, `Expected Result`, `Actual Result` are DEDICATED FIELDS** — not H2 sections inside the description. The body itself becomes a narrative / customer Q&A transcript instead.
- **`Component` is a single-value field** (`RDI`) — different from MOD multi-select Components and from RED's `customfield_10181` single-select that routes to Cluster/CM/etc.
- **No `Severity` field** shown on RDSC bugs.
- **No `Found By` / `Issue source` / `Seen by Customer/s` fields** shown.
- **No 6-section `RCA` template field** shown — RDSC doesn't use the same RCA scaffold as RED/MOD.
- **`Affected Organizations` can be multi-valued** (`Axis Bank Ltd, ICICI Bank Ltd`) — RDI bugs often span customers because the same Oracle/RDI defect surfaces at multiple banks.
- **Attachments** are typically RDI-specific: `container.log.txt`, `application.properties` (the Debezium config), customer-provided shell command transcripts.
- **`Story Points`** appears on RDSC bugs (estimating engineering effort) — uncommon on RED bugs at file time.
- **Sprint listing all 6 sprints** (Sprint 201-206) indicates the bug churned across multiple sprints before fix — typical of long-running RDI feature work tied to a parent Epic.

## Issue links pattern (Cloners)

```
Cloners:
  clones  RDSC-3919  ICICI attempted to bring down one of ... (Closed)
```

- **`clones`** (not `relates to`) — when the same RDI defect affects multiple customers, TSEs clone the original ticket. The cloned ticket retains the original Steps to Reproduce / Expected / Actual fields and gets a new customer-specific narrative.
- This is the **RDSC multi-customer pattern**: rather than adding a customer to one Jira's `Affected Organizations`, the team prefers separate cloned tickets per customer because the investigation pipeline (logs, Pacemaker config, RAC topology) differs per customer.

## Description body structure (narrative + Q&A transcript)

```markdown
Creating a new ticket for <Customer>. Let's share the Story from the other Jira.

Hello Team, we have a similar case that was previously raised by <prior-TSE> with <Customer> on ticket
<ZD-ID>. Here is some information:

> <Indented quote block: customer's verbatim incident description — what happened, what was affected,
> what they want to understand.>

Q1. <Question 1 from TSE>
A: <Customer answer>

Q2. <Question 2>
A: <Customer answer>

Q3. <Question 3>
A: <Customer answer>

Q4. <Question 4>
A: <Customer answer>

A little bit more information from the customer, after we asked for the commands they used to stop the DB.

> <Indented quote: customer's clarification paragraph>

How do they reboot the Nodes?

    <code block: customer-provided shell commands per node>

And additional information

> 1. Can you confirm if this procedure involves a forceful stop...
> Forceful shutdown
> Yes, the procedure involved a forceful shutdown...
>
> 1. From the example above, it looks like it is immediately brought back up...
> Startup timing after shutdown
> The node was not brought up immediately...

Detailed failover timeline:-
Node 1
- Shutdown: YYYY-MM-DD HH:MM:SS
- Startup: YYYY-MM-DD HH:MM:SS

Node 2
- Shutdown: YYYY-MM-DD HH:MM:SS
- Startup: YYYY-MM-DD HH:MM:SS

Internal test from R&D
> Overview:
> <R&D engineer's test methodology + version matrix tested>
>
> Test steps:
> 1. <numbered>
> 2. <numbered>
>
> Results and observations:
> 1. <observation>
> 2. <observation>
>
> Next steps:
> - <action>
> - <action>

<Related ticket link>:
https://redislabs.atlassian.net/browse/<RDSC-NNNN>?focusedCommentId=NNNN
```

### Section observations

- **No H2 headers** — flat narrative with bolded inline labels (`Q1.`, `Detailed failover timeline:-`, `Internal test from R&D`, etc.).
- **Customer Q&A transcript style** — the body literally captures the support email/ticket back-and-forth verbatim (with TSE's questions and customer's answers).
- **Customer-provided shell commands** are preserved in a fenced/indented code block — even when long (20+ lines of crsctl operations).
- **R&D's internal test report is embedded** in the body as a separate labeled section (`Internal test from R&D`) with its own Overview / Test steps / Results / Next steps subsections — RDI engineering often documents their reproduction attempts inline.
- **Detailed failover timeline** uses bulleted Shutdown/Startup pairs per node, NOT a table — RDSC pattern.
- **Related ticket link** at the end with a `focusedCommentId` deep-link — points to the specific comment in the cloned ticket where R&D's earlier analysis lives.

## Attachments pattern (RDSC-typical)

- `container.log.txt` — Debezium container stdout/stderr
- `application.properties` — Debezium connector configuration (source DB host, RAC nodes, schema, table includes, etc.)

These two are the **standard RDI bug pair**. Always preserve them — engineering needs both to reproduce.

## Notes / nuances

- **`Support-Attention` label** (vs `Support` on RED/MOD) — RDSC-specific label indicating active TSE engagement. May be combined with `rca_related` when the bug is in scope for an RCA.
- **Multi-customer `Affected Organizations`** allowed AND `Cloners` link to original ticket — two separate ways the multi-customer impact is tracked. Use both.
- **`Component: RDI`** (free-text-ish field, single value) — RDSC routes by sub-component differently than RED. Confirm allowed values before filing.
- **Parent / Epic Link to a "Supporting <vendor product>" Epic** (here: `Supporting Oracle RAC work loads`, RDSC-4015) — RDSC bugs are typically filed under a vendor/feature Epic. TSE should identify the right Epic before filing.
- **Body preserves customer's verbatim email/ticket text** in indented quote blocks — RDSC TSE workflow is more "transcript-driven" than RED (which curates into Steps/Expected/Actual structure).
- **Customer's exact shell commands preserved** with original formatting (including IP addresses) — operations team needs these for incident analysis. Don't paraphrase.
- **Timestamps include timezone** (IST in this case) — RDI bugs often involve APAC customers, so timezone preservation matters.
- **No `Severity` rating** — RDI bugs use `Priority` only.
- **No customer-name-prefix in description first line** — but title DOES start with customer name (`AXIS - After one of the RAC instances...`). RDSC title convention differs from RED/MOD.
