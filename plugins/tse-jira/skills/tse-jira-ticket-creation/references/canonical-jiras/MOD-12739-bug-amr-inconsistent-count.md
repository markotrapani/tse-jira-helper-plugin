# MOD-12739 — AMR - Inconsistent count results

> **Link:** https://redislabs.atlassian.net/browse/MOD-12739
> **Issue Type:** Bug (id 10004)
> **Project:** MOD (RedisModules)
> **Domain:** AMR / Azure Managed Redis / RediSearch / topology validation / coordinator connection management / silent timeout / shard fan-out
> **When to use this anchor:** TSE-filed Bug in MOD project for an **Azure Managed Redis (AMR)** customer — query results returning inconsistent counts due to coordinator-shard topology inconsistency. Strong reference for: (1) any AMR bug shape with the `AMR`, `Azure-Integration` labels and `ICM ID/s`, (2) module connection-management bugs traceable to a specific code path, and (3) bugs where the customer has limited cluster access (no shard SSH) and the TSE coordinates with the Azure PG team via ICM.
> **Added:** 2026-05-12

## Header fields used

| Field            | Value                                                          |
|------------------|----------------------------------------------------------------|
| Project          | RedisModules (MOD)                                             |
| Type             | Bug                                                            |
| Priority         | High                                                           |
| Severity         | (not shown explicitly — Impact Score 103 indicates high impact) |
| Status           | Closed (resolution: `Done`)                                    |
| Components       | `RedisAI, RediSearch` (multi-select — MOD-specific)            |
| Affects versions | `RediSearch v2.10.20`                                          |
| Fix versions     | `RediSearch v8.2.11 - priv`, `v8.4.8 - priv`, `v2.10.29 - priv`, `v8.6.5 - priv` |
| Labels           | `AMR`, `Azure-Integration`, `RCA_received`, `Urgent` ← 4 labels |
| Parent / Epic    | RediSearch - Production issues (MOD-2120)                      |
| Sprint           | Sprint 202-206 - AI/ML (multi-sprint — engineering)            |
| Reporter         | TSE who filed (Ofir Yanai)                                     |
| Assignee         | Engineer (Omer Lerman)                                         |

## Custom fields populated

| fieldId               | Name                   | Value                                                       |
|-----------------------|------------------------|-------------------------------------------------------------|
| —                     | Reported Version/Build | `7.28.0-68142941771` (Azure tenant version)                  |
| `customfield_10025`   | Environment/s          | `[Production]`                                              |
| `customfield_10595`   | Affected Organizations | `[Azure]` (NOT the end-customer name — Azure is the tenant) |
| —                     | Seen by Customer/s     | `Azure`                                                     |
| `customfield_10036`   | Zendesk ID/s           | `155624`                                                     |
| `customfield_14258`   | ICM ID/s               | `51000000778925`        ← **AMR-specific routing**          |
| `customfield_10585`   | Impact Score           | `103`                                                        |
| `customfield_10115`   | Found by               | `Community` (MOD-specific value — not RED's `Prod/Customer`)|
| `customfield_10063`   | RCA                    | 6-section template, sections 0-4 **all populated by TSE** because Azure automation reads this field |
| —                     | BugScore               | `300` (MOD-only computed field)                              |
| —                     | Is Bug Description Set | `Yes`                                                        |

## AMR-specific markers (most distinctive)

This is the **canonical AMR-shape bug**:

1. **Labels include both `AMR` and `Azure-Integration`** (plus `Urgent` for severity escalation and `RCA_received` after closure)
2. **`ICM ID/s` field is populated** (`51000000778925`) — ICM is Microsoft's Incident Communication Management system. Required for Azure-routed bugs.
3. **`Affected Organizations = Azure`** — the customer here is Azure / Microsoft, NOT the end-customer. The TSE doesn't have direct contact with the underlying customer.
4. **`Seen by Customer/s = Azure`** — same reason.
5. **`Found By = Community`** — MOD-specific value used when the bug arrives via the Azure PG team (not directly from a paid customer).
6. **RCA template (`customfield_10063`) sections 0-4 are filled at file time** — because Azure's customer-facing automation reads section 0 ("Incident short description") and section 1 ("Bug Description"). TSE MUST populate these on AMR tickets; can be placeholders on non-AMR tickets.

## Description body structure

Investigation-heavy, comment-driven. The Jira body itself is relatively short — a single H1/H2 with customer context, commands used, and an attachment summary. The deep investigation lives in comments + the RCA template field.

```markdown
See <github-issue-link>

Customer issue:
<1-2 sentence description of symptoms with concrete numbers — e.g., "counts varying intermittently between 449 and 421">

Client: Tested with redis-cli
Cluster: Multi-shard configuration (Europe region cluster with fewer shards works fine).
Start Time: <ISO timestamp>

Commands Used:
Search count query:
    FT.SEARCH device_idx '(@HierL1:{7} @HierL2:{240} @HierL3:{40})' LIMIT 0 0 TIMEOUT 15000

Aggregate count query:
    FT.AGGREGATE device_idx '(@HierL1:{7}
    @HierL2:
    {240}
    @HierL3:
    {40}
    )' GROUPBY 0 REDUCE COUNT 0 AS total TIMEOUT 15000

Document check:
    FT.AGGREGATE device_idx '(@Id:
    {643610}
    )' TIMEOUT 5000 SORTBY 2 @Id ASC LOAD * LIMIT

Direct Redis check:
    HGETALL Device:Device:643610

Index info
    FT.INFO device_idx

Customer's Analysis:
- <bullet 1>
- <bullet 2>
- <bullet 3>

Workaround
<short paragraph: customer-side mitigation, e.g., "created new Redis resource, reindexed all data">

Cx ask: <one-line customer request, e.g., "Confirm if RediSearch module updates occurred after Oct 31. Along with the RCA and a refund">

— Cache details —
Name: <cache-name>
Location: <region>
Sku: <Balanced_B100 / etc.>
GoalStatus: Active
CurrentStatus: Running
RedisVersion: 7.4
Modules: Name: search, Semantic Version: 2.10.20

The newly created cache details:
— Cache details —
Name: <new-cache-name>
...

Permalink: Redis Cache Links - <azure-redis-cache-links-url>

FT.PROFILE, FT.SEARCH, and FT.INFO outputs in Archive.zip
<attachment-link>
```

### Section observations

- **No `## Summary` H2** — flat narrative starting with a GitHub issue link.
- **Commands shown as inline code blocks** with consistent labeling (`Search count query:`, `Aggregate count query:`, etc.).
- **"Cache details" blocks** — two of them when comparing before/after, with strike-through formatting (`-Cache details-`) to delimit. Specific to AMR where customer environments are Azure cache resources, not on-prem clusters.
- **Azure-specific permalink** to Redis Cache Links portal (`redislinks.azurewebsites.net/mds/enterprise/...`) — preserves the deep-link for the SRE team to fetch logs/metrics later.
- **"Cx ask:"** prefix — preserves customer's verbatim request (RCA + refund in this case).
- **GitHub issue link first** — many MOD bugs originate from upstream GitHub issues; the TSE preserves the link as the entry point.

## RCA field content (`customfield_10063`) — populated, not placeholder

For AMR bugs, ALL sections get populated at file time. From MOD-12739:

```
0. Incident short description:
Search queries returning inconsistent results on one cache, same queries return expected results on another cache.

1. Bug Description:
We are observing behavior that suggests some shards operate with an outdated or incorrect cluster topology
as received via DMC search.clusterset.
Indicated by the logs:
02-05-2026 15:24:13.000<search> Topology validation failed: not all nodes connected/var/opt/redislabs/log/redis-28.log24091
...

Connection management bug:
When the TCP connection between the coordinator and one of its shards drops, the connection manager attempts
to reconnect by initiating an async connect via libuv. If that connect attempt fails immediately (e.g. with
ECONNREFUSED), the connect callback handles the error but fails to schedule a reconnect timer, leaving the
connection state machine in a dead state. Even after the shard becomes reachable again, no further reconnect
is ever attempted, causing all subsequent FT.SEARCH queries to permanently return partial results until
the process is restarted.

2. Which components impacted by this bug?
Redis Search Connection management

3. What was fixed?
Setting a timeout for every connection

4. Reproduction steps?
Reproduction: Block outgoing traffic from one RediSearch shard to another using iptables -j DROP (or REJECT)
and kill the existing connection with ss -K, forcing a reconnect attempt to an unreachable host. The new
connection will stay stuck in Connecting state indefinitely because MRConn_Connect doesn't set connect_timeout
in redisOptions, so hiredis never schedules a watchdog timer and the ConnectCallback never fires.

5. Public Blocker Description:
(blank / TBD)
```

## Notes / nuances

- **MOD `Components` is MULTI-select** (`RedisAI, RediSearch`) — confirm vs RED single-select.
- **`Found by = Community`** for MOD AMR bugs (not `Prod/Customer`). The Azure PG team is treated as community for Found By routing.
- **`RCA_received` label** — added by Azure automation when R&D fills in the RCA template enough to satisfy Azure's customer-facing API. TSE shouldn't add this on creation.
- **`Urgent` label** — used for high-impact AMR bugs alongside the standard `AMR` / `Azure-Integration` pair.
- **`BugScore: 300`** — MOD-specific computed impact score (separate from Impact Score 103). Different scale, different formula. Don't populate at file time; team computes.
- **Multiple `Fix versions`** because RediSearch ships fixes to multiple parallel branches (`v8.2.11`, `v8.4.8`, `v2.10.29`, `v8.6.5`) — engineering populates after backport. TSE leaves blank at creation.
- **Sprint field with 5 sprints** is engineering's churn record — TSE leaves blank.
- **Many attachments** (15+) — profile dumps, FT.SEARCH outputs, FT.INFO outputs, RDB exports, log files. AMR investigation is attachment-heavy because the TSE can't run commands directly.
- **`Is Bug Description Set: Yes`** custom Boolean signals that the bug description meets Azure's quality criteria for forwarding to MS PG.
- **Cross-reference**: For non-AMR MOD bugs see `MOD-14916-bug-modules-perf-upgrade.md` (LTK customer, no AMR/Azure-Integration label, no ICM ID).
