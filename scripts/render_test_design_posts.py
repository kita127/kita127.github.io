#!/usr/bin/env python3
import sys
from html import escape
from pathlib import Path

import markdown

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_DESIGN_ROOT = REPO_ROOT / "test_design"


def render_markdown(markdown_text: str) -> str:
    return markdown.markdown(markdown_text, extensions=["fenced_code", "sane_lists"])


def determine_title(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return "Article"


def build_html(markdown: str, source_path: Path) -> str:
    title = determine_title(markdown)
    body = render_markdown(markdown)
    return f"""<!DOCTYPE html>
<html lang=\"ja\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{escape(title)}</title>
  <link rel=\"stylesheet\" href=\"../../../css/pandoc-posts.css\">
</head>
<body>
  <article>
    {body}
  </article>
</body>
</html>
"""


def render_file(markdown_path: Path) -> Path:
    markdown = markdown_path.read_text(encoding="utf-8")
    html_path = markdown_path.with_suffix(".html")
    html_path.write_text(build_html(markdown, markdown_path), encoding="utf-8")
    return html_path


def main() -> int:
    if not TEST_DESIGN_ROOT.exists():
        print(f"Not found: {TEST_DESIGN_ROOT}", file=sys.stderr)
        return 1

    markdown_files = sorted(TEST_DESIGN_ROOT.rglob("*.md"))
    if not markdown_files:
        print("No markdown files found under test_design.")
        return 0

    for markdown_path in markdown_files:
        output_path = render_file(markdown_path)
        print(f"Generated {output_path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
