# Bug Jira Creation — Support Team Standards

**Authoritative source**: [Jira creation for Support (CS space, page 3785981958)](https://redislabs.atlassian.net/wiki/spaces/CS/pages/3785981958).

Real field IDs and allowed values: see [`jira-schema.md`](./jira-schema.md). Don't speculate; that file is verified against the live Jira tenant.

## ⚠️ Anchor to a canonical Jira first

**Before drafting a new bug description, read the most relevant canonical Jira example in [`canonical-jiras/`](./canonical-jiras/).** That directory contains structured extracts of real Redis Jira tickets — they show how description bodies *should look* in practice. The Confluence guide describes which fields to fill; the canonical examples model the structure.

Current canonical bug example:
- [`canonical-jiras/RED-194253-bug-cert-chain.md`](./canonical-jiras/RED-194253-bug-cert-chain.md) — code-level bug, multi-component infra, with engineering investigation present

If no canonical example fits the new bug exactly, pick the closest one and flag low confidence in the preview output.

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

**Set by the TSE based on customer impact.** Two important rules:

1. **Severity is NOT computed from impact score.** They're independent fields with different purposes:
   - **Impact Score** (`customfield_10585`, 8-130) — prioritization signal for R&D scheduling
   - **Severity** (`customfield_10180`, 4-level) — how badly the customer is affected by this specific bug
2. ⚠️ **Severity is NOT inherited from the Zendesk Severity field.** Zendesk's Severity uses different categories (typically `Normal` / `High` / `Urgent`) and doesn't map 1:1 to Jira's `0/1/2/3` scale. A Zendesk ticket marked `Normal` may correspond to a Jira `2 - Medium` *or* `3 - Low` depending on actual customer impact. Treat Zendesk Severity as advisory at best.

Always ask the TSE for the Jira severity. If they haven't specified, default to `2 - Medium` and flag for review.

Values use the numeric prefix exactly as listed (don't drop the `N - ` prefix when setting via API):

| Value           | ID    | When                                                                                  |
|-----------------|-------|---------------------------------------------------------------------------------------|
| `0 - Very High` | 10331 | Complete availability loss; endpoint not responding; continuous client disconnects; stuck state machine; critical security issue/vulnerability |
| `1 - High`      | 10330 | Risk for data loss; upgrade failure; cross-cluster investigation; persistent latency increase; system alert that activated R&D on-call |
| `2 - Medium`    | 10329 | Usability of specific features; RCA for cluster failure/bug; supportability enhancement (more impactful) |
| `3 - Low`       | 10328 | Workaround exists; cosmetic bug (typo); supportability enhancement (less impactful) |

API format: `"customfield_10180": { "id": "10329" }` (single-select option object).

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

If a workaround exists, describe it in the **Workaround custom field** with a multi-paragraph + code-block ADF structure. The description body has a `## Workaround` H2 heading only — no content, since the content lives in the field.

**Pattern** (per RED-194253's Workaround field):

```
<One-line statement of what to do, ending in colon>:

<code block with commands or config>

<Optional caveat paragraph explaining downsides / when this stops working>
```

**ADF skeleton:**

```jsonc
"customfield_10374": {
  "type": "doc",
  "version": 1,
  "content": [
    { "type": "paragraph",
      "content": [{ "type": "text", "text": "<lead-in sentence ending in colon>:" }] },
    { "type": "codeBlock",
      "attrs": { "language": "bash" },
      "content": [{ "type": "text", "text": "<commands / config here>" }] },
    { "type": "paragraph",
      "content": [{ "type": "text", "text": "<caveat paragraph>" }] }
  ]
}
```

For workarounds without code, use just paragraph blocks. Specify **complicated vs simple** implementation as part of the lead-in or caveat.

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

**Keep labels minimal — 2 to 3 max.** Per RED-194253 (canonical example), real bugs use just 2 labels (`Encryption, Support`). Don't sprawl.

**Required:**
- One of `CS` or `Support` — TSE-team identifying tag

**Plus 1-2 domain tags** matching the bug's primary subject:
- For Azure (ACRE/AMR): `Azure-Integration` + (`AMR` or `ACRE`)
- For specific subsystems: `Encryption`, `Cluster`, `Replication`, `terraform`, etc.

**Optional / situational:**
- `Azure_RCA_req` — if an RCA is needed from R&D for an Azure ticket
- `e2e_ta_coverage` — ONLY add if the user explicitly asks. Don't default-add this.

**Anti-patterns:**
- Don't add 5+ labels just because they could apply. The first 2-3 carry the routing signal.
- Don't add `terraform-provider` AND `terraform` — pick one.
- Don't restate facts already in custom fields (e.g., don't add `production` as a label — that's `customfield_10025`).

### Found By (`customfield_10115`)

Single-select. **TSE default: `Prod/Customer`** (id `10149`).

| Value             | ID    | When                                                  |
|-------------------|-------|-------------------------------------------------------|
| Manual testing    | 10147 | Internal manual QA caught it                          |
| Automation        | 10148 | Internal automation/test suite caught it              |
| **Prod/Customer** | 10149 | **Default for TSE-filed bugs** — customer reported it |

API format: `"customfield_10115": { "id": "10149" }`.

### Issue source (`customfield_10177`)

Single-select. **TSE default: `Product Bug`** (id `10322`).

| Value           | ID    | When                                          |
|-----------------|-------|-----------------------------------------------|
| **Product Bug** | 10322 | **Default** — actual defect in Redis product |
| Test Code       | 10323 | The bug is in test code, not the product     |

API format: `"customfield_10177": { "id": "10322" }`.

### Reported Version/Build (`customfield_10056`)

**Always add the reported versions.** Multiple comma-separated: `"7.2.4, 6.0.2"`.

### Seen by Customer/s (`customfield_10027`) — ALWAYS REQUIRED for Production tickets

⚠️ **Critical validation rule** (verified live, caught in RED-196654 dry-run):

> When `customfield_10025` (Environment) includes `Production`, the field `customfield_10027` (Seen by Customer/s) is **REQUIRED**. The project workflow rejects the create with `"Seen By Customer is required for Environment/s = Production"` if omitted.

Per Support Confluence docs, this field is "replaced by Affected Organizations" — but the project validation rule is independent. **Set both:**

| Field                            | fieldId             | Value                                    |
|----------------------------------|---------------------|------------------------------------------|
| Affected Organizations (canonical)| `customfield_10595` | `[{"id":"<resolved_id>"}]`               |
| Seen by Customer/s (validation)  | `customfield_10027` | `"<customer_name>"` (plain string)       |

Since TSE bugs are almost always for customer-originated `Environment=Production` issues, treat `customfield_10027` as **always required** — never optional. Set it even when Affected Organizations resolved cleanly. The two fields aren't mutually exclusive; setting both is the canonical approach.

### Affected Organizations (`customfield_10595`)

Select customer name(s) from the dropdown. **This field replaces the old "Seen by Customer/s" field** per Support docs.

The field has **9,253+ options** — enumerating them all is impractical for a single create call. Use this resolution procedure:

#### Resolution procedure

1. **Page through `allowedValues` looking for a match.** Call `getJiraIssueTypeMetaWithFields` with:
   - `cloudId: 06f73ca7-8f2c-4392-b40a-08288e9d0ba3`
   - `projectIdOrKey: RED` (or relevant project)
   - `issueTypeId: 10004` (Bug)
   - `maxResults: 50`
   - `startAt: 0`, then `50`, then `100`, …

   In each response, search `customfield_10595.allowedValues` for a **case-insensitive substring match** on the customer name.

2. **Cap the search at 5 pages (~250 options).** Customer names usually surface in early alphabetical pages. Beyond that, the cost of token usage outweighs the benefit — fall through to the fallback.

3. **If a match is found**:
   ```jsonc
   "customfield_10595": [{ "id": "<resolved_id>" }]   // single-select-from-list format
   ```

4. **If NO match is found** within the search cap:
   - **Skip `customfield_10595` entirely** in the payload.
   - **Set `customfield_10027` (Seen by Customer/s)** to the customer name as a free-text fallback. This field is deprecated per Support docs but still functional, and gives R&D a searchable customer reference.
   - **Add the customer name as a label** (underscored if multi-word) so it's discoverable in JQL.
   - **In the post-create output, explicitly tell the TSE**:
     > "Affected Organizations was not auto-resolved from the dropdown. Please open the new ticket in the browser and select `<customer>` from the Affected Organizations dropdown manually before saving."

5. **Never invent an option ID.** If substring search across the searched pages returns no match, do NOT guess based on similar names. The dropdown is canonical — wrong IDs route the ticket to the wrong account in CS reporting.

#### Multi-customer

If multiple customers are affected, repeat the procedure for each. Concatenate matched options into the array:

```jsonc
"customfield_10595": [
  { "id": "<aetna_id>" },
  { "id": "<cvs_id>" }
]
```

#### Why not query the full list once?

The field has ~9,253 entries. A full fetch (paginated to maxResults=50) is ~185 calls and burns a lot of tokens for a single field lookup. The 5-page cap is a pragmatic trade-off; the free-text fallback is reliable when alphabetical search misses.

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

## RCA Template Block (`customfield_10063`) — Universal, NOT Azure-only

**Populate this on EVERY bug.** This was reclassified in v0.7 after seeing RED-194253 (non-Azure cert-chain bug) with the full template populated.

Send as ADF on the initial `createJiraIssue` payload (not a post-save step):

```
------------------------------
0. Incident short description: <one-line customer-readable description>
1. Bug Description:
2. Which components impacted by this bug?
3. What was fixed?
4. Reproduction steps?
5. Public Blocker Description:
------------------------------
```

**TSE responsibility at file time:**

- **Section 0** — fill in with a one-line customer-readable description. For Azure ACRE/AMR tickets, this is critical because customer-facing automation reads section 0. For non-Azure tickets, still fill it in so the field isn't a wall of placeholder text.
- **Sections 1-5** — leave as placeholders. Engineering / PM fills them during triage and dev.

**ADF format** — see [`jira-schema.md` → "RCA Template Block"](./jira-schema.md) for the exact ADF document structure.

**No post-save edit needed** — the template is part of the initial create payload. If for some reason the create doesn't include it, fall back to an `editJiraIssue` follow-up.

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

## Description Body Template

**Anchored to [`canonical-jiras/RED-194253-bug-cert-chain.md`](./canonical-jiras/RED-194253-bug-cert-chain.md).** Use H2 sections, not a flat label-prefix block. Customer/cluster/subscription/BDB data lives **only** in custom fields — do NOT duplicate them as bolded prefix lines in the description.

```markdown
## Summary

{Single paragraph statement of the problem. Start with the customer-visible symptom,
then narrow to the technical cause hypothesis if known. Reference specific subsystems/
functions affected. Keep under ~150 words.}

## Root Cause                                    [OPTIONAL]

{Only include if TSE+eng have a hypothesis. Code snippets in fenced blocks. Reference
specific files / functions / line numbers. Use bullets / numbered lists for steps in
the broken logic.}

## Customer Impact

{Bullet list. Each bullet = a concrete observable behavior.}
- ...

## Steps to Reproduce

{Numbered list. Each step = concrete action. Sub-steps allowed where setup is complex.}
1. ...

## Expected Behavior

{One short paragraph — what should happen.}

## Actual Behavior

{One short paragraph — what does happen.}

## Evidence from Support Case

{Concrete artifacts: file contents, log excerpts, config snippets, output dumps. Use
fenced code blocks. Use bolded subheaders if you have multiple evidence types.}

**Certificate Chain Uploaded** (...):
    <fenced or indented block with the content>

**trusted_ca.pem Contents:**
    <fenced or indented block>

## Workaround

(see Workaround field — `customfield_10374`)

## Suggested Fix                                 [OPTIONAL]

{Short paragraph or two with the proposed code/behavior change. Only when TSE+eng
have a hypothesis.}

## Related Code Paths                            [OPTIONAL]

{Bulleted list of file paths with function names + line numbers. Only when engineering
analysis is present.}

## Pending Information                           [OPTIONAL]

{Outstanding requests from the customer or open questions for triage.}
- ...

## Related Jiras                                 [OPTIONAL]

{Linked tickets with one-line context. Issue links will also be created separately
via createIssueLink — this section is for human readability.}
- RED-XXXXX — {short context}

## Zendesk Reference

- Ticket: https://redislabs.zendesk.com/agent/tickets/{ticket_id}
```

### Rules

- **No bolded `Label: value` prefix block** at the top. Customer name, cluster/region, subscription, BDB IDs, product all live in fields. Per RED-194253 anchor.
- **No "Customer expectations:" line** in the description body. The Confluence guide says to include customer expectations, but the canonical anchor (RED-194253) doesn't have a literal line — the expectation is implicit through structure (presence of "Suggested Fix" = fix wanted; presence of bug template populated = engineering investigation requested).
- **Sections are optional unless marked otherwise.** A TSE-filed ticket at file-time typically has: Summary, Customer Impact, Steps to Reproduce, Expected, Actual, Evidence, Workaround (heading only), Pending Information, Zendesk Reference. The optional sections (Root Cause, Suggested Fix, Related Code Paths) appear when engineering work has happened.
- **Code/config inline** uses fenced code blocks with language hints when possible (` ```bash `, ` ```python `).
- **Numbered & bulleted lists** are the dominant body format. Plain prose is for Summary, Expected Behavior, Actual Behavior, and short paragraphs in other sections.
- **Active-Active mapping table** goes inside `## Evidence from Support Case` as a sub-table (not its own H2).
- **Log references** in `cluster_name, node_id, shard_id` format inside `## Evidence from Support Case`.
- **Keep total description under ~3000 chars** when possible (RED-194253 is ~2500). Extract relevant content from Zendesk — don't paste the entire thread.

### When no canonical example fits

Pick the closest canonical-jiras entry and add an explicit confidence note in the preview file's pre-flight checks: "Anchor: RED-XXXXX (closest available match for {issue shape}) — review structure carefully."

Suggest the user save the resulting Jira as a new canonical example once filed and reviewed.

## Screenshots & Other Customer-Provided Files (v0.10+)

When a Zendesk PDF is provided, the skill should **also scan the same directory for image attachments** (PNG / JPG / JPEG / GIF / WEBP) and other supplementary files (TXT logs, ZIP, manifest snippets). Customers commonly attach screenshots to Zendesk that we want to carry over to the Jira.

### Discovery

If the user runs `/tse-jira:bug ~/Downloads/packages/<ZD>/ticket.pdf`, the skill should:

1. Inspect the directory containing the PDF (`~/Downloads/packages/<ZD>/`) for sibling image files
2. List them in the dry-run output's preview file so the TSE can confirm they're relevant
3. For each image, decide where it logically belongs in the description body

### Embedding strategy

**The Atlassian MCP does NOT support attachments via `createJiraIssue` or any other tool.** Workaround:

1. **In the description (markdown payload)**: insert image references using markdown syntax `![alt text](filename.png)` at the chosen embed spots. These render as broken/missing images in Jira **until** the files are manually attached.
2. **In the HTML preview**: embed the actual image inline via `<img src="file://<absolute-path>">` so the TSE sees the final layout visually.
3. **In the .md preview**: reference with file paths so VS Code / similar viewers can render the PNG inline.
4. **Post-create checklist**: explicitly remind the TSE to manually attach the images in the Jira browser UI. Once attached, the description's image references resolve.

### Choosing meaningful embed spots

Match image content to description section:

| Image content | Likely section |
|---|---|
| Config / manifest snippet that triggers the bug | `## Steps to Reproduce` (after the textual step that mentions the config) |
| Error screenshot from logs or terminal | `## Evidence from Support Case` (with a subsection title naming the scenario) |
| UI screenshot showing the bug | `## Evidence from Support Case` (with caption explaining what to look at) |
| Architecture / topology diagram | `## Evidence from Support Case` (as a sub-section) |
| Customer's full Terraform / Kubernetes / config file | `## Evidence from Support Case` (with `<details>` collapsible if long) |
| Grafana / monitoring screenshot | Linked from `customfield_10375` (Metrics) field; embedded in description if it's primary evidence |
| Generic "this looks broken" UI shot | `## Actual Behavior` (as supporting visual) |

### Example pattern (Aetna #162249)

The customer provided 3 screenshots. Embed strategy used in the dry-run preview:

```markdown
## Steps to Reproduce

...
2. Write a Terraform manifest using `redis-cloud` provider v2.15 with a `dynamic "override_region"` block:

   ![Override Region block](Override Region block.png)

   The dynamic block iterates over `var.database_regions` and configures `remote_backup` per region with GCS storage.
...

## Evidence from Support Case

### East region failure (us-east4)

![East region terraform apply failure](AA East Fail.png)

Full Terraform diagnostic for us-east4 ... [analysis paragraph]

### West region failure (us-west2)

![West region terraform apply failure](AA West Fail.png)

Identical failure pattern for us-west2, confirming the bug isn't region-specific.
```

### Caption pattern

For each embedded image, follow it with:
- A **1-2 sentence caption** explaining what to look at in the image
- A **filename callout** for the TSE: `📎 Override Region block.png (manually attach to Jira)`
- (Optional) **highlighted clues** — call out specific values, log lines, or fields in the image that are relevant to root-cause analysis (e.g., "Note `time_utc:cty.NullVal(cty.String)` at the bottom — possible null-handling issue")

The skill's job is to **extract value from screenshots** that the TSE might miss if they just looked at the bare PDF — pointing out specific signal in the visual.

### Pre-flight checklist additions

When screenshots are detected, add:

- ✅ `<N> screenshots found and embedded at meaningful spots`
- ⚠️ `Screenshots referenced but NOT attached — MCP doesn't support attachments. TSE must manually attach <filename1>, <filename2>, ... in browser after Jira creation.`

### Sidebar attachment panel (HTML preview)

The HTML preview should include a sidebar section titled **"📎 Attachments to upload"** listing all referenced screenshots so the TSE can copy/paste filenames when attaching.

### Post-create checklist additions

- "Manually attach the N screenshots in the new Jira's browser UI (`<list of paths>`)"
- "Verify image references in description body resolve to inline images once attached"

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
