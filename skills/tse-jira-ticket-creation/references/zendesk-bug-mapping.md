# Zendesk → Jira Bug Field Mapping

Adapted from `jira-helper/src/jira_creator.py` (`_map_zendesk_to_jira`, `_detect_project`, etc.).

## Zendesk PDF Anatomy

Standard Redis Zendesk PDF print filename: `redislabs.zendesk.com_tickets_<TICKET_ID>_print.pdf`

Extractable from the PDF body:

| Zendesk Field | How to find it |
|---|---|
| Ticket ID | Filename or top-of-PDF header |
| Subject (→ Summary) | First line after "Subject:" or page header |
| Customer / Account | "Requester" or "Organization" field |
| Description | "Description" section or first comment |
| Comments / Thread | Subsequent timestamped agent + customer replies |
| Priority | Stated Zendesk priority — Urgent / High / Normal / Low |
| Tags | Account tags (ARR, product, region) |
| Custom fields | Product version, cluster ID, region (if filled in Zendesk) |

## Project Auto-Detection

Apply rules in order; first match wins.

### RDSC (Redis Data Integration)

Match if **any** of these are present in summary or description (case-insensitive):

- `RDI` (word-boundary)
- `Redis Data Integration` / `redis-data-integration`
- `Debezium`
- `add_field`, `jmespath`, `redis.write`
- `pipeline yml`, `pipeline yaml`, `CDC pipeline`
- `json_parse`, `row_format`

### MOD (Redis Modules)

Match if **any** of:

- Module command prefix in summary: `ft.`, `ft_`, `json.`, `ts.`, `bf.`, `cf.`, `cms.`, `topk.`, `graph.`, `ai.`, `search.`, `hnsw`, `knn`
- Module name in brackets in summary: `[RediSearch ...]`, `[ReJSON ...]`, `[Search ...]`, `[Bloom ...]`, `[TimeSeries ...]`, `[Graph ...]`, `[RedisAI ...]`
- Module version string pattern: `(search|rejson|redisjson|redisearch|bf|bloom|timeseries|graph|redisai)[:\s]+\d+\.\d+\.\d+` — e.g., `search:8.2.8`, `ReJSON 8.2.8`
- Combined with module-related keywords: "index corruption", "index non-functional", "ft.search", "ft.info", "json.get", "ts.add", "vector index"

### DOC (Documentation)

Match if the ticket is purely about docs.redis.io / redis.io documentation — typos, broken links, missing examples, incorrect API reference. Heuristic: subject contains "docs", "documentation", "redis.io", or "broken link"; no operational impact.

### RED (Redis — default)

Everything else. Redis Software (Enterprise) / Redis Cloud operational issues, cluster behavior, DMC/proxy, replication, sharding, ACL, etc.

## Issue Type

For bug workflow, always `Bug`. Don't use `Task`, `Story`, or `Epic` for support-originated tickets.

## Field Mapping Table

| Jira Field | Value | Source |
|---|---|---|
| Project | RED / MOD / DOC / RDSC | Auto-detected (see above) |
| Issue Type | Bug | Constant |
| Summary | Zendesk subject (cleaned, ≤255 chars) | PDF |
| Description | See "Description Body" below | PDF + impact score |
| Priority | Highest / High / Medium / Low / Lowest | From impact score band |
| Severity | Very High / High / Medium / Low | From final score threshold |
| Assignee | Unassigned by default | User can specify |
| Reporter | Current user (Marko Trapani) | Auth context |
| Labels | See "Labels" below | Derived |
| Components | DMC / Redis / Cluster / module name | Content detection |

### Severity Thresholds (Final Score → Severity)

| Final Score | Severity |
|---|---|
| ≥ 90 | Very High |
| ≥ 70 | High |
| ≥ 50 | Medium |
| < 50 | Low |

### Priority Mapping (Band → Priority)

| Band | Jira Priority |
|---|---|
| CRITICAL | Highest |
| HIGH | High |
| MEDIUM | Medium |
| LOW | Low |
| MINIMAL | Lowest |

## Custom Fields

These are the known custom field IDs for `redislabs.atlassian.net`. Verify with `mcp__claude_ai_Atlassian__getJiraIssueTypeMetaWithFields` before relying on them — IDs can drift.

| Field Name | Field ID (suspected) | Value |
|---|---|---|
| Sprint | `customfield_10010` | Omit unless user explicitly asks |
| Zendesk ID | (varies — check) | The `<TICKET_ID>` |
| Impact Score | (varies — check) | Final score (numeric) |
| Cache Name | (varies — check) | Extracted via regex `cache name[:\s]+([^\s,]+)` |
| Region | (varies — check) | Extracted via regex `region[:\s]+([^\s,]+)` |
| Affected Organization | (varies — check) | Azure / AWS / GCP detection |

**On unknown field ID**: don't fail. Drop the field, warn the user, and offer to leave a comment with the extra context instead.

## Component Detection

From description body, lowercase match:

| Keyword | Component |
|---|---|
| `dmc` | DMC |
| `redis` (without other matches) | Redis |
| `cluster` (without other matches) | Cluster |
| Module command/name (see project auto-detect) | RediSearch / ReJSON / RedisBloom / RedisTimeSeries / RedisGraph / RedisAI |
| (none) | Unknown |

For projects beyond RED/MOD/DOC/RDSC, **fetch project components** dynamically via `mcp__claude_ai_Atlassian__getJiraIssueTypeMetaWithFields` and present the list to the user.

## Cloud/Environment Detection

| Keyword in description | Affected Organization |
|---|---|
| `azure` (without other matches) | Azure |
| `aws`, `amazon` | AWS |
| `gcp`, `google cloud` | GCP |
| (none) | Unknown |

## Labels

Combine these (capped at ~5 labels total):

1. **Customer name** — replace spaces with underscores (`monday.com` → `monday_com`, `Acme Corp` → `Acme_Corp`)
2. **Source** — always include `Customer-Reported`
3. **Severity hint** — `P1` / `P2` / `P3` / `P4` / `P5` (from severity score)
4. **Domain keywords** — extracted from summary/description: `high_cpu`, `audit_logging`, `connection`, `cluster`, `dmc`, `acre`, `cache_link`, `replication`, `acl`, `tls`, etc.
5. **Cloud** — `azure`, `aws`, `gcp` if detected

## Description Body Template

```
{original_zendesk_description}

---

**Reported by:** {customer_name} (Zendesk #{ticket_id})
**Cluster:** {cluster_id_if_known}
**Region:** {region_if_known}
**Product:** {Redis Software | Redis Cloud | Azure Cache for Redis | RDI}

### Impact Score: {final_score} ({band})

| Component | Score | Reason |
|---|---|---|
| Impact & Severity | {n}/38 | {reason} |
| Customer ARR | {n}/15 | {reason} |
| SLA Breach | {n}/8 | {reason} |
| Frequency | {n}/16 | {reason} |
| Workaround | {n}/15 | {reason} |
| RCA Action Item | {n}/8 | {reason} |
| **Base** | **{base}** | |
| Multipliers | {support}+{account} | |
| **Final** | **{final} ({band})** | |

### Zendesk Reference

- Ticket: https://redislabs.zendesk.com/agent/tickets/{ticket_id}
- PDF: {attachment_name}
```

## Related Jira PDFs (Optional Input)

If the user provides one or more related Jira PDFs alongside the Zendesk PDF:

1. Extract Jira keys from filenames — pattern `[#RED-NNNNNN]...pdf` or content header.
2. Include keys in the "Related Tickets" section of the Bug's description.
3. After the Bug is created, call `mcp__claude_ai_Atlassian__createIssueLink` with:
   - `inwardIssueKey`: the new Bug
   - `outwardIssueKey`: each related Jira
   - `type`: `Relates` (case-sensitive — confirm via `mcp__claude_ai_Atlassian__getIssueLinkTypes` on first run)

## Anti-patterns (Don't Do This)

- **Don't fabricate ARR.** If you can't find it in the Zendesk tags or VIP list, score `0` and note "ARR unknown" in the reason. Better to under-score than to invent.
- **Don't auto-attach the Zendesk PDF.** MCP `createJiraIssue` doesn't accept attachments. Reference the PDF filename in description; the user attaches in the browser.
- **Don't paste the entire Zendesk PDF text** into the description — extract the problem statement + key indicators. Aim for under 2000 characters.
- **Don't include customer PII** (phone numbers, internal emails of non-Redis people) in the Bug description without redacting.
