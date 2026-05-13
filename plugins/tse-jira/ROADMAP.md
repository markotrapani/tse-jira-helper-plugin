# tse-jira plugin — Roadmap

Forward-looking direction for the plugin. Captures deferred items, known performance issues, and ideas surfaced during real-world use. Items are loosely grouped by theme; check items off when shipped.

Last updated: 2026-05-13 (during the v0.12.0 Aetna production-filing session).

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

- [ ] **Auto-paste Impact Score Sheet screenshot**
  - Today: TSE manually pastes a screenshot of the [Impact Score Google Sheet](https://docs.google.com/spreadsheets/d/13HQaZGXtsRi0hWxqU0oQXTmQw1LfnnrkBGl3Y5-c1Sk/edit?gid=0#gid=0) row into the Impact Score body section after creation.
  - Future: skill could programmatically render the breakdown as an image (via headless browser + a Sheets URL with row filter applied) and add it as a Jira attachment.

## Documentation

- [ ] **End-to-end production filing video / GIF**
  - Once `/tse-jira:new` is battle-tested, record a short walkthrough showing the interactive flow from invocation → preview → publish → attachments. Embed in the marketplace README.

---

Last updated: 2026-05-12 (v0.12.0 ship + Aetna production-filing session)
