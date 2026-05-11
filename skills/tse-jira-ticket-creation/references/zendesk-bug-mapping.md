# Bug Jira Creation — Support Team Standards

**Authoritative source**: [Jira creation for Support (CS space, page 3785981958)](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958).

Real field IDs and allowed values: see [`jira-schema.md`](./jira-schema.md). Don't speculate; that file is verified against the live Jira tenant.

## Zendesk PDF Anatomy

Standard Redis Zendesk PDF filename: `redislabs.zendesk.com_tickets_<TICKET_ID>_print.pdf`

Extractable from the PDF body:

| Zendesk Field | How to find it |
|---|---|
| Ticket ID | Filename, OR top of PDF |
| Subject (→ Jira Summary) | First line after "Subject:" or page header |
| Customer / Account | "Requester" or "Organization" field |
| Description | "Description" section or first comment |
| Comments / Thread | Subsequent timestamped agent + customer replies |
| Priority | Stated Zendesk priority — Urgent / High / Normal / Low |
| Tags | Account tags (ARR, product, region) |
| Custom fields | Product version, cluster ID, region, cache name (if filled in Zendesk) |

## Project Choice (Per Support Docs)

| Project | When to file |
|---|---|
| **RED** | Redis Labs / Redis Software / Redis Cloud operational issues |
| **MOD** | Redis Modules (RediSearch, ReJSON, etc.) |
| **DOC** | Documentation (typos, broken links, missing examples) |
| **RDSC** | Redis Data Integration (RDI) |

Auto-detection rules (apply in order; first match wins) — see "Auto-detection details" at end of file.

## Field-by-Field Rules

### Status
Leave default (`To Do`).

### Summary
Describe the symptom — relevant, specific, accurate. **No speculations or assumptions.**

**Azure-specific** (ACRE/AMR): Include in the summary:
- Cache name
- Region
- Link to RedisLinks page if available

Example (Azure): `"ACRE: rediscluster-ktcsproda11.eastus2 — DMC stuck at high CPU"`
Example (Cloud): `"Cluster X redis-15462: replication lag spikes during peak load"`

### Assignee
Leave default (Automatic). Don't pre-assign.

### Severity (`customfield_10180`)

**Set by the TSE based on customer impact.** NOT computed from impact score. Values use the numeric prefix exactly as listed:

| Value           | ID    | When                                                                                  |
|-----------------|-------|---------------------------------------------------------------------------------------|
| `0 - Very High` | 10331 | Complete availability loss; endpoint not responding; continuous client disconnects; stuck state machine; critical security issue/vulnerability |
| `1 - High`      | 10330 | Risk for data loss; upgrade failure; cross-cluster investigation; persistent latency increase; system alert that activated R&D on-call |
| `2 - Medium`    | 10329 | Usability of specific features; RCA for cluster failure/bug; supportability enhancement (more impactful) |
| `3 - Low`       | 10328 | Workaround exists; cosmetic bug (typo); supportability enhancement (less impactful) |

The skill should ask the TSE to confirm Severity rather than infer it from keywords. If the TSE hasn't specified, default to `2 - Medium` and flag for review.

### Data unavailable / Data loss / Downtime

| Field            | fieldId               | Yes ID | No ID  | Notes |
|------------------|-----------------------|--------|--------|-------|
| Data loss        | `customfield_10371`   | 10701  | 10702  | Affects CS rank |
| Data unavailable | `customfield_10372`   | 10703  | 10704  | Affects CS rank |
| Downtime         | `customfield_10369`   | 10699  | 10700  | Affects CS rank |

Ask the TSE Yes/No for each — these meaningfully change CS rank.

### Major Prod Channel (`customfield_10370`)

For Major prod events only — link to the relevant Slack channel.

### Event Status (`customfield_10373`)

Only allowed value: `workaround implemented` (id 10705). Set if a WA is in place; leave blank otherwise.

### Workaround (`customfield_10374`)

If a workaround exists, describe it in a few words. Specify **complicated vs simple** implementation.

### Metrics (`customfield_10375`)

Add a **Grafana link** when relevant.

### Sprint / Epic Link
**Leave blank.** Per Support docs.

### Component (`customfield_10181` — RED) or Components (MOD)

This field routes the ticket to the appropriate R&D team. Single-select for RED.

Common picks (see `jira-schema.md` for full list):
- DMC issues (especially ACRE) → `DMC`
- Cluster scaling / membership → `Cluster`
- Azure-specific integration → `Azure integration`
- Cloud SaaS API → `Cloud API`
- ACL / TLS / Auth → `Security`
- Modules → `Modules` (or file in MOD project)

### Environment/s (`customfield_10025`)

For ticket from customer issues (no matter the customer's env), **always select `Production`** (id 10007). Other environments are only for internal tests/QA.

### Description (system field)

Be informative — include as much as possible:
- Screenshots, logs, deployment configuration
- Symptoms
- Reproduction steps
- Other relevant information
- **Customer expectations (Fix / RCA / else)** ← per Support docs, must be present

For **Active-Active (A-A) cases**: include the A-A mapping table (the image in the Confluence doc shows the standard layout — Customer side cluster details vs Redis-internal mapping).

For **log references**: always mention `cluster_name, node_id, shard_id` in that format.

### Priority (`priority`)

**Leave at default `Medium`** (id 3) — to be edited by the PM later (after triage). This field describes impact on the product, not on the customer(s) (that's Severity).

### Labels (`labels`)

**Always include one of `CS` or `Support`** (TSE-team identifying tags — Support docs use these as written).

Additional labels (add when applicable):
- `e2e_ta_coverage` — if the issue could be caught with e2e tests
- **Azure (ACRE/AMR)**:
  - `Azure-Integration` (always for Azure tickets)
  - `AMR` if Active-Active Multi-Region
  - `ACRE` if Azure Cache for Redis Enterprise
  - `Azure_RCA_req` if an RCA is needed from R&D

### Reported Version/Build (`customfield_10056`)

**Always add the reported versions.** Multiple comma-separated: `"7.2.4, 6.0.2"`.

### Affected Organizations (`customfield_10595`)

Select customer name(s) from the dropdown. **This field replaces the old "Seen by Customer/s" field.** Use autocomplete / option ID lookup — the field has 9,253+ options.

If unable to match the customer name to a dropdown option, set `customfield_10027` (Seen by Customer/s, free text) as a fallback and note the discrepancy.

### Zendesk ID (`customfield_10036`)

Insert the ZD ticket ID — **numbers only**, no URL or letters. Free text field, accuracy matters. Multiple IDs comma-separated.

For AMR, IcM incident ID goes in `customfield_14258` (ICM ID/s) instead.

### Impact Score (`customfield_10585`)

The numeric final score (8–130). See [`impact-score-model.md`](./impact-score-model.md) for computation.

**Per Support docs**: the breakdown table goes in a **comment** (the team typically posts a screenshot from the impact score Google Sheet). The skill should:
1. Set `customfield_10585` to the numeric score
2. Post a markdown comment with the 6-component breakdown
3. Optionally also fill `customfield_10681` (Impact Score details) with the text breakdown as a redundant copy

Per Support docs, impact score should be **filled by the team leader of the reporting team**. The skill can compute and propose, but flag this for confirmation.

## Azure-Specific Post-Save Step

For all Azure tickets (ACRE or AMR), **after the Jira is saved**, fill the `customfield_10063` (RCA) field with this Incident Short Description template:

```
------------------------------
0. Incident short description:
```

This is the only description Azure automated reports have to go on aside from the title, so it must be populated from the onset, even before other RCA details are known.

The skill should:
1. Create the Jira with the regular field set
2. Detect "Azure" / "AMR" / "ACRE" in the labels or content
3. As a follow-up call, `editJiraIssue` to populate `customfield_10063` with the template

## Auto-detection details

### Project auto-detection (apply in order)

#### RDSC (Redis Data Integration)

Match if **any** in summary or description (case-insensitive):
- `RDI` (word-boundary)
- `Redis Data Integration` / `redis-data-integration`
- `Debezium`
- `add_field`, `jmespath`, `redis.write`
- `pipeline yml`, `pipeline yaml`, `CDC pipeline`
- `json_parse`, `row_format`

#### MOD (Redis Modules)

Match if **any** of:
- Module command prefix in summary: `ft.`, `ft_`, `json.`, `ts.`, `bf.`, `cf.`, `cms.`, `topk.`, `graph.`, `ai.`, `search.`, `hnsw`, `knn`
- Module name in summary brackets: `[RediSearch ...]`, `[ReJSON ...]`, `[Bloom ...]`, `[TimeSeries ...]`, etc.
- Module version string: `(search|rejson|redisjson|redisearch|bf|bloom|timeseries|graph|redisai)[:\s]+\d+\.\d+\.\d+`
- Combined with module keywords: "index corruption", "index non-functional", "ft.search", "ft.info", "json.get", "ts.add", "vector index"

#### DOC (Documentation)

Match if subject contains "docs", "documentation", "redis.io", "broken link" with no operational impact.

#### RED (default)

Everything else. Redis Software (Enterprise / ACRE) / Redis Cloud operational issues, cluster behavior, DMC/proxy, replication, ACL, etc.

## Description Body Template (Suggested)

```
{Symptom statement — what's broken, where, when}

**Customer expectations:** {Fix / RCA / Information / Workaround}
**Cluster / Region:** {cluster_name} / {region}
**Product:** {Redis Software | Redis Cloud | Azure Cache for Redis | RDI}
**Reported by:** {customer_name} (Zendesk #{ticket_id})

### Details

{original Zendesk description content — trimmed to relevant parts}

### Log References

| cluster_name | node_id | shard_id | Note |
|--------------|---------|----------|------|
| ...          | ...     | ...      | ...  |

### A-A Mapping (Active-Active only)

| Customer Side | Redis Internal |
|---------------|----------------|
| ...           | ...            |

### Zendesk Reference

- Ticket: https://redislabs.zendesk.com/agent/tickets/{ticket_id}
- PDF: {attachment_name}
```

Keep description under ~2000 chars when possible.

## Related Jira PDFs (Optional Input)

If the user provides one or more related Jira PDFs alongside the Zendesk PDFs:

1. Extract Jira keys from filenames (pattern `[#RED-NNNNNN]...pdf`) or content header.
2. Include keys in the "Related Tickets" section of the Bug's description.
3. After Bug creation, call `createIssueLink` with type `Relates` (id 10003) — `inwardIssueKey` = new Bug, `outwardIssueKey` = each related Jira.

## Comment with Impact Score Breakdown (Post-Creation Step)

After Bug creation, post a comment containing the 6-component breakdown:

```markdown
## Impact Score Breakdown

**Final Score:** {n} ({BAND})
**Base:** {n}  **Multipliers:** CloudOps={m1}, Customer={m2}

| Component         | Score | Max | Reasoning |
|-------------------|-------|-----|-----------|
| Impact & Severity | {n}   | 38  | {reason}  |
| Customer ARR      | {n}   | 15  | {reason}  |
| SLA Breach        | {n}   | 8   | {reason}  |
| Frequency         | {n}   | 16  | {reason}  |
| Workaround        | {n}   | 15  | {reason}  |
| RCA Action Item   | {n}   | 8   | {reason}  |

_Per Support standard, impact score should be confirmed by the team leader._
_Reference: [Impact Score model](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553)_
```

## Anti-patterns

- **Don't compute Severity from impact score.** Severity is customer-impact-judged by the TSE per Support docs.
- **Don't set Priority above default Medium.** PM bumps it during triage.
- **Don't put impact score breakdown in a custom field only.** Post as a comment per Support standard.
- **Don't omit `CS` or `Support` label.** It's the TSE team's identifying tag.
- **Don't skip Azure post-save step** for Azure tickets. The `RCA` field needs the "0. Incident short description:" template.
- **Don't fabricate ARR or customer details.** If unknown, score 0 and note "ARR unknown".
- **Don't auto-attach Zendesk PDFs** — MCP `createJiraIssue` doesn't accept attachments. Reference PDF name in description; the user attaches in the browser.
- **Don't include customer PII** (phone numbers, internal non-Redis emails) without redaction.
- **Don't paste entire Zendesk thread** into description — extract the problem statement and key indicators. Aim for under 2000 chars.
