# RED-152733 — Support package generation fails in multiple Wells Fargo clusters

> **Link:** https://redislabs.atlassian.net/browse/RED-152733
> **Issue Type:** Bug (id 10004)
> **Project:** RED (Redislabs)
> **Domain:** Support tooling / debuginfo / cluster size / log rotation / hardcoded timeout
> **When to use this anchor:** Bug in **support / operational tooling** (not user-facing functionality). Common shape: customer can't generate a support package for large clusters; problem traces to internal hardcoded timeouts or log rotation policy. Strong reference for "this internal feature doesn't scale to our customer's cluster size" bugs. Also a good **lean** Bug template — minimal labels, focused description, single S3 evidence path.
> **Added:** 2026-05-12

## Header fields used

| Field            | Value                                |
|------------------|--------------------------------------|
| Project          | Redislabs (RED)                      |
| Type             | Bug                                  |
| Priority         | Medium (default; not bumped)         |
| Severity         | `2 - Medium`                         |
| Status           | Closed (resolution: `RCA Provided`)  |
| Components       | None                                 |
| Affects versions | `7.4.6`                              |
| Labels           | `Support`           ← only 1 label    |
| Sprint           | Core Escalation                      |

## Custom fields populated

| fieldId               | Name                   | Value                                                       |
|-----------------------|------------------------|-------------------------------------------------------------|
| `customfield_10180`   | Severity               | `2 - Medium`                                                |
| `customfield_10181`   | Component              | `Cluster` (single-select; routes to Cluster team)           |
| `customfield_10025`   | Environment/s          | `[Production]`                                              |
| `customfield_10026`   | Product/s              | `[RS (Redis Software)]`                                     |
| `customfield_10056`   | Reported Version/Build | `7.4.6-102`                                                 |
| `customfield_10595`   | Affected Organizations | `[Wells Fargo]`                                             |
| `customfield_10027`   | Seen by Customer/s     | `Wells Fargo`                                               |
| `customfield_10036`   | Zendesk ID/s           | `132293`                                                    |
| `customfield_10585`   | Impact Score           | `73`                                                        |
| `customfield_10369`   | Downtime               | `No`                                                        |
| `customfield_10063`   | RCA                    | 6-section template, sections 1 and 3 filled in post-resolution |

## Resolution = "RCA Provided" pattern

Note the **Resolution: RCA Provided** value — used when a bug is closed because:
- The behavior is explained / documented (not necessarily fixed in code)
- A workaround / mitigation is identified
- No code change was deemed necessary by engineering

Different from `Done` (code fix shipped) or `Won't Fix`.

## Description body structure

Lean / minimal — appropriate for operational tooling bugs. **No H2 headers**, flat narrative.

```markdown
{Customer} has indicated that they have not successfully been able to generate a full cluster support
package from several clusters with either the UI or with rladmin for a majority of their clusters. Most
if not all of these clusters have at least 100 BDBs.

They can use the {alternative tool} to generate {alternative output}. However these do {limitations}.

I believe but I have not yet proven that this is due to {hypothesis}, as they log {specific error code}
errors.

When generating from {method 1}, they eventually receive the error "{error message}"
When generating with {method 2}, they received the error "{error message}"

{Specific log file}, showing all relevant {endpoint} requests during customer testing. Most notable
are the {status code} responses for {endpoint paths}:

    <log excerpt: ~10-20 lines of structured access log entries>

{Hypothesis paragraph based on log data}

I have not been able to replicate this in my lab at the moment.

I have the following node specific support packages here:

s3://gt-logs/<ZD>/<file>.tar.gz
...

Let me know if any other information could be useful to troubleshoot this.
```

### Section observations

- **No H2 headers** — flat narrative with log excerpts and bullet points.
- **Multiple methods documented** — UI + rladmin + node-specific debuginfo script, each with its symptom.
- **Specific HTTP error codes** in log excerpts (`504 UT`).
- **TSE's hypothesis** is explicitly hedged: "I believe but I have not yet proven that this is due to {hypothesis}".
- **Reproduction caveat**: "I have not been able to replicate this in my lab at the moment".
- **Open-ended close**: "Let me know if any other information could be useful to troubleshoot this."

## Pattern: scale-limited bugs

This is a "the feature doesn't scale to our customer's environment" bug. Pattern recognition:

- **Trigger**: customer can perform operation X for small N, but fails at large N (BDB count, node count, log size, etc.)
- **Evidence**: HTTP 5xx / timeout errors, specific timing data (here: "9 minutes, close to the 10-minute timeout")
- **Resolution**: usually `RCA Provided` (root cause explained, workaround documented) rather than a code fix
- **Workaround** is often customer-side action (delete extra rotated logs, upgrade) rather than a service-side fix

## Notes / nuances

- **Single label `Support`** — minimal labels for "ordinary" bugs.
- **No Azure-Integration label** — Wells Fargo is on-prem RS, not Azure.
- **Resolution `RCA Provided`** — different from `Done`. Use when no code fix is needed but the customer gets an explanation + workaround.
- **`Sprint: Core Escalation`** — engineering put this in their escalation sprint after triage. TSE should leave Sprint blank at file time.
- **Component=Cluster** — the bug touches debuginfo / support-package generation which is owned by the Cluster team (even though the error manifests through envoy/HTTP layer). Pick component by ownership, not where the symptom shows up.
- **Multi-stage resolution in comments** — engineering's recommendation came in stages. TSE-filed bug description should NOT prematurely document these — they come out of engineering investigation.
