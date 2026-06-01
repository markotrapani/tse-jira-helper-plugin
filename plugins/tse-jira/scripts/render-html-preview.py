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
    """
    output = template
    loops = fields.get("loops", {})

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

    # Detect unsubstituted placeholders (informational unless --strict)
    leftover = sorted(set(re.findall(r"\{[A-Z][A-Z_]+\}", rendered)))
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
