# DOC-6506 — Go-redis Smart Client Handoff lists default EndpointType as EndpointTypeExternalIP instead of EndpointTypeAuto

> **Link:** https://redislabs.atlassian.net/browse/DOC-6506
> **Issue Type:** Bug (id 10004)
> **Project:** DOC (Documentation)
> **Domain:** Documentation / Client libraries / go-redis / smart client / cluster handoff / default values
> **When to use this anchor:** TSE-filed Bug against the DOC project where a public Redis docs page has incorrect technical content (wrong default value, wrong type name, wrong example, etc.) noticed from internal Slack chatter or a customer ticket. Strong reference for "the doc says X but the code/runtime actually does Y" bugs — minimal body, no troubleshooting evidence, just the documentation defect and what should be correct.
> **Added:** 2026-05-12

## Header fields used

| Field            | Value                                                          |
|------------------|----------------------------------------------------------------|
| Project          | Documentation (DOC)                                            |
| Type             | Bug                                                            |
| Priority         | High                                                           |
| Status           | Complete (resolution: `Done`)                                  |
| Reporter         | TSE who filed (Louis Scheffer)                                 |
| Assignee         | Docs engineer (Andrew Gareth Stark)                            |
| Labels           | `Support`                ← only 1 label                         |
| Components       | None                                                           |
| Affects versions | None                                                           |
| Fix versions     | None                                                           |
| Sprint           | Sprint 206 (engineering set later)                             |
| Effort           | XS                                                             |

## Custom fields populated

| fieldId               | Name                   | Value                                                       |
|-----------------------|------------------------|-------------------------------------------------------------|
| —                     | Severity               | **NOT populated** (DOC bugs don't carry the RED severity field) |
| —                     | Component (single-select) | **NOT populated** in DOC (no Cluster/CM-style routing field) |
| `customfield_10595`   | Affected Organizations | `[Zepto]`                                                   |
| `customfield_10585`   | Impact Score           | `36`                                                         |
| —                     | Man days               | `0`                                                          |
| —                     | Effort                 | `XS`                                                         |

DOC-specific observations:
- **No `Severity` field shown** on DOC bugs (unlike RED/MOD which always populate `1 - High` / `2 - Medium` / etc.).
- **No `Component` single-select** field shown (DOC doesn't route by Cluster/CM/Modules sub-team).
- **No `Environment/s` / `Product/s` / `Seen by Customer/s` fields shown** (DOC doesn't carry the production-customer routing fields RED uses).
- **No `Zendesk ID/s` field shown** here — DOC bugs can originate from internal Slack rather than a Zendesk ticket.
- **No `Found By` / `Issue source` fields shown** (those are RED-specific).
- **No `RCA` template field** populated (DOC bugs don't use the 6-section bug RCA template).
- **`Impact Score details` table** does appear on DOC bugs — same impact scoring framework as RED/MOD, even without all the other custom fields.

## Description body structure

Very lean. **No H2 sections.** Just a 2-3 sentence statement of what the doc says vs. what's actually true, with an inline link to the doc page and (optionally) a screenshot/quote of the offending text.

```markdown
An issue with the [go-redis Smart Client Handoff documentation](<link>) was noticed in
#ask-client-libs.

> This documentation page is incorrect. The default is Auto for all clients, the fqdn is
> reported from the server…

<inline screenshot or quoted text from the doc page showing the wrong content>
```

### Section observations from DOC-6506

- **Single paragraph + blockquote** describing the defect — no Steps to Reproduce, no Expected/Actual, no Workaround, no Suggested Fix.
- **Quoted excerpt from the doc page** shows the literal incorrect text. In this case: `EndpointType: ... The default is EndpointTypeExternalIP.`
- **Source attribution** — TSE notes WHERE they noticed the discrepancy (`#ask-client-libs` Slack channel). For DOC bugs originating from a customer ticket, would replace with Zendesk reference.
- **Attached screenshots** (`image-20260422-181650.png`, `image-20260422-182847.png`) provide visual proof — common pattern for DOC bugs.

## Related issue linking pattern

- **`Relates`** link to a related CAE (client-libs) ticket: `CAE-2793 Client dialup timeout in go-redis when...` — this DOC bug was noticed during investigation of a runtime client-libs issue, so the docs fix relates to the upstream client issue. Pattern: when a TSE finds a doc defect while debugging a client problem, link the runtime ticket as `relates to`.

## Notes / nuances

- **Priority `High` but no Severity field** — DOC bugs use priority, not the RED/MOD severity scale.
- **Single `Support` label** — same minimal labeling as a lean RED bug. No `CS`, no `client-libs`, no `Documentation` label.
- **Resolution `Done`** when the doc page is corrected (not `RCA Provided` — doc bugs always have a concrete fix or they get rejected as "Won't Fix").
- **Effort field (XS / S / M / L)** appears on DOC bugs — sizes the writing effort. TSE leaves blank at file time; docs team sets later.
- **No `Affected Organizations` requirement** but it IS populated here (`Zepto`) — useful when the doc bug came from a real customer interaction even if filed via Slack. Optional in DOC.
- **No description-body customer-name prefix** — same as RED-194253. The customer name lives only in the field.
- **Cross-reference**: when a doc bug is discovered while triaging a real customer issue, also leave a Zendesk ID/s value if the DOC project has that field; otherwise leave the link in the description body.
- **Compare to RED-186235** (low-severity UI bug) for shape; both are lightweight, but DOC bugs lack the RED Severity / SM Component / Found By scaffolding entirely.
