# tse-jira plugin — Roadmap

Forward-looking direction for the plugin. Captures deferred items, known performance issues, and ideas surfaced during real-world use. Items are loosely grouped by theme; check items off when shipped.

Last updated: 2026-06-01 (v0.15.4 — schema-truth update across DOC / MOD / RDSC + no-source-in-body rule for /tse-jira:doc).

## Recently shipped

### v0.15.4 — schema-truth update + no-source-in-body rule (2026-06-01)

The A1 dry-run review surfaced two distinct issues worth fixing in one patch:

- [x] **Encode the "no TSE-internal source attribution in description body" rule** in SKILL.md Workflow D + commands/doc.md. Marko's feedback: *"the actual jira should not reference this kind of source info"* — referring to closing lines like `**Source:** FF support audit 2026-05-26 (DOC_BUG_QUEUE A1; Wall #1 in DEPLOYMENT_LOG.md)`. Such attribution clutters the body, ages poorly, and adds zero value to the docs team reading the ticket. Captured as memory `feedback-no-internal-source-in-doc-body`. Pre-flight detect-and-warn (no auto-mutation) added to the skill's behavioral spec; active enforcement in the render pipeline deferred to v0.15.5+ if drift is observed.
- [x] **Schema-truth update for DOC / MOD / RDSC.** Live MCP queries against `redislabs.atlassian.net` confirmed/corrected several entries in `references/jira-schema.md`:
  - **DOC:** added `Design` (`customfield_10376`) and `Vulnerability` (`customfield_10395`) to the fields-that-exist list — previously missing. Confirmed Bug (10074) and Task (10023) have **identical 22-field schemas** (only issuetype differs).
  - **MOD:** clarified that `Found by` (`customfield_10178`, lowercase b) is a **different field** than RED's `Found By` (`customfield_10115`, capital B). Documented MOD's full field list (36 fields total) including BOTH `Impact Score` and `BugScore`.
  - **RDSC:** split into two distinct sections — **RDSC Bug** (10004, 29 fields, has dedicated `Steps to Reproduce`/`Expected Result`/`Actual Result` custom fields) and **RDI Customer Issue** (14992, 23 fields, **9 REQUIRED at schema level** including `Database Information`, `Type of Setup`, `Impact Score`). The two RDSC issue types have fundamentally different field sets — the plugin must branch on which one applies.
  - **Projects table:** expanded with an "Other TSE-relevant Issue Types" column to capture DOC Task (10023) and RDSC RDI Customer Issue (14992) alongside the defaults.
- [ ] **RDSC project ID still pending verification.** The table currently has `?` for RDSC; resolve via `getVisibleJiraProjects` next session.
- [ ] **Active detect-and-warn implementation for internal-source patterns in description body.** v0.15.4 documents the rule but doesn't enforce it in code. If TSEs (or AI drafting finding files) drift from the rule, add a pre-flight scan in the render flow that quotes offending paragraphs and asks for confirmation. v0.15.5+ candidate.
- [ ] **Add a canonical RDI Customer Issue extract to `references/canonical-jiras/`.** Next time we file via type 14992, save the structure as `RDSC-XXXXX-rdi-customer-issue.md` to anchor future filings.

### v0.15.3 — `{N}` placeholder + attach-warning fixes (2026-06-01)

Surfaced during the second real `/tse-jira:doc` live test (FF DOC A1, the OCI helm chart URL gap). Two bugs in v0.15.2 that the first test didn't catch:

- [x] **Add `N` to `SCALAR_PLACEHOLDERS` (for real this time).** v0.15.2's commit message claimed to add both `SUMMARY_FIRST_60_CHARS` and `N`, but only the former actually landed. `N` (the screenshot count) was still missing from the script's known-scalar set, generating `warning: unknown scalar placeholder 'N' — ignored` and leaving `{N}` literally in the rendered HTML.
- [x] **Make the `.attach-warning` div conditional on `screenshots_to_attach` being non-empty.** The template has a comment `<!-- Attachment warning (v0.10+): only render if customer-provided screenshots exist -->` but neither v0.15.0/0.15.1/0.15.2 actually enforced that. DOC tickets with no images were rendering a spurious "The {N} screenshots referenced below need to be manually attached..." notice — wrong on two counts (the {N} leak above + the block shouldn't appear at all). Now stripped via a new `strip_conditional_blocks()` pre-step that runs before `substitute_scalars` (because the matched template text contains `{N}`).
- [x] **Auto-compute `N` from `len(loops.screenshots_to_attach)` in `main()`.** Callers don't have to hand-set the count anymore — and if they do, their value is respected.
- [x] **Verified with `--strict` mode.** Re-rendering A1 with the same inputs now passes `--strict` (no unsubstituted placeholders) and the HTML drops from 23,704 → 23,315 bytes because the spurious attach-warning block is gone.

### v0.15.2 — render-html-preview.py handles empty loop arrays (2026-05-27)

- [x] **Patch `render-html-preview.py` to handle empty loop arrays.** First real `/tse-jira:doc` test showed that DOC tickets without related Jiras / labels / screenshots left the template's example placeholders (`{LINK_TYPE}`, `{LABEL}`, `{SCREENSHOT_FILENAME}`, etc.) in the output because the existing `if items:` branches only handled the non-empty case. Now empty arrays explicitly replace their example block with a muted "none" / "no labels" / "no attachments" notice. **Visual consistency with RED-bug previews restored** — DOC tickets now render through the same template + script.
- [x] ~~**Add `SUMMARY_FIRST_60_CHARS` + `N` to `SCALAR_PLACEHOLDERS`.**~~ ⚠️ Only `SUMMARY_FIRST_60_CHARS` actually landed in the v0.15.2 commit; `N` was missed. v0.15.3 closes the gap.
- [x] **Closes the DOC-HTML-template gap from v0.15.1 ROADMAP.** Turned out we didn't need a separate DOC template — the existing template handles DOC fine once empty arrays are cleaned up. Just needed `(n/a — DOC schema)` strings for the RED-only sidebar fields. (Future polish: make those sidebar sections conditional so they hide entirely when not applicable, instead of showing as "(n/a)" — but that's purely cosmetic and not blocking.)

### v0.15.1 — assignee-auto-suggest removal + DOC HTML template item (2026-05-27)

- [x] **Remove auto-suggest-assignee logic from `/tse-jira:doc`.** v0.15.0 auto-suggested Kaitlyn Michael for FF-prefixed titles. **This was the wrong design** — feedback from Marko during the first real test: "we shouldn't ever automatically set assignees. We should let Jira / the teams handle that." Updated `commands/doc.md` + SKILL.md Workflow D to make `--assignee <email>` explicit-user-provided only, with no auto-detection. Default is Unassigned. Captured as a general principle for future workflows: the skill should never infer an assignee.
- [ ] **Add a DOC-shaped HTML preview template.** v0.15.0 shipped with only the existing RED-bug-shaped `preview-template.html`. When `/tse-jira:doc` was first tested, the skill had to bypass `render-html-preview.py` and generate the HTML manually because the RED template has Severity/Component/Environment fields that don't apply to DOC. A `references/preview-template-doc.html` variant (or a project-shape switch in the existing template) would close this gap. Tracking issue: title-only for now; pick this up the next time DOC bugs are filed.

### v0.15.0 — `/tse-jira:doc` command (2026-05-27)

- [x] **Add `/tse-jira:doc` for DOC-project filings from internal findings.** The plugin had DOC schema support documented in `references/jira-schema.md` but no command that fit non-Zendesk-derived input. Added during the FeatureForm Support audit when ~15 doc bugs surfaced from internal observations (Support audit, Slack discussions) that didn't fit `/tse-jira:bug`'s Zendesk-PDF requirement.
  - Targets DOC project (id `10037`) with minimal field set per the existing schema doc
  - Supports both Bug (`10074`) and Task (`10023`) issue types — auto-detects from title
  - Renders `_Issue created in Slack from a [message](URL)._` footer matching DOC-6659 convention
  - Auto-suggests Kaitlyn Michael as assignee for FF-prefixed titles
  - Same dry-run / publish safety model as `/bug` and `/rca`
  - Updated `/new` interactive router to add Doc as a 4th option
  - Updated SKILL.md with full Workflow D specification

## Performance

The actual MCP write calls are fast; the slow part of a filing is the preview generation. Targets below cluster around making the dry-run cheaper, not the publish step.

- [ ] **Use `references/preview-template.html` template substitution instead of writing the HTML from scratch.**
  - **Observed problem:** During the v0.12.0 Aetna preview generation, writing the final `.html` (~42KB) took noticeably longer than expected. The skill is currently re-typing the whole CSS + layout boilerplate on every filing, even though `references/preview-template.html` was designed for placeholder substitution (`{SUMMARY}`, `{DESCRIPTION_HTML}`, `{PRIORITY}`, etc.).
  - **Fix:** `Read` the template once, then use `Edit` with the substitution placeholders to produce the final HTML. Only the description body + field values change per filing — the styles, layout primitives, and section structure are constant.
  - **Expected impact:** ~50% reduction in `.html` write time. The CSS block alone is ~160 lines that don't need to be regenerated per filing.
  - **SKILL.md already calls this out** — the skill is instructed to do template substitution but the implementation has drifted to "write the whole file from scratch." Bug in execution, not in design.

- [ ] **Consider a `.md` template too** (or a partial — at least the H2 section skeleton).
  - The H2 structure for Bug Jiras is canonical (Summary / Possible Root Cause / Customer Impact / Impact Score / Steps to Reproduce / Expected / Actual / Evidence / Workaround / Asks for R&D / Related Code Paths). Only the content inside each section changes.
  - Less impactful than the HTML template (the `.md` is ~27KB vs ~42KB) but the same idea.

- [ ] **Reduce interactive-mode prompt count by batching where possible.**
  - Today the bug flow runs ~7 sequential prompts. Some can be batched into a single `AskUserQuestion` with multiple questions: e.g., "Embed which screenshots? + Severity?" could be one round trip if the screenshots are detected.
  - Trade-off: batching increases cognitive load per prompt. Don't batch unrelated questions.

- [ ] **Cache schema option-ID lookups.**
  - The Affected Organizations dropdown has ~9,253 options and the `getJiraIssueTypeMetaWithFields` response is ~2MB. Currently the skill grep's a saved file on each filing.
  - Could cache `{customer_name → option_id}` mappings in `~/.claude/.tse-jira-cache.json`. Refresh on cache miss. Apply same idea to Severity / Component / Product / Found By / Issue Source — those are stable across filings.
  - Watch: cache stale-ness when JIRA Admins add/rename options. Validate on cache hit by checking the value back against the schema.

## Skill-encoded rules pending integration

Behavioral rules that have been captured as session memory but are not yet hard-coded into the SKILL.md / reference docs. The plugin currently relies on the agent re-reading memory at session start; integration into the docs would make the rules survive memory-bypass scenarios and be visible to other engineers.

- [ ] **Zendesk-is-not-Jira relevance filter** (memory: `feedback-zendesk-is-not-jira`, 2026-05-13)
  - Each candidate Evidence / Asks subsection has to pass the test: "Does this directly support understanding or fixing the bug?" If R&D would skim past it, drop it.
  - Real-world catch: Aetna TF bug v0.12 production filing included a "Key-name discrepancy" subsection (rfcTaxiAutomation-key vs taxi-redis-key) that wasn't load-bearing for the bug mechanism — removed in correction-pass after Marko flagged it.
  - **Integration target:** add a "Relevance filter" subsection to `references/zendesk-bug-mapping.md`'s "What to extract" guidance.

- [ ] **Dedicated custom-field sections (Workaround / Impact Score details / Action Items) — not body H2s** (memory: `feedback-dedicated-custom-field-sections`, 2026-05-13)
  - The RED project's Bug create/edit screen renders dedicated textarea sections below the description: RCA, Action Items, Release Notes, Workaround, Impact Score details. Content belongs in the **fields**, not in body H2 sections.
  - Real-world catch: RED-196844 (v0.12.0 Aetna TF bug filing) had body `## Workaround`, `## Impact Score`, and `## Asks for R&D` H2 sections that should have been (or also been) the corresponding field values: `customfield_10374`, `customfield_10681`, `customfield_10672`.
  - **Supersedes:** the earlier `feedback-impact-score-workflow` rule that said "add `## Impact Score` H2 to description body" — that destination was wrong. The Google Sheet → screenshot workflow is still valid, but the paste destination is the **Impact Score details field**, not a body section.
  - **Integration target:**
    - Update `references/zendesk-bug-mapping.md` description-body template to remove `## Workaround`, `## Impact Score`, `## Asks for R&D` H2 sections.
    - Update `references/jira-schema.md` to clearly document each dedicated field as the canonical content destination (currently buried in the field reference table — should be promoted to a "Description body vs custom-field sections" rules block at the top).
    - Update `references/impact-score-model.md` "Posting on the Ticket" section to point at `customfield_10681` instead of body.
    - Pre-flight Checks in dry-run preview should list each field's destination (Workaround → field / Impact Score details → field / Action Items → field) with ADF status.

- [ ] **Visual structure: horizontal separators between major sections + collapsible `expand` for long technical content** (preference 2026-05-13)
  - Marko's design preference: separate major H2 sections with horizontal rules; hide long technical content (Terraform error dumps, raw ADF, multi-page code excerpts) behind Jira's expand macro so the description stays scannable.
  - **Horizontal rules — easy.** ADF has a `rule` node. The MCP's markdown→ADF converter maps `---` on its own line to `rule`. Just include `---` between major sections in the description body. No code changes needed; just update `references/zendesk-bug-mapping.md` body template to use them.
  - **Expand macros — harder.** Jira Cloud expand is an ADF node:
    ```jsonc
    { "type": "expand", "attrs": { "title": "Click to see raw error output" },
      "content": [ /* nested paragraphs / code blocks / etc */ ] }
    ```
    The MCP markdown→ADF converter has no native expand syntax — `<details>` and `{expand}` Confluence-macro forms are dropped or passed through as text. To get real collapsibles, the description must be passed with `contentFormat: adf` and `expand` nodes constructed as JSON.
  - **Implementation paths:**
    1. **Markdown-mode only:** add `---` between sections. Skip expand. Description stays readable inline; long blocks (Actual Behavior code, raw ADF examples) stay visible. Cheapest.
    2. **ADF-mode for description:** switch the entire description to ADF. Enables expand. Requires the skill to construct an ADF document for the description (much more verbose than markdown). Custom fields already use ADF, so the templating cost is incremental but real.
    3. **Hybrid: markdown for prose + ADF substitution for specific sections.** Render the description body as markdown, then run a post-process that replaces `{{EXPAND title="X"}}...{{/EXPAND}}` markers with `expand` ADF nodes before sending. Most complex; preserves authoring readability.
  - **Recommendation when implementing:** start with path 1 (horizontal rules only). Measure whether the description still feels too long after that. Only escalate to path 2 if expand becomes necessary for specific known-long sections (raw TF apply output, multi-page debug logs).
  - **Integration target:** `references/zendesk-bug-mapping.md` body template (add `---` between H2 sections); SKILL.md interactive flow (offer the TSE the choice "wrap long technical blocks in expand?" at preview time if path 2 is implemented).
  - **Quick empirical test before committing:** create a test Jira in a sandbox project with `---` and an expand macro via the MCP, then `getJiraIssue` with `responseContentFormat: adf` to confirm both round-trip correctly. Cheap to validate.

- [ ] **Description body needs explicit image-paste markers, not abstract "see attached" references** (observation 2026-05-13, post-publish of RED-196844)
  - Current pattern: `See the attached "Override Region block.png" for the customer's exact HCL screenshot.` — names the file but doesn't tell the TSE filing the Jira *where* in the description body to paste the image after they upload it.
  - Better pattern: explicit paste-here markers at the spot the image belongs:
    ```
    📸 _Paste `Override Region block.png` here._
    ```
    Or even more explicit:
    ```
    [ ⬇️  paste customer's HCL screenshot here: `Override Region block.png`  ⬇️ ]
    ```
  - Each marker should:
    - Use a distinctive emoji or bracket convention so it's easy to spot scrolling the body
    - Name the file explicitly (path basename only — TSE matches against their local download)
    - Sit at the exact paragraph where the image should land in the rendered Jira
    - Be self-deleting after paste — i.e., the TSE removes the marker line when they drop the image (or the marker becomes the image's caption)
  - **Integration target:** update `references/zendesk-bug-mapping.md` and SKILL.md "Workflow A" guidance to use this pattern in `## Steps to Reproduce` and `## Evidence from Support Case`. Update HTML preview's `.screenshot` block CSS to render the marker visually (e.g., dashed border, "PASTE HERE" overlay).
  - Same applies to Workaround / Action Items / Impact Score details fields if they need images — paste-here markers at the right spot.

- [ ] **`## Customer Impact` H2 may be redundant** (observation 2026-05-13, post-publish of RED-196844)
  - Customer impact is often implied through other elements of a well-formed Bug: the Summary names the symptom, the Customer ARR component of the impact score captures business weight, the Workaround field describes whether the customer is blocked, the Affected Organizations field names who's affected. A dedicated `## Customer Impact` bullet list can end up restating these.
  - Marko's framing: "I also don't think 'Customer Impact' is totally justified as its own section since this is kind of implied throughout."
  - **Decision needed:** make it optional in the template (include only when the impact is non-obvious from the rest), or drop entirely from the default body template.
  - The canonical [RED-194253](https://redislabs.atlassian.net/browse/RED-194253) does have a Customer Impact section, but its description is heavier on raw customer-visible behavior (cluster unhealthy, CRDB sync fails, specific error strings) that doesn't double up with Summary. The RED-196844 (Aetna) version was more abstract ("blocks adoption", "breaks idempotency") — these read as restated framing.
  - **Integration target:** update `references/zendesk-bug-mapping.md` description-body template — mark `## Customer Impact` as OPTIONAL with a guidance note: "Include only when the customer-visible behavior is concrete and non-obvious from Summary. Skip when impact is implied through ARR, Affected Organizations, Workaround, or the symptom narrative."

- [ ] **Short AI-acknowledgment publishes; verbose Analysis Note doesn't** (memory: `feedback-tse-humility-with-rd`, refined 2026-05-13)
  - The full Analysis Note paragraph stays in preview-only metadata (top of `.md` / banner in `.html`).
  - A one-line acknowledgment at the start of "Possible Root Cause" — e.g., "Support-side hypothesis (AI-assisted code review of `<repo> @ <tag>`) — please verify." — DOES go in the publish-bound body. R&D readers need this signal for trust calibration.
  - Real-world catch: rev-3 of the Aetna preview removed the AI-acknowledgment entirely, then v0.12.0 fresh-flow regen rediscovered the need for the short version after Marko asked "why does our TSE hypothesis not mention this was ai assisted investigation of the codebase".
  - **Integration target:** update `references/zendesk-bug-mapping.md` description-body template to include the one-liner at the head of the "Possible Root Cause" section.

## Discovery / Inference

- [ ] **Glean Search for related Jiras** (proposed 2026-05-12, Aetna TF bug session)
  - When auto-inferring related Jiras from a Zendesk PDF, also run a Glean code/document search to find semantically-related Jiras that aren't explicitly cited in the thread.
  - Query patterns: customer name + topic area (e.g., `Aetna terraform`), customer name + key technical signal (e.g., `Aetna CMEK`), or symptom + product (e.g., `"Provider produced inconsistent result after apply" rediscloud`).
  - Use `mcp__claude_ai_Glean__search` if claude.ai Glean connector is available; surface top 3-5 candidate Jiras as additional options in the interactive prompt.
  - Implementation deferred — current flow uses Zendesk-PDF-text-only inference (per `feedback-auto-infer-related-jiras` memory rule).

- [ ] **Detect cluster-incident-shape RCAs for the Zendesk-required-waiver path**
  - Per v0.12 RCA contract: cluster-incident-shape RCAs (automation-initiated, e.g. RCA-563) waive the ≥1 Zendesk requirement.
  - Detection heuristics: cluster ID prefix in summary (`#prod__<date>_<cluster>-<account>_<symptom>`), `Reporter: Incident` on the source Jira, `causes` link types from CINC/PRB tickets.
  - Currently the interactive flow asks for Zendesk PDFs unconditionally — should branch when cluster-incident shape is detected.

## Schema / Field Resolution

- [ ] **Add a `Terraform` component or `terraform-provider` Component option to the RED Jira schema**
  - Today there's no dedicated component for TF provider bugs — they get filed against `Cloud API` as a proxy.
  - Action: file a JIRA Admin request to add `Terraform Provider` (or similar) as a component option on the RED project.
  - Once added, update `references/jira-schema.md` and bug auto-detection to route TF-related bugs to the new component.

- [ ] **Affected Organizations: cache common customer→option-ID mappings**
  - The 9,253-option dropdown is paginated and slow to search. The skill currently does up to 5 paged fetches.
  - Could keep a small `customer_id_cache.json` in the plugin (or in `~/.claude/`) mapping recently-resolved customer names → option IDs. Refresh on miss.
  - Trade-off: stale cache vs. token cost. Worth implementing if/when customer-name lookups become a noticeable latency cost.

## Interactive UX

- [ ] **Auto-suggest project from Zendesk PDF content with confidence score**
  - Current bug flow detects project from PDF keywords (RDSC / MOD / DOC / RED) but doesn't surface a confidence score to the user.
  - When confidence is medium/low, the AskUserQuestion prompt should highlight the auto-detected choice as "Recommended" and put the next-likeliest second.

- [ ] **Severity recommendation from impact-score components**
  - Today: TSE confirms severity manually (intentional — per Support docs, severity ≠ impact score).
  - Future: skill could recommend a severity based on the Data Loss / Data Unavailable / Downtime triple + Impact & Severity component. TSE still has final say.

## Publishing / Post-Create

- [ ] **Auto-attach files via Atlassian REST API**
  - MCP's `createJiraIssue` doesn't accept attachments — we tell the TSE to manually attach screenshots / Zendesk PDF / TF zip in the browser.
  - If the MCP ever exposes an attachment endpoint, automate that step. Until then: leave as a post-publish manual checklist item.

- [ ] **Google Sheets MCP integration for Impact Score Sheet** (proposed 2026-05-13, post-RED-196844 filing)
  - Currently the TSE manually adds a row to the [Impact Score Sheet](https://docs.google.com/spreadsheets/d/13HQaZGXtsRi0hWxqU0oQXTmQw1LfnnrkBGl3Y5-c1Sk/edit?gid=0#gid=0) for each filed Jira, then screenshots the row and pastes into `customfield_10681` (Impact Score details).
  - **Implementation paths:**
    1. **Sheets MCP write** — if a Google Sheets MCP server is available in claude.ai (or installed locally), the plugin appends a row programmatically — Jira key + 6 component scores + multipliers + final + reasoning columns. TSE doesn't touch the Sheet. Cleanest path.
    2. **Sheets API direct** — helper script that uses Google's OAuth + Sheets API. More setup (service account credentials, scope grants). Fallback.
  - After the row is in the Sheet, the screenshot step is either: (a) replaced by the next ROADMAP item (auto-render via headless browser), or (b) optional — the textual ADF breakdown in `customfield_10681` plus a deep-link to the Sheet row is arguably sufficient for R&D triage.
  - **Out of scope for v0.14.x.** Strong candidate for v0.15+.

- [ ] **Auto-paste Impact Score Sheet screenshot**
  - Today: TSE manually pastes a screenshot of the [Impact Score Google Sheet](https://docs.google.com/spreadsheets/d/13HQaZGXtsRi0hWxqU0oQXTmQw1LfnnrkBGl3Y5-c1Sk/edit?gid=0#gid=0) row into the `customfield_10681` (Impact Score details) field after creation.
  - Future: skill could programmatically render the breakdown row as an image (via headless browser + a Sheets URL with row filter applied) and add it to the Jira. Dependent on the Sheets MCP item above being implemented first.

## Documentation

- [ ] **End-to-end production filing video / GIF**
  - Once `/tse-jira:new` is battle-tested, record a short walkthrough showing the interactive flow from invocation → preview → publish → attachments. Embed in the marketplace README.

---

Last updated: 2026-05-12 (v0.12.0 ship + Aetna production-filing session)
