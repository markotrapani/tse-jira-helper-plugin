# Impact Score Model

Adapted from `jira-helper/src/impact_score_calculator.py` and `intelligent_estimator.py`.

## Formula

```
Base Score = Impact&Severity + CustomerARR + SLABreach + Frequency + Workaround + RCAActionItem
Final Score = Base Score × (1 + SupportMultiplier + AccountMultiplier)
```

- Base range: **8 – 100**
- Multipliers: **0 – 0.15 each** (so total multiplier ∈ [0, 0.30])
- Final range: **8 – 130**

Round final score to one decimal place.

## Components

### 1. Impact & Severity (0 – 38 points)

Based on priority/severity level. Extract from ticket priority field, or infer from impact language.

| Priority | Points | Indicators |
|---|---|---|
| **P1** | 38 | Service down, data loss, security breach, "critical", "production outage" |
| **P2** | 30 | Service degraded, major feature broken, "high severity", widespread impact |
| **P3** | 22 | Functional issue affecting some users, workaround exists, "medium severity" |
| **P4** | 16 | Monitoring/metrics issue, cosmetic, single user, service confirmed stable/functional |
| **P5** | 8 | Documentation, request for info, low-impact question |

### 2. Customer ARR (0 – 15 points)

Annual Recurring Revenue of affected customer. ARR comes from Zendesk account tags or known customer reputation.

| Tier | Points | Criteria |
|---|---|---|
| Very High | 15 | ARR > $1M (single customer) |
| High | 13 | ARR $500K – $1M |
| Medium | 10 | ARR $100K – $500K |
| Many Low | 8 | >10 low-ARR customers affected |
| Few Low | 5 | 2–10 low-ARR customers affected |
| Single Low | 0 | 1 low-ARR customer or unknown ARR |

**VIP customers** (override to 15 even if ARR unknown):
- `monday.com`, `salesforce`, `azure` (Microsoft), key strategic accounts. Maintain this list in deployment-specific notes.

### 3. SLA Breach (0 or 8 points)

Binary: was SLA breached?

| State | Points | Indicators |
|---|---|---|
| Breached | 8 | "SLA breach", "missed SLA", customer escalation due to response/resolution time |
| Not breached | 0 | Service stable/functional, no SLA escalation language |

Be skeptical: many tickets mention "SLA" without indicating an actual breach. Look for explicit breach claims.

### 4. Frequency (0 – 16 points)

How often the issue occurs.

| Frequency | Points | Indicators |
|---|---|---|
| >4 occurrences | 16 | "multiple times", "recurring", "every X hours", explicit count >4, "intermittent over weeks" |
| 2–4 occurrences | 8 | "happened again", "second time", explicit count 2–4 |
| Single | 0 | "first time", one timestamp only, no recurrence language |

### 5. Workaround (5 – 15 points)

Availability and complexity of workaround.

| Workaround | Points | Indicators |
|---|---|---|
| None | 15 | "no workaround", "blocked", "service unusable" |
| Performance impact | 12 | Workaround exists but degrades performance / operational cost ("works but slow", "manual restart required") |
| Complex | 10 | Multi-step workaround, requires expertise / coordination |
| Simple | 5 | One-line config change, restart, well-documented |

Note: minimum is 5, not 0. Some workaround always assumed unless explicitly "none".

### 6. RCA Action Item (0 or 8 points)

Is this ticket part of an RCA?

| State | Points | Indicators |
|---|---|---|
| Yes | 8 | Linked to an RCA ticket, "RCA action item" label, "follow-up from RCA", description references root cause analysis |
| No | 0 | Standalone bug, no RCA linkage |

## Multipliers

Multipliers add 0 – 0.15 each (0 – 15%). Both are optional and default to 0.

### Support Multiplier (0 – 0.15)

Adds urgency for tickets that block the support team's ability to operate.

| Trigger | Multiplier |
|---|---|
| Ticket blocks support team workflow (e.g., diagnostic tooling broken) | 0.10 |
| Customer-facing escalation requiring exec attention | 0.15 |
| Standard ticket | 0.00 |

### Account Multiplier (0 – 0.15)

Adds urgency for accounts at retention risk.

| Trigger | Multiplier |
|---|---|
| Account flagged for retention risk by CSM | 0.15 |
| Customer threatening churn or contract termination | 0.15 |
| New account in onboarding, sensitive to early issues | 0.10 |
| Standard ticket | 0.00 |

## Priority Bands (from Final Score)

| Score range | Band | Action |
|---|---|---|
| 90 – 130+ | **CRITICAL** | Immediate attention, escalate |
| 70 – 89 | **HIGH** | Current sprint priority |
| 50 – 69 | **MEDIUM** | Upcoming sprint |
| 30 – 49 | **LOW** | Backlog |
| 8 – 29 | **MINIMAL** | Defer or close |

## Severity Mapping (Final Score → Jira Severity)

For the Bug workflow's Severity field:

| Final Score | Severity (Jira) |
|---|---|
| ≥ 90 | Very High |
| 70 – 89 | High |
| 50 – 69 | Medium |
| < 50 | Low |

## Priority Mapping (Band → Jira Priority)

For the Bug workflow's Priority field:

| Band | Jira Priority |
|---|---|
| CRITICAL | Highest |
| HIGH | High |
| MEDIUM | Medium |
| LOW | Low |
| MINIMAL | Lowest |

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
| Multipliers | 0 | No support/account flags |
| **Final** | **81 (HIGH)** | |

### Example 2: Documentation typo

| Component | Score | Reasoning |
|---|---|---|
| Impact & Severity | 8 | P5 — doc only |
| Customer ARR | 0 | No ARR data |
| SLA Breach | 0 | n/a |
| Frequency | 0 | Single report |
| Workaround | 5 | Simple — read elsewhere |
| RCA Action Item | 0 | Standalone |
| **Base** | **13** | |
| Multipliers | 0 | |
| **Final** | **13 (MINIMAL)** | |

### Example 3: P1 outage with churn risk

| Component | Score | Reasoning |
|---|---|---|
| Impact & Severity | 38 | P1 — production down |
| Customer ARR | 15 | >$1M customer |
| SLA Breach | 8 | Resolution SLA missed |
| Frequency | 16 | Repeated outages |
| Workaround | 15 | None |
| RCA Action Item | 8 | RCA ticket linked |
| **Base** | **100** | |
| Support multiplier | 0.10 | Blocking support tooling |
| Account multiplier | 0.15 | Customer threatening churn |
| **Final** | **125 (CRITICAL)** | 100 × 1.25 |
