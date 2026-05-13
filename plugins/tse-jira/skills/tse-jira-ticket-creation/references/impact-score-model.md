# Impact Score Model

**Authoritative source**: [Jira - Impact Score (DevOps space, page 4267671553)](https://redislabs.atlassian.net/wiki/spaces/DevOps/pages/4267671553).

The impact score is relevant across all Redis platforms — AMR, Redis Cloud, Redis Software.

## Who Fills It

Per the Confluence doc, **the score should be filled by the team leader of the reporting team** (Support / CS / CloudOps), not by individual TSEs unilaterally.

> The skill computes the score as a recommendation. The team leader confirms / adjusts before it goes on the ticket. The skill should explicitly flag this when generating a score.

## Guidance Rules

From the impact score doc:

1. Scores may change as more details or incidents surface — treat as living.
2. **If in doubt, lean towards the lower score** since R&D is highly occupied with many tickets we open.

## Formula

```
Base Score = Impact&Severity + CustomerARR + SLABreach + Frequency + Workaround + RCAActionItem
Final Score = Base Score × (1 + CloudOpsMultiplier + CustomerMultiplier)
```

- Base range: **8 – 100**
- Multipliers: **0 – 0.15 each** (so total multiplier ∈ [0, 0.30])
- Final range: **8 – 130**

**The final score MUST be stored as an integer in `customfield_10585`.** Round to the nearest whole number; per the "if in doubt, lean lower" guidance, prefer floor on ties (e.g., `56.5 → 56`, not `57`).

## Components

### 1. Impact & Severity (0 – 38 points)

Reflects the severity AND the impact caused by the bug — not necessarily on the customer, but also on other components (SM, control plane, etc.). Severity is measured **both** by the **magnitude** of the impact and **how long** it lasted. Can also reflect **potential impact**, scored by probability of happening.

| Priority | Points | Definition (from Confluence) |
|---|---|---|
| **P1** | 38 | Single service in a **stopped** state with no backup or redundancy. Multiple services in a **degraded** state. Immediate financial or security impact to customers/partners or the business. |
| **P2** | 30 | Single service in a **degraded** state. Immediate financial or security impact to customers/partners business. |
| **P3** | 22 | Non-critical business service is **stopped** or severely **degraded**. Critical business service at risk of entering a degraded/stopped state. Possible financial or security impact. |
| **P4** | 16 | Non-critical business service at risk of entering a degraded/stopped state. |
| **P5** | 8 | No current or potential impact — more of an INFO. (Question: is a Jira required?) |

### 2. Customer ARR (0 – 15 points)

Whether a VIP customer is involved + their ARR. Can be updated if non-VIPs are initially impacted and a VIP joins later.

| Tier | Points | Criteria |
|---|---|---|
| Very High | 15 | ARR > $1M |
| High      | 13 | $500K < ARR ≤ $1M |
| Medium    | 10 | $100K < ARR ≤ $500K |
| Many Low  | 8  | >10 low-ARR customers affected |
| Few Low   | 5  | <10 low-ARR customers affected |
| Single Low| 0  | Single low-ARR customer |

ARR source spreadsheet (internal): https://docs.google.com/spreadsheets/d/1E2qBdR3MD9gq20el8CzwjvN44BLtcq7SE6fKG3fJYD4/

### 3. SLA Breach (0 or 8 points)

For Redis Cloud, reference the [SLA agreement](https://redis.io/legal/redis-cloud-service-level-agreement/). For Redis Software, calculate based on outage length.

**Thresholds:**

| Topology     | Redis Cloud      | Redis Software    |
|--------------|------------------|-------------------|
| Active-Active| 99.999% (26s/month, 5m13s/year) | > 5 min downtime |
| Multi-AZ     | 99.99% (4m21s/month, 52m9.8s/year) | > 1 hour downtime |
| Single-AZ (HA) | 99.9% (43m28s/month, 8h41m38s/year) | > 9 hours downtime |

| State        | Points | Indicators |
|--------------|--------|-----------|
| Breached     | 8      | Outage exceeded thresholds; explicit SLA claim in ticket |
| Not breached | 0      | Within thresholds |

Be skeptical: many tickets mention "SLA" without indicating an actual breach. Look for explicit breach claims or use the outage length to compute.

### 4. Frequency (0 – 16 points)

A single event scores lower; repeating events score higher.

| Frequency       | Points | Indicators |
|-----------------|--------|------------|
| Single          | 0      | "first time", one timestamp only |
| 2–4 occurrences | 8      | "happened again", "second time", count 2–4 |
| > 4 occurrences | 16     | "multiple times", "recurring", "every X hours", count >4 |

### 5. Workaround (5 – 15 points)

Ease of applying the workaround and its impact both matter.

| Workaround             | Points | Description |
|------------------------|--------|-------------|
| Single command, no impact | 5  | One-line config change, restart, well-documented |
| Complex steps, no impact  | 10 | Multi-step but performance unaffected |
| Any steps, performance impact | 12 | WA works but degrades performance / operational cost |
| No workaround             | 15 | Requires a new version / fix |

Minimum is 5 (not 0). Some workaround almost always assumed unless explicitly "none".

### 6. RCA Action Item (0 or 8 points)

Tickets that represent an action item of an ongoing RCA score higher — customer empathy and world-class service require these to be high priority.

| State                    | Points | Indicators |
|--------------------------|--------|-----------|
| Part of an RCA action item | 8 | Linked to an RCA ticket; "RCA action item" label; description references RCA |
| Not part of RCA           | 0 | Standalone bug |

## Multipliers

Multipliers add 0 – 0.15 each (0 – 15%). Both optional, default 0. **Names per Confluence**: `CloudOps Multiplier` and `Customer Multiplier` (not "Support" or "Account" — those were my earlier mis-naming).

### CloudOps Multiplier (0 – 0.15)

Some bugs/features have a relatively lower base score but block upcoming versions or pose high risk to service.

| Trigger | Multiplier |
|---|---|
| Blocker for upcoming release | 0.10 – 0.15 |
| High operational risk | 0.10 |
| Standard ticket | 0.00 |

### Customer Multiplier (0 – 0.15)

Cases that impact deal closures, customer confidence, and ongoing efforts by customer-facing teams. Quantifying the impact is not always necessary — judgment call by customer-facing teams.

| Trigger | Multiplier |
|---|---|
| Renewal at risk | 0.15 |
| Customer threatening churn | 0.15 |
| Trust impact / new account in onboarding | 0.10 |
| Standard ticket | 0.00 |

## Priority Bands (from Final Score)

| Score range | Band | Action |
|---|---|---|
| 90 – 130+ | **CRITICAL** | Immediate attention, escalate |
| 70 – 89   | **HIGH** | Current sprint priority |
| 50 – 69   | **MEDIUM** | Upcoming sprint |
| 30 – 49   | **LOW** | Backlog |
| 8 – 29    | **MINIMAL** | Defer or close |

**Note**: These bands inform *prioritization expectations* communicated to R&D. The Jira `Priority` system field is **separately** left at `Medium` on creation (PM sets it during triage). The Jira `Severity` custom field is **separately** set by the TSE based on customer impact (see `zendesk-bug-mapping.md`). Don't conflate the three.

## Worked Examples

### Example 1: Azure DMC High CPU (real incident shape)

| Component | Score | Reasoning |
|---|---|---|
| Impact & Severity | 30 | P2 — service degraded across 4 clusters |
| Customer ARR | 15 | Azure (>$1M) |
| SLA Breach | 0 | No breach claim |
| Frequency | 16 | 4+ occurrences across 3 weeks |
| Workaround | 12 | Manual DMC restart works but operationally expensive |
| RCA Action Item | 8 | Linked RCA exists |
| **Base** | **81** | |
| CloudOps multiplier | 0 | Not a release blocker |
| Customer multiplier | 0 | No churn/renewal flag |
| **Final** | **81 (HIGH)** | |

### Example 2: Documentation typo

| Component | Score | Reasoning |
|---|---|---|
| Impact & Severity | 8 | P5 — doc only, INFO |
| Customer ARR | 0 | Single low-ARR / unknown |
| SLA Breach | 0 | n/a |
| Frequency | 0 | Single report |
| Workaround | 5 | Simple — read elsewhere |
| RCA Action Item | 0 | Standalone |
| **Base** | **13** | |
| **Final** | **13 (MINIMAL)** | |

### Example 3: P1 outage with churn risk

| Component | Score | Reasoning |
|---|---|---|
| Impact & Severity | 38 | P1 — production down, security impact |
| Customer ARR | 15 | >$1M customer |
| SLA Breach | 8 | Outage exceeded thresholds |
| Frequency | 16 | Repeated outages |
| Workaround | 15 | None |
| RCA Action Item | 8 | RCA ticket linked |
| **Base** | **100** | |
| CloudOps multiplier | 0.10 | Blocker for upcoming release |
| Customer multiplier | 0.15 | Customer threatening churn |
| **Final** | **125 (CRITICAL)** | 100 × 1.25 |

## Posting on the Ticket

Real TSE practice (refined 2026-05-13 after RED-196844 production-filing review; supersedes both earlier "post a comment" and "add `## Impact Score` H2 to body" guidance):

1. **Compute the score** using the [Impact Score Google Sheet](https://docs.google.com/spreadsheets/d/13HQaZGXtsRi0hWxqU0oQXTmQw1LfnnrkBGl3Y5-c1Sk/edit?gid=0#gid=0). Each ticket gets a row; the sheet does the math.
2. **Set `customfield_10585`** (Impact Score) to the **integer** final score.
3. **Populate `customfield_10681`** (Impact Score details) with an ADF document containing the 6-component breakdown. This is the **dedicated UI section** rendered below the description body — content does NOT go in a description-body H2 section.
4. **Take a screenshot** of the row in the Google Sheet showing the breakdown; **paste it into the Impact Score details field** in the browser after `createJiraIssue` succeeds. The textual breakdown in `customfield_10681` acts as a fallback in case the screenshot isn't pasted.

**Do NOT:**
- Add an `## Impact Score` H2 section in the description body. The breakdown lives in `customfield_10681`, not the body. (This corrects the earlier rule that said "body H2".)
- Call `addCommentToJiraIssue` with the breakdown — no post-create comment.

Why integer-only: the field is consumed by triage tooling that treats it as a whole number. Per the "if in doubt, lean lower" guidance, prefer floor on ties (e.g., `56.5 → 56`).

### ADF skeleton for `customfield_10681`

⚠️ **Do NOT include a "Max" column** in the breakdown table. It duplicates info already in the component definitions in this doc and is visual filler in the rendered Jira UI. Use 3 columns only: Component / Score / Reasoning. Similarly, do NOT use `<X>/38` denominator-inline syntax — just `<X>`.

Use a 3-column ADF table (Component / Score / Reasoning) followed by Base / CloudOps mult / Customer mult / Final rows. Per the RED-196844 (Aetna TF bug) production filing pattern:

```jsonc
{
  "type": "doc", "version": 1,
  "content": [
    { "type": "paragraph", "content": [
      { "type": "text", "text": "Final Score: <N> (<BAND>)", "marks": [{"type":"strong"}] },
      { "type": "text", "text": " — Base <B> × (1 + <CloudOps_mult> + <Customer_mult>) = <raw> → floored to <N> per \"lean lower\" guidance." }
    ]},
    { "type": "table", "attrs": {"isNumberColumnEnabled": false, "layout": "default"}, "content": [
      // Header row: Component / Score / Reasoning
      { "type": "tableRow", "content": [
        { "type": "tableHeader", "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Component" }]}]},
        { "type": "tableHeader", "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Score" }]}]},
        { "type": "tableHeader", "content": [{ "type": "paragraph", "content": [{ "type": "text", "text": "Reasoning" }]}]}
      ]},
      // 6 component rows (Impact & Severity, Customer ARR, SLA Breach, Frequency, Workaround, RCA Action Item)
      // — each: tableCell{Component-name} / tableCell{integer-score} / tableCell{one-line-reasoning}
      // Then Base row: bold "Base" / bold integer / empty cell
      // Then CloudOps mult. row: name / "0.NN" / reasoning
      // Then Customer mult. row: name / "0.NN" / reasoning
      // Then Final row: bold "Final" / bold integer / "Band: <BAND>. Raw <raw> → floored per 'lean lower'."
    ]},
    { "type": "paragraph", "content": [
      { "type": "text", "text": "Sheet link: " },
      { "type": "text", "text": "Impact Score Sheet (row to be added for <new-key>)",
        "marks": [{"type":"link","attrs":{"href":"https://docs.google.com/spreadsheets/d/13HQaZGXtsRi0hWxqU0oQXTmQw1LfnnrkBGl3Y5-c1Sk/edit?gid=0#gid=0"}}]}
    ]},
    { "type": "paragraph", "content": [
      { "type": "text", "text": "Screenshot of the Sheet row to be pasted here by TSE after manually adding the row.", "marks": [{"type":"em"}] }
    ]},
    { "type": "paragraph", "content": [
      { "type": "text", "text": "Score is a recommendation pending team leader confirmation." }
    ]}
  ]
}
```

See also: [`zendesk-bug-mapping.md`](./zendesk-bug-mapping.md) → "Description body vs custom-field sections" for the complete field-destination map.
