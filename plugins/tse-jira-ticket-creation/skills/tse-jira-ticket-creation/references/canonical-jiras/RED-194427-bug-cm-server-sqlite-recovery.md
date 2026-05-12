# RED-194427 — cm_server does not self-recover from SQLITE_READONLY on sessions.db, leaving UI login permanently broken on the affected node until manual DB deletion

> **Link:** https://redislabs.atlassian.net/browse/RED-194427
> **Issue Type:** Bug (id 10004)
> **Project:** RED (Redislabs)
> **Domain:** cm_server / SQLite / sessions store / no-self-recovery / observability gap / single-customer report
> **When to use this anchor:** **TSE-filed "resilience gap" Bug** where the underlying trigger is uncertain but the lack of self-recovery + lack of logging is itself worth filing. Use when: (1) single ZD but severe failure mode, (2) root cause unknown / multiple hypotheses, (3) TSE has framed explicit AI-assisted hypotheses + AI-assisted R&D asks, (4) the negotiated fix is **defensive / preventive** (better logging, permission-fixup at install) rather than business-logic correction, (5) there's an observability gap (error appears only in HTTP response, never in server logs).
> **Added:** 2026-05-12

## Header fields used

| Field            | Value                                                       |
|------------------|-------------------------------------------------------------|
| Project          | Redislabs (RED)                                             |
| Type             | Bug                                                         |
| Priority         | Medium                                                      |
| Severity         | (not displayed; Impact Score 48 consistent with Medium)     |
| Status           | Escalation progress (`Resolution: Unresolved`)              |
| Components       | None                                                        |
| Affects versions | `8.0.10_patch1_Cross`                                       |
| Labels           | **None** ← zero labels (unusual)                            |
| Sprint           | Core Escalation                                             |
| Parent / Epic    | (none)                                                      |

### Issue links

| Link type    | Target      | Notes                                                                 |
|--------------|-------------|-----------------------------------------------------------------------|
| split to     | RED-195277  | R&D follow-up sub-task for the logging-improvement ask (To Do)        |

## Custom fields populated

| fieldId               | Name                   | Value                                                       |
|-----------------------|------------------------|-------------------------------------------------------------|
| `customfield_10181`   | Component              | `CM` (routes to Cluster Manager / cm_server team)           |
| `customfield_10025`   | Environment/s          | `[Production]`                                              |
| `customfield_10027`   | Seen by Customer/s     | `Tesla`                                                     |
| `customfield_10036`   | Zendesk ID/s           | `160214` (single ZD)                                        |
| `customfield_10585`   | Impact Score           | `48`                                                        |
| `customfield_10063`   | RCA                    | 6-section template, all blank placeholders                  |

> **Notable field absences** in this PDF (worth correcting for TSE-filed bugs):
> - No `Affected Organizations` value despite `Seen by Customer/s = Tesla` — populate both.
> - No `Product/s` value — should be `[RS (Redis Software)]` for any cm_server bug.
> - No `Reported Version/Build` (`customfield_10056`) — `Affects versions` is set instead.
> - No `Severity` value displayed.
> - **Zero Labels** — TSE-filed bugs should at minimum have `Support` or `CS` + 1-2 domain tags.

## Description body structure

**H2-sectioned** (matches RED-194253 style) but with new section types adapted for investigation-incomplete state.

```markdown
## Summary

<3 paragraphs>:
- Para 1: Single-customer report. ZD + version + verbatim error string + path that failed + filesystem state.
  Observed behavior (no self-detect, no auto-recover).
- Para 2: **Why-this-is-worth-filing meta-argument** — even from a single occurrence, the lack of recovery
  is itself the bug. "Whatever the upstream trigger ... any future occurrence will require manual intervention."
- Para 3: Timeline of occurrences + explicit reproducibility statement: "We have not reproduced it in-lab.
  We do not know whether the trigger is specific to {customer}'s environment or something more general."

## Potential triggers (AI hypotheses)

<Explicit "AI hypotheses" framing distinguishes confirmed cause from candidate mechanisms>:
- Lead paragraph rules out the obvious candidate using documented error taxonomy.
- Numbered hypothesis list (2 mechanisms), each 1-2 sentences, both flagged unconfirmed.
- Closing line ties hypotheses to the customer-questions section: "The customer questions below
  distinguishes these."

## Open questions for the customer

<Numbered list, each question designed to discriminate between hypotheses>.

## Evidence

<Bulleted concrete artifacts: verbatim UI error, mount output, workaround timestamp>.

**Notable evidence gap** (bolded paragraph): documents what was searched and didn't appear, with
specific grep scope + result. The absence is itself a finding.

## Workaround

<Lead-in sentence>:

    <code block: 3 shell commands>

## AI-Assisted Asks for R&D

<Numbered list of 5 concrete scoped asks>. Each ask:
- Verb-first imperative ("Detect at startup.", "Log the SQLite subcode...", "Quarantine and regenerate.")
- Bold lead phrase summarizing the ask
- 2-4 sentences explaining mechanism + why tractable + which evidence-gap it closes

## Support Packages

<S3 paths, one per line, each with parenthetical state description: "(Apr 15, while issue was present)",
"(Apr 22, post-workaround)">.
```

### Section observations

- **H2 sections used heavily** — but adapted for an investigation-incomplete bug: Summary / Potential triggers / Open questions / Evidence / Workaround / AI-Assisted Asks for R&D / Support Packages.
- **"AI hypotheses" / "AI-Assisted Asks for R&D" headers** are explicit acknowledgements of AI-assisted analysis. Honest framing — engineering reviewers can weight accordingly.
- **Explicit non-reproduction statement** ("We have not reproduced it in-lab") mirrors RED-152733's hedge.
- **Concrete evidence-gap paragraph**: not vague — specifies the grep scope ("Apr 17 14:24 through Apr 22 01:18") and the result ("zero SQLite references").
- **5 R&D asks scoped as a menu** — engineering can adopt incrementally. Don't just say "fix this" — propose options tied to specific failure-mode hypotheses and evidence gaps.
- **No customer name in body** beyond Summary para 1 ("Tesla experienced..."); rest of narrative uses "the customer" / "the operator".
- **Workaround content in description, not field** — opposite of RED-194253 which puts content in `customfield_10374` and uses the description heading as a marker. For TSE-filed bugs, **prefer populating `customfield_10374`** so the workaround is field-searchable.

## Notes / nuances

- **Single ZD, single customer** (Tesla, ZD-160214) — lowest customer-evidence threshold of any canonical bug here. Compensated by the explicit "why this is worth filing" framing in Summary para 2. **Pattern**: when filing a resilience-gap bug from a single occurrence, the description must explicitly argue the bug is general, not customer-specific.
- **Status = `Escalation progress`, Resolution = `Unresolved`, Sprint = `Core Escalation`** — engineering accepted into escalation track, no fix shipped yet. Different from RED-152733 (`Closed / RCA Provided`) and RED-127842 (`Closed / Done`). Use this state combo while engineering is actively discussing approach in comments.
- **Zero Labels** is a known gap — TSE-filed bugs should default to `Support` (or `CS`) + 1-2 domain tags even when uncertain.
- **Component = `CM`** routes to Cluster Manager (cm_server) team — bug surfaces in UI but ownership is server-side because cm_server holds the SQLite handle.
- **Engineering discussing fix scope in comments**: should we re-apply permissions during install/upgrade only, or on every supervisord pre-start? Nikolay references precedent — a similar change was made for syncers folder in PR #39157. **Pattern**: when engineering weighs fix scope, **reference precedent PRs / similar prior fixes** in comments.
- **Split-to RED-195277** — engineering split the logging-improvement ask (#2 from the R&D-asks list) into a separate sub-task. **Pattern**: when a TSE files multiple R&D asks, engineering may split them into separate sub-tasks.
- **"AI hypotheses" framing is honest and scoped** — TSE explicitly rules out hypotheses that don't fit (ENOSPC → SQLITE_FULL, not SQLITE_READONLY) before proposing candidates. Buys credibility for the remaining hypotheses.
- Cross-reference:
  - RED-152733 for "lab-non-reproducible + customer-specific scale issue" pattern.
  - RED-194253 for full H2 structure (this bug uses H2s differently — investigation-incomplete sections rather than fix-ready sections).
  - RED-127842 for the multi-customer aggregation pattern that this bug **explicitly avoided** (single ZD, no aggregation).
