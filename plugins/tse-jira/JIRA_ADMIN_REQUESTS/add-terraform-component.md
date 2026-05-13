# JIRA Admin Request — Add `Terraform Provider` component to RED project

> **Status:** Draft (not yet filed). Marko Trapani to file at his convenience.
> **Project affected:** RED (Redislabs / id 10020)
> **Field affected:** Component (`customfield_10181`) on Bug issue type (id 10004)
> **Filed by:** Marko Trapani (marko.trapani@redis.com)
> **Drafted:** 2026-05-13 (during tse-jira v0.14.0 development)

## Background

The `redis/rediscloud` Terraform provider ([github.com/RedisLabs/terraform-provider-rediscloud](https://github.com/RedisLabs/terraform-provider-rediscloud)) is an increasingly common surface area for customer-facing bugs. In 2026 alone, Support has filed multiple TF-provider bugs against the RED project:

| Filed | Topic | Component picked (current) | Component WE wanted |
|---|---|---|---|
| RED-196844 (2026-05-13) | `Provider produced inconsistent result after apply` when setting `remote_backup` in `override_region` for A-A database | Cloud API | Terraform Provider |
| (older similar tickets exist for CMEK / pending-subscription / GCP edge cases) | various | various | Terraform Provider |

Because no `Terraform Provider` component exists today, Support TSEs default to **`Cloud API`** as the closest proxy. That works for routing but introduces two problems:

1. **R&D triage signal is lost.** A bug routed to `Cloud API` is mixed in with non-TF Cloud-API issues. The TF-provider owners (a different sub-team / repo) have to filter through unrelated Cloud-API tickets to find their backlog.
2. **Cross-ticket discovery breaks down.** A TSE looking for "all TF-provider bugs filed in Q2" can't filter by component — they'd have to grep titles / labels.

## Request

Please add a new option to the `Component` field (`customfield_10181`) on the RED project, with the following properties:

- **Option name (visible label):** `Terraform Provider`
- **Description (visible to TSEs / R&D):** "Issues in the `redis/rediscloud` Terraform provider — schema bugs, plan/apply inconsistencies, missing fields, version-specific regressions. The provider repo is github.com/RedisLabs/terraform-provider-rediscloud."
- **Auto-assignee (if your Jira instance supports component default assignees):** the TF-provider squad's lead, or whoever currently owns issues in `RedisLabs/terraform-provider-rediscloud`.

## Confirmation

Once added, please reply with:

1. The option ID assigned to the new component (so I can update the `tse-jira` plugin's reference docs).
2. Whether component default-assignee is configured.

## What changes in the `tse-jira` plugin when this is added

The plugin's `references/jira-schema.md` includes a list of valid RED Bug components and how the skill auto-detects them. Once Admin confirms the new option exists, I'll:

1. Update `references/jira-schema.md` → "RED Bug Components" list to include `Terraform Provider`.
2. Update `references/zendesk-bug-mapping.md` → component auto-detection rules to route TF-provider bugs to the new component (signals: `redis/rediscloud` provider mentioned, `terraform apply` failure, override_region / remote_backup / CMEK schema errors, `terraform-provider-rediscloud` GitHub references in the Zendesk).
3. Backfile: where possible, update existing TF-provider bugs that were routed to `Cloud API` to use the new component instead (TSE-judgment per ticket).

## Background reading (R&D context)

For Admins or stakeholders curious about the volume:

- `redis/rediscloud` is published to the Terraform Registry at https://registry.terraform.io/providers/redislabs/rediscloud
- Active development: github.com/RedisLabs/terraform-provider-rediscloud
- Recent releases (v2.13 / v2.14 / v2.15 in Feb–May 2026 alone) suggest ongoing schema churn and bug surface area
- Common bug shapes:
  - Plan↔Apply state-correlation failures (RED-196844 is the canonical recent example)
  - Schema mismatches between provider version and Redis Cloud API
  - CMEK / encryption configuration edge cases on subscription operations

## Where to file this request

TBD per Redis JIRA Admin process. Likely candidates:

- An OPCR ticket assigned to the Jira Admin team
- A direct Slack request in `#jira-admin` (or whatever the equivalent channel is)
- A Confluence-page request form

Marko: pick the path that works in your org. The text above is ready to paste into whichever vehicle you use.

## After filing

Update this file with:

- The OPCR ticket ID (or other tracker reference)
- The date filed
- The status (filed / in-progress / done)
- The assigned option ID once Admin confirms

Then file a `tse-jira` plugin version bump (probably v0.14.x docs patch) to reflect the new component in `references/jira-schema.md`.
