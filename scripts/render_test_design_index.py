#!/usr/bin/env python3
import re
import sys
from html import escape
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_DESIGN_ROOT = REPO_ROOT / "test_design"
INDEX_PATH = TEST_DESIGN_ROOT / "index.html"
START_MARKER = "<!-- generated-post-links:start -->"
END_MARKER = "<!-- generated-post-links:end -->"


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def extract_title(html_path: Path) -> str:
    html = html_path.read_text(encoding="utf-8")

    title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = strip_tags(title_match.group(1))
        if title:
            return title

    heading_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    if heading_match:
        title = strip_tags(heading_match.group(1))
        if title:
            return title

    return html_path.stem.replace("-", " ").title()


def extract_summary(html_path: Path) -> str:
    html = html_path.read_text(encoding="utf-8")
    body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.IGNORECASE | re.DOTALL)
    if not body_match:
        return ""

    body_html = body_match.group(1)
    text = strip_tags(body_html)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""

    sentences = re.split(r"(?<=[。.!?])\s+", text)
    summary = " ".join(sentences[:2])
    if len(summary) > 120:
        summary = summary[:117] + "..."
    return summary


def build_link_section(html_files: list[Path]) -> str:
    items = []
    for html_path in html_files:
        relative_path = html_path.relative_to(TEST_DESIGN_ROOT).as_posix()
        href = "./" + relative_path
        title = escape(extract_title(html_path))
        summary = escape(extract_summary(html_path))
        if summary:
            items.append(f'    <li><a href="{href}">{title}</a><div class="post-summary">{summary}</div></li>')
        else:
            items.append(f'    <li><a href="{href}">{title}</a></li>')

    return f"""{START_MARKER}
<section>
  <h2>記事一覧</h2>
  <ul>
{chr(10).join(items)}
  </ul>
</section>
{END_MARKER}"""


def update_index_html(index_html: str, section_html: str) -> str:
    pattern = re.compile(rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}", re.DOTALL)
    if pattern.search(index_html):
        return pattern.sub(section_html, index_html, count=1)

    if "</main>" in index_html:
        return index_html.replace("</main>", f"{section_html}\n</main>", 1)

    return index_html.replace("</body>", f"{section_html}\n</body>", 1)


def main() -> int:
    if not TEST_DESIGN_ROOT.exists():
        print(f"Not found: {TEST_DESIGN_ROOT}", file=sys.stderr)
        return 1

    html_files = sorted(
        path
        for path in TEST_DESIGN_ROOT.rglob("*.html")
        if path.is_file() and path != INDEX_PATH
    )

    if not html_files:
        print("No HTML files found under test_design.")
        return 0

    index_html = INDEX_PATH.read_text(encoding="utf-8")
    section_html = build_link_section(html_files)
    updated_html = update_index_html(index_html, section_html)

    if updated_html != index_html:
        INDEX_PATH.write_text(updated_html, encoding="utf-8")
        print(f"Updated {INDEX_PATH.relative_to(REPO_ROOT)}")
    else:
        print("No change needed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
