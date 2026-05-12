# MOD-14916 — Redisearch performance degradation after upgrading to 8.0.2-52

> **Link:** https://redislabs.atlassian.net/browse/MOD-14916
> **Issue Type:** Bug (id 10004)
> **Project:** MOD (RedisModules)
> **Domain:** Modules / RediSearch / performance regression / post-upgrade
> **When to use this anchor:** TSE-filed Bug in MOD project. Customer-reported performance degradation tied to a specific version upgrade. Includes structured before/after comparison, multiple test environments, attached screenshots/graphs, S3 support-package paths. Strong reference for performance / regression bugs across MOD.
> **Added:** 2026-05-12

## Header fields used

| Field            | Value                                                          |
|------------------|----------------------------------------------------------------|
| Project          | RedisModules (MOD)                                             |
| Type             | Bug                                                            |
| Priority         | Medium (default; not bumped)                                   |
| Severity         | `0 - Very High`                                                |
| Status           | Closed (this is post-resolution)                               |
| Components       | RedisAI, RediSearch                                            |
| Affects versions | Search OSS 8.2.6                                               |
| Labels           | `Support`                ← only 1 label                         |
| Parent / Epic    | RedsiSearch - Production issues (MOD-2120)                     |
| Sprint           | Sprint 207 - AI/ML (engineering set later)                     |

## Custom fields populated

| fieldId               | Name                   | Value                                                       |
|-----------------------|------------------------|-------------------------------------------------------------|
| `customfield_10180`   | Severity               | `0 - Very High`                                              |
| `customfield_10025`   | Environment/s          | `[Production]`                                               |
| `customfield_10056`   | Reported Version/Build | `8.0.2-52`                                                   |
| `customfield_10595`   | Affected Organizations | `[LTK]`                                                      |
| `customfield_10027`   | Seen by Customer/s     | `LTK`                                                        |
| `customfield_10036`   | Zendesk ID/s           | `158675`                                                     |
| `customfield_10585`   | Impact Score           | `95`                                                          |
| `customfield_10115`   | Found by               | `Customer/Customer success` (note: this is MOD-specific value — RED uses `Prod/Customer`) |
| `customfield_10063`   | RCA                    | 6-section template (sections all empty at file-time)         |
| —                     | BugScore               | `285` (MOD-only field; computed by team)                     |

## Notes on MOD vs RED differences

- **`Components` is MULTI-select in MOD** (`RedisAI, RediSearch`) — different from RED where Component is single-select.
- **`Found by`** in MOD uses `Customer/Customer success` (not `Prod/Customer` like RED). Confirm fieldId + allowed values for MOD before filing.
- **`BugScore`** appears on MOD tickets but I haven't seen it on RED. Likely a MOD-specific custom field for impact tracking.
- **Parent / Epic Link** is heavily used in MOD — file under an Epic when one exists for the affected module.

## Description body structure

```markdown
## {Customer}: {one-line symptom}

## Context

{Background narrative paragraph(s) — what happened leading up to this bug, version progression, hardware
choices, previous related Jiras with hyperlinked refs. This is unusual vs RED-194253 (which uses Summary first)
— in MOD performance bugs the Context section comes first because the upgrade history matters as much as
the bug itself.}

- {Bulleted historical points with Jira links}
- ...

## What we decided to do:

{Action narrative — what tests were run, what cluster/hardware combos, what load test setup.}

- {Bulleted decisions with detail}
- ...

## Verified / Observed

- {Bulleted observation list — what the data shows}
- ...

## Attachments / Support packages

{S3 paths to support packages, ft.info dumps, monitor outputs, RDB exports. Grafana dashboard links.}
- `s3://gt-logs/<ZD>/<phase>/<file>`
- ...
```

### Section sequence (this Jira's actual order)

1. `<Customer>: <symptom>` — single line summary statement (no H2)
2. `Context` — historical narrative with prior-Jira hyperlinks
3. `What we decided to do:` — action plan as bulleted list
4. Observed-data summary with screenshot/graph callouts (attachment-driven)
5. S3 paths for support packages, ft.info, monitor data, RDB exports

## Pattern: Comparing multiple versions / environments

Performance regression bugs often involve **comparing 3+ environments**:

- Previous "good" version (here: 7.4 database)
- Current "bad" version (here: 8.2 database after upgrade)
- An interim test environment to isolate variables (here: 8.2.1 on identical hardware)

Each gets:
- A cluster + DB ID
- Hardware spec (e.g., `c8g.16xlarge` ARM vs `c7i.16xlarge` Intel)
- A dedicated support package S3 path
- Grafana dashboard links

The description should clearly tag each.

## Notes / nuances

- **Heavy use of S3 paths** — every support package, ft.info dump, monitor output is referenced by S3 URL. The skill should preserve these as inline bullets, not collapse them.
- **Hyperlinked Jiras inline** in narrative paragraphs (e.g., "this issue: https://redislabs.atlassian.net/browse/MOD-14500") — markdown auto-links work.
- **Single label** (`Support`) is typical for MOD bugs. Don't sprawl.
- **Severity 0 (Very High) with Priority Medium** is normal — severity reflects customer impact (production performance degradation), priority is the PM-set default that gets bumped during triage.
- **No explicit Customer Impact / Steps to Reproduce / Expected / Actual sections** — this is a long-running investigation Jira where the narrative subsumes those. For initial-creation MOD perf bugs, the skill can either follow this narrative shape OR use the RED-194253 H2-sectioned shape. Lean toward narrative when the bug is fundamentally a "performance is worse after upgrade and we have data to show it" kind of report.
- **No `Workaround` section** in description — performance regressions typically don't have a clean workaround.
- **RCA template (6-section) populated even though this is MOD project** — universal pattern confirmed.
