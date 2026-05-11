# Jira Schema — Real IDs for redislabs.atlassian.net

Verified via `getVisibleJiraProjects`, `getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`, `getIssueLinkTypes`, and inspection of the canonical template ticket **RCA-41**.

**Cloud ID:** `06f73ca7-8f2c-4392-b40a-08288e9d0ba3`
**Base URL:** `https://redislabs.atlassian.net`

**Authoritative Support documentation** (re-read on doubt):
- [Jira creation for Support](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958) — Customer Support team's Jira creation guide
- [Jira - Impact Score](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553) — impact score definitions
- [RCA Initiation and Data Collection Procedure](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4575690753) — RCA creation procedure
- [RCA-41](https://redislabs.atlassian.net/browse/RCA-41) — RCA template ticket (clone this)

## Projects (Confirmed)

| Key   | ID    | Name                | TSE Default Issue Type     |
|-------|-------|---------------------|----------------------------|
| RED   | 10020 | Redislabs           | Bug (10004)                |
| MOD   | 10026 | RedisModules        | Bug (10004)                |
| DOC   | 10037 | (Documentation)     | Bug (10074)                |
| RDSC  | ?     | (Redis Data Integration) | Bug (10004) — Support docs don't single out a special TSE type; treat like other projects |
| RCA   | 10245 | Root Cause Analysis | **RCA (10590)** — confirmed by RCA-41 template |

> **Important:** Bug issue type ID differs by project. RED+MOD share `10004`, DOC uses `10074`. Always pass the right `issuetype` ID from this table.

> **For Azure RCAs**: Per Support docs, every Azure RCA also needs a RED or MOD Bug Jira associated. Create the Bug first (if not already filed), then the RCA, then link with `Relates`.

## Issue Link Types (Confirmed)

| Name                  | ID    | Inward            | Outward       | Use For |
|-----------------------|-------|-------------------|---------------|---------|
| **Relates**           | 10003 | relates to        | relates to    | **Bug ↔ related Jira; RCA ↔ related bug; per Support docs the canonical link** |
| **Cloners**           | 10001 | is cloned by      | clones        | Set automatically when cloning RCA-41 (we replicate this when creating programmatically) |
| Blocks                | 10000 | is blocked by     | blocks        | Dependencies |
| Duplicate             | 10002 | is duplicated by  | duplicates    | Dedup |
| Defect                | 10205 | created by        | created       | (rare) |
| Fixed by              | 10212 | Fix               | Fixed by      | After R&D fix |
| Problem/Incident      | 10207 | is caused by      | causes        | Incident hierarchy |
| Post-Incident Reviews | 11215 | is reviewed by    | reviews       | (rare) |

**Default for our skill:** `Relates` (10003) for both bug↔related-Jira and RCA↔related-bug links.

## RED Bug — Custom Fields (Confirmed, 62 total)

Source: `getJiraIssueTypeMetaWithFields` (cloudId, projectIdOrKey=RED, issueTypeId=10004).

### Required

| System Field | fieldId    | Notes                              |
|--------------|------------|------------------------------------|
| Project      | `project`  | `{"key":"RED"}` or `{"id":"10020"}` |
| Issue Type   | `issuetype`| `{"id":"10004"}` (Bug)             |
| Summary      | `summary`  | One-line title; for Azure include cache name + region + RedisLinks page link |

### Standard Support TSE Fields

| Field Name                | fieldId               | Type             | TSE Default / Notes |
|---------------------------|-----------------------|------------------|---------------------|
| Zendesk ID/s              | `customfield_10036`   | string           | Numbers only, no URLs/letters. Comma-separate multiple |
| Affected Organizations    | `customfield_10595`   | array of option  | **Use this — replaces "Seen by Customer/s"**. Customer dropdown (~9,253 entries) |
| Component                 | `customfield_10181`   | option (single)  | Routes to team: Cluster / DMC / CRDB / RCP / SM / Core Platform / Cloud API / Modules etc. |
| Environment/s             | `customfield_10025`   | array of option  | **Always `Production`** (id 10007) for customer-originated tickets |
| Product/s                 | `customfield_10026`   | array of option  | `RS (Redis Software)` for ACRE/Software; `RCP(RV/Pro/Flexible)` or `RCE` for Cloud |
| Reported Version/Build    | `customfield_10056`   | string           | **Always add.** Comma-separated for multiple (e.g., `"7.2.4, 6.0.2"`) |
| Workaround                | `customfield_10374`   | string           | Free text — describe WA + complicated/simple |
| Severity                  | `customfield_10180`   | option           | **TSE judges customer impact** — see "Severity Definitions" below. NOT mapped from impact score. |
| Priority                  | `priority`            | system           | **Leave default (`Medium`).** PM sets later during triage. |
| Impact Score              | `customfield_10585`   | number           | The numeric 8–130 score |
| Impact Score details      | `customfield_10681`   | string           | Per Support docs, **breakdown goes in a comment** with screenshot, NOT in this field. The field can hold a text version as backup |
| Data loss                 | `customfield_10371`   | option           | Yes (10701) / No (10702) — affects CS rank |
| Data unavailable          | `customfield_10372`   | option           | Yes (10703) / No (10704) — affects CS rank |
| Downtime                  | `customfield_10369`   | option           | Yes (10699) / No (10700) — affects CS rank |
| Major Prod Channel        | `customfield_10370`   | string           | Slack link for Major prod events |
| Event Status              | `customfield_10373`   | option           | Only allowed value: `workaround implemented` (10705) — set if WA in place |
| Metrics                   | `customfield_10375`   | string           | **Grafana link** (per Support docs) |
| ICM ID/s                  | `customfield_14258`   | string           | Azure IcM incident IDs (for AMR) |
| Seen by Customer/s        | `customfield_10027`   | string           | **Deprecated** per Support docs — use Affected Organizations instead |
| RCA                       | `customfield_10063`   | string           | Linked RCA key. **Azure-specific**: after save, populate with `------------------------------\n0. Incident short description:\n` template |
| RCA Request Date          | `customfield_10522`   | date             | YYYY-MM-DD when RCA requested |
| Sprint                    | `customfield_10010`   | array            | **Leave blank** per Support docs |
| Target Version            | `customfield_10423`   | option           | Restricted list — usually leave for R&D |
| Verified in Production    | `customfield_10515`   | option           | Yes / No |
| Action Items              | `customfield_10672`   | string           | Free text — rare on creation, filled later |

### RED Bug Severity Values (`customfield_10180`)

**TSE judges based on customer impact** — these are not derived from the impact score. From Support Confluence doc:

| Value           | ID    | When to use                                                                                  |
|-----------------|-------|----------------------------------------------------------------------------------------------|
| `0 - Very High` | 10331 | Complete availability loss; endpoint not responding; continuous client disconnects; stuck state machine; critical security issue |
| `1 - High`      | 10330 | Risk for data loss; upgrade failure; cross-cluster investigation; persistent latency increase; system alert that activated on-call |
| `2 - Medium`    | 10329 | Usability of specific features; RCA for cluster failure/bug; supportability enhancements (more impactful) |
| `3 - Low`       | 10328 | Workaround exists; cosmetic bugs (typo); supportability enhancements (less impactful) |

### RED Bug Components (`customfield_10181`)

**Single-select**. Routes to the appropriate R&D team.

Full TSE-relevant list (30+ options total):
```
AI Services, Automation, Azure integration, Back Office, Beaver, Chef,
Cloud API, Cloud k8s Infra, Cluster, Cluster Interface, CM, Core Platform,
CRDB, DMC, Grafana, Growth Hacking, InfraDevOps, k8s/PCF, LangCache,
Metrics, Modules, Ops Portal, Prometheus stack, RCP, RDI, RDI-Infra,
redis Server, RedisInsight, Security
```

**Common TSE picks:**
- ACRE / Redis Software DMC issues → `DMC`
- Cluster scaling / membership → `Cluster`
- Azure-specific behavior → `Azure integration`
- Modules → `Modules` (or file in MOD project)
- Cloud SaaS portal / API → `Cloud API`
- ACL / TLS / Auth → `Security`

### RED Bug Products (`customfield_10026`)

Multi-select. Pick one or more:

```
RCE (Essential/fixed), RCP(RV/Pro/Flexible), RS (Redis Software), SM,
K8s, PCF, Automation, Documentation, OpsMail, RedisInsight, OpsManager,
NewBO, Grafana, RDI
```

**Common TSE picks:**
- Azure Cache for Redis Enterprise (ACRE) → `RS (Redis Software)`
- Redis Cloud → `RCP(RV/Pro/Flexible)` or `RCE (Essential/fixed)`
- Software on-prem → `RS (Redis Software)`

### RED Bug Environment (`customfield_10025`)

Multi-select. **TSE rule: always `Production`** for customer-originated tickets.

| Value         | ID    |
|---------------|-------|
| Development   | 10004 |
| QA Manual     | 10005 |
| QA Automation | 10150 |
| **Production**| **10007** |
| Staging       | 10006 |
| RCE/Beta      | 10674 |
| UAT           | 10918 |

### System Fields (Bug)

| Field           | fieldId       | TSE Notes |
|-----------------|---------------|-----------|
| Description     | `description` | Markdown or ADF. Include: customer expectations (Fix/RCA/else); for A-A include mapping table; log references in `cluster_name, node_id, shard_id` format |
| Priority        | `priority`    | Leave `Medium` (id 3). PM sets later. |
| Labels          | `labels`      | **Always include `CS` or `Support`**. Add `e2e_ta_coverage` if e2e-testable. For Azure: `Azure-Integration` + (`AMR` or `ACRE`). For Azure RCA-needed: also `Azure_RCA_req` |
| Affects versions| `versions`    | Skip unless user specifies — 1,600+ options |
| Fix versions    | `fixVersions` | Leave blank — R&D fills |
| Assignee        | `assignee`    | Leave blank (Automatic) |
| Status          | (workflow)    | Leave default (To Do) |

## RCA (issueTypeId 10590) — Custom Fields (Confirmed via RCA-41)

Source: `getJiraIssueTypeMetaWithFields` (cloudId, projectIdOrKey=RCA, issueTypeId=10590). Total fields = 40.

> **This is the issue type used by RCA-41**, the canonical Support template. There's also a `Support RCA` type (16251) with mostly the same fields, but the Support procedure docs and RCA-41 itself use **plain `RCA` (10590)**.

### Required

| System Field | fieldId    | Notes                              |
|--------------|------------|------------------------------------|
| Project      | `project`  | `{"key":"RCA"}` or `{"id":"10245"}` |
| Issue Type   | `issuetype`| `{"id":"10590"}` (RCA)              |
| Summary      | `summary`  | `<Customer Name> - RCA <mm/dd/yyy>` per RCA-41 template; for multi-customer use `<ClusterID>` or `<Major Service>` |

### Custom Fields — Populate Directly (Not in Description)

**Critical**: RCA content lives in dedicated custom fields, NOT mixed into description body. RCA-41 shows the canonical placement.

| Field Name                              | fieldId               | Type                       | RCA-41 Default / Notes |
|-----------------------------------------|-----------------------|----------------------------|-------|
| **Start time (UTC)**                    | `customfield_10469`   | datetime                   | Incident start time |
| **End time (UTC)**                      | `customfield_10470`   | datetime                   | Incident end time |
| **Zendesk**                             | `customfield_10475`   | textarea (ADF)             | RCA-41 default: bullet list with `#XXXXXX` link to Zendesk ticket URL |
| **Slack**                               | `customfield_10476`   | textarea (ADF)             | RCA-41 default: bullet list `#prod-YEARMONTHDATE-cXXXXXX` with Slack link |
| **Initial Root Cause**                  | `customfield_10490`   | textarea (ADF)             | RCA-41 default: `<Add your initial RCA here>` |
| **Final Root Cause & Conclusions**      | `customfield_10467`   | textarea (ADF)             | RCA-41 default: 5 bullets `<Add your final RCA and Conclusions here>` |
| **Action item(s)**                      | `customfield_10478`   | textarea (ADF)             | RCA-41 default: ADF table — see "Action Items Template" below |
| **Affected component**                  | `customfield_10495`   | array of option (multi-checkbox) | 44 options — see below |
| **Cluster ID**                          | `customfield_10516`   | array of strings (labels)  | Cluster names |
| **Account name**                        | `customfield_10520`   | array of strings (labels)  | Customer name (underscores for spaces) |
| **Account ID**                          | `customfield_10521`   | array of strings (labels)  | If known |
| **Product**                             | `customfield_10519`   | option (select)            | Redis Cloud (11122) / Redis Software (11123) / AMR (11209) — default is Redis Cloud |
| **Is Customer RCA needed?**             | `customfield_10619`   | option (select)            | Yes (23171) / No (23172) — TSE default Yes |
| Is the Customer RCA delivered?          | `customfield_14159`   | array (multi-checkbox)     | Yes (34627) — leave empty initially |
| Customer RCA                            | `customfield_10496`   | URL                        | Link to customer-facing RCA doc when ready |
| Contributors                            | `customfield_10472`   | array of user              | People involved in investigation |
| INFO PANEL                              | `customfield_11853`   | textarea (ADF)             | Read-only info panel — leave default |
| Start date                              | `customfield_10059`   | date                       | (Optional — different from Start time) |
| Timestamp of TIMELINE                   | `customfield_10487`   | datetime                   | Workflow-stage timestamp |
| Timestamp of ROOT CAUSE and ACTION ITEMS| `customfield_10488`   | datetime                   | Workflow-stage timestamp |
| Timestamp of RCA APPROVAL by R&D        | `customfield_10492`   | datetime                   | R&D-set |
| Timestamp of RCA approval by CloudOps   | `customfield_10494`   | datetime                   | CloudOps-set |
| TTR                                     | `customfield_10589`   | number                     | Time to resolution |

### RCA Description Body (RCA-41 default)

The description IS NOT a giant container. RCA-41's actual description:

```markdown
**Summary:** <Add the summary here.>

---

| **Date and Time _(UTC)_** | **Activity** |
| --- | --- |
| MMM-DD-YYYY, HH:MM | <What happened/what has been done>  |
| MMM-DD-YYYY, HH:MM | <What happened/what has been done>  |
| MMM-DD-YYYY, HH:MM | <What happened/what has been done>  |
```

That's it. Summary line + Timeline table. Everything else lives in dedicated custom fields.

### RCA-41 Action Items Template (`customfield_10478` default ADF)

```markdown
After updating the table below, ensure the tickets are linked with the `relates to` type.

| Description           | Type                              | Owner  | Ticket                   |
|-----------------------|-----------------------------------|--------|--------------------------|
| <What is the AI about?>| **Investigate** or **Prevent** or **Mitigate** | @name | <jira-ticket> e.g: RED-999999 |
| <What is the AI about?>| **Investigate** or **Prevent** or **Mitigate** | @name | <jira-ticket> e.g: RED-999999 |
| <What is the AI about?>| **Investigate** or **Prevent** or **Mitigate** | @name | <jira-ticket> e.g: RED-999999 |
```

The "After updating..." line in RCA-41 is rendered in **red text** (ADF `textColor` attr `#ff0000`). For TSE-created RCAs, populate with the actual action items but keep the red instruction line.

### RCA Status Workflow

Initial status when creating: **`Data Collection`** (id 10732).
TSE transitions to **`Root Cause and Action Items`** (id 10856) when data entry is complete.
Then progresses: **`Pending Action Items`** (10857) → **`Final Review`** (10736) → **`RCA Completed`** (10730) — driven by Engineering / Leadership.

**TSE rule**: Don't auto-transition past `Root Cause and Action Items`.

## RCA Affected Component (`customfield_10495`)

**Multi-checkbox.** 44 allowed values. Same options for both RCA and Support RCA issue types.

```
RediSearch (11118), RedisTimeSeries (11127), Vector Similarity (11128),
RedisAI (11129), RedisJSON (11130), RedisGraph (11131), RedisGears (11132),
Redis Stack (11133), Feature Store (11134), RedisBloom (11135),
Infra: Build + Release (11136), Clients (11137), EcoSystem (11138),
Infra: Automation (11139), Redis (11140), DataTypes (11141), SM (11142),
Cluster (11143), RCP (11144), k8s/PCF (11145), CRDB (11146), DMC (11147),
CM (11148), Automation (11149), InfraDevOps (11150), redis Server (11151),
Back Office (11152), Cloud API (11153), Azure integration (11154),
Syncer (11155), Modules (11156), Core Platform (11157), Chef (11158),
RDI-Infra (11159), Prometheus (11160), Growth Hacking (11161),
Grafana (11162), RDI (11163), RedisInsight (11164), Beaver (23163),
CloudOps (26835), Cluster Interface (26840), LangCache (34924)
```

> **Note**: The RCA list uses `RedisJSON` and `Vector Similarity`; the RED Bug Component list uses `Modules` and doesn't have Vector Similarity. Don't assume parity.

## RCA Product (`customfield_10519`)

**Single select. Only 3 options.** Default: `Redis Cloud`.

| Value           | ID    | When to pick                                  |
|-----------------|-------|-----------------------------------------------|
| Redis Cloud     | 11122 | Redis Cloud (RCP/RCE) incidents (default)     |
| Redis Software  | 11123 | Software / Enterprise / ACRE                  |
| AMR             | 11209 | Active-Active Multi-Region                    |

## RCA Slack Channel Convention

From RCA-41 default and procedure doc:

- Generic: `#prod-{YYYYMMDD}-c{cluster_id_short}`
- More descriptive: `#prod_incident-{YYYYMMDD}-{customer_lower}_{cluster_short}_zd{zendesk_id}`

Both forms are accepted; the descriptive form is preferred when single-customer/single-cluster.

If no Slack channel exists yet, populate with `No prod channel (yet)` (free text).

## Field Resolution Strategy for Unknown Projects

When the user wants to file into a project not covered above:

1. Resolve project key via `getVisibleJiraProjects` with `searchString`
2. Fetch issue types via `getJiraProjectIssueTypesMetadata`
3. For the chosen issue type, fetch schema via `getJiraIssueTypeMetaWithFields`
4. **Filter the field list** before showing to the user — RED Bug has 62 fields, most irrelevant. Show only fields covered in the "Standard Support TSE Fields" table above, plus any required fields
5. **Cache the resolved IDs** for that project+issuetype in conversation memory

## Caveats

- **Affected Organizations** (`customfield_10595`) has 9,253+ options — use autocomplete (search by name → resolve ID); don't enumerate.
- **Critical priority** (id 12003) is non-standard. Default to `Medium` (3) per Support docs; PM bumps later.
- **DOC Bug schema** (issueTypeId 10074) and **MOD Bug schema** not yet fully probed. The skill should fetch on first use of those projects.
- **Date format**: Support procedure says title is `<mm/dd/yyy>` (RCA-41 raw template uses this) — note `yyy` not `yyyy`. Most real RCA clones use `mm/dd/yyyy` (e.g., RCA-461 "Vizio - RCA 12/16/2025"). Either form is widely accepted.
