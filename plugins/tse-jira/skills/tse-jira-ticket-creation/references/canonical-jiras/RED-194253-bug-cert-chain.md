# RED-194253 — Intermediate CA certificates not added to trusted_ca.pem when uploading 3-level certificate chain for INE

> **Link:** https://redislabs.atlassian.net/browse/RED-194253
> **Issue Type:** Bug (id 10004)
> **Domain:** Encryption / TLS / certificate chain / INE / multi-level PKI
> **When to use this anchor:** Code-level bugs in cluster components where:
> - The TSE has done deep technical investigation (with engineer collaboration)
> - There's a clear root cause with specific code references
> - Steps to reproduce are concrete
> - A workaround exists but is operationally painful
> - The customer has an active support package available
> **Added:** 2026-05-12

## Header fields used

| Field            | Value                |
|------------------|----------------------|
| Project          | Redislabs (RED)      |
| Type             | Bug                  |
| Priority         | Medium (default)     |
| Severity         | `2 - Medium`         |
| Status           | To Do                |
| Reporter         | (TSE who filed)      |
| Assignee         | Unassigned (default) |
| Labels           | `Encryption`, `Support`  ← just 2 |
| Components       | None                 |
| Affects versions | Master               |
| Sprint           | (blank)              |

## Custom fields populated

| fieldId               | Name                   | Value pattern                                                        |
|-----------------------|------------------------|----------------------------------------------------------------------|
| `customfield_10180`   | Severity               | `2 - Medium`                                                          |
| `customfield_10181`   | Component              | `Cluster` (single-select; routes to Cluster team)                     |
| `customfield_10025`   | Environment/s          | `[Production]`                                                        |
| `customfield_10026`   | Product/s              | `[RS (Redis Software)]`                                               |
| `customfield_10595`   | Affected Organizations | `[<Customer Name>]` (e.g. "PNB Metlife")                              |
| `customfield_10027`   | Seen by Customer/s     | `<Customer Name>` (validation requirement when Environment=Production) |
| `customfield_10036`   | Zendesk ID/s           | numeric only (e.g. `"160185"`)                                        |
| `customfield_10585`   | Impact Score           | integer/float (e.g. `40`)                                             |
| `customfield_10115`   | Found By               | `Prod/Customer` (id 10149) — TSE default for customer-reported bugs   |
| `customfield_10177`   | Issue source           | `Product Bug` (id 10322) — TSE default for actual defects             |
| `customfield_10063`   | RCA                    | **6-section template** (general, NOT Azure-only) — see RCA Template Block below |
| `customfield_10374`   | Workaround             | ADF with paragraphs + code blocks (see Workaround content below)      |

## RCA Template Block (`customfield_10063`)

Every bug at file-time should have this template seeded. The TSE fills in section 0 immediately; sections 1-5 get filled in by Engineering / PM during triage and dev:

```
------------------------------
0. Incident short description:
1. Bug Description:
2. Which components impacted by this bug?
3. What was fixed?
4. Reproduction steps?
5. Public Blocker Description:
------------------------------
```

For Azure ACRE/AMR tickets specifically, the customer-facing automation reads section 0, so it must be populated at file time with a customer-readable one-liner.

For non-Azure tickets, sections 1-5 just get filled later — leave them as placeholders.

## Description body structure (the important part)

Real H2-sectioned body. Each section has a clear purpose. **No bolded `Label: value` prefix block at the top** — that data lives in fields.

```markdown
## Summary

<Single paragraph statement of the problem. Start with the customer-visible symptom, then narrow to the technical
cause hypothesis if known. Reference the specific subsystem/function affected. Keep under ~150 words.>

Example (from RED-194253):
> When a customer uploads a certificate chain with 3 or more levels (Leaf → Intermediate CA → Root CA)
> for `data_internode_encryption`, only the Root CA is extracted and added to `trusted_ca.pem`. The
> intermediate CA certificate is NOT added, causing TLS client verification to fail when components
> like DMC/Syncer connect to Redis shards.

## Root Cause                                    ← OPTIONAL (only if TSE+eng have a clear hypothesis)

<Technical explanation. Include code snippets in fenced blocks when relevant. Reference specific files,
functions, line numbers. Use bulleted/numbered lists for steps in the broken logic.>

Example (from RED-194253):
> The function `extract_ca_from_cert_chain()` in `cnm/cnm/certificates/operations.py` only extracts
> self-signed certificates (where `subject == issuer`) to add to the trust store:
>
>     def extract_ca_from_cert_chain(ordered_chain: str) -> tuple[Optional[str], str]:
>         ...
>         root_cert = certificates[-1]
>         if is_ca(root_cert) and root_cert.subject == root_cert.issuer:  # Only extracts self-signed ROOT
>             ca_cert = certificates.pop()
>             return pem_encode([ca_cert]), pem_encode(certificates)
>         return None, pem_encode(certificates)
>
> This logic works for 2-level PKI (Leaf + Root) but fails for 3-level PKI (Leaf + Intermediate + Root) because:
> 1. The Root CA is correctly added to `trusted_ca.pem`
> 2. The Intermediate CA is NOT added to `trusted_ca.pem`
> 3. When Redis shard verifies DMC's client certificate (using `tls-auth-clients yes`), it cannot build
>    the trust chain because the Intermediate CA is missing

## Customer Impact

<Bullet list of customer-visible effects. Each bullet should be a concrete observable behavior.>

Example:
> - After uploading customer-provided INE certificates, the cluster becomes unhealthy
> - CRDB synchronization fails between clusters
> - DMC proxy logs show: `SSL routines::unexpected eof while reading`
> - Shards show: `ERROR: 503 Service Unavailable`
> - Disabling `data_internode_encryption` is the only workaround

## Steps to Reproduce

<Numbered list. Each step is a concrete action. Sub-steps allowed where setup is complex.>

Example:
> 1. Create a 3-level certificate chain:
>    - Leaf cert (signed by Intermediate CA)
>    - Intermediate CA cert (signed by Root CA)
>    - Root CA cert (self-signed)
> 2. Combine into a single PEM file in order: Leaf → Intermediate → Root
> 3. Upload as `data_internode_encryption` certificate via API or rladmin
> 4. Observe cluster health degradation

## Expected Behavior

<One short paragraph. What should happen.>

Example:
> All CA certificates in the chain (both Intermediate CAs and Root CA) should be added to `trusted_ca.pem`
> so that TLS client certificate verification succeeds.

## Actual Behavior

<One short paragraph. What does happen.>

Example:
> Only the Root CA is added to `trusted_ca.pem`. Intermediate CA certificates are dropped, resulting in
> a TLS verification failure.

## Evidence from Support Case

<Concrete artifacts: file contents, log excerpts, config snippets, output dumps. Use fenced code blocks.
Use bolded "label" subheaders if you have multiple evidence types.>

Example:
> **Certificate Chain Uploaded** (`data_internode_encryption_cert.pem`):
>
>     Certificate 1: CN=reddb.pmli.corp (Leaf — signed by SUB CA)
>     Certificate 2: CN=PNB MetLife SUB CA (Intermediate — signed by Root)  ← NOT ADDED TO trusted_ca
>     Certificate 3: CN=PNB MetLife Root Certificate Authority (Root — self-signed)  ← ADDED TO trusted_ca
>
> **trusted_ca.pem Contents:**
>
>     Certificate 1: CN=reddb.pmli.corp (Internal CA)
>     Certificate 2: CN=PNB MetLife Root Certificate Authority  ← Root CA only
>
> Missing: CN=PNB MetLife SUB CA (Intermediate CA)
>
> **Redis Shard Configuration:**
>
>     tls-auth-clients yes
>     tls-ca-cert-file /etc/opt/redislabs/trusted_ca.pem

## Workaround

<HEADING ONLY in the description. Actual workaround content lives in customfield_10374 (Workaround).
Do not duplicate. The heading exists in the description as a navigational marker.>

## Suggested Fix                                 ← OPTIONAL (only when TSE+eng have a hypothesis)

<Short paragraph or two with the proposed code/behavior change.>

Example:
> Modify `extract_ca_from_cert_chain()` to extract **all CA certificates** from the chain (not just the
> self-signed root) and add them to the trust store.
>
> Alternatively, add a new function that identifies all certificates with `is_ca() == True` and adds them
> to `trusted_ca.pem`.

## Related Code Paths                            ← OPTIONAL (only when engineering analysis present)

<Bulleted list of file paths with function names and line numbers.>

Example:
> - `cnm/cnm/certificates/operations.py`:
>   - `extract_ca_from_cert_chain()` — line 475
>   - `is_ca()` — line 305
>   - `add_certs_to_trusted_ca()` — line 578
> - `cnm/cnm/http_services/cluster_api/certificate_handler.py`:
>   - `_validate_certificate()` — lines 314-315 (calls extract_ca_from_cert_chain)
>   - `_update_certificates_on_all_nodes()` — lines 428-429 (only trusts root_ca)

## Support Package Reference

<S3 paths or other artifact links. Bulleted list.>

Example:
> - s3://gt-logs/exa-to-gt/ZD-160185-RED-194253/Prod_15April26_debuginfo.7D67D97046CF58EC.tar.gz
> - s3://gt-logs/exa-to-gt/ZD-160185-RED-194253/DR_debuginfo.EBFF57FC5A7198EC.tar.gz
```

## Workaround field content pattern (`customfield_10374`)

Multi-paragraph ADF with code blocks. Pattern:

```
<One-line statement of what to do>:

<code block with commands or config>

<Optional caveat paragraph explaining downsides / when this stops working>
```

Example from RED-194253:

```
Manually append the intermediate CA certificate to /etc/opt/redislabs/trusted_ca.pem on all nodes:

# Extract intermediate CA from the cert chain
# Append to trusted_ca.pem
cat intermediate_ca.pem >> /etc/opt/redislabs/trusted_ca.pem

But any upgrade or addition of nodes will need this change to be done manually. So not dependable.
I have asked the customer to disable INE temporarily.
```

ADF skeleton for this kind of content:

```jsonc
{
  "type": "doc",
  "version": 1,
  "content": [
    { "type": "paragraph",
      "content": [{ "type": "text", "text": "<lead-in sentence ending in colon>:" }] },
    { "type": "codeBlock",
      "attrs": { "language": "bash" },
      "content": [{ "type": "text", "text": "<commands here>" }] },
    { "type": "paragraph",
      "content": [{ "type": "text", "text": "<caveat paragraph>" }] }
  ]
}
```

## Notes / nuances

- **Labels are minimal**: just `Encryption, Support` — 2 labels. Not 5+.
- **Customer name appears in 2 fields** (`Affected Organizations` + `Seen by Customer/s`) but **NOT** in the description body. The description never starts with "**Customer:** PNB Metlife" or similar prefix.
- **The RCA template field is populated** even though this is a non-Azure ticket. This is the general 6-section template (sections 1-5 are placeholders).
- **Found By = Prod/Customer** and **Issue source = Product Bug** are set explicitly — both are required-feeling fields per how Support uses them.
- **No "Customer Expectations: Fix" line** in the description body. The Confluence doc says "include customer expectations" but real bugs convey this implicitly through structure (the presence of Suggested Fix → request is for a fix; the presence of RCA template → may need an RCA; etc.).
- **Code/config inline in description** uses fenced code blocks (or 4-space indent in the rendered Jira PDF). The skill should use fenced code blocks in markdown — Jira renders them.
- **Numbered & bulleted lists** are used heavily. Plain prose is rare in a real bug body.
