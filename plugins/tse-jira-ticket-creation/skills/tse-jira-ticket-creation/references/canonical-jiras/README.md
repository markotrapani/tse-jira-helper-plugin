# Canonical Jiras

A library of real, well-formed Redis Jira tickets that the skill should anchor against when drafting new ones. Each file extracts the **structure and patterns** of a real ticket so the skill produces output that matches what TSEs actually file — not a Confluence-derived approximation.

## Why this directory exists

Marko caught a poor v0.6 dry-run on 2026-05-12 where the description body was a flat "bolded label: value" prefix block + free text. Looking at a real reference Jira ([RED-194253](https://redislabs.atlassian.net/browse/RED-194253)) revealed that real bugs use proper H2 sections (Summary / Root Cause / Customer Impact / Steps to Reproduce / Expected Behavior / Actual Behavior / Evidence from Support Case / Workaround / Suggested Fix / Related Code Paths / Support Package Reference).

**Confluence docs describe field rules; canonical-jiras describe description style.** Both are needed.

## How the skill uses these

Per the workflow in `SKILL.md`:

1. Before drafting a new Jira description body, the skill **scans this directory** for the closest matching canonical Jira (by issue type and domain).
2. The skill **mirrors the H2 section structure** from that canonical example.
3. The skill **never duplicates field values** (customer, cluster, product, BDB IDs) as bolded prefix lines in the description. Those live in custom fields only.
4. If no close match exists, the skill picks the closest and **explicitly flags low confidence** in the preview.

## Adding new canonical references

When you (Marko) file a Jira that came out well, add it here as a future anchor:

1. **Filename convention:** `<KEY>-<type>-<domain-tag>.md` — e.g., `RED-194253-bug-cert-chain.md`, `RCA-461-rca-multicluster-azure.md`, `MOD-12345-bug-rejson.md`.
2. **Extract via Jira PDF + getJiraIssue** — the skill can pull the rendered description body and field values directly.
3. **Strip customer-specific identifiers** (customer names, account IDs, specific cluster names) — replace with `<CUSTOMER>`, `<CLUSTER>`, etc. — UNLESS the example is intentionally illustrative of how to name those things.
4. **Add metadata header** to the file (see template below).
5. **Bump the plugin version** so the new reference ships with an explicit version.

### Canonical file template

```markdown
# <KEY> — <one-line description>

> **Link:** https://redislabs.atlassian.net/browse/<KEY>
> **Issue Type:** <Bug | RCA | Improvement | Security | ...>
> **Domain:** <cert/TLS, CMEK, modules, AA replication, Terraform provider, Azure ACRE, ...>
> **When to use this anchor:** <conditions under which this is a good template>
> **Added:** <YYYY-MM-DD>

## Header fields used

| Field | Value |
|---|---|
| ... | ... |

## Description body structure

### Summary
<example content or shape>

### Root Cause (optional)
<example or shape>

### Customer Impact
<example or shape>

### ... (other sections)

## Custom fields populated

| fieldId | Name | Value pattern |
|---|---|---|
| customfield_... | ... | ... |

## Notes / nuances
<anything weird about this one that the skill should know>
```

## Current canonical references

| File | Type | Domain | Best for drafting |
|---|---|---|---|
| `RED-194253-bug-cert-chain.md` | Bug | Encryption / TLS / cert chain | INE, CMEK-adjacent, certificate validation, multi-level PKI bugs. Strong reference for code-level bugs with engineering investigation present. |
| `RED-127842-bug-azure-dmc-ccs-binding.md` | Bug | Azure / ACRE / DMC / CCS / race condition | Azure-specific bugs with race conditions. Demonstrates Azure-Integration label pattern and multi-ZD aggregation (16 Zendesk tickets aggregated to one Jira). |
| `RED-152733-bug-support-package-timeout.md` | Bug | Support tooling / debuginfo / hardcoded timeouts | "Internal feature doesn't scale to customer's environment" bugs. Lean Bug template — minimal labels, flat-narrative description, single S3 evidence path. Resolution: `RCA Provided` (no code fix). |
| `MOD-14916-bug-modules-perf-upgrade.md` | Bug | Modules / RediSearch / performance regression / post-upgrade | MOD-project performance bugs comparing 3+ environments (before/after/control). Heavy S3 evidence, screenshots, Grafana dashboard links. Narrative-style description (Context → Decisions → Observations) rather than H2-sectioned. |
| `RCA-583-rca-amex-ccs-quorum-loss.md` | RCA | CCS quorum loss / topology change overload / cluster recovery | The canonical real-world RCA shape. Strong reference for any RCA workflow — Initial Root Cause structure with Contributing Factors, Log Evidence, R&D to assess, Final Root Cause filled by engineering, Action items table. |
| `RED-188607-bug-aa-upgrade-modules.md` | Bug | A-A upgrade / module configuration / admin command failure | Upgrade-path Bugs where a documented post-upgrade admin command fails with sequential validation errors, with raw CLI + cnm_http debug-log evidence and multi-org ZD aggregation. Flat-narrative chronological style. |
| `RED-193156-bug-ad-ldap-auth-upgrade.md` | Bug | AD/LDAP auth / Cluster Manager UI / post-upgrade regression | Post-upgrade regression Bugs with broad blast radius (multiple customers within days), where the fix involves both a workaround and a release-notes known-issue entry via a DOC ticket split. Hybrid label-block + H2-less style. |
| `RED-194427-bug-cm-server-sqlite-recovery.md` | Bug | cm_server / SQLite / UI login / resilience gap | TSE-filed "resilience gap" Bugs from a single customer occurrence where root cause is uncertain but the lack of self-recovery + observability gap is itself the bug. Uses AI-hypothesis framing and a menu of scoped R&D asks. |

(Marko: add more as they come in.)
