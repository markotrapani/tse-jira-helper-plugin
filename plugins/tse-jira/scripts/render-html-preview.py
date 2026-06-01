#!/usr/bin/env python3
"""
render-html-preview.py — substitute a Jira-preview field map into the
HTML preview template (`references/preview-template.html`) and write the
output to disk.

Purpose: the tse-jira skill should NOT write the full ~500-line HTML
template from scratch on every preview. That's slow (~30+ seconds of
agent tokens) and error-prone. This script does the substitution in a
single pass.

USAGE (called by the skill via Bash tool):

    python3 plugins/tse-jira/scripts/render-html-preview.py \
        --template /path/to/preview-template.html \
        --input /path/to/fields.json \
        --output /path/to/RED-bug-<timestamp>.html

The fields.json contains scalar placeholders (SUMMARY, PRIORITY, ...)
plus arrays for iteration sections (labels, screenshots, issue_links,
preflight_checks, sidebar_field_groups). Format documented in
`fields.schema.md` next to this script.

This is intentionally pure-stdlib (no dependencies) so it runs on any
macOS python3.x without setup.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path


# Scalar placeholders that get a direct string substitution.
SCALAR_PLACEHOLDERS = {
    "TICKET_KEY_OR_PREVIEW", "SUMMARY", "SUMMARY_FIRST_60_CHARS",
    "TYPE", "STATUS", "PROJECT", "PROJECT_NAME",
    "CANONICAL_ANCHOR", "ISO_TIMESTAMP", "SKILL_VERSION",
    "PRIORITY", "SEVERITY", "REPORTER", "ASSIGNEE", "SPRINT",
    "COMPONENT", "ENVIRONMENT", "PRODUCT", "REPORTED_VERSION",
    "AFFECTED_ORGS", "SEEN_BY", "ZENDESK_IDS", "ICM_IDS",
    "IMPACT_SCORE", "IMPACT_BAND", "FOUND_BY", "ISSUE_SOURCE",
    "DATA_LOSS", "DATA_UNAVAIL", "DOWNTIME",
    "WORKAROUND_HTML", "DESCRIPTION_HTML", "COMMENT_HTML",
    "CREATE_PAYLOAD_JSON", "COMMENT_PAYLOAD_JSON", "LINK_PAYLOADS_JSON",
    "MD_PATH", "HTML_PATH",
    "SCREENSHOT_SOURCE_DIR",
    "N",  # v0.15.3 — screenshot count, used in the attach-warning copy
    "RCA_SECTION_0",  # v0.15.5 — RCA template section 0 (Azure ACRE/AMR only; blank/n-a otherwise)
}

# Loop-style placeholders — the template contains a single example line
# per loop kind; we expand it per array element. The template uses a
# comment marker `<!-- LOOP: <kind> -->` then a single example using the
# loop's placeholder names. For backwards compatibility with the current
# template (which doesn't yet have explicit LOOP markers), we fall back
# to regex-based per-line expansion for the known patterns below.
LOOP_KINDS = {
    "preflight_checks": ["CHECK_ITEM"],
    "issue_links": ["LINK_TYPE", "LINKED_KEY", "LINKED_SUMMARY"],
    "labels": ["LABEL"],
    "screenshots_to_attach": ["SCREENSHOT_FILENAME"],
}


def substitute_scalars(template: str, fields: dict) -> str:
    """Replace {PLACEHOLDER} tokens with values from fields['scalars'].

    Unknown placeholders are left literal so the caller can spot missing
    inputs. HTML-escape policy: scalar values are inserted as-is (the
    template uses pre-escaped HTML in {DESCRIPTION_HTML} etc; trivia
    fields like {AFFECTED_ORGS} should already be plain text the user
    wants to render).
    """
    scalars = fields.get("scalars", {})
    output = template
    for key, value in scalars.items():
        if key not in SCALAR_PLACEHOLDERS:
            print(f"warning: unknown scalar placeholder '{key}' — ignored", file=sys.stderr)
            continue
        token = "{" + key + "}"
        output = output.replace(token, str(value))
    return output


def expand_loops(template: str, fields: dict) -> str:
    """Expand known loop-style placeholder lines.

    The current preview-template.html has single example lines that
    repeat-per-item. We expand them in place using the arrays in
    fields['loops']. Each loop kind is matched by the unique
    placeholder tokens it contains.
    """
    output = template
    loops = fields.get("loops", {})

    # PRE-FLIGHT CHECKS — single <li>{CHECK_ITEM}</li> in template
    # Each check item is itself an HTML fragment (the script writer can
    # add class="warning" / class="error" on each <li> if appropriate).
    items = loops.get("preflight_checks", [])
    if items:
        rendered = "\n        ".join(items)
        output = output.replace("<li>{CHECK_ITEM}</li>", rendered)
    else:
        # Empty: replace the example so the placeholder doesn't survive.
        output = output.replace(
            "<li>{CHECK_ITEM}</li>",
            '<li class="muted">(no pre-flight checks recorded)</li>',
        )

    # ISSUE LINKS — pattern with LINK_TYPE / LINKED_KEY / LINKED_SUMMARY
    example_link_block = (
        '      <div class="issue-link">\n'
        '        <span class="link-type-badge">{LINK_TYPE}</span>\n'
        '        <span>→</span>\n'
        '        <a href="https://redislabs.atlassian.net/browse/{LINKED_KEY}">{LINKED_KEY}</a>\n'
        '        <span style="color: var(--color-text-muted);">— {LINKED_SUMMARY}</span>\n'
        '      </div>'
    )
    items = loops.get("issue_links", [])
    if items:
        link_html_lines = []
        for link in items:
            link_html = (
                '      <div class="issue-link">\n'
                f'        <span class="link-type-badge">{html.escape(link["link_type"])}</span>\n'
                '        <span>→</span>\n'
                f'        <a href="https://redislabs.atlassian.net/browse/{html.escape(link["linked_key"])}">{html.escape(link["linked_key"])}</a>\n'
                f'        <span style="color: var(--color-text-muted);">— {html.escape(link["linked_summary"])}</span>\n'
                '      </div>'
            )
            link_html_lines.append(link_html)
        rendered = "\n".join(link_html_lines)
        output = output.replace(example_link_block, rendered)
    else:
        # Empty: replace the example block with a muted "none" notice
        output = output.replace(
            example_link_block,
            '      <p class="muted" style="margin: 0;">No related Jiras to link.</p>',
        )

    # LABELS — single <span class="label-pill">{LABEL}</span>
    items = loops.get("labels", [])
    if items:
        rendered = "\n        ".join(
            f'<span class="label-pill">{html.escape(lbl)}</span>' for lbl in items
        )
        output = output.replace('<span class="label-pill">{LABEL}</span>', rendered)
    else:
        output = output.replace(
            '<span class="label-pill">{LABEL}</span>',
            '<span class="muted">No labels.</span>',
        )

    # SCREENSHOTS_TO_ATTACH — single <li><code>{SCREENSHOT_FILENAME}</code></li>
    items = loops.get("screenshots_to_attach", [])
    if items:
        rendered = "\n          ".join(
            f'<li><code>{html.escape(s)}</code></li>' for s in items
        )
        output = output.replace(
            '<li><code>{SCREENSHOT_FILENAME}</code></li>', rendered
        )
    else:
        output = output.replace(
            '<li><code>{SCREENSHOT_FILENAME}</code></li>',
            '<li class="muted">(no attachments)</li>',
        )

    return output


def strip_conditional_blocks(template: str, fields: dict) -> str:
    """Remove conditional template blocks based on field state (v0.15.3+).

    Some template blocks should only render when their underlying data
    exists. This runs BEFORE substitute_scalars so it can match the
    untouched {PLACEHOLDER} tokens in the template text.

    Currently handles:
    - .attach-warning div — removed when screenshots_to_attach is empty.
      The template's comment says "only render if customer-provided
      screenshots exist" but v0.15.2 didn't enforce that. The block
      contains a `{N}` placeholder for the screenshot count, so it must
      be matched and removed before substitute_scalars replaces {N}.
    - Comment-to-be-posted H2 + comment-block (v0.15.5) — removed when
      COMMENT_HTML is empty, whitespace-only, or contains only an HTML
      comment. DOC tickets don't post a comment, so this prevents the
      heading-with-empty-body cosmetic noise.
    - RCA Template (Section 0) sidebar section (v0.15.5) — removed when
      RCA_SECTION_0 is missing, empty, or starts with "(n/a". DOC and
      non-Azure tickets don't populate the RCA template, so the sidebar
      block becomes filler.
    """
    output = template
    loops = fields.get("loops", {})
    scalars = fields.get("scalars", {})

    # v0.15.3: attach-warning
    screenshots = loops.get("screenshots_to_attach", [])
    if not screenshots:
        attach_warning_block = (
            '    <!-- Attachment warning (v0.10+): only render if customer-provided screenshots exist -->\n'
            '    <div class="attach-warning">\n'
            '      <strong>⚠️ Attachment workflow:</strong> The {N} screenshots referenced below need to be manually attached to the new Jira in the browser after creation. MCP <code>createJiraIssue</code> doesn\'t support attachments. Once attached, the image references in the description will resolve to inline images in Jira.\n'
            '    </div>'
        )
        output = output.replace(
            attach_warning_block,
            '    <!-- attachment workflow notice omitted: no attachments -->',
        )

    # v0.15.5: Comment-to-be-posted block — strip when COMMENT_HTML is empty
    # or contains only an HTML comment. The template block spans the H2
    # heading + the comment-block div + 2 leading/trailing newlines.
    comment_html = scalars.get("COMMENT_HTML", "").strip()
    comment_html_is_empty_or_html_comment = (
        not comment_html
        or re.fullmatch(r"\s*(?:<!--.*?-->\s*)+", comment_html, re.DOTALL) is not None
    )
    if comment_html_is_empty_or_html_comment:
        comment_section_block = (
            '    <h2>Comment to be posted (after create)</h2>\n'
            '    <div class="comment-block">\n'
            '      <div class="comment-header">\n'
            '        <span>📝 Comment by Marko Trapani (auto-posted after createJiraIssue)</span>\n'
            '        <span>{ISO_TIMESTAMP}</span>\n'
            '      </div>\n'
            '      <div class="comment-body">\n'
            '        {COMMENT_HTML}\n'
            '      </div>\n'
            '    </div>'
        )
        output = output.replace(
            comment_section_block,
            '    <!-- comment-to-be-posted section omitted: no comment for this ticket -->',
        )

    # v0.15.5: RCA Template (Section 0) sidebar — strip when RCA_SECTION_0
    # is missing, empty, or marked n/a. Azure ACRE/AMR tickets that DO
    # populate section 0 keep the block.
    rca_section_0 = scalars.get("RCA_SECTION_0", "").strip()
    rca_block_inapplicable = (
        not rca_section_0
        or rca_section_0.lower().startswith("(n/a")
        or rca_section_0.lower().startswith("n/a")
    )
    if rca_block_inapplicable:
        rca_sidebar_block = (
            '    <div class="sidebar-section">\n'
            '      <h3>RCA Template (Section 0)</h3>\n'
            '      <div class="field-row" style="grid-template-columns: 1fr; gap: 4px;">\n'
            '        <div class="field-label">0. Incident short description:</div>\n'
            '        <div class="field-value">{RCA_SECTION_0}</div>\n'
            '      </div>\n'
            '      <div class="field-row muted" style="grid-template-columns: 1fr;">\n'
            '        <div class="field-label" style="color: var(--color-text-subtle);">Sections 1-5 left as placeholders for Engineering / PM.</div>\n'
            '      </div>\n'
            '    </div>'
        )
        output = output.replace(
            rca_sidebar_block,
            '    <!-- RCA Template sidebar omitted: not applicable to this ticket (DOC schema, or non-Azure RED/MOD) -->',
        )

    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Substitute Jira-preview fields into preview-template.html",
    )
    parser.add_argument("--template", type=Path, required=True,
                        help="Path to preview-template.html")
    parser.add_argument("--input", type=Path, required=True,
                        help="Path to fields.json (see fields.schema.md)")
    parser.add_argument("--output", type=Path, required=True,
                        help="Path to write the substituted HTML")
    parser.add_argument("--strict", action="store_true",
                        help="Fail if any {PLACEHOLDER} remains after substitution")
    args = parser.parse_args()

    if not args.template.is_file():
        print(f"error: template not found: {args.template}", file=sys.stderr)
        return 2
    if not args.input.is_file():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 2

    template = args.template.read_text(encoding="utf-8")
    fields = json.loads(args.input.read_text(encoding="utf-8"))

    # v0.15.3: auto-compute the screenshot count `N` from the loops array, so
    # callers don't have to set it manually. If the caller already provided
    # scalars.N, respect that; otherwise derive from len(screenshots_to_attach).
    scalars = fields.setdefault("scalars", {})
    if "N" not in scalars:
        scalars["N"] = str(len(fields.get("loops", {}).get("screenshots_to_attach", [])))

    # v0.15.3: strip conditional blocks BEFORE scalar substitution so block
    # patterns containing {N} or other placeholders still match the template.
    rendered = strip_conditional_blocks(template, fields)
    rendered = substitute_scalars(rendered, fields)
    rendered = expand_loops(rendered, fields)

    # Detect unsubstituted placeholders (informational unless --strict).
    # v0.15.5: regex now allows digits in placeholder names — previously
    # `{RCA_SECTION_0}` (digit suffix) silently escaped detection, leading
    # to literal `{RCA_SECTION_0}` text in rendered output.
    leftover = sorted(set(re.findall(r"\{[A-Z][A-Z0-9_]+\}", rendered)))
    if leftover:
        msg = f"warning: {len(leftover)} unsubstituted placeholders: {', '.join(leftover[:10])}"
        if len(leftover) > 10:
            msg += " ..."
        print(msg, file=sys.stderr)
        if args.strict:
            return 3

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"wrote {args.output} ({len(rendered)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
