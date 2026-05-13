# Jira Schema — Real IDs for redislabs.atlassian.net

Verified via `getVisibleJiraProjects`, `getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`, `getIssueLinkTypes`, and inspection of the canonical template ticket **RCA-41**.

**Cloud ID:** `06f73ca7-8f2c-4392-b40a-08288e9d0ba3`
**Base URL:** `https://redislabs.atlassian.net`

**Authoritative Support documentation** (re-read on doubt):
- [Jira creation for Support](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958) — Customer Support team's Jira creation guide
- [Jira - Impact Score](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553) — impact score definitions
- [RCA Initiation and Data Collection Procedure](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4575690753) — RCA creation procedure
- [RCA-41](https://redislabs.atlassian.net/browse/RCA-41) — RCA template ticket (clone this)

## RCA Template Block (`customfield_10063`)

**TSE default: LEAVE BLANK.** Per Marko (2026-05-12 correction): "for that RCA section.. we don't have to fill it out. That is for R&D to fill out." This field is R&D's working area during triage and development — TSEs don't seed it.

**Narrow exception — Azure ACRE/AMR tickets only:** the customer-facing Microsoft automation reads section 0, so for AMR / ACRE bugs, populate section 0 with a one-line customer-readable description. Sections 1–5 still stay as placeholders. See canonical [`MOD-12739-bug-amr-inconsistent-count.md`](./canonical-jiras/MOD-12739-bug-amr-inconsistent-count.md).

**For ALL non-Azure bugs (RED / DOC / MOD non-AMR / RDSC / etc.):** omit `customfield_10063` from the `createJiraIssue` payload entirely. Don't fabricate the 6-section ADF skeleton.

The template that R&D works against (for reference only — TSE does NOT seed this):

```
------------------------------
0. Incident short description: <one-line customer-readable description — Azure ACRE/AMR ONLY>
1. Bug Description:
2. Which components impacted by this bug?
3. What was fixed?
4. Reproduction steps?
5. Public Blocker Description:
------------------------------
```

**ADF format** — IF you're filing an Azure ACRE/AMR ticket and need to populate section 0, the field is a textarea so it still requires ADF (per the Known Validation Gotchas section below).

**ADF format** — textarea custom fields require ADF (per the Known Validation Gotchas section below):

```jsonc
"customfield_10063": {
  "type": "doc",
  "version": 1,
  "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "------------------------------"}]},
    {"type": "paragraph", "content": [{"type": "text", "text": "0. Incident short description: <one-liner>"}]},
    {"type": "paragraph", "content": [{"type": "text", "text": "1. Bug Description:"}]},
    {"type": "paragraph", "content": [{"type": "text", "text": "2. Which components impacted by this bug?"}]},
    {"type": "paragraph", "content": [{"type": "text", "text": "3. What was fixed?"}]},
    {"type": "paragraph", "content": [{"type": "text", "text": "4. Reproduction steps?"}]},
    {"type": "paragraph", "content": [{"type": "text", "text": "5. Public Blocker Description:"}]},
    {"type": "paragraph", "content": [{"type": "text", "text": "------------------------------"}]}
  ]
}
```

## ⚠️ Known Validation Gotchas

Two non-obvious gotchas verified against the live tenant (caught while filing RED-196654 on 2026-05-11). The skill must handle both proactively or `createJiraIssue` returns 400.

### Gotcha 1 — Textarea custom fields require ADF, not strings

The system `description` field accepts markdown via `contentFormat: "markdown"`. **But custom textarea fields reject raw strings.** Their values must be a full Atlassian Document Format (ADF) document.

**Wrong** (returns `"Operation value must be an Atlassian Document"`):
```jsonc
"customfield_10374": "Manual config via Redis Cloud Console..."
```

**Right** (minimum viable ADF for one-line text):
```jsonc
"customfield_10374": {
  "type": "doc",
  "version": 1,
  "content": [
    { "type": "paragraph",
      "content": [ { "type": "text", "text": "Manual config via Redis Cloud Console..." } ] }
  ]
}
```

**Fields that are textareas requiring ADF on redislabs.atlassian.net:**

| fieldId             | Name                                  | Issue Type |
|---------------------|---------------------------------------|------------|
| `customfield_10374` | Workaround                            | RED Bug    |
| `customfield_10681` | Impact Score details                  | RED Bug    |
| `customfield_10063` | RCA (Azure post-save template)        | RED Bug    |
| `customfield_10467` | Final Root Cause & Conclusions        | RCA        |
| `customfield_10475` | Zendesk                               | RCA        |
| `customfield_10476` | Slack                                 | RCA        |
| `customfield_10478` | Action item(s)                        | RCA        |
| `customfield_10490` | Initial Root Cause                    | RCA        |
| `customfield_11853` | INFO PANEL                            | RCA        |

Plain string fields (e.g. `customfield_10036` Zendesk ID/s, `customfield_10056` Reported Version/Build, `customfield_10027` Seen by Customer/s) are unaffected — they take strings.

### Gotcha 2 — `Environment = Production` requires `Seen by Customer/s` (even though "deprecated")

A project workflow validation rule requires `customfield_10027` (Seen by Customer/s) to be non-empty whenever `customfield_10025` (Environment) includes `Production` (id 10007).

The Support Confluence doc says "Seen by Customer/s" has been replaced by `customfield_10595` (Affected Organizations). **But the validation rule is independent of the docs.** Setting `customfield_10595` alone does NOT satisfy the rule.

**Wrong** (returns `"Seen By Customer is required for Environment/s = Production"`):
```jsonc
"customfield_10025": [{ "id": "10007" }],          // Production
"customfield_10595": [{ "id": "23311" }],          // Aetna in Affected Orgs
// customfield_10027 omitted because Support docs called it deprecated
```

**Right** — always set both when Production is in Environment/s:
```jsonc
"customfield_10025": [{ "id": "10007" }],
"customfield_10595": [{ "id": "23311" }],          // canonical dropdown
"customfield_10027": "Aetna"                       // string, satisfies validation
```

Since TSE bugs are almost always for customer-originated issues with `Environment=Production`, the skill should treat `customfield_10027` as **always required**, never optional, regardless of whether Affected Organizations resolved.

## ⚠️ Project-Shape Schema Differences (READ THIS BEFORE FIELD MAPPING)

Each Redis Jira project has a **different field schema** — not just different allowed values, but different fields available, different custom field IDs, and different description body conventions. The most common mistake is applying RED Bug's full custom-field set to a DOC or RDSC ticket. **Don't do that.**

This section is the canonical reference for what fields each project supports. The skill MUST consult the matching canonical-jiras example before mapping fields:

### RED (Redislabs) — full TSE schema

Full custom-field set documented elsewhere in this file. All the standard TSE fields apply: Severity, Component, Environment/s, Product/s, Reported Version/Build, Affected Organizations, Seen by Customer/s, Found By, Issue source, RCA (6-section template), Workaround, Data loss/Unavailable/Downtime, Impact Score, etc.

**Canonical examples**: RED-194253, RED-127842, RED-152733, RED-186235, RED-188607, RED-193156, RED-194427.

### MOD (RedisModules) — RED-like but with MOD-specific differences

Most RED fields apply, **but with these differences**:

- **Components is multi-select** (e.g., `RedisAI, RediSearch`) — not single-select like RED.
- **Found by** uses different allowed values: includes `Community` (not just `Manual testing / Automation / Prod/Customer`). AMR-routed bugs typically use `Community`.
- **MOD-specific fields**: `BugScore` (numeric — computed by team, complementary to Impact Score), `Is Bug Description Set` (Boolean).
- **AMR-routed MOD bugs**: must populate RCA template **sections 0-1** at file time (required for Azure customer-facing automation), and use labels `AMR` + `Azure-Integration`, `Affected Organizations = Azure`, `ICM ID/s` field instead of/alongside Zendesk ID.

**Canonical examples**: MOD-14916 (RediSearch perf regression, non-AMR), MOD-12739 (AMR inconsistent count results).

### DOC (Documentation) — sparse schema, don't apply RED-style

DOC project schema is **fundamentally minimal**:

- ❌ NO `Severity` field
- ❌ NO `Component` single-select
- ❌ NO `Environment/s` field
- ❌ NO `Product/s` field
- ❌ NO `Seen by Customer/s` field
- ❌ NO `Found By` field
- ❌ NO `Issue source` field
- ❌ NO 6-section `RCA` template field
- ✅ `Impact Score` (`customfield_10585`) is available
- ✅ `Affected Organizations` (`customfield_10595`) is available
- ✅ `Effort` (DOC-specific custom field)
- ✅ Standard Jira fields (Summary, Description, Priority, Labels, Assignee, Reporter, etc.)

**The skill should NOT attempt to populate the RED-style customfield set on DOC tickets.** Verify available fields via `getJiraIssueTypeMetaWithFields` before construction.

**Canonical example**: DOC-6506 (Go-redis SmartClient handoff incorrect default endpoint type).

### RDSC (Redis Data Integration) — dedicated structured fields

RDSC schema differs **fundamentally** from RED:

- ❌ NO `Severity` field
- ❌ NO 6-section `RCA` template field
- ❌ NO `Found By` field
- ❌ NO `Issue source` field
- ❌ NO `Seen by Customer/s` field
- ✅ **Dedicated `Steps to Reproduce` custom field** — not a description H2 section!
- ✅ **Dedicated `Expected Result` custom field** — not a description H2 section!
- ✅ **Dedicated `Actual Result` custom field** — not a description H2 section!
- ✅ Standard fields (Affected Organizations, Impact Score, Workaround, Labels)
- ✅ Labels: `Support-Attention`, `rca_related` (RDSC-specific tags, instead of `CS`/`Support`)
- ✅ Multi-valued `Affected Organizations` when same defect affects multiple customers (often paired with `Cloners` link to sibling customer ticket)
- ✅ Special issue type `RDI Customer Issue` (id `14992`) — distinct from regular `Bug` (id `10004`)

**Description body becomes a customer Q&A transcript** — verbatim email quotes, customer-provided shell commands, attached `container.log.txt` + `application.properties`. The "structured" sections (repro / expected / actual) live in the dedicated custom fields, not in the body.

**Canonical example**: RDSC-4706 (AXIS / Debezium / Oracle RAC SCN files).

### RCA (Root Cause Analysis) — two distinct title shapes

The RCA project supports **two distinct ticket shapes** with different reporters, labels, and field-population patterns:

#### Shape A: Customer-RCA (TSE-initiated)

- **Title**: `<Customer> - RCA <mm/dd/yyyy>` (e.g., "American Express - RCA 04/02/2026")
- **Reporter**: the TSE who initiated (Marko Trapani, etc.)
- **Labels**: `Escalations_RCA`, `rca_RTTI_automation`, `rca_r&d`
- **Initial Root Cause**: multi-paragraph narrative (4-6 paragraphs) covering incident timeline, contributing factors, log evidence cross-references
- **Description body**: Incident Summary (H2) + Timeline table (H2)
- **Linked Issues**: `Relates` to bug Jiras
- **Canonical example**: RCA-583.

#### Shape B: Cluster-incident-RCA (automation-initiated)

- **Title**: `#prod__<YYYY-MM-DD>_<cluster>-<account>_<symptom>` (e.g., "#prod__2026-03-24_mc1716-autumn_reshard-stuck")
- **Reporter**: `Incident` (automation account, not a human TSE)
- **Labels**: includes `FRRT-label` (Final RC Report Time tracking)
- **Initial Root Cause**: **1-2 sentences only** (NOT multi-paragraph)
- **Description body**: emoji-prefixed `## Summary` + milestone-style timeline + a `🕵️‍♂️ What happened (in detail):` line containing the long technical narrative
- **Linked Issues**: `causes` link to CINC (incident) and PRB (problem) tickets
- **Cluster ID field**: dedicated and populated (rather than embedded in title for the customer-RCA shape)
- **Canonical example**: RCA-563.

The skill should detect which shape based on whether the incident is customer-driven (TSE initiating, customer name available) vs cluster-driven (automation alert, cluster ID as the primary identifier).

### Severity 3 - Low pattern (any project)

Severity-3 bugs are typically cosmetic / workaround-exists / supportability and use a distinctive minimal pattern:

- `Data loss: No` (`customfield_10371`) + `Data unavailable: No` (`customfield_10372`) + `Downtime: No` (`customfield_10369`) — the Boolean trio confirms zero operational impact
- `SM Component` (`customfield_10155`) often populated when the bug is in a UI subsystem (e.g., `Emails`)
- Description body is **minimal flat narrative** — no H2 sections, embedded screenshot inline, brief CLI verification block, one-line `ASK:` suffix
- Labels: minimal (just `CS` or `Support` + one domain tag)

**Canonical example**: RED-186235 (UI email settings cosmetic).

---

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
| RCA                       | `customfield_10063`   | string (textarea) | **Universal 6-section template — populate on EVERY bug, not Azure-specific.** See "RCA Template Block" below. |
| Found By                  | `customfield_10115`   | option (single)  | TSE default `Prod/Customer` (id 10149). Values: Manual testing (10147) / Automation (10148) / **Prod/Customer (10149)** |
| Issue source              | `customfield_10177`   | option (single)  | TSE default `Product Bug` (id 10322). Values: **Product Bug (10322)** / Test Code (10323) |
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
