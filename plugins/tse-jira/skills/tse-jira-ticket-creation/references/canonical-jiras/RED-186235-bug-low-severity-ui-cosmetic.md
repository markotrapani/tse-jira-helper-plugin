# RED-186235 — Administrator's emails settings in UI are not reflective of default values

> **Link:** https://redislabs.atlassian.net/browse/RED-186235
> **Issue Type:** Bug (id 10004)
> **Project:** RED (Redislabs)
> **Domain:** CM (Cluster Manager) / UI / Administrator user defaults / email alerts / cosmetic display bug / low-severity
> **When to use this anchor:** TSE-filed RED Bug at **Severity 3 - Low** for a **cosmetic UI inconsistency** with no data loss / no availability impact. The bug is real (UI doesn't match backend state) but operationally minor — easy workaround, low Impact Score. Strong reference for: (1) the **minimal Sev-3 Bug shape** with stripped-down body (no Customer Impact / Steps to Reproduce H2 sections — just inline prose); (2) bugs where `Data loss: No` and `Data unavailable: No` custom Booleans are populated to confirm low-impact classification; (3) UI bugs where the discrepancy is best shown via embedded UI screenshot + CLI verification output.
> **Added:** 2026-05-12

## Header fields used

| Field            | Value                                                          |
|------------------|----------------------------------------------------------------|
| Project          | Redislabs (RED)                                                |
| Type             | Bug                                                            |
| Priority         | Medium (default; not bumped — appropriate for Sev 3)           |
| Severity         | `3 - Low`                ← key marker                          |
| Status           | Closed (resolution: `Done`)                                    |
| Reporter         | TSE who filed (Isaac Li)                                       |
| Assignee         | Engineer (Gal Marziano)                                        |
| Labels           | `Support`                ← only 1 label                         |
| Components       | None                                                           |
| Affects versions | `7.22.2`, `8.0.10_patch5_Cross`                                |
| Fix versions     | None (kept blank at close — RCA Provided / Dev block reason)   |
| Parent / Epic    | `cm catch all 2026` (RED-180864)                               |
| Sprint           | Sprint 202-208 - CM-Refresh (multi-sprint engineering churn)   |
| Story Points     | `1`                                                             |

## Custom fields populated

| fieldId               | Name                   | Value                                                       |
|-----------------------|------------------------|-------------------------------------------------------------|
| `customfield_10180`   | Severity               | `3 - Low`                                                    |
| `customfield_10181`   | Component (single-select) | `CM`            ← routes to Cluster Manager team          |
| `customfield_10026`   | Product/s              | `RS (Redis Software)`                                       |
| `customfield_10025`   | Environment/s          | `Production`                                                |
| `customfield_10595`   | Affected Organizations | `[Aviso Wealth]`                                            |
| `customfield_10027`   | Seen by Customer/s     | `Aviso Wealth`                                              |
| `customfield_10036`   | Zendesk ID/s           | `155664`                                                     |
| `customfield_10585`   | Impact Score           | `21`         ← low (reflects Sev 3 cosmetic nature)          |
| `customfield_10115`   | Found By               | `Prod/Customer`                                             |
| —                     | SM Component           | `Emails`     ← scaling-manager sub-component (Sev-3 specific) |
| —                     | Data loss              | `No`         ← explicit Boolean confirming no data loss       |
| —                     | Data unavailable       | `No`         ← explicit Boolean confirming no DU              |
| `customfield_10374`   | Workaround             | "Workaround is to use the UI to 'enable' alerts for the Administrator, save, then disable them. From there, we can see within the ccs that email_alerts are disabled." |
| —                     | Block Reason           | `Dev`        ← engineering classification                    |
| `customfield_10063`   | RCA                    | 6-section template, ALL sections blank (placeholder only)    |

## Sev-3 Low specific markers

The combination of fields that signal this is a low-severity cosmetic bug:

- **`Severity: 3 - Low`** (the primary signal)
- **`Impact Score: 21`** (well below the 40+ typical for prod customer bugs)
- **`Data loss: No`** AND **`Data unavailable: No`** explicitly populated — confirms zero operational impact
- **Single label `Support`** — no `Encryption` / `Urgent` / `AMR` escalation labels
- **`Story Points: 1`** — minimal engineering effort estimate
- **`Block Reason: Dev`** — categorizes the block as a dev issue (not customer-blocked or design-blocked)

## Description body structure

**Flat narrative, NO H2 sections.** Inline prose with:
1. Setup explanation (1 paragraph)
2. UI screenshot reference
3. Backend verification via CLI (code block)
4. Brief observation paragraph
5. Numbered Reproduction steps (3 steps)
6. Workaround paragraph (also lives in customfield_10374 — duplicated for readability)
7. **ASK:** one-line statement of desired fix

```markdown
When a user configures a new cluster, a user with the Username "Administrator" is created by default with their
email address.

When checking the email settings in Access Control → Users → Administrator → Edit, the Alerts are are not
checked.

<embedded UI screenshot showing unchecked checkboxes>

However, the user will still be configured with alerts enabled.

    sh-5.1$ ccs-cli hgetall user:1
    5) "name"
    6) "Administrator"
    7) "email_alerts"
    8) "enabled"

It is understandable that this user should start with email alerts turned on by default. However, this setting
is not configured in the UI correctly. The "Receive alerts for databases" box is not checked.

Reproduction steps are pretty straightforward
1. create a new cluster
2. Verify within the UI that the Administrator's Alerts are shown as disabled
3. Check within the CCS (ccs-cli hgetall user:1) that their email alerts are indeed enabled.

Workaround is to use the UI to "enable" alerts for the Administrator, save, then disable them. From there, we
can see within the ccs that email_alerts are disabled.

ASK: The "Receive alerts for databases" box for the Administrator should be checked by default within the UI.
```

### Section observations

- **No `## Summary` / `## Customer Impact` / `## Expected` / `## Actual` / `## Evidence` H2 headers** — this is the **lean Sev-3 shape**, much smaller than RED-194253.
- **Reproduction is inline numbered list**, NOT a `## Steps to Reproduce` H2 — appropriate for trivially-reproducible cosmetic bugs.
- **Embedded UI screenshot** in body (visible as `image-20260205-221729.png` attachment) — for UI bugs, the screenshot IS the evidence. No need for log excerpts.
- **CLI verification block** shows ground-truth backend state — pattern for "UI says X but backend says Y" bugs.
- **`ASK:` prefix** at the end states the desired fix in one line — standard cosmetic-bug closer. Substitutes for a `## Suggested Fix` section.
- **Workaround duplicated** in description body AND in `customfield_10374` field — TSE keeps the body readable while also populating the structured field for triage automation.

## Issue links pattern

```
Blocks:
  is blocked by  RED-188887  PUT /v1/users/{uid} with bdbs_email_a... (Closed)
```

- **`is blocked by`** — a related API-layer bug that needed to be fixed first. Engineering links these during triage. TSE doesn't usually populate at file time.

## Affects versions pattern — multiple versions including `_patch` suffix

```
7.22.2, 8.0.10_patch5_Cross
```

- **Comma-separated multi-value** allowed in `Affects versions`.
- **`_patch5_Cross` suffix** appears on cross-branch patch builds — Engineering names builds this way. TSE captures verbatim from the customer's `rladmin status` / version output.

## Notes / nuances

- **Sev 3 Bugs don't need a long writeup** — the lean shape is correct, not lazy. Don't pad with empty Customer Impact / Steps / Expected / Actual sections.
- **`SM Component: Emails`** — Scaling Manager sub-component field. Distinct from the main `Component: CM` field. Routes within the CM team to the specific feature area.
- **`Data loss: No` + `Data unavailable: No`** — these two Booleans together are the formal Sev-3 marker (no DL / no DU). TSE should populate them on every RED bug, not just low-sev ones — they drive customer-facing impact reporting.
- **`Block Reason: Dev`** — engineering-set after triage. TSE leaves blank.
- **Story Points: 1** — set by engineering during sprint planning. TSE leaves blank at file time.
- **Sprint listed across 6 sprints** (Sprint 202-208) — engineering churn, not TSE responsibility.
- **`Found By: Prod/Customer`** — same as standard RED bug (not `Community` like AMR-routed MOD bugs).
- **`Affected Organizations` populated** even though Sev-3 cosmetic — the customer DID see it, so it counts. Not a "internal-only" bug.
- **Single Zendesk ID** (`155664`) — typical for a single-customer cosmetic report.
- **No `Workaround` H2 in description** — the workaround sentence is inline before the ASK. Different from RED-194253 which keeps a `## Workaround` heading as a navigational marker.
- **Compare to RED-194253** (Sev-2 Medium, deep technical analysis) for the long-form Bug shape vs this lean Sev-3 shape. Both are valid; TSE picks based on technical depth, not customer politeness.
- **Compare to RED-152733** (also lean, but Sev-2 / scale-limited tooling bug) — this Sev-3 cosmetic shape is even lighter: no log excerpts at all, just a UI screenshot + 4-line CLI output.
