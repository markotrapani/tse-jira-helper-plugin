# RED-188607 — Calling --update-db-config-modules step for A-A upgrade is broken in 8.0.10

> **Link:** https://redislabs.atlassian.net/browse/RED-188607
> **Issue Type:** Bug (id 10004)
> **Project:** RED (Redislabs)
> **Domain:** Active-Active / CRDB / upgrade / module configuration / cnm_http payload mismatch
> **When to use this anchor:** **Upgrade-path Bug** affecting Active-Active (CRDB). Use when a documented post-upgrade admin command fails with sequential validation errors and the TSE has reproduced it locally + identified an API-level workaround. Good template for "the official upgrade procedure is broken at step N" bugs with raw CLI + debug-log evidence.
> **Added:** 2026-05-12

## Header fields used

| Field            | Value                                                       |
|------------------|-------------------------------------------------------------|
| Project          | Redislabs (RED)                                             |
| Type             | Bug                                                         |
| Priority         | Medium                                                      |
| Severity         | `1 - High`                                                  |
| Status           | Closed (Resolution: `Done`)                                 |
| Components       | None                                                        |
| Affects versions | `8.0.10_Jan_Cross`                                          |
| Labels           | `Support`, `e2e_ta_coverage`         ← 2 labels             |
| Sprint           | Sprint 203 - Cluster Interface                              |
| Story Points     | 2                                                           |
| Parent / Epic    | Cluster Production Bugs - Q1 2026 (RED-181944)              |

## Custom fields populated

| fieldId               | Name                   | Value                                                       |
|-----------------------|------------------------|-------------------------------------------------------------|
| `customfield_10180`   | Severity               | `1 - High`                                                  |
| `customfield_10181`   | Component              | `CRDB` (routes to CRDB / A-A team)                          |
| `customfield_10025`   | Environment/s          | `[Production]`                                              |
| `customfield_10026`   | Product/s              | `[RS (Redis Software)]`                                     |
| `customfield_10056`   | Reported Version/Build | `8.0.10-76`                                                 |
| `customfield_10595`   | Affected Organizations | `[Progressive Casualty Insurance Company, SYCOD, T-Mobile]` (3 orgs) |
| `customfield_10027`   | Seen by Customer/s     | `Sycod, T-Mobile, Progressive Casualty Insurance Company`   |
| `customfield_10036`   | Zendesk ID/s           | `156645, 157927, 158065` (3 IDs aggregated)                 |
| `customfield_10585`   | Impact Score           | `75`                                                        |
| `customfield_10369`   | Downtime               | `No`                                                        |
| `customfield_10371`   | Data loss              | `No`                                                        |
| `customfield_10063`   | RCA                    | 6-section template, all sections blank placeholders         |

## Description body structure

**Flat narrative** (no H2 headers). Chronological field investigation: customer report → first command + error → hypothesis-driven patch → second command + error → log evidence → reproduction artifacts.

```markdown
Customer {Org} reported an issue through Zendesk ticket {ZD-ID}.

When the cluster is upgraded from {old-ver} to {new-ver}, {documented procedure with link to manual}
fails with the following error:

    <code block: CLI invocation + task status transitions + error message>

In the assumption that it expects {field-X}, patched it with the following command:

    <code block: curl PATCH workaround>

This helped move this issue forward. However, the same command failed with the next one about
{next error}:

    <code block: CLI rerun + new error>

{One-sentence interpretation of the mismatch}:

    <code block: ~15 lines of cnm_http DEBUG log showing the bad payload>

Note: {scope clarification — e.g. "applies only to clusters upgraded from 7.22; also reproduces
on fresh 8.0.10 CRDBs"}.

DevOps reported a similar issue in the cloud {RED-XXXXXX link}

How to work around this problem?
Would it affect all the upgrades to 8.0.10?

Reproduction steps: s3://gt-logs/zendesk-tickets/ZD-{id}/reproduction.txt

Support packages from the local lab:
s3://gt-logs/zendesk-tickets/ZD-{id}/{pre-upgrade}.tar.gz
s3://gt-logs/zendesk-tickets/ZD-{id}/{post-upgrade}.tar.gz
```

### Section observations

- **No H2 headers.** Flat chronological narrative with embedded code blocks (CLI invocations, curl, ~15-line debug log excerpt).
- **TSE hypothesis inline**: "In the assumption that it expects tls_mode property in db_config, patched it with..." — shows reasoning, not just symptoms.
- **Customer ask at the end** is literal questions, not a "Customer Expectations: Fix" line.
- **Cross-Jira reference inline** establishes prior art ("DevOps reported a similar issue in the cloud {RED-link}").
- **Two support packages bracketing the upgrade** (pre + post) for diffing.
- **Scope-narrowing note**: "only the cluster upgraded from 7.22 to 8.0.10. If I create a new CRDB in 8.0.10, same issue" — important triage hint.

## Notes / nuances

- **Multi-org aggregation early**: 3 ZDs from 3 orgs (Sycod, T-Mobile, Progressive) bundled under one Jira. Smaller-scale version of RED-127842's pattern.
- **Labels = `Support, e2e_ta_coverage`** — the `e2e_ta_coverage` label flags this for QA test-automation backlog. For TSE-filed bugs, use `Support` or `CS` + a domain tag; add `e2e_ta_coverage` if a test-gap is suspected.
- **No `Azure-Integration`** — on-prem RS customers.
- **Component = CRDB** routes by ownership (the broken `--update-db-config-modules` flag is a CRDB feature) even though the error surfaces through `cnm_http`. Same lesson as RED-152733: pick component by ownership, not where the symptom shows up.
- **Resolution = `Done`** (code fix shipped to master + cherry-picked) — different from RED-152733's `RCA Provided`. Use `Done` only when engineering ships actual code change.
- **Workaround lives in a comment, not in `customfield_10374`** — Sonya's curl PATCH workaround posted as a comment post-filing. Pattern: when workaround is discovered during engineering triage, it tends to land as a comment. For TSE-filed bugs where a workaround is already known at file time, populate `customfield_10374` directly.
- **Sprint set post-filing by engineering** — TSE should leave Sprint blank at file time.
- **RCA template seeded but unfilled at close** — consistent with the broader pattern; only Azure ACRE/AMR tickets reliably get section 0 populated.
- **Reproduction artifact pattern**: plain `.txt` reproduction script + tarballs at `s3://gt-logs/zendesk-tickets/ZD-{id}/...`. Reuse this S3 path convention.
