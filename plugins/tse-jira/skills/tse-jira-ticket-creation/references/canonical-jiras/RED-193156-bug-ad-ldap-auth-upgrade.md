# RED-193156 — AD/LDAP authentication fails on Cluster Manager UI after upgrade to 8.0.16-33

> **Link:** https://redislabs.atlassian.net/browse/RED-193156
> **Issue Type:** Bug (id 10004)
> **Project:** RED (Redislabs)
> **Domain:** LDAP / Active Directory / Cluster Manager UI / TLS client cert / regression / release-notes-worthy
> **When to use this anchor:** **Post-upgrade regression Bug** with broad blast radius — same bug surfaced at 4+ customers within days. Use when a recently-released minor introduces a regression that blocks core admin functionality (UI login) and the fix path involves both a workaround and a release-notes known-issue entry. Shows the **release-notes + DOC ticket split** pattern, the **"this is already fixed on master"** discovery, and the **`urgent` + `release_notes` label combination**.
> **Added:** 2026-05-12

## Header fields used

| Field            | Value                                                       |
|------------------|-------------------------------------------------------------|
| Project          | Redislabs (RED)                                             |
| Type             | Bug                                                         |
| Priority         | High (bumped from default)                                  |
| Severity         | `1 - High`                                                  |
| Status           | Closed (Resolution: `Done`)                                 |
| Components       | None                                                        |
| Affects versions | None (left blank)                                           |
| Labels           | `release_notes`, `urgent`         ← 2 labels                |
| Sprint           | Sprint 206 - Cluster Interface                              |
| Story Points     | 1                                                           |
| Parent / Epic    | Cluster Production Bugs - Q1 2026 (RED-181944)              |

### Issue links

| Link type           | Target              | Notes                                                  |
|---------------------|---------------------|--------------------------------------------------------|
| is cloned by        | RED-193420, RED-193421 | Cherry-picks to 8.0.18 and 8.0.16                   |
| duplicates          | RED-192533          | Upstream master fix                                    |
| is duplicated by    | RED-194263          | Later customer-reported duplicate                      |
| split to            | DOC-6482            | "Add known issue and workaround" to release notes      |

## Custom fields populated

| fieldId               | Name                   | Value                                                       |
|-----------------------|------------------------|-------------------------------------------------------------|
| `customfield_10180`   | Severity               | `1 - High`                                                  |
| `customfield_10181`   | Component              | `Core Platform`                                             |
| `customfield_10025`   | Environment/s          | `[Development]`  ← **not** Production (see Notes)           |
| `customfield_10026`   | Product/s              | `[RS (Redis Software)]`                                     |
| `customfield_10595`   | Affected Organizations | `[Paychex]`                                                 |
| `customfield_10027`   | Seen by Customer/s     | `T-Mobile`                                                  |
| `customfield_10036`   | Zendesk ID/s           | `159837` (referenced in body)                               |
| `customfield_10585`   | Impact Score           | `109`                                                       |
| —                     | Added to Release Notes | `Yes`                                                       |
| `customfield_10063`   | RCA                    | 6-section template, all blank placeholders                  |

## Description body structure

**Hybrid style**: opens with a flat problem statement, then **bold `**Label**:` block** for environment/topology, then code blocks for config + logs, then closing analysis. No H2 headers.

```markdown
{Version} suppose to fix {feature} but now we have {N} tickets with {symptom} after upgrading to
{version}, it seems like there is another issue and the workaround from {prior-RED-link} is not working

**Product**: Redis Software (RS)
**Previous version**: {ver}
**Current version**: {ver}
**OS**: {os}
**Topology**: {topology}
**Clusters**:
- {cluster1.fqdn}
- {cluster2.fqdn}
**Upgrade method**: {tool + command}, on {date}.

Issue:

After the upgrade from {old} → {new}, {symptom-description}.

Users previously {prior-working-state} can no longer {failing-action}.

The same {credentials/config} work on other clusters still running pre-{cutoff-version} versions.

{Prior-functional-state confirmation. No-manual-changes confirmation. Health-check confirmation}.

LDAP configuration (from both clusters):

    <code block: ~10 lines of config key:value, sensitive values marked "(redacted in ticket)">

Logs (example from {node}/{logfile}):

    <code block: 2-3 raw WARN/ERROR log lines with timestamps + error message verbatim>

Observed behavior:

{One-paragraph plain-language summary of what the user sees}.

**Customer**: {Org}

{Customer-impact paragraph}.

Analysis / Notes:

{TSE hypothesis paragraph, explicitly hedged: "Failure appears related to..."}.

{Open-question paragraph: "Need to confirm whether this is a regression in {version} or an
upgrade path issue (config not migrated / new requirement not documented)"}.

**Zendesk ticket**: {zendesk-url}
```

### Section observations

- **No H2 headers**, but bold `**Label**:` prefix lines drive structure. Hybrid between RED-194253's full H2 layout and RED-127842's pure flat narrative.
- **Opening sentence references prior Jira** ("the workaround from {RED-link} is not working") — establishes this as a follow-on regression.
- **Explicit redaction marker**: `ca_cert: configured (redacted in ticket).` Use this pattern when omitting sensitive config values.
- **`Customer`: {Org}** appears inline in body — unusual; most canonical bugs keep customer name only in fields.
- **`Analysis / Notes:`** at the bottom = TSE's hypothesis + open questions block. Equivalent to "Root Cause" but explicitly hedged.

## Notes / nuances

- **Labels = `release_notes, urgent`** — both signal "needs visibility now". The `release_notes` label drives a **DOC ticket split** (see DOC-6482). When a bug is going into known-issues, label it `release_notes` and create a DOC sub-task.
- **No `CS` or `Support` label** — bug was filed by an R&D-adjacent reporter, not a TSE. For TSE-filed bugs, still add `Support` or `CS`.
- **Environment/s = `Development`** despite real production impact at Paychex — likely a field-misuse. For TSE-filed bugs where production customers are blocked, use `Production`.
- **`Affected Organizations` and `Seen by Customer/s` don't match** (`Paychex` vs `T-Mobile`) — unusual; normally these should align. Reflects that T-Mobile was added later as more customers hit the issue.
- **Customer count grew during the bug's life**: Paychex → UWM → Amex (22/Apr) → National Bank of Kuwait (23/Apr). This bug aggregates via comments rather than `customfield_10036` the way RED-127842 did. For TSE-filed upgrade-regression bugs where new affected customers keep arriving, **add each new ZD ID to `customfield_10036`** and add a brief comment summarizing each occurrence.
- **DOC-6482 split-to link** drives release-notes known-issue. Rachel Elledge's comment captures the exact known-issue text + workaround REST API call (PUT /v1/cluster/certificates). Pattern: link a `DOC-NNNN` ticket and seed it with proposed known-issue prose.
- **Workaround discovery via duplicate search**: Vladimir's comment links to RED-192533 (already-fixed-on-master upstream) and quotes the workaround. **For TSE-filed regression bugs, always search Jira for an existing master-fix first** — the cherry-pick may already exist.
- **Two clone tickets (CP to 8.0.18 + CP to 8.0.16)** — the cherry-pick workflow uses clones, not sub-tasks. Each CP gets its own Jira.
- **Resolution = `Done`** + `Added to Release Notes = Yes` — fix shipped in 8.0.18 (2026-04-20), documented in release notes.
- **No code snippet of the root-cause fix** in description — engineering work happened in linked RED-192533. This bug is the "downstream customer-visible regression report", not the engineering analysis.
- Cross-reference RED-127842 for the multi-customer aggregation pattern at larger scale (16 ZDs vs ~4 here).
